# Firewall Sizing and Eligibility

Use this reference only when an external, remote-access or cross-trust boundary is justified. An isolated network does not acquire a firewall merely because the product category exists.

## Required inputs

Record facts, assumptions and TBDs separately:

- boundary, traffic direction, trust zones and permitted applications;
- measured peak traffic, growth horizon and encrypted-traffic ratio;
- required services: stateful control, application identification, IPS, AV, URL filtering, SSL inspection, VPN and logging;
- concurrent sessions, new sessions per second, VPN users/tunnels and routing/NAT mode;
- interface count, media, speed, bypass or segmentation needs;
- availability target, HA mode, maintenance behavior and single-survivor requirement;
- subscription term, signature update, centralized management, support and implementation scope.

Missing traffic, enabled-service or encrypted-traffic facts remain TBD. Do not invent a utilization or degradation factor.

## Metric separation

Never substitute one vendor metric for another:

| Requirement | Evidence that may satisfy it | Evidence that does not satisfy it alone |
|---|---|---|
| basic forwarding | stateful/firewall throughput under stated packet profile | interface line rate |
| application and threat control | NGFW or threat-protection throughput with required engines enabled | maximum firewall throughput |
| IPS | IPS throughput with policy/signature profile stated | NGFW marketing headline without IPS conditions |
| SSL inspection | inspected throughput, CPS and concurrent SSL sessions under stated cipher/test profile | unencrypted threat throughput |
| connection scale | concurrent sessions and CPS | Gbps alone |
| remote access | licensed users/tunnels, encrypted throughput and authentication support | generic VPN checkbox |

Vendor test profiles are not interchangeable. Record packet size, traffic mix, enabled engines, software release and test conditions when available.

## Sizing sequence

1. Confirm that the boundary and allowed flows exist.
2. Establish measured peak demand and explicit growth assumptions.
3. Map every Mandatory security service to the corresponding performance metric.
4. Size each HA member to carry the required load after the defined member failure; do not add two appliance ratings.
5. Check throughput, CPS, concurrent sessions, SSL sessions, VPN scale, interfaces and routing features independently.
6. Verify that subscriptions, licenses, storage/log export, HA cables/modules, optics and support are included.
7. Validate current lifecycle, orderability and the exact software/hardware configuration.
8. Define acceptance tests and upgrade triggers before comparing price.

## Mandatory gate

Return one status for every required metric:

- `PASS`: current configuration-specific evidence meets the requirement and reserve.
- `CONDITIONAL`: a required value, test profile, license, lifecycle fact or exact configuration is unresolved.
- `FAIL`: the documented value is below the requirement or a required capability is absent.

`eligible_for_pricing=true` only when all Mandatory technical and license-scope gates pass. A bare appliance price cannot anchor a complete protected-service budget.

## Output fields

For each candidate record: boundary/use case, requirement metric, demand and reserve, vendor metric and test profile, enabled services, HA survivor result, session/CPS/VPN checks, interface scope, license/subscription term, lifecycle evidence/date, status, `eligible_for_pricing`, TBDs, acceptance test and upgrade trigger.

## Positive and negative cases

Positive: measured peak is 1.5 Gbps, required IPS/App/AV services are defined, one HA member has current 3 Gbps threat-performance evidence under a comparable profile, session/CPS and licenses pass, and the exact configuration is orderable. It may pass technical eligibility.

Negative:

- 10 GbE ports and 20 Gbps stateful throughput do not satisfy a 3 Gbps SSL-inspected threat requirement.
- SSL inspection without inspected-throughput and SSL-session evidence is `CONDITIONAL`.
- Two 1 Gbps HA members cannot satisfy a 1.5 Gbps single-survivor requirement by adding their ratings.
- Missing IPS/AV/application-control subscriptions make the complete configuration ineligible for pricing.
- No stated interconnection or trust boundary means firewall need is unresolved, not automatically required.

Do not create a universal percentage discount from firewall throughput to threat throughput. Use current manufacturer evidence or keep the result unresolved.
