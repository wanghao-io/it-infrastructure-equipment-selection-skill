# IT Infrastructure Equipment Selection Agent Skill

[![Release](https://img.shields.io/github/v/release/wanghao-io/it-infrastructure-equipment-selection-skill)](../../releases/latest)
[![CI](https://github.com/wanghao-io/it-infrastructure-equipment-selection-skill/actions/workflows/validate-skill.yml/badge.svg)](../../actions/workflows/validate-skill.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**Cross-platform Agent Skill for IT infrastructure architecture, server sizing, storage sizing, network design, UPS sizing, SCADA / industrial IT/OT planning, hardware selection, current price research, BOM budgeting, vendor comparison, RFQ/tender specifications, compliance checks and network topology generation.**

面向企业 IT 基础设施与工业 IT/OT 项目的**设备选型、容量规划、实时询价、采购预算和技术方案设计**，支持 OpenAI Codex、Claude Code、GitHub Copilot、Gemini CLI 及其他兼容 Agent Skills 的 Host。

[中文说明](#中文说明) · [English](#english) · [完整输入示例](examples/full-feature-input.md) · [Release Notes](RELEASE_NOTES.md)

> **Requirements first. Architecture second. Sizing third. Products last.**
>
> 需求 → 技术适配 → 证据质量 → 价格。便宜 SKU 不能反向定义项目需求。

## What this Skill covers

| Area | Capabilities |
|---|---|
| **Architecture** | standalone server, virtualization, HCI/HA, L2/L3/core switching, firewall/security boundary, industrial IT/OT |
| **Server & Storage** | CPU/memory sizing, RAID, SSD/HDD tiers, historian retention, usable capacity, backup risk |
| **Network** | port sizing, VLAN/L3 ownership, switching architecture, expansion headroom, topology generation |
| **UPS** | W + VA sizing, runtime target, graceful shutdown, candidate technical-fit gate |
| **SCADA / OT** | I/O points, Historian, clients/Web, OPC UA/drivers, alarms, reports/API, remote-control safety |
| **Procurement** | hardware selection, live/current pricing, exact-configuration evidence, BOM, budget revision guardrails |
| **Delivery** | vendor comparison, tender/RFQ specs, compliance checks, Mermaid/Graphviz topology, project BOM |

## Quick Start

### OpenAI Codex

```bash
git clone https://github.com/wanghao-io/it-infrastructure-equipment-selection-skill.git \
  ~/.agents/skills/it-infrastructure-equipment-selection
```

调用：

```text
$it-infrastructure-equipment-selection
```

### Claude Code

```bash
git clone https://github.com/wanghao-io/it-infrastructure-equipment-selection-skill.git \
  ~/.claude/skills/it-infrastructure-equipment-selection
```

调用：

```text
/it-infrastructure-equipment-selection
```

### GitHub Copilot / `gh skill`

可使用 GitHub CLI 发现、预览和安装 Agent Skills：

```bash
gh skill preview wanghao-io/it-infrastructure-equipment-selection-skill it-infrastructure-equipment-selection
gh skill install wanghao-io/it-infrastructure-equipment-selection-skill
```

### Cross-platform installer

```bash
python scripts/install_skill.py --target codex --scope user
python scripts/install_skill.py --target claude-code --scope user
python scripts/install_skill.py --target copilot --scope user
python scripts/install_skill.py --target gemini --scope user
```

完整平台路径和安装说明见 [`references/platform-compatibility.md`](references/platform-compatibility.md)。

---

# 中文说明

## 为什么做这个 Skill

很多 IT 基础设施选型任务的问题并不是“找不到设备”，而是顺序反了：先看到某个型号或低价，再倒推需求。

这个 Skill 强制采用工程顺序：

```text
已知条件 / TBD
        ↓
强制要求 / SLA / 增长 / 预算
        ↓
最简合理架构
        ↓
CPU / 内存 / 存储 / Historian / 网络 / UPS sizing
        ↓
技术规格与 Mandatory 条件
        ↓
厂商规格 / 生命周期 / 当前可采购性
        ↓
配置匹配 + 当前价格证据
        ↓
BOM / 预算 / RFQ / 拓扑 / 风险
```

不会因为“看起来更专业”就自动堆：

- HCI / 超融合；
- 双机 HA；
- 双核心交换机；
- 防火墙；
- 国产化/信创；
- GPU/AI 基础设施。

这些架构只有在项目要求、风险或 SLA 真正需要时才加入。

## 核心能力

### 1. IT 基础设施架构与容量规划

支持：

- 物理服务器、传统虚拟化、HCI/HA 的适用性判断；
- Server CPU / memory sizing；
- SSD / HDD / RAID1/5/6/10 容量与可用空间计算；
- Historian 点数、采样周期、保留周期和增长容量；
- 网络端口与增长余量；
- VLAN 与 Layer-3 路由归属；
- UPS W / VA / runtime / graceful shutdown；
- 单点故障与补偿措施。

工程计算器：

```text
scripts/calculate_server_capacity.py
scripts/calculate_historian.py
scripts/calculate_storage.py
scripts/calculate_network_ports.py
scripts/calculate_ups.py
scripts/calculate_budget.py
```

### 2. SCADA / Historian / Industrial IT/OT

适用于制造业、工业自动化和集中监控项目，可分析：

- Runtime / Development；
- I/O 点数授权；
- Operator / Client；
- Web publishing / users；
- Historian / historical trend；
- Alarm / event；
- Report / API / ODBC / SDK；
- PLC drivers / OPC UA；
- redundancy；
- implementation / training / maintenance。

涉及远程启停、设定值或其他物理控制时，要求 PLC/设备侧安全逻辑保持权威，并考虑权限、二次确认、操作审计、命令反馈和拒绝原因。

### 3. 网络设计与拓扑

支持：

- access / aggregation / core 是否真正需要；
- L2 / light-L3 / core routing；
- VLAN / inter-VLAN routing；
- 网络端口和扩展余量；
- firewall/security boundary 触发条件；
- Mermaid 网络拓扑；
- Graphviz DOT 网络拓扑。

不会仅因为“有多个 VLAN”就自动增加核心交换机。

### 4. 实时价格研究与采购证据

先区分采购对象：

- `configurable-enterprise`：服务器、存储、HCI、配置型防火墙、项目型 UPS 等；
- `fixed-sku`：固定端口交换机、AP、大屏、Mini PC、固定型号 UPS 等；
- `commodity-component`：CPU、DIMM、SSD/HDD、光模块、线缆等。

技术参数与价格证据分开：

- **技术参数**优先厂商官网、Datasheet、配置/订购指南、兼容性矩阵和生命周期资料；
- **价格**按配置匹配度、当前可采购性和商业范围判断；
- 政采/公共资源交易记录属于历史可比证据，不自动等于当前市场价；
- ZOL/PConline 等同系列行情可以做市场背景，但不会自动成为完整企业配置的采购锚点。

价格证据等级：

```text
Verified
Market-verified
Comparable-transaction
Estimated
Needs confirmation
```

### 5. 已有预算 Revision Guard

当用户要求更新已有 BOM / CSV / XLSX 价格时，旧单价会先作为 revision baseline。

对 `configurable-enterprise` 设备，弱证据不能静默压低旧预算：

- Partial-config；
- 同系列/泛型号公开价；
- 起售价/裸机价；
- 历史成交；
- 组件模型；
- 工程估算。

如果要下调，执行：

```bash
python scripts/normalize_price_evidence.py <evidence.json> \
  --summary \
  --existing-budget <old-unit-price> \
  --product-class configurable-enterprise
```

只有：

```text
budget_revision.decision = revise-to-current-anchor
```

才允许执行对应下调。

项目内保存的厂家客服、官方店或授权渠道**人工当前报价**也可以成为强证据，不要求必须有公开 URL，但需要记录渠道、日期、配置匹配和商业范围。

### 6. Specification-first pricing

任何低价候选都必须先满足技术要求，才有资格进入价格比较。

UPS 例如不能只看 `VA`：

```bash
python scripts/calculate_ups.py 800 \
  --runtime-minutes 10 \
  --candidate-w 1500 \
  --candidate-va 2000 \
  --runtime-curve-verified \
  --shutdown-interface-verified
```

只有返回：

```text
status = eligible-for-pricing
```

该 UPS 才能作为较低预算的有效价格候选。

大屏同理：如果项目要求浏览器/BI 能力，无系统、无网络的显示设备必须把 OPS 或等效播放设备纳入完整商业范围后再比较。

### 7. Vendor Comparison / Tender / RFQ / Compliance

可生成：

- 厂商/型号比较矩阵；
- Mandatory knockout gate；
- weighted scoring；
- 厂商中立的招标/RFQ 技术参数；
- Mandatory / Recommended / Optional 分类；
- 合规检查；
- BOM 防漏项；
- 风险、TBD、升级触发条件。

Mandatory 条件不满足的候选不会靠评分“救回来”。

## 完整输入示例

如果想一次性测试全部主要能力，直接使用：

**[`examples/full-feature-input.md`](examples/full-feature-input.md)**

该示例会同时触发：

- architecture decision；
- server/storage/historian/network/UPS sizing；
- SCADA / IT/OT；
- live price research；
- budget revision guard；
- vendor comparison；
- tender/RFQ；
- Mermaid / Graphviz topology；
- compliance check；
- BOM / contingency / total budget。

实际项目不需要每次输出全部内容，可以组合使用，例如：

```text
price-research + bom-budget
internal-review + bom-budget
vendor-compare
tender-spec
detailed-design + topology-generation
compliance-check
```

## v1.1.2 — Budget Revision Guardrails & Specification-First Pricing

当前正式版重点：

- 修复弱价格证据错误压低已有服务器/企业设备预算；
- 人工精确当前报价可作为强价格证据；
- 一个 Tier-3 高匹配报价不足以单独压低已有企业设备预算；
- UPS 增加 W / VA / runtime / shutdown technical-fit gate；
- 固定 SKU 同样遵循“规格先于价格”；
- 安装器支持 Git / copy / symlink 安全更新；
- Codex / Claude Code / Copilot / Gemini CLI 跨平台兼容。

详见 [`RELEASE_NOTES.md`](RELEASE_NOTES.md)。

## 安装与更新

Git Clone 安装最适合持续更新：

```bash
git -C ~/.agents/skills/it-infrastructure-equipment-selection pull --ff-only
```

安装器更新：

```bash
python scripts/install_skill.py --target codex --scope user --update
```

安全规则包括：

- Git 更新使用 `pull --ff-only`；
- 工作区有本地修改时拒绝自动覆盖；
- `--force` 不删除 `.git`；
- copy 更新只同步 Skill 管理文件；
- symlink 安装可安全更新其 Git 源仓库。

## Repository Structure

```text
SKILL.md                         # portable core workflow
references/                      # engineering and procurement references
scripts/                         # deterministic calculators / generators / installer
assets/                          # structured examples and templates
examples/                        # reference designs and full-feature input example
agents/openai.yaml               # optional OpenAI/Codex metadata
.github/workflows/               # CI validation
```

## 回归测试

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
```

覆盖包括：

- 小型项目不自动推荐 HCI；
- VLAN 互通必须明确 L3 owner；
- OT 控制权限/联锁/审计；
- exact-current quote 不被弱低价拉偏；
- existing-budget revision guard；
- human exact quote priority；
- UPS technical-fit gate；
- Git/copy/symlink installer safety；
- Codex / Claude Code / Copilot / Gemini CLI portability。

---

# English

A portable **Agent Skill for IT infrastructure solution architecture and physical infrastructure procurement**.

It helps AI coding/engineering agents reason about and produce practical deliverables for:

- server sizing and storage sizing;
- network architecture, VLAN/L3 ownership and topology;
- UPS sizing, runtime and graceful shutdown;
- SCADA, Historian and industrial IT/OT infrastructure;
- hardware/equipment selection and current price research;
- exact-configuration procurement evidence;
- BOM and budget revision guardrails;
- vendor/model comparison;
- tender and RFQ specifications;
- compliance/risk checks;
- Mermaid and Graphviz network topology.

## Supported Agent Hosts

- OpenAI Codex
- Claude Code
- GitHub Copilot
- Gemini CLI
- other Agent-Skills-compatible hosts

Host-specific metadata is optional. The shared engineering logic remains in `SKILL.md`, `references/`, `scripts/`, `assets/` and `examples/`.

## Core Principle

```text
Requirements → architecture → sizing → technical fit → evidence quality → price
```

A cheaper product cannot silently redefine the technical requirement, and weak/partial price evidence cannot silently lower an existing configurable-enterprise budget.

## Full-Feature Example

See [`examples/full-feature-input.md`](examples/full-feature-input.md).

## License

MIT License
