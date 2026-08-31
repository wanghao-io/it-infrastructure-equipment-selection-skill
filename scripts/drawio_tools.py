#!/usr/bin/env python3
"""Optional Draw.io draft adapter and presentation-only semantic guard."""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from contracts import strict_json_dumps
from project_records import check_record, guarded_path, load_record, preflight, write_new


def parse(text):
    if len(text) > 20_000_000 or "<!DOCTYPE" in text.upper() or "<!ENTITY" in text.upper():
        raise ValueError("oversized XML or DTD/entity declarations are not allowed")
    document = ET.fromstring(text)
    pages = document.findall("diagram") if document.tag == "mxfile" else [document]
    if not pages:
        raise ValueError("no Draw.io pages")
    for page in pages:
        graph = page if page.tag == "mxGraphModel" else page.find("mxGraphModel")
        if graph is None or graph.find("root") is None:
            raise ValueError("compressed/unsupported Draw.io page; export uncompressed XML first")
    return document, pages


def graph_root(page):
    return (page if page.tag == "mxGraphModel" else page.find("mxGraphModel")).find("root")


def semantic_snapshot(text):
    _, pages = parse(text)
    signatures = {}
    for page in pages:
        page_id = page.get("id", "single-page")
        if page_id in signatures:
            raise ValueError("duplicate page ID")
        root = graph_root(page)
        ids = [e.get("id") for e in root.iter() if e.get("id") is not None]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate Draw.io ID")
        known = set(ids)
        for cell in root.iter("mxCell"):
            for key in ("parent", "source", "target"):
                if cell.get(key) is not None and cell.get(key) not in known:
                    raise ValueError(f"unknown {key} reference")
            if cell.get("edge") == "1" and (not cell.get("source") or not cell.get("target")):
                raise ValueError("edge has unresolved endpoints")
        def semantic(node):
            if node.tag in {"mxGeometry", "mxPoint", "mxRectangle", "Array"}:
                return None
            attrs = {k: v for k, v in node.attrib.items() if k != "style"}
            children = [value for child in node if (value := semantic(child)) is not None]
            return [node.tag, attrs, (node.text or "").strip(), children]
        signatures[page_id] = {
            "name": page.get("name"),
            "cells": sorted((semantic(c) for c in root), key=lambda v: json.dumps(v, sort_keys=True)),
        }
    return signatures


def compare_presentations(before, after):
    equal = semantic_snapshot(before) == semantic_snapshot(after)
    return {"status": "PASS" if equal else "FAIL", "semantic_equal": equal,
            "visual_qa": "NOT_RUN", "scope": "IDs, labels, hierarchy, metadata and endpoints; not style-encoded engineering meaning"}


def clone_group(root, group_id, prefix):
    """Copy a group plus all parent-linked descendants; rewrite every reference."""
    direct = {e.get("id"): e for e in root if e.get("id") is not None}
    if group_id not in direct:
        raise ValueError("icon group is missing")
    owned = {group_id}
    while True:
        extra = {key for key, node in direct.items()
                 if (node if node.tag == "mxCell" else node.find("mxCell")) is not None
                 and (node if node.tag == "mxCell" else node.find("mxCell")).get("parent") in owned}
        if extra <= owned:
            break
        owned.update(extra)
    mapping = {key: prefix + key for key in owned}
    if set(mapping.values()) & set(direct):
        raise ValueError("cloned icon IDs collide")
    result = []
    for key in sorted(owned):
        node = copy.deepcopy(direct[key])
        for child in node.iter():
            for attr in ("id", "parent", "source", "target"):
                if child.get(attr) in mapping:
                    child.set(attr, mapping[child.get(attr)])
                elif attr in {"source", "target"} and child.get(attr) is not None:
                    raise ValueError("icon contains an external connection")
        result.append(node)
    return result


def create(data):
    result = check_record(data, "project-delivery")
    if result["status"] == "FAIL":
        raise ValueError("delivery record is inconsistent; validate it before drawing")
    if not data["assets"]:
        raise ValueError("no assets to draw")
    doc = ET.Element("mxfile")
    page = ET.SubElement(doc, "diagram", id=data["baseline_id"], name="Logical draft")
    graph = ET.SubElement(page, "mxGraphModel", grid="1", page="1", pageWidth="1600", pageHeight="1200")
    root = ET.SubElement(graph, "root")
    ET.SubElement(root, "mxCell", id="0")
    ET.SubElement(root, "mxCell", id="1", parent="0")
    # A deterministic breadth-first layout keeps hub links away from unrelated
    # boxes. It is only a draft layout; cycles/dense graphs still need visual QA.
    neighbors = {a["id"]: set() for a in data["assets"]}
    for link in data["links"]:
        neighbors[link["source"]].add(link["target"])
        neighbors[link["target"]].add(link["source"])
    unseen, layers, offset = set(neighbors), {}, 0
    while unseen:
        seed = sorted(unseen, key=lambda key: (-len(neighbors[key]), key))[0]
        frontier, depth = [seed], 0
        unseen.remove(seed)
        while frontier:
            layers[offset + depth] = sorted(frontier)
            following = set()
            for node in frontier:
                following.update(neighbors[node] & unseen)
            unseen.difference_update(following)
            frontier = sorted(following)
            depth += 1
        offset += depth + 1
    height = max(len(nodes) for nodes in layers.values())
    positions = {key: (80 + layer * 440, 80 + (row + (height - len(nodes)) / 2) * 150)
                 for layer, nodes in layers.items() for row, key in enumerate(nodes)}
    for asset in data["assets"]:
        label = f"{asset['id']} | {asset['model'] or 'model TBD'}\nqty {asset['quantity'] if asset['quantity'] is not None else 'TBD'} | {asset['phase_id']} | {asset['disposition']}"
        cell = ET.SubElement(root, "mxCell", id="asset:" + asset["id"], value=label,
                             asset_id=asset["id"], phase_id=asset["phase_id"], disposition=asset["disposition"],
                             vertex="1", parent="1",
                             style="rounded=1;whiteSpace=wrap;html=0;fillColor=#e6f1ff;strokeColor=#234b74;fontColor=#142b42;fontSize=13;")
        x, y = positions[asset["id"]]
        ET.SubElement(cell, "mxGeometry", x=str(x), y=str(y), width="280", height="90", **{"as": "geometry"})
    for link in data["links"]:
        forward = positions[link["target"]][0] > positions[link["source"]][0]
        def port(node, other):
            peers = sorted(neighbors[node], key=lambda key: positions[key][1])
            return 0.5 if len(peers) < 2 else 0.15 + 0.7 * peers.index(other) / (len(peers) - 1)
        label = link["medium"]
        if link.get("cable_cores") is not None:
            label += f" | {link['cable_cores']} cores"
        if link["protocol"] is None:
            label += " | protocol TBD"
        cell = ET.SubElement(root, "mxCell", id="link:" + link["id"], value=label,
                             edge="1", parent="1", source="asset:" + link["source"], target="asset:" + link["target"],
                             medium=link["medium"], protocol=link["protocol"] or "TBD",
                             style=f"edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=none;strokeColor=#526579;fontColor=#263746;labelBackgroundColor=#ffffff;exitX={1 if forward else 0};entryX={0 if forward else 1};exitY={port(link['source'], link['target'])};entryY={port(link['target'], link['source'])};")
        ET.SubElement(cell, "mxGeometry", relative="1", **{"as": "geometry"})
    text = ET.tostring(doc, encoding="unicode")
    semantic_snapshot(text)
    return text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    check = sub.add_parser("check", help="Structural check only; does not render")
    check.add_argument("input", type=Path)
    diff = sub.add_parser("compare", help="Guard a presentation-only edit")
    diff.add_argument("before", type=Path)
    diff.add_argument("after", type=Path)
    generate = sub.add_parser("create", help="Generate a logical draft, not physical/cabling layout")
    generate.add_argument("input", type=Path)
    generate.add_argument("output", type=Path)
    generate.add_argument("--manifest", type=Path, required=True)
    generate.add_argument("--project-root", type=Path, required=True)
    args = parser.parse_args()
    if args.action == "create":
        manifest = load_record(args.manifest)
        preflight(manifest, "project-evidence")
        data = load_record(guarded_path(args.project_root, manifest, args.input))
        if (manifest["project_id"], manifest["baseline_id"]) != (data.get("project_id"), data.get("baseline_id")):
            raise ValueError("manifest and delivery baseline differ")
        text = create(data)
        write_new(args.output, text, root=args.project_root, manifest=manifest)
        result = {"status": "PASS", "scope": "draft-created-and-structure-checked", "visual_qa": "NOT_RUN"}
    elif args.action == "compare":
        result = compare_presentations(args.before.read_text(encoding="utf-8"), args.after.read_text(encoding="utf-8"))
    else:
        snapshots = semantic_snapshot(args.input.read_text(encoding="utf-8"))
        result = {"status": "PASS", "pages": len(snapshots), "scope": "structure-only", "visual_qa": "NOT_RUN"}
    print(strict_json_dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, ET.ParseError) as exc:
        raise SystemExit(f"error: {exc}") from None
