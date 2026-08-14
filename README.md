# IT Infrastructure Equipment Selection Agent Skill

[![Release](https://img.shields.io/github/v/release/wanghao-io/it-infrastructure-equipment-selection-skill)](../../releases/latest)
[![CI](https://github.com/wanghao-io/it-infrastructure-equipment-selection-skill/actions/workflows/validate-skill.yml/badge.svg)](../../actions/workflows/validate-skill.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

面向企业 IT 基础设施与工业 IT/OT 项目的跨平台 Agent Skill：从需求发现、最简合理架构和确定性容量计算，一直到设备选型、实时价格证据、TCO、BOM、RFQ/招标、合规检查与网络拓扑。

Supported hosts include OpenAI Codex, Claude Code, GitHub Copilot, Gemini CLI and other compatible Agent Skills hosts.

Current stable version: **v1.4.2**. See the current [Release Notes](RELEASE_NOTES.md) and cumulative [Changelog](CHANGELOG.md).

[两条使用路径](#两条使用路径) · [任务配方](#可复制任务配方) · [Schema 治理](#schema-v1--v2-治理) · [私有扩展](#私有扩展边界) · [English](#english) · [Release Notes](RELEASE_NOTES.md) · [Contributing](CONTRIBUTING.md)

> **Requirements first → architecture → sizing → Mandatory fit → evidence → price.**
>
> 便宜 SKU 不能反向定义需求；HCI、HA、双核心、防火墙、信创和 GPU 都不是默认架构。

## 当前能力

| 领域 | 能力 |
|---|---|
| 需求与决策 | 场景化需求向导、事实/假设/TBD 分离、Mandatory PASS/CONDITIONAL/FAIL、最简合理架构 |
| 计算与容量 | Server、RAID/存储、Historian、网络端口、UPS W/VA、HCI N+1、3/5 年 TCO |
| IT/OT | SCADA License 拆分、Historian、VLAN/L3 归属、OT 远程控制安全、单点风险 |
| 采购与价格 | 当前价格研究、精确配置证据、供应商独立性、商业范围归一、已有预算下调保护 |
| 交付物 | BOM、预算、服务器 RFQ、厂商比较、招标参数、合规矩阵、Mermaid/Graphviz 拓扑 |
| 数据契约 | Draft 2020-12 Schema v1/v2、严格预检、非破坏迁移、真实项目复盘阶段门禁 |
| 企业扩展 | 公共核心、私有适配器与受控原始数据的明确边界；不自动发现私有数据 |
| 可移植性 | Codex、Claude Code、Copilot、Gemini CLI；Git/copy/symlink 安全安装与更新 |

关键安全行为：

- 缺失 Mandatory 证据保持 `CONDITIONAL`，不会被评分或 TCO “救回”；
- 所有品类先通过技术适配，价格才可进入预算锚点；
- 当前价格请求在工具可用时必须做实时研究，否则标记 `Needs confirmation`；
- 一个供应商的多个报价号只算一个独立来源；同供应商报价修订按最新有效记录稳定选择；
- 不同 BOM 行、产品或项目的证据不能混入同一 `decision_scope_id`；
- 设计基线、当前报价、成交、结算和运行测量保持不同证据阶段。

## 两条使用路径

### 路径 A：Agent 完整工作流

适用于需求不完整、架构设计、产品选型、当前询价、预算修订和交付物生成。Agent 从 `SKILL.md` 的 Router 选择必要 reference，并按项目阶段组合模式。

安装到 OpenAI Codex：

```bash
git clone https://github.com/wanghao-io/it-infrastructure-equipment-selection-skill.git \
  ~/.agents/skills/it-infrastructure-equipment-selection
```

调用：

```text
$it-infrastructure-equipment-selection
```

Claude Code：

```bash
git clone https://github.com/wanghao-io/it-infrastructure-equipment-selection-skill.git \
  ~/.claude/skills/it-infrastructure-equipment-selection
```

```text
/it-infrastructure-equipment-selection
```

GitHub Copilot / `gh skill`：

```bash
gh skill preview wanghao-io/it-infrastructure-equipment-selection-skill it-infrastructure-equipment-selection
gh skill install wanghao-io/it-infrastructure-equipment-selection-skill
```

跨平台安装器：

```bash
python3 scripts/install_skill.py --target codex --scope user
python3 scripts/install_skill.py --target claude-code --scope user
python3 scripts/install_skill.py --target copilot --scope user
python3 scripts/install_skill.py --target gemini --scope user
```

完整路径、项目级安装和发现验证见 [`references/platform-compatibility.md`](references/platform-compatibility.md)。

### 路径 B：确定性 CLI 与 Schema

适合已经有明确输入，只需要可复现计算、契约校验或迁移报告的场景。该路径不执行实时研究，也不替代 Agent 的架构、兼容性和采购判断。

发现可用工具与契约：

```bash
python3 scripts/infra_cli.py list
python3 scripts/infra_cli.py list --json
python3 scripts/infra_cli.py example ups
```

运行计算器：

```bash
python3 scripts/infra_cli.py run storage -- --drives 6 --drive-tb 4 --raid 10
python3 scripts/infra_cli.py run historian -- 5000 5 --retention-days 365
python3 scripts/infra_cli.py run hci-failover -- assets/hci-failover-example.json --pretty
```

校验结构化输入：

```bash
python3 scripts/infra_cli.py validate price-evidence-v2 assets/price-evidence-v2-example.json
python3 scripts/validate_json_schemas.py --catalog
```

`assets/tool-catalog.json` 是确定性 CLI 的白名单；Agent 仍可按 Router 使用其他专用脚本。

## 可复制任务配方

### 需求发现

```text
$it-infrastructure-equipment-selection
按 guided-requirements 模式分析这个小型制造业 SCADA 项目。
先列已知事实、假设和 TBD，只追问最影响架构的 5 个问题，不预设 HCI/HA。
```

确定性需求清单：

```bash
python3 scripts/guide_requirements.py \
  --scenario manufacturing-scada-small \
  --input project-known-fields.json \
  --max-questions 5 \
  --pretty
```

### 项目方案与容量

```text
$it-infrastructure-equipment-selection
按 project-design + internal-review 输出最简合理架构。
分别计算服务器、Historian、存储、交换机端口和 UPS，并列出单点风险与升级触发条件。
```

### 当前设备选型与价格

```text
$it-infrastructure-equipment-selection
按 single-device + price-research 比较这些候选。
先做 Mandatory 技术适配，再核对生命周期与精确配置，最后用当前价格证据给出区间；弱价格只作背景。
```

### 更新已有预算

```text
$it-infrastructure-equipment-selection
按 budget-revision 更新这个 BOM。先保留每行旧单价，恢复项目内已有报价，所有降价先过技术门禁；
配置型企业设备必须运行严格价格证据 guard，并逐行报告 old/new/evidence/decision。
```

确定性 guard：

```bash
python3 scripts/normalize_price_evidence.py evidence.json \
  --summary \
  --strict-contract \
  --existing-budget 92000 \
  --product-class configurable-enterprise
```

只有 `budget_revision.decision = revise-to-current-anchor` 才允许相应下调。完整规则见 [`references/budget-revision.md`](references/budget-revision.md)。

### 服务器询价

```text
$it-infrastructure-equipment-selection
冻结服务器技术与商业 RFQ 基线，校验每份报价的配置、税费、License、维保、实施、有效期和可订购性，
再按供应商独立性给出询价区间和控制上限。
```

```bash
python3 scripts/compare_server_quotes.py assets/server-rfq-example.json --pretty
```

### 厂商比较与 TCO

```text
$it-infrastructure-equipment-selection
按 vendor-compare + tco-analysis 比较候选。FAIL 淘汰，CONDITIONAL 不得排在 PASS 前；
对合格方案分别展示 CAPEX、3 年和 5 年 TCO。
```

```bash
python3 scripts/calculate_tco.py assets/tco-example.json --format markdown
```

### 招标、合规与拓扑

```text
$it-infrastructure-equipment-selection
按 tender-spec + compliance-check + topology-generation 输出厂商中立的技术参数、证据/验收要求和逻辑拓扑。
不要发明 VLAN ID、IP、端口、冗余链路或安全区域。
```

### 真实项目复盘

```text
$it-infrastructure-equipment-selection
按 real-project retrospective 整理这些设计、报价和运行材料。先标证据阶段并做范围归一；
没有成交、结算或运行记录时，不声称验证了最终准确率。发布前匿名化。
```

## Schema v1 / v2 治理

所有契约采用 Draft 2020-12。权威版本状态在 [`schemas/catalog.json`](schemas/catalog.json)，使用 `python3 scripts/infra_cli.py list` 可发现命名契约。

- 未版本化路径及 `schema_version: 1` 是冻结的 v1 契约，继续兼容；
- 破坏性增强放在 `schemas/v2/`，使用独立 `$id`；
- 未知或未来版本明确拒绝，不猜测兼容性；
- Schema 是结构预检，不证明技术适配、证据真实性或当前可订购性；
- 迁移可以搬移已知字段，但不能自动补造 `PASS`、`Verified`、零、供应商身份、决策作用域或当前日期。

当前 v2 重点：

- Price evidence：一个显式 `decision_scope_id`，每条记录明确技术门禁，声明证据等级与系统派生等级分离；
- Project retrospective：运行测量结构化，并在预算预测与成交/结算比较前要求技术和商业范围归一。

非破坏迁移报告：

```bash
python3 scripts/migrate_schema.py price-evidence price-evidence-v1.json \
  --decision-scope-id project:bom-line-server-01
```

默认只输出报告且不修改源文件；`--output` 只能写入尚不存在的新路径。详见 [`references/schema-governance.md`](references/schema-governance.md)。

## 私有扩展边界

企业私有模板、产品事实和报价采用：

```text
公共 Skill（规则、Schema、确定性门禁）
                  ↑ 显式的最小化结构化输入
私有适配器（校验、脱敏、决策字段剥离）
                  ↑
受控数据源（原始报价、联系人、客户/合同数据）
```

边界规则：

- 公共 Skill checkout 保持干净、可 `git pull --ff-only`；
- 私有模板和适配器使用独立私有仓库；原始报价和联系人进入有权限控制的数据源，不进入代码仓库；
- 只从当前任务明确给出的路径加载扩展，不扫描 Home、环境变量或邻接目录；
- 私有模板 ID 使用命名空间并拒绝冲突，不能弱化 Mandatory、证据或 TBD 规则；
- 供应商文件中的 `technical_fit_status`、`eligible_for_pricing`、`comparable` 和证据等级必须剥离后独立派生；
- 临时导出限制权限并在任务结束后清理，公开日志不回显敏感内容。

Manifest 示例和契约：

```bash
python3 scripts/infra_cli.py validate private-extension-manifest-v1 \
  assets/private-extension-manifest-example.json
```

详见 [`references/private-extensions.md`](references/private-extensions.md)。公共项目提供边界和契约，不提供自动私有数据加载器。

## BOM 与商业口径

最终 BOM 必须检查隐藏配件、License、维保、实施、税费、运输、备份和交付范围。中文 CSV 使用 UTF-8 with BOM。

如果任一重要行的税、维保、License、实施或交付仍未知，不得把整个项目描述为“含税到货”“完整范围”或“All licenses included”。列出受影响行并使用 `TBD` / `Needs confirmation`。详见 [`references/bom-checklist.md`](references/bom-checklist.md)。

## 安装、更新与仓库结构

Git Clone 安装适合持续更新：

```bash
git -C ~/.agents/skills/it-infrastructure-equipment-selection pull --ff-only
```

安装器更新：

```bash
python3 scripts/install_skill.py --target codex --scope user --update
```

更新器拒绝 dirty Git checkout，`--force` 不删除 `.git`，copy 更新只同步受管运行文件。

```text
SKILL.md                         # invariant + workflow router
references/                      # 按任务渐进加载的工程与采购方法
scripts/                         # 确定性计算、校验、生成、迁移和安装工具
assets/tool-catalog.json         # CLI 工具/契约白名单
assets/                          # 模板与结构化示例
schemas/                         # 冻结 v1 契约
schemas/v2/                      # 破坏性增强契约
examples/                        # 方法示例与匿名复盘；不是默认架构
agents/openai.yaml               # 可选 OpenAI/Codex metadata
```

## 测试与社区

运行完整测试与发布校验：

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 scripts/validate_release.py
```

回归范围包括 Router/不可违反原则、场景模板、Mandatory 排序、全品类价格门禁、供应商独立性与顺序稳定性、决策作用域、服务器 RFQ、HCI N+1、UPS、TCO、Schema v1/v2、非破坏迁移、私有边界、安装器和跨平台兼容性。

项目中的真实复盘示例均以文件自身的 `evidence_stage` 和 Schema 为准；不要根据示例数量或设计预算变化推断成交、结算或运行准确率。

- 使用与设计问题：[GitHub Discussions](https://github.com/wanghao-io/it-infrastructure-equipment-selection-skill/discussions)
- 缺陷、功能和文档：[GitHub Issues](https://github.com/wanghao-io/it-infrastructure-equipment-selection-skill/issues)
- 贡献指南：[CONTRIBUTING.md](CONTRIBUTING.md)
- 支持与安全：[SUPPORT.md](SUPPORT.md) · [SECURITY.md](SECURITY.md)
- 治理与维护者：[GOVERNANCE.md](GOVERNANCE.md) · [MAINTAINERS.md](MAINTAINERS.md)
- 独立模拟前向验证与 v1.5 门禁方案：[docs/forward-validation-v1.4.2.md](docs/forward-validation-v1.4.2.md)
- 发布历史：[CHANGELOG.md](CHANGELOG.md) · [RELEASE_NOTES.md](RELEASE_NOTES.md)

项目当前公开披露的人类 bus factor 为 **1**。文档、测试和发布手册降低知识集中风险，但不会把自动化等同于第二位真实维护者。

## English

This repository provides two complementary entry points:

1. **Agent workflow** — route from requirements to the minimum justified architecture, sizing, Mandatory technical gates, current evidence and project artifacts.
2. **Deterministic CLI/contracts** — discover and run whitelisted calculators, validate v1/v2 JSON contracts and produce conservative migration reports without pretending that calculation replaces engineering research.

Core guarantees:

- scenario templates guide discovery and never force HCI, HA, core switching, firewalls, Xinchuang or GPU;
- PASS/CONDITIONAL/FAIL gates precede scoring and TCO;
- every product class must pass technical fit before price anchoring;
- current-price work uses live research when available;
- exact configurations, supplier independence, decision scope and commercial completeness control price evidence;
- existing-budget reductions use the deterministic revision guard;
- OT safety logic remains authoritative in the PLC/equipment layer;
- v1 contracts remain supported, breaking changes use versioned v2 paths, and migrations never invent decision facts;
- private extensions are explicit and separate from the public checkout and raw confidential data.

Start with:

```bash
python3 scripts/infra_cli.py list
python3 scripts/infra_cli.py validate price-evidence-v2 assets/price-evidence-v2-example.json
```

See [`SKILL.md`](SKILL.md) for routing, [`references/schema-governance.md`](references/schema-governance.md) for contract compatibility, [`references/private-extensions.md`](references/private-extensions.md) for private-data boundaries and [`examples/full-feature-input.md`](examples/full-feature-input.md) for a full project prompt.

MIT License.
