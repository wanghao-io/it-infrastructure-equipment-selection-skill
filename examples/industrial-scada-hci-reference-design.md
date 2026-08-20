# Industrial SCADA + HCI Reference Design

[中文说明](#中文说明) | [English](#english)

---

# 中文说明

## 案例背景

某制造企业建设智能生产系统，需要实现生产设备集中监控、生产数据采集、历史数据分析、报表管理以及 IT/OT 网络融合管理。

本文仅作为公开技术案例，不包含任何真实项目名称、客户信息、设备品牌或商业数据。

## 项目需求（脱敏）

规模：

- SCADA 监控点：约 3000 点
- PLC/控制设备：50+ 台
- 工业网络区域：多个生产区域
- 支持一期建设并预留后续扩展
- 要求高可靠运行

主要业务：

- SCADA 实时监控
- 历史数据库
- OPC 数据采集
- 报表分析
- 运维管理

---

## 待验证的边界架构

下图只表示“存在经确认的 IT/OT 互联和受控数据交换需求”时的一种候选边界。若互联方向、协议、远程访问和跨信任域需求尚未确认，防火墙与工业 DMZ 均保持 TBD，不能由案例默认引入。

```
生产设备
    |
PLC / 控制系统
    |
工业交换网络
    |
OT核心网络
    |
工业防火墙
    |
工业DMZ
    |
IT基础设施平台
```

---

## 计算平台方案比较

仅凭“高可靠”无法确定三节点 HCI。先冻结可用性目标、RTO/RPO、维护窗口、工作负载、共享存储条件和故障域，再比较：

- 独立服务器加备份；
- 传统虚拟化加共享存储或复制；
- 满足仲裁、N+1、重建与支持矩阵要求的 HCI。

只有 HCI 在 Mandatory 门禁和全生命周期复杂度比较中胜出时，才进入节点设计。以下业务清单只是容量输入：

承载业务：

- SCADA Server
- Historian Database
- OPC Server
- Reporting Server
- Backup Server
- Management Server

若选择 HCI，仍必须验证：

- 支持 N+1 故障能力评估
- 保留未来扩展空间
- 关键业务虚拟化部署
- 单节点故障后的 CPU、内存、有效存储、IOPS 和网络容量
- 仲裁、存储保护、重建空间、交换网络与故障域独立性

---

## 网络设计

网络分层：

- PLC控制网络
- 工业设备接入网络
- OT核心网络
- IT业务网络
- 管理网络

安全原则：

- PLC网络不直接访问互联网
- IT与OT边界部署防火墙
- 远程访问采用 VPN 和身份认证
- 移动访问默认只读

---

## 典型输出结果

通过本 Skill 可以生成：

- 服务器规格建议
- 超融合节点规划
- 存储容量估算
- 网络设备 BOM
- 防火墙规格建议
- UPS容量估算
- 招标参数核验表
- 项目预算表

---

# English

## Background

A manufacturing enterprise is building a smart production system requiring centralized monitoring, industrial data collection, historical analysis and IT/OT integration.

This document is a public reference example. It does not contain real customer information, project names, vendors or confidential data.

## Requirements

Typical scale:

- Around 3000 SCADA points
- 50+ PLC/control devices
- Multiple industrial network zones
- Phase-one deployment with future expansion capability

Applications:

- SCADA
- Historian database
- OPC data acquisition
- Reporting
- Infrastructure management

## Conditional Boundary Architecture

The diagram below is only a candidate when an explicit IT/OT interconnection and controlled data-exchange requirement exists. Firewall and industrial-DMZ scope remain TBD until flows, protocols, remote access and trust boundaries are confirmed.

```
Production Equipment
        |
PLC / Control System
        |
Industrial Network
        |
OT Core Network
        |
Industrial Firewall
        |
Industrial DMZ
        |
IT Infrastructure Platform
```

## Design Output

The skill can generate:

- Server sizing
- HCI planning
- Storage estimation
- Network BOM
- Firewall requirements
- UPS sizing
- Compliance checking
- Procurement documentation

HCI is not a default. Compare standalone servers, traditional virtualization/shared storage and HCI only after availability, RTO/RPO, workload, maintenance and failure-domain requirements are explicit. A capacity calculation cannot by itself prove that HCI is required.

## Principle

Requirements first. Sizing second. Products last.
