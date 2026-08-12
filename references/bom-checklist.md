# Project BOM Checklist

Use this checklist before finalizing a procurement BOM or budget. Include only categories relevant to the project, but explicitly check hidden accessories, licenses and services.

## Server / Compute

- chassis/model
- CPU model and quantity
- memory module size/count and expansion slots
- boot SSD/NVMe
- application/database SSD
- historical/archive HDD/SSD
- RAID/HBA/controller
- RAID cache and power-loss protection where required
- NIC speed/port count
- management/BMC interface
- PSU quantity/wattage and redundancy
- power cords
- rail kit / cable-management arm
- operating system / database license if required
- warranty/support term

## Storage / Backup

- NAS/SAN/backup appliance
- drive model/capacity/count
- RAID level
- spare drive if required
- network interface
- backup software/license
- retention/versioning requirement
- backup media/secondary copy where required

## Network

- switch model and port count
- Layer-2/Layer-3 feature requirement
- power supplies/fans
- uplink modules
- optical transceivers
- DAC/AOC
- fiber/copper patch cords
- stacking modules/cables if used
- feature/license subscriptions if applicable
- warranty/support

## Security (only when required)

- firewall/security appliance
- IPS/AV/threat subscription
- VPN/remote-access license
- support term
- required optics/cables

## UPS / Power

- UPS VA and W rating
- topology/type (line-interactive/online etc.)
- runtime target
- battery pack/cabinet if required
- communication card/USB/network management
- graceful-shutdown software/integration
- bypass/maintenance accessories where required
- PDU quantity/rating
- power distribution and earthing accessories

## Rack / Cabling

- rack height/depth/load rating
- shelves
- vertical/horizontal cable management
- PDU
- patch panel
- copper/fiber modules
- structured cable
- patch cords
- labels
- grounding/bonding parts
- spare consumables

## Workstations / Operator Stations

- PC/industrial PC
- CPU/memory/storage
- NIC
- display
- keyboard/mouse
- OS license
- SCADA client license
- industrial environmental requirement if applicable
- warranty

## Large Screens / Dashboards

- commercial display / TV / LED display
- size/resolution/brightness
- built-in player/browser capability
- OPS module when required
- wall/floor mount
- HDMI/network cable
- remote power/auto-start requirement
- Web/dashboard license/session
- installation and commissioning

Do not add both OPS and a separate mini PC unless there is a specific technical reason.

## SCADA / Historian / BI

Request commercial confirmation separately for:

- SCADA Runtime
- SCADA Development
- I/O point license and tier
- operator/client licenses
- Web publishing / Web clients
- historian / historical trend
- alarm/event management
- reporting / API / ODBC / SDK
- Modbus TCP driver
- OPC UA client/server module
- actual PLC vendor drivers
- redundancy/HA module only when required
- BI commercial license if used
- dashboard/report development scope

## OT Remote Control

For remote start/stop or setpoint control include:

- role/permission configuration
- second-confirmation configuration where required
- operation audit/logging
- PLC/equipment permissive integration
- command feedback/status
- FAT/SAT test cases

See `references/ot-control-safety.md`.

## Services

- installation
- rack/stack/cabling
- network configuration
- SCADA configuration/point import
- communication integration
- historian/alarm/trend configuration
- BI/dashboard development
- FAT/SAT
- commissioning
- documentation/source-file handover
- training
- maintenance/support

## Budget Output Check

Before issuing the budget confirm:

- quantity and unit
- exact configuration scope
- tax/VAT assumption
- warranty/support term
- mandatory accessories included
- required licenses included
- implementation included/excluded
- price evidence type/date
- contingency percentage
- optional/compressible items
- explicit excluded scope

For Chinese CSV output, prefer UTF-8 with BOM so Excel opens Chinese fields correctly.
