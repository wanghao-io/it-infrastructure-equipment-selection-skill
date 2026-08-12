# Procurement Research and Evidence Workflow

Use this reference when selecting real equipment, estimating budgets, validating current models, or comparing market prices.

## 1. Separate Evidence Types

Do not use one source for everything. Treat these as different evidence classes:

1. Technical specification evidence
2. Compatibility/certification evidence
3. Lifecycle and availability evidence
4. Current market price evidence
5. Historical transaction evidence

A source strong in one class may be weak in another.

---

## 2. Source Hierarchy

### A. Technical Specifications — highest priority

Prefer, in order:

1. Manufacturer official product page
2. Official datasheet / product specification PDF
3. Official product configurator or ordering guide
4. Official compatibility/interoperability matrix
5. Official support portal and lifecycle/EOS/EOL notices

Examples of evidence to verify here:

- CPU/socket/core limits
- DIMM count and supported memory capacity
- PCIe generation and slot layout
- RAID/HBA options
- NIC speeds and transceiver support
- switch port types and stacking capability
- firewall NGFW/IPS/threat-protection throughput
- power supply redundancy
- OS/hypervisor support
- lifecycle status

Do not use marketplace product titles or reseller descriptions as the sole source for critical technical requirements.

### B. Compatibility and Certification

Prefer:

1. Manufacturer compatibility matrix
2. OS/hypervisor official HCL
3. Component vendor qualification list
4. Formal certification or test report from an authoritative organization

For domestic/Xinchuang requirements, only perform this check when the project explicitly requires it.

### C. Historical Procurement Price — strong budget benchmark

For China-based public-sector comparable transactions, prefer:

1. 中国政府采购网 (ccgp.gov.cn) — central and local award/transaction notices
2. 中央政府采购网 (zycg.gov.cn) — electronic marketplace, batch procurement, inquiry and transaction information
3. Provincial/municipal official government procurement or public-resource trading platforms

Use historical procurement records as **comparable transaction evidence**, not as a live quote.

China Government Procurement Network identifies itself as the Ministry of Finance-designated national government procurement information publication medium, making award and transaction notices useful evidence for historical procurement benchmarking.

### D. Current Enterprise Market Price

Prefer:

1. Manufacturer direct quote or official store, where available
2. Manufacturer-authorized distributor/reseller quote
3. Enterprise procurement platforms (for example JD Business/JD Enterprise Procurement)
4. Mainstream retail/e-commerce listings for commodity devices

Use marketplace prices only as a budget reference unless the exact seller, exact configuration, warranty, tax and service scope are known.

---

## 3. Search Strategy

### Step 1 — derive search keys from the technical requirement

Build a normalized key set:

- product category
- manufacturer or architecture constraint, if any
- minimum CPU/core/memory/storage/network requirements
- exact interface requirements
- required OS/hypervisor compatibility
- warranty/service requirement
- region/currency/tax requirement

Do not start from a favorite product model.

### Step 2 — find candidate product families

Search manufacturer domains first.

Useful query patterns:

```text
site:<manufacturer-domain> <product-category> <key-spec>
site:<manufacturer-domain> <model> datasheet
site:<manufacturer-domain> <model> ordering guide
site:<manufacturer-domain> <model> compatibility
site:<manufacturer-domain> <model> EOL OR EOS OR lifecycle
```

Example:

```text
site:dell.com PowerEdge 25GbE datasheet
site:hpe.com ProLiant ordering guide
site:huawei.com server compatibility openEuler
```

### Step 3 — verify exact configuration

For configurable systems, record more than the chassis name.

Server configuration should normally include:

- chassis/model
- CPU model and quantity
- memory module capacity/count
- boot/storage drives
- RAID/HBA/controller
- NIC model/speed/port count
- PSU quantity/wattage
- rail kit
- warranty/support term

Network equipment should include required optics/DAC/AOC, power supplies, fans, stacking/licensing and support.

A model family is not a procurement configuration.

### Step 4 — verify lifecycle and supportability

Before price comparison, check:

- current/active product status
- EOS/EOL announcements
- support end date if known
- firmware/security update availability
- required software version compatibility
- region-specific availability where relevant

Avoid recommending discontinued equipment as the primary choice unless the user explicitly wants used/legacy hardware.

### Step 5 — collect historical transaction evidence

Search official procurement records with model/category plus key configuration terms.

Useful patterns:

```text
site:ccgp.gov.cn <model> 中标
site:ccgp.gov.cn <product-category> 服务器 中标
site:ccgp.gov.cn <key-spec> 成交
site:zycg.gov.cn <model> 成交
site:zycg.gov.cn <product-category> 电子竞价
```

For each comparable record capture:

- publication/transaction date
- buyer or project type
- model/configuration
- quantity
- total and/or unit price if disclosed
- tax status if disclosed
- warranty/service scope
- bundled software/accessories

Reject a historical price as directly comparable when configuration or service scope differs materially.

### Step 6 — collect current market evidence

For commodity or semi-standard equipment, collect 2–5 current sources where possible.

Record:

- seller/channel
- exact SKU/configuration
- listed or quoted price
- VAT/tax status
- shipping
- warranty/support
- included accessories/software
- query date

### Step 7 — normalize before comparing

Normalize prices to the same scope:

```text
Comparable Cost = hardware + mandatory accessories + required licenses + warranty/support + tax + required implementation
```

Do not compare:

- bare chassis vs fully configured server
- switch without optics vs switch with full optics
- firewall appliance-only vs appliance + 3-year security subscription
- UPS main unit vs UPS + battery cabinet

### Step 8 — produce a confidence-based budget

Classify evidence:

- **Verified** — official technical source or direct formal quote
- **Market-verified** — multiple comparable current market sources
- **Comparable-transaction** — authoritative historical procurement record with comparable configuration
- **Estimated** — engineering estimate based on partial market evidence
- **Needs confirmation** — configuration, availability or commercial terms not adequately verified

Recommended budget output:

```text
Technical recommendation: exact minimum/recommended configuration
Current market range: CNY X–Y
Comparable procurement range: CNY A–B
Recommended project budget: CNY M–N
Evidence date: YYYY-MM-DD
Confidence: Market-verified / Estimated / ...
```

---

## 4. Price Interpretation Rules

- Do not average unrelated prices.
- Prefer configuration-matched evidence over a larger number of weak sources.
- Government procurement transaction prices can include service, tax, warranty, software and project-specific commercial conditions; inspect the notice before using the number.
- Retail/e-commerce prices can omit enterprise warranty, tax or project services.
- Distributor quotes may be more realistic for enterprise servers, storage, firewalls and HCI than public retail listings.
- For highly configurable enterprise equipment, give a budget range unless a formal quote exists.
- Record the research date because prices and product availability change.

---

## 5. Required Output for Equipment Research

For important selections, provide a compact evidence table:

| Candidate | Technical fit | Lifecycle | Technical source | Price evidence | Budget range | Confidence |
|---|---|---|---|---|---|---|

Then state:

- why the recommended candidate is selected
- why cheaper alternatives were rejected or accepted
- whether higher-priced alternatives provide meaningful value
- what must still be confirmed by the vendor or reseller

---

## 6. Anti-patterns

Do not:

- search only one e-commerce site and call that the market price
- use a reseller page to prove a critical hardware specification when official data exists
- compare different configurations by chassis/model name alone
- assume HCI is required whenever virtualization appears
- assume domestic/Xinchuang requirements unless stated or evidenced
- treat an old government procurement price as a current quote
- hide unknown warranty, licensing, optics or service costs
- return a precise budget when evidence only supports a range
