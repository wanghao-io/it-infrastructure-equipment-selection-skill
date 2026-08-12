# Skill Trigger Tests

## Should Trigger

### Equipment selection and sizing

- Select a server configuration for 30 virtual machines and estimate the project budget.
- Size one physical server for SCADA runtime, historian, BI and Web publishing.
- Estimate RAID10 usable storage and historian retention for 2000 historical points.
- Size an economical UPS for a 600W server/network/backup load with 10 minutes for graceful shutdown.
- Estimate switch quantities, spare ports, uplinks and optics for a campus or OT network.

### Requirement-driven architecture

- Compare standalone servers, traditional virtualization and HCI for this project.
- We no longer require HCI; determine the simplest architecture that still meets the availability target.
- We have five VLANs on one access switch; tell me whether Layer-3 routing or a core switch is actually required.
- Determine whether a dedicated firewall is needed for this isolated OT network, and state the trigger for adding one later.
- The project explicitly requires domestic/Xinchuang compatibility; select a compatible platform.

### SCADA / OT

- Break this 3000-point domestic SCADA requirement into Runtime, Development, client, Web, historian and driver licenses for RFQ.
- Size historical storage from point count, sample rate and retention period.
- Design safe SCADA remote start/stop for an air-compressor station with permissions, confirmation, audit and PLC interlocks.
- Decide whether four operator stations need full client licenses or some can use Web/read-only licensing.

### Vendor / model comparison

- Compare these three server vendors using mandatory requirements, lifecycle, TCO and expansion capability.
- Build a project-specific vendor comparison matrix from these candidate switch configurations.

### Tender / RFQ generation

- Generate vendor-neutral tender parameters from this server requirement list.
- Turn this infrastructure design into an RFQ technical specification and supplier compliance table.
- Produce a Chinese CSV budget with price evidence type, contingency and compressible items.

### Topology generation

- Generate a Mermaid network topology from this list of VLANs, switches, servers and operator stations.
- Produce a Graphviz DOT topology for this branch and data-center architecture.

### Reference designs

- Create an anonymized small data-center reference design using the repository examples as a method template.
- Show a healthcare IT infrastructure reference design, but recalculate capacity from my requirements.

## Should Not Trigger

- Explain what DNS is.
- Write a Python web application.
- Fix a printer driver.
- Explain the difference between TCP and UDP.
- Draw a generic flowchart unrelated to IT infrastructure planning.

## Expected Behavior

The skill should activate for infrastructure architecture decisions, sizing, equipment selection, procurement evidence, SCADA/OT infrastructure, vendor/model comparison, tender/RFQ generation, BOM/budget and infrastructure topology artifacts.

It should not activate for general IT education, unrelated software development or routine endpoint troubleshooting.

When triggered, it should not automatically add HCI, core switching, firewalls or Xinchuang unless requirements justify them.
