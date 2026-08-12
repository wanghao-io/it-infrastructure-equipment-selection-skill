# IT Infrastructure Equipment Selection Skill

[中文说明](#中文说明) | [English](#english)

> Requirements first. Architecture second. Sizing third. Products last.

**Current release: v1.1.1**

---

# 中文说明

这是一个遵循 **Agent Skills** 结构的 IT 基础设施解决方案工程师 Skill，用于项目级设备选型、容量规划、预算、实时询价、招标参数、合规核验和网络拓扑输出。

当前面向以下 Agent Host：

- OpenAI Codex
- Claude Code
- GitHub Copilot
- Gemini CLI
- 其他兼容 Agent Skills 格式的平台（以各平台当前实现为准）

核心工程逻辑只维护一份 `SKILL.md + references + scripts + assets + examples`。`agents/openai.yaml` 只是 OpenAI/Codex 的可选增强元数据，不是 Skill 的运行依赖。

它的目标不是把每个项目都做成“大而全”的数据中心，而是：

> **用满足实际需求的最简架构，明确风险，再选择可采购的设备和软件。**

因此以下方案全部是**按需**而不是默认：

- 超融合 HCI
- 高可用/双机
- 核心交换机/双核心
- 防火墙/安全边界
- 国产化/信创
- 工业 IT/OT 分区
- GPU/AI 基础设施

## v1.1.1 重点：价格准确性 + 跨平台 Agent Skills

v1.1.1 一方面修复企业级硬件询价和预算准确性，另一方面把仓库从 Codex 单平台定位扩展为可复用的跨平台 Agent Skill。

价格侧：

- 当前完全同配置报价优先于低匹配历史成交价、裸机价和同系列起售价；
- 同机箱/同系列不再自动视为同一采购配置；
- 服务器等高度可配置设备按 CPU、内存、SSD、HDD、RAID、网卡、电源、维保、税和附件计算配置匹配度；
- 两个及以上当前同配置报价直接形成主市场区间，不再与旧政采价或泛型号价格做平均；
- 当前价格请求在具备联网能力时必须先做实时研究；
- 先区分 `configurable-enterprise`、`fixed-sku`、`commodity-component`，再选择价格渠道；
- 京东/天猫官方或企业渠道、厂商/授权报价、ZOL/市场聚合器、价格历史和政采记录按证据角色使用，不硬编码单一网站优先级；
- 起售价、不可下单、低匹配、商业范围不完整、二手/翻新等信号会被排除出主预算锚点并保留排除原因。

平台兼容侧：

- `SKILL.md` 使用可移植 frontmatter：`name`、`description`、`license`；
- 新增 [`references/platform-compatibility.md`](references/platform-compatibility.md)；
- 新增 `scripts/install_skill.py`，支持 Codex、Claude Code、GitHub Copilot、Gemini CLI 的用户级和项目级安装；
- 平台特定能力（联网、Shell、Python、MCP 等）按“当前 Host 实际可用能力”处理，不假设每个平台工具完全相同；
- 无法联网时不会把旧价格冒充实时报价，而是降级为 `Needs confirmation` / 工程估算。

详细方法：

- [`references/exact-configuration-pricing.md`](references/exact-configuration-pricing.md)
- [`references/live-price-research.md`](references/live-price-research.md)
- [`references/price-evidence.md`](references/price-evidence.md)
- [`references/platform-compatibility.md`](references/platform-compatibility.md)

结构化价格证据可运行：

```bash
python scripts/normalize_price_evidence.py assets/price-evidence-example.json --summary
```

## 平台兼容与安装

### OpenAI Codex

用户级：

```bash
git clone https://github.com/wanghao-io/it-infrastructure-equipment-selection-skill.git \
  ~/.agents/skills/it-infrastructure-equipment-selection
```

或在已克隆仓库中：

```bash
python scripts/install_skill.py --target codex --scope user
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

或：

```bash
python scripts/install_skill.py --target claude-code --scope user
```

调用：

```text
/it-infrastructure-equipment-selection
```

Claude Code 也可以根据 `description` 自动选择 Skill。

### GitHub Copilot

用户级推荐使用可移植 `.agents/skills` 路径：

```bash
python scripts/install_skill.py --target copilot --scope user
```

项目级默认安装到：

```text
.github/skills/it-infrastructure-equipment-selection/
```

### Gemini CLI

Gemini CLI 支持 `.agents/skills` 兼容路径：

```bash
python scripts/install_skill.py --target gemini --scope user
```

安装后可在 Gemini CLI 中检查：

```text
/skills list
```

修改后可：

```text
/skills reload
```

### 项目级安装

```bash
python scripts/install_skill.py --target codex --scope project --project-dir /path/to/project
python scripts/install_skill.py --target claude-code --scope project --project-dir /path/to/project
python scripts/install_skill.py --target copilot --scope project --project-dir /path/to/project
python scripts/install_skill.py --target gemini --scope project --project-dir /path/to/project
```

开发阶段可用 `--mode symlink`；需要覆盖现有安装时显式加 `--force`。

> Skill 格式兼容不等于各平台提供完全相同的联网、浏览器、Shell、Python 或 MCP 工具。涉及实时价格时，若当前 Host 无实时搜索能力，Skill 会明确降低置信度，而不是假设数据已经验证。

## v1.1.0 正式版重点

### 1. 架构决策

新增 [`references/architecture-decision.md`](references/architecture-decision.md)。

可以判断：

- 单服务器 vs 虚拟化 vs HCI/HA
- 二层网管交换机 vs 轻三层 vs 独立核心/汇聚
- 是否需要防火墙/边界设备
- 是否需要国产化/信创
- 经济型 UPS vs 在线长延时 UPS
- 大屏内置播放 vs OPS vs Mini PC

关键规则：

- 虚拟化不等于必须 HCI。
- VLAN 不等于路由；多个 VLAN 需要互通时必须明确谁承担三层路由。
- 单服务器可以是合理的低预算方案，但必须暴露单点风险并检查 RAID、UPS/自动关机、独立备份。

结构化检查工具：

```bash
python scripts/evaluate_architecture.py <requirements.json> --pretty
```

### 2. SCADA / Historian / OT 专项

新增：

- [`references/scada-sizing.md`](references/scada-sizing.md)
- [`references/ot-control-safety.md`](references/ot-control-safety.md)

SCADA 采购不再只写“软件1套”，而是按需拆分：

- Runtime
- Development
- I/O 点数档位
- 操作站/客户端
- Web 发布/并发用户
- Historian/历史趋势
- 报警
- API/ODBC/SDK/报表接口
- Modbus TCP / OPC UA / PLC 品牌驱动
- 冗余模块（仅在需要时）
- 安装调试、培训、维护

远程启动/停止等 OT 控制必须保留 PLC/设备侧许可与联锁，并考虑权限、二次确认、操作审计和执行反馈。

### 3. 更实用的工程计算器

```text
scripts/calculate_server_capacity.py   # 虚拟化或多服务整合服务器CPU/内存
scripts/calculate_historian.py         # Historian点数/采样周期/保留容量
scripts/calculate_storage.py           # RAID1/5/6/10及保留容量
scripts/calculate_network_ports.py     # 端口余量及跨VLAN三层需求
scripts/calculate_ups.py               # W、VA、短时续航目标/自动关机
scripts/calculate_budget.py            # BOM合计及不可预见费
```

例如：

```bash
python scripts/calculate_server_capacity.py --services-json assets/server-workload-example.json
python scripts/calculate_historian.py 2000 5 --retention-days 365
python scripts/calculate_storage.py --drives 4 --drive-tb 4 --raid 10
python scripts/calculate_network_ports.py 30 --vlan-count 5 --inter-vlan
python scripts/calculate_ups.py 600 --runtime-minutes 10
```

### 4. 设备选型与预算证据

详细方法：

- [`references/procurement-research.md`](references/procurement-research.md)
- [`references/price-evidence.md`](references/price-evidence.md)

技术参数与价格证据分开：

- **技术参数**：优先厂商官网、Datasheet、配置/订购指南、兼容性矩阵、生命周期公告。
- **当前市场价**：优先当前、可购、配置匹配的报价；企业采购平台和市场聚合器按证据角色使用。
- **历史可比成交价**：政府采购/公共资源交易等正式成交记录可作为历史基准，但不是实时报价。
- **预算**：比较完整配置，而不是只比较机箱型号。

证据等级：

```text
Verified
Market-verified
Comparable-transaction
Estimated
Needs confirmation
```

### 5. 厂商比较、招标参数和网络拓扑

厂商/型号比较：

```bash
python scripts/compare_vendors.py assets/vendor-comparison-example.json
```

规则：强制项先淘汰，再做加权评分；评分是项目级配置评分，不是品牌永久排名。

招标/RFQ参数：

```bash
python scripts/generate_tender_spec.py assets/tender-requirements-example.json
```

按 Mandatory / Recommended / Optional 生成尽量厂商中立、可验收的技术条款。

网络拓扑：

```bash
python scripts/generate_topology.py assets/topology-input-example.json --format mermaid --markdown
python scripts/generate_topology.py assets/topology-input-example.json --format dot
```

不会自动虚构 VLAN ID、IP、物理端口、冗余链路或安全区域。

## 输出模式

见 [`references/output-profiles.md`](references/output-profiles.md)：

- `quick-selection`
- `internal-review`
- `procurement-rfq`
- `detailed-design`
- `compliance-check`
- `bom-budget`

可以组合，例如：

```text
internal-review + bom-budget
procurement-rfq + tender-spec
detailed-design + topology-generation
```

中文预算 CSV 推荐字段模板：[`assets/project-budget-template.csv`](assets/project-budget-template.csv)。CSV 生成工具默认可使用 `utf-8-sig`，便于中文版 Excel 直接打开。

## 工作流程

```text
已知条件 / 假设 / TBD
        ↓
强制要求 / 可用性 / 预算
        ↓
最简合理架构决策
        ↓
CPU / 内存 / Historian / 存储 / 网络 / UPS容量
        ↓
技术规格
        ↓
官方规格与生命周期验证
        ↓
实时价格 / 配置匹配 / 历史可比成交证据
        ↓
按需生成厂商矩阵 / 招标参数 / 拓扑
        ↓
BOM + 预算区间 + 可压缩项
        ↓
风险 / 升级触发条件 / 待厂家确认项
```

## BOM 防漏项

见 [`references/bom-checklist.md`](references/bom-checklist.md)。目前覆盖：

- Server / Storage / Backup
- Network / optics / cabling
- UPS / PDU / rack
- Workstation
- Large display / OPS
- SCADA / Historian / BI 授权
- OT远程控制配置
- 安装、调试、培训、维保

## Examples

- [Industrial SCADA + HCI Reference Design](examples/industrial-scada-hci-reference-design.md)
- [Enterprise Campus IT Infrastructure Reference Design](examples/enterprise-campus-reference-design.md)
- [Healthcare IT Infrastructure Reference Design](examples/healthcare-it-reference-design.md)
- [Small Data Center / Server Room Reference Design](examples/small-datacenter-reference-design.md)

Examples 是方法模板，不是默认架构。所有容量、冗余和安全设计都必须针对新项目重新判断。

## 回归测试

当前回归测试覆盖：

- 小规模单服务器不应自动推荐 HCI；
- 多 VLAN 互通必须明确 Layer-3；
- 未要求信创时不应强制信创；
- 隔离小型 OT 不自动堆防火墙；
- 单服务器必须暴露 RAID/UPS/备份要求；
- OT 远程启停必须保留权限、审计、联锁和执行反馈；
- 当前完全同配置报价不能被更低的历史价、聚合器价、裸机价或起售价拉低；
- Agent Skills frontmatter 满足可移植约束；
- Codex / Claude Code / Copilot / Gemini CLI 安装路径映射与复制安装可回归验证。

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
```

---

# English

A portable Agent Skill for IT infrastructure solution architects covering equipment selection, sizing, procurement research, BOM/budget, tender specifications and topology generation.

## Supported Agent Hosts

The shared `SKILL.md` is designed for:

- OpenAI Codex
- Claude Code
- GitHub Copilot
- Gemini CLI
- other hosts implementing the Agent Skills format

OpenAI-specific `agents/openai.yaml` metadata is optional and does not contain the core workflow.

## Design Principle

> Requirements first. Architecture second. Sizing third. Products last.

The skill deliberately avoids forcing HCI, HA, core switching, firewalls or domestic/Xinchuang platforms into every project.

## v1.1.1 Pricing Accuracy & Portability

- Live current-price research when live research tools are available
- Procurement-object classification: configurable enterprise, fixed SKU and commodity component
- Exact-configuration pricing priority for highly configurable enterprise hardware
- Configuration-match scoring for servers and similar equipment
- Exact current quote ranges are not blended with weaker historical or generic prices
- Starting/base prices, unavailable offers and incomplete commercial scopes are excluded from primary budget anchors
- Market aggregators and price-history tools are treated according to evidence role rather than as universal authorities
- Portable Agent Skills frontmatter and resource layout
- Cross-platform installer for Codex, Claude Code, GitHub Copilot and Gemini CLI
- Host capability differences handled explicitly instead of assuming identical tools

## Quick Install

```bash
python scripts/install_skill.py --target codex --scope user
python scripts/install_skill.py --target claude-code --scope user
python scripts/install_skill.py --target copilot --scope user
python scripts/install_skill.py --target gemini --scope user
```

See [`references/platform-compatibility.md`](references/platform-compatibility.md) for host-specific discovery locations and verification steps.

## v1.1.0 Highlights

- Requirement-driven architecture decisions
- SCADA/historian sizing and licensing breakdown
- OT remote-control safety requirements
- Service-based server sizing
- Historian retention calculator
- RAID-aware storage sizing
- W/VA/runtime-objective UPS sizing
- Network port and inter-VLAN routing checks
- Structured price evidence normalization
- Project budget CSV template and contingency calculation
- Engineering scenario regression tests

## Procurement Principle

Technical facts should be verified with manufacturer documentation. Price evidence is evaluated separately by configuration match, current orderability and commercial scope; exact configured cost should include required accessories, licenses, warranty/support, tax and implementation scope.

## Artifacts

Optional modes include:

- vendor/model comparison
- tender/RFQ specification generation
- Mermaid/Graphviz topology generation
- anonymized industry reference designs

## License

MIT License
