# IT Infrastructure Equipment Selection Skill

[中文说明](#中文说明) | [English](#english)

---

# 中文说明

这是一个面向 **Codex / AI Agent** 的 IT 基础设施解决方案工程师 Skill。

目标是帮助 IT 架构师、售前工程师和运维工程师完成企业级基础设施项目规划，包括：

- 服务器与虚拟化基础设施选型
- 存储容量规划
- 网络设备选型
- 防火墙性能评估
- UPS 容量计算
- 工作站与终端规划
- 工业 IT/OT 架构设计（按需）
- 超融合 HCI 架构设计（按需）
- 国产化/信创适配分析（按需）
- 厂商/型号比较矩阵（按需）
- 自动生成招标/RFQ技术参数（按需）
- 自动生成 Mermaid / Graphviz 网络拓扑图（按需）
- 招标参数核验
- BOM 编制
- 项目预算估算
- 当前在售型号、生命周期与价格证据调研
- 多行业脱敏参考设计

核心原则：

> 先理解业务需求，再进行容量计算，最后选择具体产品。

> 架构跟着需求走，不默认强制使用 HCI、信创、双机、双核心或其他特定方案。

避免简单根据商品型号倒推技术方案。

---

## 工作流程

```text
需求分析
    ↓
约束与可用性目标
    ↓
选择合适的架构模式
    ↓
容量计算
    ↓
技术规格定义
    ↓
官方规格 / 生命周期验证
    ↓
市场价格 + 可比采购成交记录调研
    ↓
按需生成：厂商矩阵 / 招标参数 / 网络拓扑
    ↓
BOM 与预算区间
    ↓
采购决策
```

---

## 新增能力（v1.1.0 开发中）

### 厂商 / 型号比较矩阵

比较对象是**项目中的具体配置**，不是给品牌打永久分数。

- 先定义强制淘汰条件
- 再做加权评分
- 强制项不满足直接 `FAIL`
- 配置需统一到 CPU、内存、硬盘、网卡、授权、维保、附件等可比口径
- 分数必须同时显示证据等级

参考：[`references/vendor-comparison.md`](references/vendor-comparison.md)

工具：

```bash
python scripts/compare_vendors.py assets/vendor-comparison-example.json
```

### 自动生成招标 / RFQ 参数

从项目需求生成可量化、可验收、尽量厂商中立的技术参数和供应商响应表。

- Mandatory / Recommended / Optional 分级
- 为关键条款增加验收证据要求
- 不必要时不锁品牌、型号或专有功能
- 未确认项保留 `TBD`

参考：[`references/tender-specification.md`](references/tender-specification.md)

工具：

```bash
python scripts/generate_tender_spec.py assets/tender-requirements-example.json
```

### 自动生成网络拓扑图

从结构化 JSON 输入生成逻辑拓扑：

- Mermaid：适合 GitHub / Markdown
- Graphviz DOT：适合后续渲染和程序化处理

不会自动虚构 VLAN、IP、物理端口、冗余链路或安全区域。

参考：[`references/network-topology.md`](references/network-topology.md)

工具：

```bash
python scripts/generate_topology.py assets/topology-input-example.json --format mermaid --markdown
python scripts/generate_topology.py assets/topology-input-example.json --format dot
```

---

## 设备选型与预算证据

设备参数和价格不能只靠单一电商搜索。

本 Skill 将证据分开处理：

- **技术参数**：优先厂商官网、官方 Datasheet、配置指南、兼容性矩阵和生命周期公告。
- **当前市场价格**：优先厂商/授权渠道报价，企业采购平台作为市场参考。
- **历史成交价格**：可使用中国政府采购网、中央政府采购网及各地官方政府采购/公共资源交易平台中的可比中标或成交记录。
- **预算输出**：必须核对具体配置、税费、维保、授权、光模块/附件及实施服务，不能只比较裸机型号。

详细方法见：[`references/procurement-research.md`](references/procurement-research.md)

---

## 示例场景

### 工业 SCADA 项目

输入：

- SCADA 点数：3000
- PLC数量：50
- 需要虚拟化平台
- 有国产化要求
- 有预算约束

此时 Skill 才会根据可用性、规模、预算和维护条件判断是否适合三节点 HCI；如果传统虚拟化、物理服务器或其他架构更合理，也应给出比较后再选择。

输出可能包括：

- VM资源规划
- 架构方案比较
- CPU/内存建议
- 存储容量设计
- 网络架构建议
- 防火墙规格
- 候选设备与官方证据
- 厂商/型号比较矩阵
- 市场价格与可比成交价格
- 招标技术参数
- Mermaid / Graphviz 网络拓扑
- BOM清单
- 风险分析

---

## 核心能力

- Server sizing
- Virtualization infrastructure planning
- HCI sizing (when required)
- Storage planning
- Network architecture design
- Firewall sizing
- UPS calculation
- Industrial IT/OT infrastructure planning (when required)
- 国产化/信创适配（按需）
- Product lifecycle validation
- Authoritative procurement research
- Project-specific vendor/model comparison
- Tender/RFQ specification generation
- Mermaid / Graphviz topology generation
- BOM generation
- Compliance checking
- Procurement risk analysis

---

## Examples

- [Industrial SCADA + HCI Reference Design](examples/industrial-scada-hci-reference-design.md)
- [Enterprise Campus IT Infrastructure Reference Design](examples/enterprise-campus-reference-design.md)
- [Healthcare IT Infrastructure Reference Design](examples/healthcare-it-reference-design.md)
- [Small Data Center / Server Room Reference Design](examples/small-datacenter-reference-design.md)

案例均应脱敏并聚焦工程方法，不公开客户特定敏感信息。示例中的容量、冗余和架构不是默认配置，必须按新项目重新计算。

---

## 项目结构

```text
.
├── SKILL.md
├── references/
│   ├── procurement-research.md
│   ├── vendor-comparison.md
│   ├── tender-specification.md
│   └── network-topology.md
├── scripts/
│   ├── compare_vendors.py
│   ├── generate_tender_spec.py
│   └── generate_topology.py
├── assets/
├── examples/
├── tests/
└── agents/
```

---

## 安装

复制到 Codex Skill 目录：

```bash
~/.agents/skills/it-infrastructure-equipment-selection-skill
```

调用：

```text
$it-infrastructure-equipment-selection
```

---

# English

AI Agent skill for IT infrastructure solution architects.

This skill helps engineers design, validate and document enterprise infrastructure projects while keeping architecture choices requirement-driven rather than forcing a predefined pattern.

Typical capabilities include:

- Servers and virtualization infrastructure
- Storage
- Network equipment
- Firewalls
- UPS
- Workstations
- HCI when justified by project requirements
- Industrial IT/OT architecture when required
- Domestic/Xinchuang compatibility analysis when required
- Product lifecycle validation
- Equipment pricing and comparable procurement research
- Project-specific vendor/model comparison matrices
- Vendor-neutral tender/RFQ specification generation
- Mermaid / Graphviz logical network topology generation
- Anonymized multi-industry reference designs

## Design Principle

> Requirements first. Sizing second. Products last.

> Architecture follows requirements. HCI, domestic platforms, redundancy and other specialized patterns are optional, not defaults.

## Workflow

```text
Requirements
    ↓
Constraints and availability targets
    ↓
Architecture decision
    ↓
Capacity sizing
    ↓
Technical specification
    ↓
Official product/lifecycle validation
    ↓
Market and comparable procurement research
    ↓
Optional artifacts: comparison matrix / tender spec / topology
    ↓
BOM and budget range
    ↓
Procurement decision
```

## Optional artifact tools

```bash
python scripts/compare_vendors.py assets/vendor-comparison-example.json
python scripts/generate_tender_spec.py assets/tender-requirements-example.json
python scripts/generate_topology.py assets/topology-input-example.json --format mermaid --markdown
```

## Procurement Research

Technical specifications should be verified primarily with manufacturer documentation. Current pricing should use comparable enterprise market evidence, while official government procurement award records can provide historical comparable transaction benchmarks when configurations are sufficiently similar.

See [`references/procurement-research.md`](references/procurement-research.md).

## Examples

- [Industrial SCADA + HCI Reference Design](examples/industrial-scada-hci-reference-design.md)
- [Enterprise Campus IT Infrastructure Reference Design](examples/enterprise-campus-reference-design.md)
- [Healthcare IT Infrastructure Reference Design](examples/healthcare-it-reference-design.md)
- [Small Data Center / Server Room Reference Design](examples/small-datacenter-reference-design.md)

## License

MIT License
