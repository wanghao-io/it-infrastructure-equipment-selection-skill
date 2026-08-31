# Cabling Estimates

Use only when cable quantity or physical routing is requested. Do not interpret a logical topology as a surveyed cable route.

## Evidence and inputs

Record source drawing/version, unit calibration, route endpoints, tray/path basis and a site-survey owner.
Keep horizontal path, vertical travel, cabinet termination slack, detours, waste and procurement rounding separate.
Use user/site/vendor constraints rather than a universal extra-length percentage.
A user requesting more reserve changes the explicit reserve/detour input, not the source measurement.

```text
route_m = path_m + vertical_m + termination_m + detour_m
purchase_m = ceil(route_m × (1 + waste_ratio) / round_to_m) × round_to_m
```

The project-delivery helper implements this formula and labels any non-surveyed or uncalibrated route as estimated.
Do not add the same slack in both path and detour/waste.
Compare distance with the selected media/interface's current official limit; no generic distance rule proves a particular link.
Account for fiber cores, connector pairs, termination panels, transceivers/DAC/AOC and spare paths separately.

## Negative cases

- Undefined CAD units cannot produce a measured construction length.
- Straight-line distance does not prove a tray route.
- A five-core cable does not identify RS485, Modbus, analog IO or gateway compatibility.
- Fourteen machines sharing a controller do not automatically consume fourteen switch ports.
- Increasing reserve must not lower procurement length.

## Survey output

Who supplies the information, source/locator, required decision, measurement method, uncertainty and update trigger.
For WLAN also record client density/type, roaming, metal obstructions, ceiling height, interference, mounting, coverage and capacity measurements. Area-only AP counts remain preliminary.
