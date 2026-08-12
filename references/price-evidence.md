# Structured Price Evidence

Use this schema when equipment/budget research returns multiple prices. The goal is to decide whether two prices are actually comparable before using them in a budget.

## Recommended JSON Record

```json
{
  "candidate": "model/configuration name",
  "configuration": "CPU, memory, drives, NIC, licenses, support and mandatory accessories",
  "source_type": "official-quote | authorized-channel | government-award | enterprise-marketplace | retail",
  "source": "source name or URL",
  "source_date": "YYYY-MM-DD",
  "hardware_price": 0,
  "mandatory_accessories": 0,
  "required_licenses": 0,
  "warranty_support": 0,
  "required_implementation": 0,
  "tax_amount": 0,
  "shipping": 0,
  "currency": "CNY",
  "tax_included": true,
  "warranty": "3 years",
  "comparable": true,
  "evidence_level": "Verified | Market-verified | Comparable-transaction | Estimated | Needs confirmation",
  "notes": ""
}
```

## Comparable Cost

Normalize to:

```text
hardware
+ mandatory accessories
+ required licenses
+ warranty/support
+ required implementation
+ tax
+ shipping
```

Use `scripts/normalize_price_evidence.py`.

## Comparability Gate

Before treating a price as directly comparable, confirm:

- same functional class;
- materially equivalent CPU/memory/storage/network configuration;
- same included licenses;
- comparable warranty/support term;
- same tax treatment;
- mandatory accessories included;
- implementation scope understood;
- source date sufficiently current for the decision.

If one of these materially differs, keep the evidence but set `comparable: false` and explain why.

## Interpretation

Prefer a smaller number of configuration-matched records over many unrelated prices.

Do not average:

- bare chassis and configured server;
- switch without optics and switch with optics;
- appliance-only firewall and licensed/subscribed firewall;
- UPS main unit and UPS plus battery cabinets;
- historical award including services and current retail hardware-only price.

## Output

For important equipment show:

| Candidate | Exact configuration | Source type/date | Normalized cost | Comparable? | Evidence level | Note |
|---|---|---|---:|---|---|---|

Then derive a **budget range**, not a false-precision single number, unless a formal current quotation exists.
