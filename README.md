# IT Infrastructure Equipment Selection Skill

[中文说明](#中文说明) | [English](#english)

> Requirements first. Architecture second. Sizing third. Products last.

**Current release: v1.1.2**

---

# 中文说明

这是一个遵循 **Agent Skills** 结构的 IT 基础设施解决方案工程师 Skill，用于项目级设备选型、容量规划、预算、实时询价、招标参数、合规核验和网络拓扑输出。

支持：

- OpenAI Codex
- Claude Code
- GitHub Copilot
- Gemini CLI
- 其他兼容 Agent Skills 格式的平台

核心工程逻辑只维护一份：

```text
SKILL.md
references/
scripts/
assets/
examples/
```

`agents/openai.yaml` 是 OpenAI/Codex 的可选扩展元数据，不是核心运行依赖。

## v1.1.2：预算修订保护 + 规格先于价格

v1.1.2 重点修复真实项目中发现的两个问题：

1. 弱价格证据错误压低已有预算；
2. 为了匹配便宜 SKU，反过来降低技术规格。

现在统一执行：

```text
需求
  ↓
技术适配
  ↓
价格证据质量
  ↓
价格
```

### 已有预算下调保护

当用户要求“更新价格 / 重新核价 / 优化预算”时，Skill 会先读取旧 BOM/CSV/XLSX，把旧单价保留为 revision baseline。

对于服务器、存储、HCI、配置型防火墙等 `configurable-enterprise` 设备：

- PConline/ZOL 等同系列部分配置行情不能单独压低已有预算；
- 起售价、裸机价、历史成交、组件估算、工程估算不能单独作为下调锚点；
- 一个 Tier-3 高度匹配报价不足以单独下调；
- 至少需要一个 Tier-1/2 当前精确报价，或两个独立 Tier-3 高度匹配当前报价；
- 证据不足时保留旧预算，并标记 `Needs confirmation`；
- 强证据显示旧预算偏低时允许上调。

结构化检查：

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

才允许执行相应下调。

### 人工询价也是有效证据

用户提供或项目目录中保存的当前厂家客服、官方店、授权代理人工报价，即使没有公开 URL，也可以成为强证据，但必须记录：

- 渠道/卖方
- 报价日期
- 完整配置匹配
- 税/维保/附件/实施等商业范围

### UPS：先验证规格，再比较价格

UPS 不能只看 `VA`。

必须同时检查：

- 受保护负载 W
- 容量余量
- UPS 实际输出 W
- UPS VA
- 目标续航
- 厂商运行时间曲线
- 自动关机接口/软件兼容性

例如：

```bash
python scripts/calculate_ups.py 800 \
  --runtime-minutes 10 \
  --candidate-w 1500 \
  --candidate-va 2000 \
  --runtime-curve-verified \
  --shutdown-interface-verified
```

只有：

```text
status = eligible-for-pricing
```

该候选才可以作为更低预算的价格依据。

因此 `1500VA/900W` 不会仅因为“1500VA 看起来够大”就自动视为满足项目要求。

### 大屏/固定 SKU 同样遵循规格先于价格

例如项目要求浏览器/BI 展示能力时，无系统、无网络的大屏只有在把 OPS 或等效播放设备计入完整商业范围后，才能与“带浏览器能力”的方案比较价格。

### 预算汇总措辞

如果服务器、SCADA 或其他重要行仍存在税务、维保、实施、运输范围未确认，Skill 不会笼统写成“全部含税到货”。

应明确：

```text
按当前可获得证据估算；已标识项目的税务、维保、实施和/或交付范围仍需确认。
```

## v1.1.1：精准询价 + 跨平台 Agent Skills

v1.1.1 引入：

- 当前精确配置报价优先于弱历史/泛型号价格；
- 服务器配置匹配评分；
- exact-current quote range；
- `configurable-enterprise` / `fixed-sku` / `commodity-component` 分类；
- 实时价格研究；
- 跨平台 Agent Skills 安装；
- OpenAI / Claude Code / Copilot / Gemini CLI 兼容。

详细方法：

- [`references/exact-configuration-pricing.md`](references/exact-configuration-pricing.md)
- [`references/live-price-research.md`](references/live-price-research.md)
- [`references/price-evidence.md`](references/price-evidence.md)
- [`references/ups-sizing.md`](references/ups-sizing.md)
- [`references/platform-compatibility.md`](references/platform-compatibility.md)

## 安装

### OpenAI Codex

推荐 Git Clone，后续更新最简单：

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

### 安装器

```bash
python scripts/install_skill.py --target codex --scope user
python scripts/install_skill.py --target claude-code --scope user
python scripts/install_skill.py --target copilot --scope user
python scripts/install_skill.py --target gemini --scope user
```

项目级：

```bash
python scripts/install_skill.py --target codex --scope project --project-dir /path/to/project
python scripts/install_skill.py --target claude-code --scope project --project-dir /path/to/project
python scripts/install_skill.py --target copilot --scope project --project-dir /path/to/project
python scripts/install_skill.py --target gemini --scope project --project-dir /path/to/project
```

## 更新

Git Clone 安装：

```bash
git -C ~/.agents/skills/it-infrastructure-equipment-selection pull --ff-only
```

安装器更新：

```bash
python scripts/install_skill.py --target codex --scope user --update
```

更新规则：

- Git 安装执行安全 `git pull --ff-only`；
- Git 工作区有本地修改时拒绝自动覆盖；
- `--force` 不会删除 `.git`；
- copy 安装只同步 Skill 管理的文件，保留额外本地文件；
- symlink 安装可更新其 Git 源仓库。

## 工程能力

### 架构决策

- standalone physical server
- virtualization / HCI / HA
- L2 / L3 / core switching
- firewall/security boundary
- domestic/Xinchuang
- industrial IT/OT
- large display / OPS / Mini PC

不会因为“看起来更专业”就自动堆 HCI、双核心、防火墙或信创方案。

### SCADA / Historian / OT

支持：

- Runtime / Development
- I/O 点数档位
- 客户端/Web用户
- Historian/趋势
- 报警
- API/ODBC/SDK/报表
- PLC驱动 / OPC UA
- 冗余模块
- 实施、培训、维护
- OT远程启停权限、联锁、审计和执行反馈

### 工程计算器

```text
scripts/calculate_server_capacity.py
scripts/calculate_historian.py
scripts/calculate_storage.py
scripts/calculate_network_ports.py
scripts/calculate_ups.py
scripts/calculate_budget.py
```

### 可选输出

- vendor/model comparison
- tender/RFQ specification
- Mermaid / Graphviz topology
- reference design
- BOM / budget
- compliance check

## 证据等级

```text
Verified
Market-verified
Comparable-transaction
Estimated
Needs confirmation
```

技术参数和价格证据分开：

- 技术参数优先厂商官网、Datasheet、配置/订购指南、兼容性矩阵、生命周期公告；
- 当前市场价看配置匹配、可采购性和商业范围；
- 政采/公共资源成交记录属于历史可比证据，不自动等于当前市场价。

## 回归测试

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
```

当前覆盖包括：

- 小规模单服务器不自动推荐 HCI；
- 多 VLAN 互通必须明确 Layer-3；
- OT 控制权限/联锁/审计；
- exact-current quote 不被弱低价拉偏；
- 已有服务器预算下调 guard；
- 人工精确报价优先级；
- UPS W/VA/续航/关机接口 technical-fit gate；
- Git/copy/symlink 安装更新安全性；
- Codex / Claude Code / Copilot / Gemini CLI 兼容路径。

---

# English

A portable Agent Skill for IT infrastructure solution architects covering equipment selection, sizing, procurement research, BOM/budget, tender specifications and topology generation.

## Supported Hosts

- OpenAI Codex
- Claude Code
- GitHub Copilot
- Gemini CLI
- other Agent-Skills-compatible hosts

## v1.1.2 Highlights

v1.1.2 enforces two procurement rules:

> **Weak price evidence must not silently lower an existing configurable-enterprise budget.**

> **A cheaper SKU must satisfy the existing technical requirement before its price can influence the BOM.**

The workflow is now:

```text
Requirements → technical fit → evidence quality → price
```

UPS candidates can be deterministically checked for real output W, VA, runtime verification and graceful-shutdown integration before they become `eligible-for-pricing`.

The release also includes safe Git/copy/symlink update behavior added after v1.1.1.

## Quick Install

```bash
python scripts/install_skill.py --target codex --scope user
python scripts/install_skill.py --target claude-code --scope user
python scripts/install_skill.py --target copilot --scope user
python scripts/install_skill.py --target gemini --scope user
```

Git-based update:

```bash
git -C ~/.agents/skills/it-infrastructure-equipment-selection pull --ff-only
```

See [`references/platform-compatibility.md`](references/platform-compatibility.md) for discovery paths and verification.

## Procurement Principle

Technical facts should be verified with manufacturer documentation. Price evidence is evaluated separately by configuration match, current orderability and commercial scope. A lower-priced candidate must first pass technical-fit checks.

## License

MIT License
