# Live Market Price Research

## Quick path

1. Freeze one decision scope, product class, exact configuration and commercial basis.
2. Verify technical fit and lifecycle before collecting price.
3. Prefer current exact quotes; normalize tax, delivery, licenses, support and implementation.
4. Count normalized suppliers/channels, not quote IDs, as independent evidence.
5. Run the strict price-evidence guard before revising a baseline; keep unresolved lines unchanged.

Sections: [Core rule](#core-rule) · [Recover evidence](#0-recover-existing-project-price-evidence) · [Classify](#1-classify-the-procurement-object-first) · [Channels](#2-china-market-search-channels) · [Workflow](#3-search-workflow) · [Source strategy](#4-source-strategy-by-product-class) · [Output](#5-real-time-price-output) · [Confidence](#6-confidence-guidance) · [Batch BOM](#7-batch-bom-price-research) · [Anti-patterns](#8-anti-patterns)

Use this reference when the user asks for a **current price, current market range, live procurement budget, or quotation-oriented BOM**.

The goal is not to find the largest number of prices. The goal is to obtain the strongest current price evidence for the exact procurement object.

## Core Rule

**Current price research must be live when live research tools are available, but existing current project quotations must be recovered before weaker public context is searched.**

Do not answer a current-price request from model memory, an old project budget, or a historical procurement transaction when current market research is available.

Do not discard a current exact quotation supplied by the user or preserved in project files merely because it is not publicly indexed. For configurable enterprise equipment, a traceable human quotation can be stronger price evidence than a public same-family listing.

If live web/search access is unavailable, state that the current price cannot be verified and return only an engineering estimate or a structured quotation request. Do not present an old number as a current market price.

For highly configurable equipment, also load `references/exact-configuration-pricing.md`.

---

## 0. Recover Existing Project Price Evidence

Before external web research, inspect the current project/task scope for already available quotations.

Check, when accessible:

- explicit prices and quote details in the current user message;
- the BOM/budget file being updated;
- attached or directly referenced quotation/evidence files;
- project-local files whose names clearly indicate quotation evidence, such as `quote`, `quotation`, `price-evidence`, `询价`, `报价` or similar.

Do not scan unrelated personal directories. Search only the project/task workspace that the user has asked you to work on.

For each recovered quotation, capture:

```text
seller/channel
quote date
exact configuration
price
VAT/tax status
warranty/support
mandatory accessories/licenses/services
orderability/validity when known
```

A user-supplied manufacturer/customer-service/authorized-channel quotation does **not** need a public URL to qualify as strong current evidence if the source, date, configuration and commercial scope are recorded.

If an exact quote was mentioned in another conversation/session but is not accessible now, say so and ask the user to provide it again or save it into the project. Do not recreate the quote from memory.

When updating project files and the environment permits it, preserve important current quotations in structured form (for example an adjacent `price-evidence.json` or explicit BOM evidence columns) so a future session does not lose them.

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

### Step 8 — apply the existing-budget revision guardrail

When the user is updating, optimizing or compressing an existing BOM, compare the proposed new price against the previous unit budget.

For `configurable-enterprise` equipment, **do not lower the previous unit budget using only Tier 4–7 evidence**.

A downward revision requires either:

- at least one Tier 1/2 exact-current quote; or
- at least two independent Tier 3 highly matched current quotes with explicit normalization of remaining differences.

If the only evidence is public partial-config/model-family/context pricing, keep the old number only as a provisional carry-forward (or use `TBD`) and mark `Needs confirmation`.

Never produce a compressed control price using logic such as:

```text
same-family public price
+ estimated memory/storage/RAID uplift
= new lower server budget
```

That is an engineering estimate, not sufficient evidence for lowering an existing configured-enterprise budget.

---

## 4. Source Strategy by Product Class

| Product class | Primary current-price evidence | Secondary context | Weak / contextual only |
|---|---|---|---|
| Configurable server/storage/HCI | exact manufacturer/official/authorized current quote, including user/project-saved human quote | exact enterprise marketplace quote; highly matched current quote | generic listings; old transactions; component estimate |
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

If a previous BOM amount is retained because strong current evidence is missing, label it clearly, for example:

```text
Previous budget: CNY 65,000
Current public evidence: partial/generic only
Revised budget: CNY 65,000 provisional carry-forward
Evidence: Needs confirmation
Reason: weak evidence cannot justify downward revision
```

Do not label that retained figure as a verified current market price.

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

1. recover existing project quotation evidence before external search;
2. classify every line as configurable enterprise / fixed SKU / commodity;
3. choose the search strategy per line;
4. normalize tax, warranty, licenses and accessories;
5. record price date and source for every material line;
6. flag lines with only weak evidence;
7. apply the downward-revision guardrail to existing configurable-enterprise budgets;
8. calculate budget only after the line-level evidence is visible;
9. do not hide high-uncertainty items inside one project total.

Recommended columns:

```text
category
brand/model
exact configuration
quantity
previous budget unit price
current quote low
current quote high
recommended budget unit price
source/channel
source date
configuration match
price evidence tier
confidence
revision decision/exclusion notes
```

When practical, persist exact human quotations into a project-local structured evidence file so later BOM revisions can reuse them.

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
- claim high confidence when current availability or configuration scope is not verified;
- lower an existing configured-enterprise budget using only partial public configurations plus an engineering adjustment;
- ignore a stronger current user/project quotation because it lacks a public webpage.
