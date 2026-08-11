# IT Infrastructure Equipment Selection Skill

[中文说明](#中文说明) | [English](#english)

---

# 中文说明

这是一个面向 **Codex / AI Agent** 的 IT 基础设施解决方案工程师 Skill。

目标是帮助 IT 架构师、售前工程师和运维工程师完成企业级基础设施项目规划，包括：

- 服务器选型
- 超融合架构设计
- 存储容量规划
- 网络设备选型
- 防火墙性能评估
- UPS 容量计算
- 工作站与终端规划
- 工业 IT/OT 架构设计
- 国产化/信创适配分析
- 招标参数核验
- BOM 编制
- 项目预算估算

核心原则：

> 先理解业务需求，再进行容量计算，最后选择具体产品。

避免简单根据商品型号倒推技术方案。

---

## 核心能力

- Server sizing
- Hyper-Converged Infrastructure sizing
- Storage planning
- Network architecture design
- Firewall sizing
- UPS calculation
- Industrial IT/OT infrastructure planning
- 国产化平台适配
- BOM generation
- Compliance checking
- Procurement risk analysis

---

## 工作流程

```
需求分析
    ↓
业务负载评估
    ↓
容量计算
    ↓
技术规格定义
    ↓
产品验证
    ↓
价格调查
    ↓
BOM输出
    ↓
风险分析
```

---

## 项目结构

```
.
├── SKILL.md
├── references/
├── scripts/
├── assets/
├── tests/
└── agents/
```

---

## 安装

复制到 Codex Skill 目录：

```bash
~/.agents/skills/it-infrastructure-equipment-selection-skill
```

然后调用：

```
$it-infrastructure-equipment-selection
```

---

# English

AI Agent skill for IT infrastructure solution architects.

This skill helps engineers design, validate and document enterprise infrastructure projects including:

- Servers
- Hyper-converged infrastructure
- Storage
- Network equipment
- Firewalls
- UPS
- Workstations
- Industrial IT/OT infrastructure

## Design Principle

> Requirements first. Sizing second. Products last.

The skill avoids selecting products first and reverse-engineering requirements.

## Workflow

```
Requirements
    ↓
Capacity sizing
    ↓
Technical specification
    ↓
Product validation
    ↓
Pricing research
    ↓
BOM generation
```

## License

MIT License
