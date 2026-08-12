# Healthcare IT Infrastructure Reference Design

> An anonymized, illustrative example. It is not a clinical-system certification guide. Final design must follow the organization's security, privacy, availability and vendor-support requirements.

## Scenario

A healthcare organization needs infrastructure for business systems, clinical applications, database workloads, centralized identity, backup and segmented network access.

The design must prioritize availability, supportability, security boundaries and recovery objectives. HCI or other specialized platforms are optional choices, not defaults.

## Example inputs

- Multiple business and clinical application servers
- Database workloads with defined backup and recovery requirements
- Staff, medical-device/IoT and guest network segments
- Remote support for authorized vendors
- 24x7 critical services for selected workloads
- Central backup and monitoring

## Design questions

1. Which workloads are truly critical and require HA or rapid recovery?
2. Which systems must remain isolated or tightly filtered?
3. What RPO/RTO targets apply to each service tier?
4. Is HCI, traditional virtualization plus shared storage, or a mixed architecture more appropriate?
5. What maintenance/support level is required for compute, storage, firewall and UPS equipment?
6. How should backup capacity and retention be calculated?

## Possible logical architecture

```text
Internet / External Services
        |
   Edge Firewall
        |
   Enterprise Core
    /      |       \
Staff   Server    Guest
LAN     Network   Network
          |
    Application / DB
          |
       Backup
```

Medical-device or specialized equipment networks should be added only where project requirements identify them and should not be assumed to have unrestricted access to business or Internet networks.

## Expected Skill output

- Service criticality and availability assumptions
- Architecture alternatives and trade-offs
- Compute/memory/storage sizing
- Backup capacity model
- Network segmentation requirements
- Firewall performance and interface requirements
- UPS sizing for critical infrastructure
- Vendor/model comparison with hard compliance gates
- Tender parameters and compliance table when requested
- Logical network topology when requested

## Procurement notes

Lifecycle, compatibility and vendor support are especially important. Any application, database, hypervisor, HBA/NIC or operating-system compatibility claim should be verified against authoritative vendor documentation before procurement.
