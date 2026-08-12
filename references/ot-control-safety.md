# OT Remote-Control Safety Reference

Use this reference whenever SCADA, HMI, BI, web clients or remote operator stations can issue commands to PLCs, machines, compressors, pumps, valves or other physical equipment.

## 1. Core Rule

SCADA may issue an operator command request, but it must not bypass equipment safety logic.

The final permissive decision belongs in the PLC/equipment controller or certified local safety system.

A normal command path is:

```text
Authenticated operator
  -> select equipment
  -> issue command
  -> second confirmation when the action has operational risk
  -> SCADA records the command request
  -> PLC/equipment controller checks permissives/interlocks
  -> equipment executes or rejects
  -> SCADA receives feedback and records the result
```

## 2. Required Checks for Remote Start/Stop

For remote start/stop, confirm at least:

- local/remote selector state;
- emergency-stop chain remains locally effective;
- protection/fault status;
- process permissives;
- maintenance/lockout status where applicable;
- command source authorization;
- command timeout/debounce behavior;
- positive running/stopped feedback;
- failure/rejection feedback.

The actual permissive list is equipment-specific and must be provided/approved by the machine or PLC responsible party.

## 3. Authorization

Use role-based control permissions.

Separate, where practical:

- read-only monitoring;
- alarm acknowledgement;
- normal operation;
- remote start/stop;
- parameter/setpoint changes;
- engineering/maintenance functions.

Do not give large-screen displays or read-only dashboards write/control permissions.

## 4. Confirmation and Human Factors

For consequential commands such as remote start/stop:

- identify the exact equipment;
- show current state and relevant permissives;
- require deliberate confirmation;
- prevent accidental repeated command submission;
- show command result/rejection clearly.

Do not use a generic confirmation that hides which asset is being controlled.

## 5. Audit Trail

Record at least:

- user/account;
- timestamp with synchronized time;
- workstation/client source where available;
- equipment identifier;
- requested command/value;
- pre-command state if available;
- accepted/rejected result;
- resulting equipment feedback;
- reason for rejection/failure where available.

For important production systems, define retention and export requirements for operation logs.

## 6. Network Behavior

Control traffic should use explicitly required protocols/ports only.

Do not expose PLC/control networks directly to the Internet.

When an OT system later connects to office IT, cloud, vendor remote support or Internet services, re-evaluate boundary protection, remote-access control, logging and authentication. Do not assume a previously isolated LAN remains safe after interconnection.

## 7. Fail-Safe Expectations

Loss of SCADA, server, network or Web client should not defeat local equipment protection.

Define expected behavior for:

- network interruption during command;
- SCADA/server restart;
- stale data;
- duplicate commands;
- communication recovery;
- conflicting local and remote commands.

## 8. Procurement / Acceptance Clauses

For remote-control functions, procurement specifications should require evidence of:

- role/permission configuration;
- second confirmation where required;
- operation audit log;
- PLC/equipment permissive logic;
- command feedback;
- failed-command behavior;
- local emergency/protection function remaining effective;
- FAT/SAT test cases for accepted and rejected commands.

## 9. FAT/SAT Minimum Test Set

Test at least:

1. authorized remote start succeeds when all permissives are true;
2. unauthorized user cannot issue the command;
3. remote command is rejected when local mode is selected;
4. remote start is rejected when an interlock/fault is active;
5. emergency stop remains effective regardless of SCADA state;
6. command and result appear in the audit log;
7. network loss does not create an unintended start/stop;
8. system recovery does not replay stale commands.

## 10. Anti-patterns

Do not:

- write directly around PLC permissive logic;
- replace hardwired/local safety protection with SCADA software logic;
- grant control permission to dashboard-only accounts;
- treat a successful network write as proof that the machine actually started;
- omit command audit records for remote operational control.
