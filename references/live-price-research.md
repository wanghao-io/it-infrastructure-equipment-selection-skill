# Live Market Price Research

Use this reference when the user asks for a **current price, current market range, live procurement budget, or quotation-oriented BOM**.

The goal is not to find the largest number of prices. The goal is to obtain the strongest current price evidence for the exact procurement object.

## Core Rule

**Current price research must be live when live research tools are available.**

Do not answer a current-price request from model memory, an old project budget, or a historical procurement transaction when current market research is available.

If live web/search access is unavailable, state that the current price cannot be verified and return only an engineering estimate or a structured quotation request. Do not present an old number as a current market price.

For highly configurable equipment, also load `references/exact-configuration-pricing.md`.

---

## 1. Classify the Procurement Object First

Do not use one shopping workflow for every device.

### A. Highly configurable enterprise equipment

Examples:

- rack servers;
- storage arrays;
- HCI nodes;
- firewalls with subscriptions/licenses;
- modular/core switches;
- enterprise UPS systems with battery options;
- workstations with project-specific configurations.

Price depends on configuration and commercial scope. The preferred evidence is a current configuration-level quotation.

### B. Fixed or semi-standard enterprise SKU

Examples:

- fixed-port switches;
- wireless APs;
- access controllers with a known license bundle;
- standard Mini PCs;
- monitors/displays;
- fixed-capacity NAS models;
- fixed UPS SKUs.

Multiple current listings can be useful if the exact SKU, tax and warranty are comparable.

### C. Standard components / commodity items

Examples:

- CPU;
- memory modules;
- SSD/HDD;
- optics;
- patch cords;
- standard accessories.

Retail/enterprise marketplace prices and price-history tools are more useful here than they are for a fully configured server.

---

## 2. China-Market Search Channels

These are **channel examples**, not permanent authority rankings. Verify availability and relevance at research time.

### Manufacturer / official / authorized channels

Use for:

- exact configurable quotations;
- warranty/service scope;
- availability and lead time;
- final commercial confirmation.

For configurable equipment, a human-configured quote from manufacturer direct sales, an official brand store/customer-service channel, or an authorized partner can be the strongest current price evidence when the full configuration is matched.

### JD / Tmall enterprise or official brand channels

Useful for:

- fixed SKUs;
- standard components;
- current availability;
- tax-included retail/enterprise pricing;
- configurable server listings **only after the exact configuration is confirmed with the seller**.

Do not use the product-card starting price of a configurable server as the configured-server price.

### ZOL / market aggregators

Useful for:

- market sanity checks;
- observing the spread across multiple sellers;
- identifying candidate channels to verify.

Aggregator prices do not automatically become procurement anchors. Confirm whether the price is for the exact SKU/configuration and whether tax, warranty, licenses and accessories are included.

### Price-history tools

Examples may include price-history services for mainstream e-commerce products.

Best suited to:

- SSD/HDD;
- memory;
- CPUs;
- displays;
- Mini PCs;
- other relatively standard SKUs.

Use as trend/context evidence, not as the primary configured-enterprise quote unless the exact procurement SKU is truly fixed and comparable.

### Deal/community aggregators

Useful as weak context for standard components and retail products. They are not primary evidence for enterprise configuration-level budgets.

### Government/public procurement transactions

Use as historical comparable transactions. They are valuable for cross-checking enterprise pricing, but they are not live quotations and must not override stronger current exact-configuration evidence.

---

## 3. Search Workflow

### Step 1 — normalize the requirement

Convert the user request into an exact procurement description.

For a server, capture at minimum:

```text
form factor/chassis
CPU model x quantity
memory capacity/type/module count
system SSD quantity/capacity/type
application/database SSD quantity/capacity/type
HDD quantity/capacity/type
RAID controller/cache/PLP
NIC ports/speed
BMC requirement
PSU quantity/wattage/redundancy
rails/accessories
warranty/support
tax requirement
```

Do not start pricing until the configuration is normalized enough to tell whether two offers are comparable.

### Step 2 — verify current model and technical compatibility

Use manufacturer documentation for technical facts and lifecycle.

Price channels must not be used as the sole evidence for critical technical specifications.

### Step 3 — search exact-config/current channels

For highly configurable equipment, prefer obtaining or finding **2–3 current exact-configuration quotations**.

A useful server search is not merely:

```text
<model> price
```

It includes the major pricing drivers, for example:

```text
<model> <CPU> 128GB 2x960GB 2x1.92TB 4x4TB RAID dual PSU
```

If the public listing exposes only a base configuration, treat it as a lead and seek a seller/customer-service configuration quote.

### Step 4 — collect broad market context

After exact/current quote attempts, use aggregators and other channels to judge whether the observed quotes are plausible.

For standard components/SKUs, collect multiple current comparable offers directly.

### Step 5 — collect historical context

Search authoritative procurement transactions only after the current object/configuration is understood.

Historical evidence helps answer whether the current quote is plausible, not whether the historical price should replace a current exact quote.

### Step 6 — normalize scope

Normalize every price record to the same commercial scope:

```text
hardware
+ mandatory accessories
+ licenses/subscriptions
+ warranty/support
+ implementation
+ tax
+ shipping
```

### Step 7 — reject or downgrade misleading signals

Flag or exclude a price from the primary anchor when one or more apply:

- starting/base configuration only;
- configuration cannot be reconstructed;
- CPU/memory/storage/RAID differs materially;
- price excludes mandatory license/subscription;
- tax status unknown or different;
- warranty/support materially different;
- used/refurbished/grey-market status;
- seller cannot confirm orderability;
- price is stale;
- price is an obvious promotional/traffic-attraction figure with unavailable configuration;
- bundled service scope makes it incomparable.

Do not delete these records silently. Keep them as context with an exclusion reason.

---

## 4. Source Strategy by Product Class

| Product class | Primary current-price evidence | Secondary context | Weak / contextual only |
|---|---|---|---|
| Configurable server/storage/HCI | exact manufacturer/official/authorized current quote | exact enterprise marketplace quote; highly matched current quote | generic listings; old transactions; component estimate |
| Firewall/security appliance | exact appliance + required subscription/license quote | authorized/current market quote | appliance-only price when subscriptions are mandatory |
| Fixed switch/AP | exact SKU current official/enterprise listings | multi-seller aggregator/current authorized channel | stale historical prices |
| UPS | exact UPS + battery/runtime configuration quote | fixed-SKU market listings | main-unit-only price when battery cabinet is required |
| CPU/RAM/SSD/HDD | current official/enterprise marketplace price | price-history / multi-seller comparison | old project experience |
| Cabling/optics/accessories | current comparable SKU/channel quote | aggregator/history | AI experience estimate |

---

## 5. Real-Time Price Output

For quotation-oriented research, output fields such as:

| Item | Exact configuration/SKU | Current quote(s) | Market/context range | Recommended inquiry budget | Source/date | Match | Confidence |
|---|---|---:|---:|---:|---|---:|---|

For a configurable device, also show excluded price evidence when it could otherwise mislead the reader.

Example format:

```text
Product: Example 2U server
Exact current quote A: CNY 89,000 tax included
Exact current quote B: CNY 91,500 tax included
Generic chassis listing: CNY 48,000 — excluded: configuration incomplete
Historical transaction: CNY 65,000 — context only: older/different storage scope
Primary market range: CNY 89,000–91,500
Recommended inquiry budget: current exact quote range, plus separately stated contingency if required
Confidence: Market-verified / Exact-config
Evidence date: YYYY-MM-DD
```

Never fabricate brand/model prices in examples. Public examples should be synthetic or clearly labeled as historical/project-specific evidence.

---

## 6. Confidence Guidance

### High

Normally requires:

- two or more current comparable exact-SKU/exact-config prices;
- tax and warranty scope known;
- availability/orderability reasonably confirmed;
- no material configuration ambiguity.

### Medium

Typical when:

- only one exact quote exists; or
- multiple highly matched but not exact prices exist; or
- some service/tax/accessory scope remains uncertain.

### Low

Typical when:

- only generic model-family prices exist;
- evidence is mainly historical;
- current availability cannot be confirmed;
- configuration is incomplete;
- budget relies materially on engineering estimates.

Use evidence labels from `references/price-evidence.md` in addition to this confidence description.

---

## 7. Batch BOM Price Research

When pricing a full project BOM:

1. classify every line as configurable enterprise / fixed SKU / commodity;
2. choose the search strategy per line;
3. normalize tax, warranty, licenses and accessories;
4. record price date and source for every material line;
5. flag lines with only weak evidence;
6. calculate budget only after the line-level evidence is visible;
7. do not hide high-uncertainty items inside one project total.

Recommended columns:

```text
category
brand/model
exact configuration
quantity
current quote low
current quote high
recommended budget unit price
source/channel
source date
configuration match
price evidence tier
confidence
exclusion/notes
```

---

## 8. Anti-Patterns

Do not:

- use an old internal budget as a current price;
- price a configured server from a public starting price;
- search only one marketplace;
- treat aggregator seller count as proof of comparability;
- use price-history tools as the primary source for a custom enterprise configuration;
- treat manufacturer list price as automatically equal to transaction price;
- use a fixed source ranking without considering product class and configuration match;
- average misleading low-price signals into an exact current quote range;
- output a current price without a price date;
- claim high confidence when current availability or configuration scope is not verified.
