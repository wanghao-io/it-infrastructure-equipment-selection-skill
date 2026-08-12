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
- 招标参数核验
- BOM 编制
- 项目预算估算
- 当前在售型号、生命周期与价格证据调研

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
BOM 与预算区间
    ↓
采购决策
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

中国政府采购网是财政部指定的国家级政府采购信息发布媒体，其公开中标/成交公告适合用于历史采购价格的可比性参考；当前企业市场价仍需结合实时渠道信息判断。

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
- 市场价格与可比成交价格
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
- BOM generation
- Compliance checking
- Procurement risk analysis

---

## Examples

- [Industrial SCADA + HCI Reference Design](examples/industrial-scada-hci-reference-design.md)

案例均应脱敏并聚焦工程方法，不公开客户特定敏感信息。

---

## 项目结构

```text
.
├── SKILL.md
├── references/
│   └── procurement-research.md
├── scripts/
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

This skill helps engineers design, validate and document enterprise infrastructure projects, while keeping architecture choices requirement-driven rather than forcing a predefined pattern.

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
BOM and budget range
    ↓
Procurement decision
```

## Procurement Research

Technical specifications should be verified primarily with manufacturer documentation. Current pricing should use comparable enterprise market evidence, while official government procurement award records can provide historical comparable transaction benchmarks when configurations are sufficiently similar.

See [`references/procurement-research.md`](references/procurement-research.md).

## Examples

- [Industrial SCADA + HCI Reference Design](examples/industrial-scada-hci-reference-design.md)

## License

MIT License
