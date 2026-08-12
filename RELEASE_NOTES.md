# IT Infrastructure Equipment Selection Skill v1.2.1

## 预算与询价门禁热修

v1.2.1 修复 v1.2.0 发布后复核发现的所有问题：所有品类的预算下调均强制要求明确技术适配；`TBD`/非法费用不再按零处理；同一供应商的多个报价号不再伪装为独立证据；服务器报价增加完整 RFQ 基线、供应商身份、报价新鲜度和风险准备金校验；Mandatory 未知值、HCI 节点整数以及真实工作流回归测试也已修正。

## 可执行询价、容量与发布门禁

v1.2.0 把“建议”落成确定性工具：服务器报价必须同时通过技术配置、商业范围、有效期、币种和独立证据检查；HCI N+1 会验证故障后的 CPU、内存、存储、IOPS、网络和故障域。安装器、BOM、TCO、拓扑、评分和发布链路也加入了严格回归门禁。

服务器询价示例：

```bash
python3 scripts/compare_server_quotes.py assets/server-rfq-example.json --pretty
```

HCI N+1 示例：

```bash
python3 scripts/calculate_hci_failover.py assets/hci-failover-example.json --pretty
```

## 预算修订保护 + 规格先于价格

v1.1.2 是一次针对实际项目回归问题的修复版本，重点解决两个风险：

1. **已有预算被弱价格证据错误下调**；
2. **为了匹配便宜商品，反过来降低项目技术规格**。

核心原则现在明确为：

> **需求 → 技术适配 → 证据质量 → 价格。价格不能反向定义需求。**

## 已有预算下调保护

当用户要求更新现有 CSV / XLSX / BOM 价格时，Skill 会先保留原单价作为 revision baseline。

对于服务器、存储、HCI、配置型防火墙等 `configurable-enterprise` 设备：

- PConline/ZOL 等同系列部分配置价、起售价、泛型号报价、历史成交、组件估算和工程估算不能单独作为下调依据；
- 一个 Tier-3 高度匹配报价不足以单独下调；
- 至少需要一个 Tier-1/2 当前精确报价，或两个独立 Tier-3 高度匹配当前报价；
- 弱证据不足时，保留原预算并标记 `Needs confirmation`；
- 当前精确报价高于旧预算时，允许按强证据上调，不会因为“保护旧预算”而掩盖低估风险。

确定性检查：

```bash
python3 scripts/normalize_price_evidence.py <evidence.json> \
  --summary \
  --existing-budget <old-unit-price> \
  --product-class configurable-enterprise
```

只有：

```text
budget_revision.decision = revise-to-current-anchor
```

才允许执行相应下调。

项目内保存的人工询价、用户提供的当前报价，只要能记录渠道、日期、配置匹配和商业范围，即使没有公开 URL，也可以成为强价格证据。

## 规格先于价格

v1.1.2 新增通用 technical-fit gate：

> **便宜 SKU 必须先证明满足原需求，才有资格进入价格比较。**

这条规则同样适用于固定 SKU。

例如：

- 大屏需要浏览器/BI 能力时，无系统无网络的大屏必须把 OPS 或等效播放设备计入完整范围后才能比较；
- UPS 不能只看 `VA` 标称值，必须同时检查真实输出 W、VA、目标续航、自动关机接口/软件兼容性。

## UPS 候选门禁

`scripts/calculate_ups.py` 现在可以对具体 UPS SKU 做技术适配检查：

```bash
python3 scripts/calculate_ups.py 800 \
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

以下情况会返回 `not-eligible-for-pricing`：

- 实际输出 W 不足；
- VA 不足；
- 目标负载下续航曲线未确认；
- 项目需要自动关机但接口/软件兼容性未确认。

因此类似 `1500VA/900W` 的产品不会再仅因为“1500VA 看起来够大”就被当成等价替代。

## 安装/更新修复

同时正式包含 v1.1.1 发布后的安装器热修：

- Git Clone 安装支持安全更新；
- `--update` 支持 Git / copy / symlink；
- `--force` 不会删除 `.git`；
- Git 工作区存在本地修改时拒绝自动覆盖；
- copy 更新只同步 Skill 管理的运行文件，并保留额外本地文件。

Git Clone 用户可直接：

```bash
git -C ~/.agents/skills/it-infrastructure-equipment-selection pull --ff-only
```

## 预算汇总措辞

如果服务器、SCADA 或其他重要行仍存在税务、维保、实施、运输范围未确认，Skill 不再把项目总预算笼统写成“含税到货”或“完整范围已确认”。

更推荐：

```text
按当前可获得证据估算；已标识项目的税务、维保、实施和/或交付范围仍需确认。
```

## 回归测试

v1.1.2 新增/强化测试覆盖：

- 已有服务器预算不能被 Partial-config / ZOL / PConline / 工程估算错误下调；
- 当前精确人工报价可以覆盖弱公开行情；
- 一个 Tier-3 报价不足以单独压低服务器预算；
- `1500VA/900W` UPS 在真实输出 W 不足时不得进入价格比较；
- UPS 只有容量够但续航未验证时仍不得进入价格比较；
- 满足 W / VA / 续航 / 关机接口的 UPS 才返回 `eligible-for-pricing`；
- 安装器不会破坏 Git 元数据；
- 跨平台 Agent Skills 回归测试继续保留。

---

# English

## Budget Revision Guardrails & Specification-First Pricing

v1.1.2 fixes two procurement risks found in real project regression testing:

- weak or partial price signals incorrectly lowering an existing enterprise budget;
- cheaper products silently redefining the technical requirement.

The enforced order is now:

> **Requirements → technical fit → evidence quality → price.**

For configurable enterprise equipment, weak context such as model-family listings, aggregators, historical transactions or engineering estimates cannot by themselves justify lowering an existing budget.

UPS candidates now have a deterministic technical-fit gate. A candidate may influence a lower budget only after real-output W, VA, runtime and required graceful-shutdown integration are validated. The helper returns either `eligible-for-pricing` or `not-eligible-for-pricing`.

This release also includes the safe installation/update fixes added after v1.1.1.

## Upgrade

Git-based installations:

```bash
git -C ~/.agents/skills/it-infrastructure-equipment-selection pull --ff-only
```

No data migration is required.

## License

MIT License
