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

## 输入示例

### 全功能项目输入示例

下面这个示例用于一次性触发 Skill 的主要能力：架构决策、服务器/存储/Historian/网络/UPS 容量计算、SCADA/OT 规划、实时设备选型与价格证据、已有预算修订保护、厂商比较、招标参数、网络拓扑、合规检查和 BOM 预算。

> 在 Claude Code 中可把第一行 `$it-infrastructure-equipment-selection` 替换为 `/it-infrastructure-equipment-selection`；其他兼容 Host 按各自 Skill 调用方式使用。

```text
$it-infrastructure-equipment-selection

你是一名负责制造业 IT/OT 基础设施方案、设备选型和采购技术支持的高级解决方案工程师。

请为一个中小型制造工厂的一期集中监控与 IT/OT 基础设施项目做完整方案，并同时执行本 Skill 支持的架构决策、容量规划、实时价格研究、厂商比较、招标参数、网络拓扑、合规检查和 BOM 预算功能。

一、项目背景

- 工厂为两层建筑，一期使用面积约 5,000 平方米，后续可能扩展到 10,000–15,000 平方米。
- 一期建设 SCADA 集中监控、历史数据、报警、报表、BI 大屏和少量现场操作站。
- 不预设 HCI、双机、双核心或防火墙，是否需要由需求和风险决定。
- 优先采用维护简单、生命周期稳定、当前可采购的设备。
- 如果没有明确国产化/信创要求，不要强制加入信创约束。

二、SCADA / OT 规模

- SCADA 授权规模约 3,000 I/O 点。
- 历史记录点约 1,200 点。
- 平均有效采样周期按 5 秒估算，关键点可更快。
- 历史数据至少保留 1 年，并预留 30% 容量余量。
- 4 个现场操作站。
- 2 块 100 英寸大屏，用于生产、报警、设备状态和能耗展示。
- 大屏必须具备浏览器/BI 展示能力；若显示设备本身不具备，应把 OPS 或等效播放设备计入完整 BOM 和价格范围。
- 需要 OPC UA、主流 PLC 通讯驱动、报警、历史趋势、报表/API。
- 有少量设备需要通过 SCADA 发起远程启停，但 PLC/设备侧安全联锁必须保持最高优先级；需要权限、二次确认、操作审计、命令反馈和拒绝原因。

三、服务器与存储

计划用 1 台物理服务器集中承载 SCADA、Historian、数据库、Web/BI 和接口服务，请先判断单服务器架构是否合理，再做容量计算。

初始参考配置：

- 2U 机架式服务器
- 单 CPU 12–16 核
- 128GB ECC
- 2×960GB 企业级 SSD RAID1：系统
- 2×1.92TB 企业级 SSD RAID1：数据库/热数据
- 4×4TB 企业级 HDD RAID10：历史归档
- 硬 RAID，带缓存和掉电保护
- 独立 BMC
- 双电源 1+1
- 至少 2×1GbE
- 3 年质保

请根据实际负载重新计算 CPU、内存、Historian、数据库和存储容量，不要因为我给了参考配置就默认它一定正确。

四、网络

- 一期预计约 30 个有线 IT/OT 端口。
- 规划 5 个 VLAN：管理、服务器、SCADA/操作站、生产 OT、访客/办公。
- 部分 VLAN 需要互通，请明确 Layer-3 路由功能由谁承担。
- 优先判断 1 台 48 口轻三层网管交换机是否足够，不要因为有多个 VLAN 就自动增加核心交换机。
- 后续端口数可能增长约 50%。
- 如果安全边界确实需要防火墙，请说明触发条件、保护对象和性能口径；否则不要为了“完整”而强行加入。

五、UPS

UPS 只保护服务器、交换机和必要管理设备，不保护 4 台现场电脑和 2 块大屏。

目标：

- 断电后至少支撑 10 分钟或完成数据库/SCADA 安全停止与服务器优雅关机。
- 必须同时校验 W、VA、容量余量、目标负载下运行时间曲线、纯正弦波/服务器电源兼容性，以及 USB/串口/网络关机接口和软件兼容性。
- 任何更便宜的 UPS SKU 必须先通过 technical-fit gate，只有 `eligible-for-pricing` 才能作为下调预算依据。

六、已有预算基线

这是一个“重新核价”任务。下面是现有单价基线，不能被弱证据静默覆盖：

- 中心服务器：92,000 元/台
- 48 口交换机：6,500 元/台
- UPS：5,000 元/台
- 现场控制电脑：4,500 元/套，共 4 套
- 100 英寸大屏：22,000 元/块，共 2 块
- 国产 SCADA 软件包：60,000 元/套

对于服务器、存储、配置型防火墙等 `configurable-enterprise` 设备，如果要下调已有预算，必须执行预算 revision guard。

PConline/ZOL 同系列部分配置、裸机价、起售价、历史成交、组件估算、工程估算只能作为背景，不能单独把已有预算往下调。

如果项目目录或用户提供资料中存在厂家客服、官方店、授权代理的当前人工报价，应优先复用；只要渠道、日期、配置匹配和商业范围可确认，即使没有公开 URL，也可以作为强证据。

七、设备选型与实时价格

请基于当前可获得信息：

1. 查找仍在售/可采购的候选产品；
2. 技术规格优先使用厂商官网、Datasheet、配置指南、兼容性矩阵或生命周期资料；
3. 价格按 `configurable-enterprise`、`fixed-sku`、`commodity-component` 分类选择证据渠道；
4. 对企业定制设备优先寻找完整配置级当前报价；
5. 对固定 SKU 收集多个当前可比报价；
6. 标出税、维保、License、附件、实施、运输等商业范围是否完整；
7. 对不能作为主预算锚点的低价信号保留“排除原因”；
8. 不要为了匹配低价 SKU 反向降低原技术需求。

八、厂商比较

对关键设备至少给出 2–3 个候选厂商/型号或产品系列，并执行 vendor comparison。

比较维度至少包括：

- Mandatory 技术要求是否满足
- 生命周期/当前可采购性
- 配置匹配度
- 维保与实施
- 扩展性
- 运维复杂度
- 当前价格证据质量
- 项目总成本

Mandatory 不满足的候选必须先淘汰，不能靠加权评分救回来。

九、招标/RFQ 参数

基于推荐方案生成一版厂商中立的采购/询价技术参数：

- 按 Mandatory / Recommended / Optional 分类；
- 关键参数要可测量、可验收；
- 对服务器、交换机、UPS、大屏、现场电脑和 SCADA 软件分别生成；
- 不要把推荐品牌型号直接写成排他性参数；
- 无法确认的参数写 TBD，不要虚构。

十、网络拓扑

生成：

1. Mermaid 逻辑网络拓扑；
2. Graphviz DOT 拓扑。

拓扑必须与最终 BOM 和架构决策一致。

不要虚构 VLAN ID、IP 地址、具体物理端口、冗余链路或安全区域；未知项使用逻辑名称/TBD。

十一、合规与风险检查

检查至少包括：

- 是否存在单点故障；
- 单服务器方案的 RAID、UPS、自动关机和独立备份措施；
- Layer-3 路由归属；
- OT/IT 访问边界；
- SCADA 远程启停的权限、联锁、二次确认、审计和反馈；
- 历史数据容量与保留周期；
- License/客户端/Web/OPC UA/驱动是否漏项；
- UPS 是否真实满足负载和续航；
- 大屏是否真实具备 Web/BI 播放能力；
- 税、维保、实施、运输是否已经确认。

十二、最终输出

请按以下顺序输出：

1. 已知条件 / 假设 / TBD
2. 架构决策与理由
3. CPU / 内存 / Historian / 存储 / 网络端口 / UPS 容量计算
4. 推荐技术规格
5. 当前候选设备与厂商比较矩阵
6. 当前价格证据表：报价、日期、渠道、配置匹配、证据等级、排除原因
7. 已有预算 revision 结果：旧价格、新价格/区间、是否允许修改、guard decision
8. 推荐 BOM 和预算区间
9. 10% 不可预见费及总预算
10. 可压缩项 / 可选项 / 升级触发条件
11. 招标/RFQ 技术参数
12. Mermaid 网络拓扑
13. Graphviz DOT 网络拓扑
14. 合规检查与风险清单
15. 待厂家/用户确认事项

输出预算时不要在税、维保、实施或运输尚未确认的情况下笼统写“全部含税到货”。请明确哪些项目已确认，哪些仍为 `Needs confirmation`。
```

这个输入示例故意把多个功能放在同一个任务里。实际项目不需要每次都要求全部输出；可以只调用需要的部分，例如 `price-research + bom-budget`、`vendor-compare`、`tender-spec` 或 `topology-generation`。

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
