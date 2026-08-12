# Enterprise Campus IT Infrastructure Reference Design

> An anonymized, illustrative reference design. Values are examples only and must be recalculated from project requirements.

## Scenario

A medium-size enterprise campus needs a refresh of office networking, shared application infrastructure, Internet access security, wireless access and centralized management.

The project does **not** assume HCI, dual-core switching or a domestic platform by default. Those choices are evaluated only if availability, policy, compatibility or budget requirements justify them.

## Example inputs

- Several hundred office endpoints
- Multiple departments and shared services
- Corporate Wi-Fi and guest Wi-Fi
- Central file/application services
- Internet access and remote-access requirement
- Moderate availability target
- Growth expected over the next few years

## Design questions

1. Is a single core switch sufficient, or is redundant core justified by downtime requirements?
2. Should applications use standalone servers, traditional virtualization or HCI?
3. How many access ports and PoE ports are required after growth reserve?
4. Which security subscriptions are actually required on the Internet firewall?
5. What UPS runtime is needed for network core and server equipment?

## Possible logical architecture

```text
Internet
   |
Edge Firewall
   |
Campus Core
   +-- Office Access Switches
   +-- Wireless Controller / AP Network
   +-- Server / Virtualization Network
   +-- Management Network
   +-- Guest Access Boundary
```

## Expected Skill output

- Requirement and assumption table
- Access/uplink port sizing
- Core redundancy decision with cost trade-off
- Server/virtualization alternatives
- Firewall performance requirement
- UPS sizing
- Vendor/model comparison matrix when requested
- BOM with optics, licenses, support and accessories
- Tender/RFQ parameters when requested
- Mermaid or Graphviz logical topology when requested

## Procurement notes

Compare exact configured products rather than chassis names. For switches include optics, stacking/redundancy features and licenses. For firewalls include security subscriptions and support term. For servers include CPU, memory, drives, NICs, PSU, rails and warranty.
