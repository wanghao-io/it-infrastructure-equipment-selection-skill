# Server quotation workflow

Freeze an RFQ baseline before asking for price. Include CPU/core requirements, memory capacity and module layout, disks and endurance, RAID/cache/PLP, NICs/transceivers, redundant power, rails, licenses, support, implementation, tax, freight, delivery, validity and orderability.

Use `server-rfq-v2` for exact-configuration decisions and run `python3 scripts/compare_server_quotes.py assets/server-rfq-v2-example.json --pretty`. V2 records CPU model/socket/core scope, DIMM layout, disk media/count/capacity/endurance, RAID, NIC/optics, power, rails, service level and an explicit commercial-scope basis. A quote may enter the budget anchor only when technical and commercial gates both pass. Base prices, partial configurations, expired offers, mixed currencies and duplicate evidence remain context only.

`server-rfq-v1` remains supported only as a coarse minimum gate. It cannot support an `Exact-config` or `High` claim because its frozen fields do not identify the full procurement object. Reissue a v2 RFQ before reducing a protected server budget from v1 results.

Two supplier-independent exact-configuration quotes provide a control range; two quote numbers from one supplier still count as one source. Set an explicit `as_of_date`, reject quotes older than the allowed freshness window (90 days by default), and validate the quote validity date. Use the median as a negotiation target, the high quote plus an explicit non-negative risk reserve as the control ceiling, and never use a weak web listing by itself to reduce an existing budget.

Minimum capacity and exact configuration are separate gates. V2 minimum checks use numeric lower bounds, but an anchor must also match the declared configuration exactly (including socket/DIMM/drive counts and optional declared fields). Technically adequate upgrades remain visible as alternatives, not as the same purchasing object.

The comparator requires equal normalized tax-inclusion, tax-basis and delivery-basis declarations as well as the scope ID. It does not translate commercial text or infer tax rates. Differences require documented normalization outside the comparator before reuse. An equal scope ID cannot override those differences.

V2 covers its declared fields only; it does not prove chassis/option order codes, warranty territory, license entitlement, deployment compatibility or source truth. Freeze these in the RFQ/evidence record and retain any gap as CONDITIONAL. High confidence is relative to the supplied comparable quotations, not an independent procurement certification.
