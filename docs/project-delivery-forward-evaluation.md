# Project delivery forward evaluation — 2026-08-31

These are five independent Agent executions of synthetic scenarios, not external-user adoption, live-price validation or field acceptance. Raw prompts, capability boundaries and sanitized actual outcome excerpts are in `tests/evaluations/project-delivery-forward.json`.

The evaluations ran against the development working tree based on `4cbc67e`, not an immutable release. During evaluation, fixes/clarifications were made as noted below. Final deterministic regressions and specific reruns cover those changes; this is not a claim that every full Agent answer was regenerated after every edit.

| Scenario | Observed result | Review |
|---|---|---|
| Small offline line | 3 occupied ports; 4 including stated reserve; 11 unpriced BOM rows; 6 diagram nodes/5 edges; protocol remains conditional | Preserved grouping, no invented industrial redundancy or protocol. Initial source/no-access manifest confusion corrected and hash-check rerun; conditional route/units remain |
| SCADA license/adapter | 3038 required versus 3000 licensed; native failure retained; expired license and incomplete mapping block readiness | Actual acceptance checker FAIL/exit 1; no promotion of adapter/sample evidence to native/field proof |
| Budget revision | Hold 130000 CNY provisionally; B not exact; mixed commercial bases rejected; 2×100 vs 1 blocked; 4-row TBD draft generated | Original missing fields remained missing; separate synthetic fixture exercises were explicitly distinguished |
| Phased factory | Phase-one PoE 600W; final AP quantity unknown; 100-AP/3000W is only a capacity scenario | Locked dual core/dual exit retained; capability/configuration/verification/owner separated. Unknown port aggregate issue corrected to null and original record rerun |
| Brownfield | No direct ARM/Linux purchase, no final hardware; CONDITIONAL/exit 1; unpriced pre-inquiry and recovery requirements | WIM/boot/DSN not treated as recovery; 4h/zero-current-day-loss constraints preserved. Generic guide still relies on the brownfield reference for the right question priority |

## Actual render check

A local Agent QA run generated a small synthetic Draw.io draft and exported it with the installed Draw.io CLI. The first PNG exposed links crossing intermediate boxes. The draft layout was changed to a deterministic breadth-first layout with separated connection anchors. A second export was inspected: relevant boxes/labels and hub links were readable with no intermediate-box crossings in that example. An unlinked AP remained visibly unlinked rather than inventing a connection; the record checker now warns about network assets without declared links.

This confirms only that local example/renderer. Dense graphs, custom vendor icons, compressed inputs, Word embedding and surveyed physical drawings are not certified by it. The tool continues to output `visual_qa=NOT_RUN` because it itself does not render.

## Tool/validation qualifications

- The first local Draw.io export exited 134 in the sandbox; the authorized GUI export succeeded and produced inspected PNGs.
- The bundled Skill validator initially lacked PyYAML; a temporary isolated dependency installation was used, with no system or project dependency change.
- Staged `gh skill publish --dry-run` succeeded with advisory warnings about the absent recommended frontmatter license and the copy not being a Git repository. No publish command was executed.
- The 20 planned acceptance cases are covered by executable unit/CLI checks and the relevant Agent evaluations; not all are automatic judgments. In particular compliance applicability and user-intent routing need review of actual Agent output.
- Future releases should replay these prompts against the tagged build and retain their own output/review record. Do not count this file or a prompt's existence as a new execution.
