# IT Infrastructure Equipment Selection Skill v1.4.2

## 易用性收敛，不削弱工程门禁

v1.4.2 将 `SKILL.md` 从接近上下文上限的工作流正文收敛为 196 行 Router。需求优先、未知值显式、非默认架构、Mandatory 先于评分、技术先于价格、已有预算下调保护、OT 本地安全权威和私有数据边界等十二项规则具有稳定 invariant ID，并由 Router 回归测试保护。

预算修订和 price-evidence v2 的完整规则转入按需加载的 reference。README 同时改为当前能力、Agent/CLI 两条使用路径和可复制任务配方，不再维护容易过期的版本流水账。计算公式、Schema v1 兼容性、采购门禁和输出能力均未删减。

## 更安全、更容易理解的确定性 CLI

- 从任意工作目录传入的 TCO/HCI 相对路径现在按调用者目录解析；
- TCO/HCI 在计算前自动通过命名 Schema 预检，输入失败时不会产生计算结果；
- 普通用户错误不再输出 Python traceback，维护者仍可使用 `--debug`；
- `list --all` 对全部脚本标明 public、guarded、lifecycle、deferred 或 internal，并解释适用范围及为何不能进入通用 `run`；
- 六个原公开计算器的参数、公式和输出保持兼容。

## Release 不再早于完整 CI

Tag Release 现在复用与 `main` 相同的 Linux/macOS/Windows × Python 3.10/3.12 完整验证。只有 Schema、单元/场景测试、确定性 smoke、clean-install package smoke 和临时标准目录中的 `gh skill publish --dry-run` 全部通过后，才会构建并发布归档。

Tag 必须在 metadata gate 和最终 publish gate 都等于当前 `main` HEAD；只有最终发布 job 拥有写权限，并拒绝覆盖既有 Release。GitHub Release 正文从 `CHANGELOG.md` 精确提取当前版本，历史仍保留在累计 Changelog 中。

## 独立模拟前向验证与 v1.5 决策

四个不共享审计结论的 fresh-agent 场景分别覆盖：

1. 小型办公室是否应默认采用三节点 HCI、双核心和双防火墙；
2. SCADA Historian、UPS 和手机远程启动的 OT 安全边界；
3. 使用起售价和历史成交价挑战既有服务器预算；
4. HCI N+1 容量失败与不完整 TCO 的决策优先级。

四个场景均未出现阻断性违规。详细方法、证据边界和 v1.5 门禁见 `docs/forward-validation-v1.4.2.md`。这只是独立模拟工作流验证，不代表真实外部用户采用，也不证明当前价格、成交、结算或生产运行准确率。

v1.5 暂定只扩展已有 `public-gated` 能力的安全专用入口、决策摘要层和可重复 eval；产品库、价格爬虫、自动私有数据发现、宽泛 HTTP API 和缺少实际需求的新计算器继续延后。

## 验证

- 137 项本地回归通过；
- Router、CLI、Schema、询价、预算修订、HCI、TCO、安装器、社区和 Release workflow 均有机器检查；
- 发布归档将在 Tag workflow 中再次执行全矩阵和干净安装验证。
