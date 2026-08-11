# Network Sizing Reference

## Port Planning

计算：

设备数量 + 上联端口 + 管理端口 + 备用端口

## Interface Types

关注：

- 1GE
- 10GE
- 25GE
- 40GE
- 100GE

以及：

- SFP
- SFP+
- SFP28
- QSFP

## Industrial Network

建议分层：

PLC/OT → Industrial Switch → OT Core → Firewall → DMZ → IT Network

禁止PLC控制网络直接暴露互联网。
