# IT Infrastructure Equipment Selection Skill v1.1.1

## 精准询价 + 跨平台 Agent Skills

v1.1.1 是一次以**价格准确性**和**平台兼容性**为重点的版本，主要面向服务器、存储、防火墙、HCI、企业级 UPS 等高度可配置设备的项目询价、BOM 预算和采购比价场景，同时把项目从偏 Codex 的 Skill 扩展为一套可复用的跨平台 Agent Skill。

这一版本重点解决两个实际问题：

> **同一个机箱型号或产品系列，不代表同一个采购配置，也不能直接拿公开起售价、裸机价或历史成交价去估算完整配置的当前采购价格。**

以及：

> **核心工程方法不应该绑定某一个 AI Agent 平台；只要 Host 支持 Agent Skills 结构，就应该尽量复用同一套 `SKILL.md + references + scripts`。**

核心规则调整为：

> **技术参数以厂商权威资料为准；价格锚点以配置匹配度、当前可采购性和完整商业范围为准；平台能力以当前 Host 实际提供的工具为准。**

## 本次价格修复

- 当前完全同配置报价优先于低匹配的历史成交价、同系列公开价和泛型号报价。
- 两个及以上当前同配置报价直接形成主市场价格区间，不再与旧政采价、裸机价或其他弱证据做简单平均。
- 只有一个当前同配置报价时，将其作为主要价格锚点，同时明确建议取得第二份报价后再确定采购控制价。
- 同机箱、同系列、同 CPU 并不自动视为同一采购配置。
- 裸机价、起售价、基础配置价、不可下单报价、低匹配配置、商业范围不完整的报价会被排除出主预算锚点。
- 对没有当前精确报价的高度可配置企业设备，默认输出价格区间，并标记 `Estimated` 或 `Needs confirmation`，避免给出看似精确但证据不足的单点价格。
- 用户询问当前价、实时价、市场价、询价预算或当前 BOM 预算时，在具备联网能力的情况下必须先进行实时价格研究。

## 实时询价工作流

新增按采购对象分类的实时询价方法。Skill 会先判断设备属于哪一类，再决定适合的查价方式。

### `configurable-enterprise`

高度可配置企业设备，例如：

- 机架式服务器
- 存储阵列
- HCI 节点
- 带订阅/License 的防火墙
- 模块化/核心交换机
- 项目型 UPS
- 高度定制工作站

这类设备优先寻找**完整配置级的当前报价**，而不是商品页面起售价。

### `fixed-sku`

固定或半标准 SKU，例如：

- 固定端口交换机
- AP
- 显示器/大屏
- Mini PC
- 固定型号 NAS
- 固定容量 UPS

这类设备可以更多使用当前官方店、企业采购平台和多个可比 SKU 报价。

### `commodity-component`

标准组件，例如：

- CPU
- 内存 DIMM
- SSD / HDD
- 光模块
- 线缆
- 标准附件

这类产品更适合结合电商实时价格、企业采购平台和价格历史工具判断市场区间。

## 中国市场价格渠道

针对国内项目，新增了更明确的渠道角色划分，但**不硬编码一个永远固定的网站优先级**。

- **厂商直销 / 官方客服 / 官方品牌店 / 授权合作伙伴**：适合确认完整配置、维保、税、交期以及最终企业级报价。
- **京东 / 天猫官方或企业渠道**：适合固定 SKU、标准组件，以及经过客服确认的完整定制配置。
- **ZOL / 市场聚合器**：用于观察市场价差、发现渠道和做合理性校验；如果配置、税、维保等范围不清楚，不直接作为最终预算锚点。
- **价格历史工具**：更适合 SSD、内存、硬盘、CPU、显示器、Mini PC 等标准产品，用于观察价格趋势。
- **政府采购 / 公共资源交易记录**：作为历史可比成交证据，而不是当前实时报价。

因此，服务器等企业定制设备不会再按照“看到一个同型号低价 → 按经验加配置系数”的方式估算。

## 配置匹配评分

默认服务器配置匹配模型会检查：

- CPU 型号和数量
- 内存容量 / 类型 / 模块布局
- SSD / NVMe 配置
- HDD 配置
- RAID / HBA / Cache / 掉电保护（PLP）
- 网卡 / 网络端口
- 电源数量 / 冗余
- 维保 / 技术支持
- 税务范围
- 导轨、电源线等必要附件

默认判断标准：

```text
>= 0.95      精确 / 基本等同配置
0.85–0.949   高度可比
0.70–0.849   仅可辅助比较
< 0.70       不可直接作为预算锚点
```

同型号机箱不会自动获得高匹配分。

## 价格证据优先级

1. 当前完全同配置正式报价
2. 当前完全同配置可信市场报价
3. 当前高度匹配报价
4. 历史可比采购成交
5. 拆分组件成本模型
6. 同型号 / 同系列泛配置公开价
7. 工程经验估算

低优先级价格仍然可以作为市场背景和合理性校验，但**不会再机械地把更强的当前同配置报价区间向上或向下拉偏**。

## 跨平台 Agent Skills 支持

v1.1.1 的核心 Skill 现在按可移植 Agent Skills 结构维护，并面向：

- **OpenAI Codex**
- **Claude Code**
- **GitHub Copilot**
- **Gemini CLI**
- 其他兼容 Agent Skills 格式的平台（以各 Host 当前实现为准）

核心工程逻辑只维护一份：

```text
SKILL.md
references/
scripts/
assets/
examples/
```

`agents/openai.yaml` 保留为 OpenAI/Codex 的可选扩展元数据，但其他平台不需要依赖它才能读取和执行 Skill 的核心工程流程。

### 平台路径

默认兼容路径：

```text
Codex 用户级:        ~/.agents/skills/<skill-name>/
Claude Code 用户级:  ~/.claude/skills/<skill-name>/
Copilot 用户级:      ~/.agents/skills/<skill-name>/
Gemini CLI 用户级:   ~/.agents/skills/<skill-name>/
```

项目级安装则分别使用 Host 支持的 `.agents/skills`、`.claude/skills` 或 `.github/skills` 目录。

新增：

```bash
python scripts/install_skill.py --target codex --scope user
python scripts/install_skill.py --target claude-code --scope user
python scripts/install_skill.py --target copilot --scope user
python scripts/install_skill.py --target gemini --scope user
```

详细说明见：

- `references/platform-compatibility.md`

### 平台能力降级规则

Skill 格式兼容不代表各个平台拥有完全相同的工具。

因此 v1.1.1 明确规定：

- 当前 Host 有实时 Web/Search 能力时，当前价格请求必须实时查价；
- 没有联网能力时，不得把旧数据冒充当前市场价，降级为 `Needs confirmation` 或工程估算；
- 有 Python/Shell 时优先运行确定性计算脚本；
- 没有脚本执行能力时，可以按引用文档中的公式和规则人工推导，但要明确说明计算器未实际运行；
- 不假设某个 MCP、浏览器、采购插件或 Shell 权限天然存在。

这样可以保证“跨平台”不会以牺牲证据质量为代价。

## 价格证据工具增强

`normalize_price_evidence.py` 现在支持配置匹配评分和主预算锚点选择：

```bash
python scripts/normalize_price_evidence.py assets/price-evidence-example.json --summary
```

新增/增强输出字段包括：

- `configuration_match_score`
- `evidence_priority`
- `anchor_eligible`
- `anchor_exclusion_reasons`
- `price_signal_role`
- `confidence_level`
- 推荐预算下限 / 上限

这样可以保留低价、历史价、聚合器价格等信息，同时明确为什么它们没有进入最终预算区间。

## 回归测试

价格准确性回归测试专门验证：

> 两个当前同配置服务器报价已经存在时，即使同时出现更便宜的历史成交价、ZOL/聚合器价格、裸机价或起售价，最终预算锚点仍必须保持在当前同配置报价区间。

新增平台兼容回归测试，验证：

- `SKILL.md` 的可移植 frontmatter；
- `license: MIT`；
- Codex / Claude Code / Copilot / Gemini CLI 的用户级与项目级安装路径；
- portable runtime 文件复制；
- OpenAI 专用 metadata 不成为其他平台的运行依赖。

GitHub Actions 会同时验证：

- Python 语法
- 工程场景回归测试
- 架构决策检查
- 容量计算器
- 实时价格归一化和预算锚点选择
- Agent Skills 平台兼容性
- 厂商/型号比较
- 招标参数生成
- Mermaid / Graphviz 网络拓扑生成

## 从 v1.1.0 升级

无需迁移。

已有用户直接更新 Skill 目录即可使用新的：

- 精确配置价格匹配
- 实时询价流程
- 价格证据分级
- 异常 / 起售价排除规则
- 主预算锚点选择逻辑
- Claude Code / GitHub Copilot / Gemini CLI 兼容安装

---

# English

## Pricing Accuracy & Cross-Platform Agent Skills

v1.1.1 improves both pricing accuracy and host portability for enterprise infrastructure selection, quotation-oriented BOMs and procurement comparison.

The guiding rules are:

> **Technical facts follow authoritative manufacturer documentation. Price anchors follow configuration match, current orderability and complete commercial scope.**

> **Core engineering logic stays in the portable Agent Skills layer; host-specific metadata is optional.**

## Pricing Fixes

- Current exact-configuration quotations outrank lower-match historical or generic model-family prices when setting budget anchors.
- Two or more exact current quotes define the primary observed market range without being averaged together with weaker evidence tiers.
- One exact current quote is used as the primary anchor while explicitly recommending a second quote before fixing a procurement control price.
- Same-chassis listings are no longer treated as equivalent procurement configurations.
- Bare-chassis prices, starting/base prices, unavailable offers, low-match configurations and incomplete commercial scope are excluded from the primary budget anchor.
- Highly configurable enterprise equipment without exact current quotations returns a range with `Estimated` or `Needs confirmation` instead of false precision.
- Current-price requests require live research when live research tools are available.

## Cross-Platform Support

The shared skill is designed for:

- OpenAI Codex
- Claude Code
- GitHub Copilot
- Gemini CLI
- other Agent-Skills-compatible hosts

Portable runtime:

```text
SKILL.md
references/
scripts/
assets/
examples/
```

`agents/openai.yaml` remains an optional OpenAI/Codex extension and is not required by the shared engineering workflow.

Install helper:

```bash
python scripts/install_skill.py --target codex --scope user
python scripts/install_skill.py --target claude-code --scope user
python scripts/install_skill.py --target copilot --scope user
python scripts/install_skill.py --target gemini --scope user
```

See `references/platform-compatibility.md` for host-specific discovery paths and verification.

## Configuration Match Scoring

```text
>= 0.95      Exact / effectively exact
0.85–0.949   Highly comparable
0.70–0.849   Partial comparison only
< 0.70       Not a direct budget anchor
```

## Price Evidence Priority

1. Exact current formal quotation
2. Exact current credible market quotation
3. Highly matched current quotation
4. Comparable historical transaction
5. Component-cost model
6. Generic model-family listing
7. Engineering estimate

Lower-priority evidence remains useful as context but does not mechanically pull a stronger exact-current quote range upward or downward.

## Tooling

```bash
python scripts/normalize_price_evidence.py assets/price-evidence-example.json --summary
```

## Upgrade Notes

No migration is required from v1.1.0. Existing users can update the skill directory and immediately use the new live price-research, evidence-ranking and cross-platform Agent Skills rules.

## License

MIT License
