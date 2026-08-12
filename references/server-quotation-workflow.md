# Server quotation workflow

Freeze an RFQ baseline before asking for price. Include CPU/core requirements, memory capacity and module layout, disks and endurance, RAID/cache/PLP, NICs/transceivers, redundant power, rails, licenses, support, implementation, tax, freight, delivery, validity and orderability.

Run `python3 scripts/compare_server_quotes.py assets/server-rfq-example.json --pretty`. A quote may enter the budget anchor only when technical and commercial gates both pass. Base prices, partial configurations, expired offers, mixed currencies and duplicate evidence remain context only.

Two independent exact-configuration quotes provide a control range. Use the median as a negotiation target, the high quote plus an explicit risk reserve as the control ceiling, and never use a weak web listing by itself to reduce an existing budget.
