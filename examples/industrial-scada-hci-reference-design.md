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

## 总体架构

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

## 计算平台设计

推荐采用三节点超融合架构：

承载业务：

- SCADA Server
- Historian Database
- OPC Server
- Reporting Server
- Backup Server
- Management Server

设计原则：

- 支持 N+1 故障能力评估
- 保留未来扩展空间
- 关键业务虚拟化部署

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

## Architecture

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

## Principle

Requirements first. Sizing second. Products last.
