# Draw.io and Document Delivery

Use for explicit Draw.io artifacts, physical-location views, or presentation-only changes.

## Optional adapter

`scripts/drawio_tools.py create delivery.json out/topology.drawio --manifest manifest.json --project-root /explicit/project`
creates an uncompressed logical draft from project-delivery-v1. It refuses inconsistent inputs, wrong baselines, protected/escaping paths and overwrite.
It does not create surveyed physical placement, a complete vendor icon library or a CAD conversion.

`scripts/drawio_tools.py check diagram.drawio` checks IDs, parent/edge references and pages.
`scripts/drawio_tools.py compare before.drawio after.drawio` checks presentation-only semantic equality.
Compressed diagrams must be exported as uncompressed XML with a suitable tool first; never silently discard a page.

The library's `clone_group` copies a chosen icon group plus descendants with remapped IDs.
It rejects external edge references/collisions. Use only explicitly supplied/licensed icon libraries.
The draft CLI uses plain shapes; composing vendor icons remains an explicit adapter step, not an automatic promise.

## Three independent gates

1. Structure: XML/pages/IDs/parents/endpoints.
2. Engineering semantics: equipment, quantity, labels, phase, optional state and security-zone ownership.
3. Visual QA: actual rendered pages at overall and readable-detail scales, labels, crossings, contrast, clipping and printing.

A parser PASS is not a rendered QA PASS. The helper always returns visual_qa=NOT_RUN.
When render tools are unavailable, report visual QA incomplete; do not certify the figure.
Style can encode engineering meaning in existing drawings (arrow direction, color-coded zones, dashed optional links). The semantic guard excludes style: review that legend manually or first extract explicit metadata.
Reject DTD/entity XML and oversized inputs.

## Editing modes

In presentation-only mode preserve IDs, labels, endpoints, quantities, hierarchy and custom engineering metadata.
Change only authorized geometry/style. Do not reinterpret the design to make layout easier.
Engineering changes require updated baseline and downstream BOM/RFQ review.
Use logical, physical-location and cabling views separately. If the user requests only a physical view, do not substitute a logical diagram.

Keep approved document fonts/styles and content. Replace only requested images/sections, update embedded-image baseline and render the final document using an available document tool.
No automatic font replacement, entire-document regeneration or vendor restriction removal.
Complex drawings need unambiguous routing, not necessarily zero crossings; use bridge marks, grouping or separate pages when appropriate.
