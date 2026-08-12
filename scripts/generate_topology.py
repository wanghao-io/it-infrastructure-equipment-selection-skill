#!/usr/bin/env python3
"""Generate Mermaid or Graphviz DOT network topology from structured JSON input."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from contracts import optional_bool


def load_json(path: str) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate(data: dict[str, Any]) -> None:
    zones = data.get("zones", [])
    devices = data.get("devices", [])
    links = data.get("links", [])

    zone_ids = [str(z.get("id")) for z in zones]
    device_ids = [str(d.get("id")) for d in devices]
    if len(zone_ids) != len(set(zone_ids)):
        raise ValueError("Duplicate zone id detected.")
    if len(device_ids) != len(set(device_ids)):
        raise ValueError("Duplicate device id detected.")

    known = set(device_ids)
    known_zones = set(zone_ids)
    for device in devices:
        if device.get("zone") is not None and str(device.get("zone")) not in known_zones:
            raise ValueError(f"Device references unknown zone: {device.get('id')} -> {device.get('zone')}")
    for link in links:
        source = str(link.get("source"))
        target = str(link.get("target"))
        if source not in known or target not in known:
            raise ValueError(f"Link references unknown device: {source} -> {target}")


def esc_mermaid(text: Any) -> str:
    return str(text).replace('"', "'").replace("\n", " ")


def mermaid(data: dict[str, Any]) -> str:
    validate(data)
    direction = str(data.get("direction", "LR")).upper()
    if direction not in {"LR", "RL", "TB", "BT"}:
        direction = "LR"

    zones = data.get("zones", [])
    devices = data.get("devices", [])
    links = data.get("links", [])
    by_zone: dict[str, list[dict[str, Any]]] = {}
    unzoned: list[dict[str, Any]] = []
    for d in devices:
        zid = d.get("zone")
        if zid:
            by_zone.setdefault(str(zid), []).append(d)
        else:
            unzoned.append(d)

    lines = [f"flowchart {direction}"]
    zone_map = {str(z.get("id")): z for z in zones}
    for zid, zone in zone_map.items():
        label = esc_mermaid(zone.get("label", zid))
        lines.append(f'  subgraph {zid}["{label}"]')
        for d in by_zone.get(zid, []):
            did = str(d.get("id"))
            label = esc_mermaid(d.get("label", did))
            lines.append(f'    {did}["{label}"]')
        lines.append("  end")

    for d in unzoned:
        did = str(d.get("id"))
        label = esc_mermaid(d.get("label", did))
        lines.append(f'  {did}["{label}"]')

    for link in links:
        source = str(link.get("source"))
        target = str(link.get("target"))
        label = esc_mermaid(link.get("label", ""))
        arrow = "<-->" if optional_bool(link.get("bidirectional"), "bidirectional") else "-->"
        if label:
            lines.append(f'  {source} {arrow}|"{label}"| {target}')
        else:
            lines.append(f"  {source} {arrow} {target}")
    return "\n".join(lines)


def esc_dot(text: Any) -> str:
    return str(text).replace('\\', '\\\\').replace('"', '\\"').replace("\n", " ")


def dot(data: dict[str, Any]) -> str:
    validate(data)
    zones = data.get("zones", [])
    devices = data.get("devices", [])
    links = data.get("links", [])
    by_zone: dict[str, list[dict[str, Any]]] = {}
    unzoned: list[dict[str, Any]] = []
    for d in devices:
        zid = d.get("zone")
        if zid:
            by_zone.setdefault(str(zid), []).append(d)
        else:
            unzoned.append(d)

    lines = ["digraph topology {", "  rankdir=LR;"]
    for zone in zones:
        zid = str(zone.get("id"))
        label = esc_dot(zone.get("label", zid))
        lines.append(f"  subgraph cluster_{zid} {{")
        lines.append(f'    label="{label}";')
        for d in by_zone.get(zid, []):
            did = str(d.get("id"))
            label = esc_dot(d.get("label", did))
            lines.append(f'    {did} [label="{label}"];')
        lines.append("  }")

    for d in unzoned:
        did = str(d.get("id"))
        label = esc_dot(d.get("label", did))
        lines.append(f'  {did} [label="{label}"];')

    for link in links:
        source = str(link.get("source"))
        target = str(link.get("target"))
        label = esc_dot(link.get("label", ""))
        attrs = []
        if label:
            attrs.append(f'label="{label}"')
        if optional_bool(link.get("bidirectional"), "bidirectional"):
            attrs.append('dir="both"')
        suffix = f" [{', '.join(attrs)}]" if attrs else ""
        lines.append(f"  {source} -> {target}{suffix};")
    lines.append("}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Mermaid or Graphviz DOT network topology from JSON.")
    parser.add_argument("input", help="Topology JSON input")
    parser.add_argument("--format", choices=["mermaid", "dot"], default="mermaid")
    parser.add_argument("-o", "--output", help="Output file; stdout if omitted")
    parser.add_argument("--markdown", action="store_true", help="Wrap Mermaid output in a Markdown code fence")
    args = parser.parse_args()

    data = load_json(args.input)
    text = mermaid(data) if args.format == "mermaid" else dot(data)
    if args.format == "mermaid" and args.markdown:
        text = f"```mermaid\n{text}\n```"

    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)


if __name__ == "__main__":
    main()
