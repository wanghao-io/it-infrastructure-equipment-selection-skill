# Procurement Research and Evidence Workflow

Use this reference when selecting real equipment, estimating budgets, validating current models, or comparing market prices.

For highly configurable enterprise equipment also load `references/exact-configuration-pricing.md` and `references/price-evidence.md`.

For current/live prices, quotation-oriented BOMs, or "how much can I buy it for now?" requests, also load `references/live-price-research.md`.

## 1. Separate Evidence Types

Do not use one source hierarchy for everything. Treat these as different evidence classes:

1. technical specification evidence;
2. compatibility/certification evidence;
3. lifecycle and availability evidence;
4. current configuration-level quotation evidence;
5. current market-price evidence;
6. historical transaction evidence.

A source strong in one class may be weak in another.

**Important:** manufacturer documentation remains the strongest source for technical facts, but a current exact-configuration sales quotation may be a stronger **price** anchor than an official public product listing or an older government transaction for a different configuration.

---

## 2. Technical Source Hierarchy

### A. Technical Specifications

Prefer, in order:

1. manufacturer official product page;
2. official datasheet / product specification PDF;
3. official configurator or ordering guide;
4. official compatibility/interoperability matrix;
5. official support portal and lifecycle/EOS/EOL notices.

Verify here:

- CPU/socket/core limits;
- DIMM count/type/capacity;
- PCIe generation and slot layout;
- RAID/HBA/controller options;
- NIC/interface speeds;
- switch port types and stacking/IRF capability;
- firewall NGFW/IPS/threat-protection throughput;
- power-supply redundancy;
- OS/hypervisor support;
- lifecycle status.

Do not use marketplace titles or reseller descriptions as the sole source for critical technical facts when manufacturer documentation exists.

### B. Compatibility and Certification

Prefer:

1. manufacturer compatibility matrix;
2. OS/hypervisor official HCL;
3. component-vendor qualification list;
4. formal certification/test report from an authoritative organization.

For domestic/Xinchuang requirements, only perform this check when the project explicitly requires it.

---

## 3. Pricing Evidence Hierarchy

Pricing for highly configurable enterprise equipment must be configuration-aware.

Use the highest available tier and do not mechanically blend lower tiers into it.

### Tier 1 — Exact current formal quotation

Strongest primary budget anchor when all or nearly all required configuration and commercial scope are matched.

Examples:

- manufacturer direct quotation;
- official store or official customer-service configuration quotation;
- manufacturer-authorized reseller quotation.

Capture exact configuration, tax, warranty/support, accessories, licenses, quote date and seller identity.

### Tier 2 — Exact current credible market quotation

Examples:

- enterprise procurement marketplace quotation;
- exact fixed-SKU official/brand-store quotation;
- current enterprise sales-channel quote with exact configuration.

### Tier 3 — Highly matched current quotation

Use when the quote is current and materially comparable but has small understood differences. Quantify the difference or adjustment.

### Tier 4 — Comparable historical transaction

For China-based public-sector historical benchmarking, prefer:

1. 中国政府采购网 (ccgp.gov.cn);
2. 中央政府采购网 (zycg.gov.cn);
3. provincial/municipal official government procurement or public-resource trading platforms.

Use these as **historical comparable transaction evidence**, not live quotations.

Historical evidence is valuable, but if current exact-configuration quotations exist, historical prices become context and must not average down the current quote range.

### Tier 5 — Component-cost model

Use current enterprise option/component costs to estimate a configured system when no exact quote exists. Clearly identify components that are estimated rather than quoted.

### Tier 6 — Generic model-family / aggregator / price-history context

This includes:

- same chassis/model family with incomplete CPU/memory/storage/RAID/license/service scope;
- market-aggregator prices that have not been independently verified as exact configuration/SKU quotes;
- price-history/deal-community evidence.

Useful as context, sanity checking, or channel discovery. It is not automatically a procurement-level quote for a fully configured system.

### Tier 7 — Engineering estimate

Use only when stronger evidence is unavailable. Output a range and mark `Estimated` or `Needs confirmation`.

---

## 4. Search Strategy

### Step 1 — derive search keys from the technical requirement

Build a normalized key set:

- product category;
- manufacturer/architecture constraint, if any;
- exact CPU/core/memory/storage/network requirements;
- RAID/HBA/controller requirements;
- interface and optics requirements;
- OS/hypervisor compatibility;
- warranty/service term;
- region/currency/tax requirement.

Do not start from a favorite model.

### Step 2 — classify the procurement object

Before choosing price channels, classify each item as:

- `configurable-enterprise` — server, storage, HCI, configured firewall, modular switch, project UPS, etc.;
- `fixed-sku` — fixed switch/AP/display/Mini PC/fixed UPS/NAS SKU;
- `commodity-component` — CPU, DIMM, SSD/HDD, optics, cable, accessory.

This classification changes the price-search workflow. A configured server should not use the same evidence strategy as an SSD.

### Step 3 — find candidate product families

Search manufacturer domains first for technical fit and lifecycle.

Useful patterns:

```text
site:<manufacturer-domain> <product-category> <key-spec>
site:<manufacturer-domain> <model> datasheet
site:<manufacturer-domain> <model> ordering guide
site:<manufacturer-domain> <model> compatibility
site:<manufacturer-domain> <model> EOL OR EOS OR lifecycle
```

### Step 4 — verify the exact procurement configuration

For configurable servers normally capture:

- chassis/model;
- CPU model and quantity;
- memory module capacity/count/type;
- SSD/NVMe quantity/capacity/type;
- HDD quantity/capacity/type;
- RAID/HBA/controller/cache/PLP;
- NIC model/speed/port count;
- PSU quantity/wattage/redundancy;
- rail kit/power cords/mandatory accessories;
- warranty/support term.

For network/security equipment capture:

- chassis/model;
- power supplies/fans;
- optics/DAC/AOC;
- stacking/IRF accessories;
- security subscriptions/licenses;
- controller/AP/device licenses;
- support term.

A model family is not a procurement configuration.

### Step 5 — verify lifecycle and supportability

Before selecting primary candidates check:

- active/current product status;
- EOS/EOL announcements;
- support end date where known;
- firmware/security update availability;
- required software-version compatibility;
- region-specific orderability.

Avoid discontinued products as the primary choice unless the user explicitly requests legacy/used hardware.

### Step 6 — perform live price research when current price is requested

If live research/search tools are available, **current-price requests must use them**. Do not answer a current-price question from model memory, an old internal budget, or historical procurement evidence alone.

Use `references/live-price-research.md` to choose channels by product class.

For China-market research, channel examples may include:

- manufacturer direct/official/authorized channels for configuration-level quotes;
- JD/Tmall enterprise or official brand channels for fixed SKUs, components, or seller-confirmed configured quotes;
- ZOL/market aggregators for spread/sanity checking and channel discovery;
- price-history services for relatively standard SKUs/components;
- government/public procurement for historical transaction context.

These are not a permanent fixed authority ranking. Configuration match, quote mode, tax/warranty scope and current orderability determine whether a price can anchor the budget.

If live research tools are unavailable, state that the current price cannot be verified and return only an estimate or a structured RFQ request.

### Step 7 — seek exact current quotes first for configurable enterprise equipment

For servers, storage, firewalls, HCI, modular switches and similar equipment, seek **2–3 current exact-configuration quotations** when practical.

Record:

- quote date;
- source/channel;
- exact configuration;
- quote mode (human-configured/exact-config/exact-SKU/base listing);
- tax status;
- warranty/support;
- included licenses/subscriptions;
- included accessories;
- implementation scope;
- shipping if relevant;
- orderability/lead time where known.

When two or more exact current quotes are available, their observed range becomes the primary current market range.

A public e-commerce starting price is not a configured-server quote. Treat it as a lead and seek seller/customer-service confirmation of the full BOM.

### Step 8 — collect current market context

For fixed or semi-standard devices, collect 2–5 current sources where useful.

For highly configurable enterprise devices, quantity is less important than match quality. Two exact quotations are more useful than ten generic chassis listings.

Market aggregators, price-history tools and deal communities normally remain context sources unless the exact seller/SKU/quote has been independently verified.

### Step 9 — collect historical transaction evidence

Search official procurement records with model/category plus key configuration terms.

Capture:

- publication/transaction date;
- buyer/project type;
- model/configuration;
- quantity;
- total/unit price if disclosed;
- tax status if disclosed;
- warranty/service scope;
- bundled software/accessories.

Reject a historical price as directly comparable when configuration or service scope differs materially.

### Step 10 — score configuration match

For configurable servers use the default match model in `references/exact-configuration-pricing.md` unless a better device-specific model is justified.

Default interpretation:

```text
>= 0.95  exact/effectively exact
0.85–0.949 highly comparable
0.70–0.849 partially comparable
< 0.70 not a direct budget anchor
```

Same chassis does not imply a high score.

### Step 11 — normalize commercial scope

Normalize prices to:

```text
Comparable Cost =
hardware
+ mandatory accessories
+ required licenses
+ warranty/support
+ required implementation
+ tax
+ shipping
```

Do not compare:

- bare chassis vs fully configured server;
- different CPU/memory/storage/RAID configurations as if identical;
- switch without optics vs switch with full optics;
- firewall appliance-only vs appliance + 3-year security subscription;
- UPS main unit vs UPS + battery cabinet.

### Step 12 — exclude misleading price signals from the anchor

Do not let these become primary budget anchors:

- starting/base-configuration prices;
- unavailable/non-orderable offers;
- incomplete configurations;
- used/refurbished offers when the project requires new equipment;
- quotes with materially incomplete tax/license/warranty/service scope;
- low configuration-match prices.

Keep the records visible with an exclusion reason rather than silently deleting them.

### Step 13 — select the budget anchor by evidence priority

If Tier 1 exact current quotes exist, use only Tier 1 quotes to form the primary quote range. Lower tiers remain context.

If no Tier 1 evidence exists, move to the highest available eligible tier and state the confidence/limitations.

Do not calculate one average across all evidence tiers.

Use `scripts/normalize_price_evidence.py --summary` when structured evidence is available.

---

## 5. Evidence Classes

Use:

- **Verified** — official technical evidence or a directly verified formal quote;
- **Market-verified** — multiple current configuration-comparable market quotes;
- **Comparable-transaction** — authoritative historical transaction with comparable configuration;
- **Estimated** — engineering estimate using partial evidence;
- **Needs confirmation** — configuration/commercial scope/availability not adequately verified.

For pricing, add a qualifier where useful:

```text
Market-verified / Exact-config
Market-verified / Highly-matched
Comparable-transaction
Estimated / Partial-config
Needs confirmation
```

---

## 6. Budget Output Rules

### Two or more exact current quotes

Report:

```text
Exact current quote range: CNY X–Y
Recommended project budget: normally use this observed range, optionally with a separately stated procurement contingency
Evidence date: YYYY-MM-DD
Confidence: Market-verified / Exact-config
```

Do not average Tier 4–7 evidence into the range.

### One exact current quote

Report the exact quote as the primary anchor and recommend obtaining a second quote before fixing a procurement control price.

Do not invent a narrow range around one quote unless a documented contingency rule is applied.

### No exact current quote

Use the best available matched evidence and return a range.

For highly configurable enterprise equipment, avoid a precise single-number estimate until configuration-level quotations exist.

Example:

```text
Engineering estimate: CNY 75,000–100,000
Evidence: partial current market + historical comparable transactions
Confidence: Needs confirmation
Action: obtain 2–3 exact configuration tax-included quotes
```

---

## 7. Required Output for Equipment Research

For important selections provide:

| Candidate | Product class | Technical fit | Lifecycle | Exact configuration | Match score | Price source/date | Normalized cost | Priority | Anchor eligible | Confidence |
|---|---|---|---|---|---:|---|---:|---:|---|---|

Then state:

- why the recommended candidate is selected;
- which evidence is the primary price anchor;
- which cheaper/higher prices were excluded from the anchor and why;
- whether warranty/tax/license/accessory differences remain;
- what must still be confirmed by manufacturer/reseller.

---

## 8. Price Interpretation Rules

- Do not average unrelated prices.
- Prefer configuration-matched evidence over source count.
- A current exact authorized quote can outrank an older authoritative transaction for a different configuration when pricing.
- Government transaction prices may include tax, services, warranty and bundled scope; inspect before using them.
- Retail/e-commerce listings may omit enterprise warranty, tax or options.
- Distributor/customer-service quotes may be more realistic for configured enterprise servers, storage, firewalls and HCI than public list prices.
- Aggregator prices are useful for market spread/sanity checks, but exact SKU/configuration and commercial scope still need verification.
- Price-history tools are most useful for standard SKUs/components, not custom enterprise configurations.
- Record the research date.
- If evidence supports only a range, return a range.

---

## 9. Anti-Patterns

Do not:

- answer a current-price request from memory when live research is available;
- search one marketplace and call that the market price;
- use a reseller page as sole proof of critical technical specifications when official documentation exists;
- compare different configurations by chassis/model name alone;
- let a bare-chassis, starting-price or low-storage price set the budget for a fully configured enterprise server;
- average current exact quotes with old government procurement prices;
- treat an old procurement transaction as a current quote;
- use a fixed site ranking without considering product class and configuration match;
- hide unknown warranty, tax, licensing, optics, RAID or service costs;
- return a precise budget when evidence only supports a broad estimate;
- assume HCI, Xinchuang, HA or other architectures without requirement evidence.
