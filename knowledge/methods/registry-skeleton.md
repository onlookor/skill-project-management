## 方法注册表骨架

**权威关系**：方法条目是知识层内容，不是成文法。它们受 `CONSTITUTION.md` 第 2、3 条约束（来源锚定），但不进入 `GRAMMAR.md`。方法条目的消费者是 `AGENTS.md` 第 6 条工作流的第 4 步（知识查询）。

### 条目格式

```
method = {
  method_id:        // 唯一标识，格式 M-{类别}-{序号}
  method_name:      // 方法名
  category:         // estimation | decomposition | risk | earned_value | procurement | ...
  when_to_use:      // 适用场景（条件式）
  steps:            // 步骤列表（每步一句话）
  inputs:           // 所需输入
  outputs:          // 产出
  scale_applicability: // small | medium | large（适用项目规模）
  grounding_ref:    // 指向 SOURCE_LEDGER.md 的条目
  provenance_note:  // 形式化边界
}
```

### 首批方法条目

#### M-EST-01 三点估算（PERT）

| 字段 | 内容 |
|---|---|
| `method_id` | `M-EST-01` |
| `method_name` | 三点估算（PERT：Program Evaluation and Review Technique） |
| `category` | `estimation` |
| `when_to_use` | 任务持续时间或成本存在不确定性，且可获得乐观/最可能/悲观三个估计值时 |
| `steps` | 1. 对每个任务收集乐观值 O、最可能值 M、悲观值 P；2. 计算期望值 E = (O + 4M + P) / 6；3. 计算标准差 σ = (P − O) / 6；4. 汇总期望值与方差；5. 记录估计依据与假设 |
| `inputs` | 任务清单、三个估计值、估计依据（历史数据/专家判断） |
| `outputs` | 期望值、标准差、置信区间 |
| `scale_applicability` | `small` / `medium` / `large` |
| `grounding_ref` | `PMBOK8-2025`（仅原则层交叉验证；具体公式为通用运筹学方法，本技能不宣称其为 PMBOK 原文） |
| `provenance_note` | PERT 公式为通用运筹学方法；本条目将其作为估算方法登记，不宣称 PMBOK 原文包含该公式。`grounding_ref` 指向 PMBOK 仅用于原则层一致性检查。**待补充更精确的来源锚定**（登记于 `TODO.md`）。 |

#### M-DEC-01 WBS 工作分解

| 字段 | 内容 |
|---|---|
| `method_id` | `M-DEC-01` |
| `method_name` | WBS（Work Breakdown Structure，工作分解结构） |
| `category` | `decomposition` |
| `when_to_use` | 需要把项目范围分解为可管理的工作包时 |
| `steps` | 1. 以 Deliverable 为导向确定第一层分解；2. 逐层分解至工作包（8–80 小时规则为常见准则，非强制）；3. 为每个工作包分配唯一标识；4. 检查 100% 规则（子层之和覆盖父层全部范围）；5. 登记每个工作包的 Accountable 与 Responsible |
| `inputs` | 项目范围陈述、Deliverable 清单 |
| `outputs` | WBS 层级结构、工作包清单 |
| `scale_applicability` | `small` / `medium` / `large` |
| `grounding_ref` | `PMBOK8-2025`（仅原则层交叉验证） |
| `provenance_note` | WBS 为通用项目管理方法；本条目登记其步骤，不宣称 PMBOK 原文的逐字表述。**待补充更精确的来源锚定**（登记于 `TODO.md`）。 |

#### M-RISK-01 风险登记与评估

| 字段 | 内容 |
|---|---|
| `method_id` | `M-RISK-01` |
| `method_name` | 风险登记与评估（Risk Register and Assessment） |
| `category` | `risk` |
| `when_to_use` | 项目启动时及每个阶段关口 |
| `steps` | 1. 识别风险（来源：项目事实、历史项目、专家判断）；2. 评估概率与影响（定性：高/中/低；定量：若数据可得）；3. 计算风险值 = 概率 × 影响；4. 为每个风险指定应对策略（规避/转移/减轻/接受）；5. 指定风险 owner（Responsible）；6. 登记触发条件与监测指标 |
| `inputs` | 项目背景、历史数据、专家判断 |
| `outputs` | 风险登记册、应对计划、监测指标 |
| `scale_applicability` | `small` / `medium` / `large` |
| `grounding_ref` | `PMBOK8-2025`（仅原则层交叉验证） |
| `provenance_note` | 风险登记为通用项目管理方法；本条目登记其步骤。**待补充更精确的来源锚定**（登记于 `TODO.md`）。 |

#### M-EV-01 挣值分析

| 字段 | 内容 |
|---|---|
| `method_id` | `M-EV-01` |
| `method_name` | 挣值分析（EVA：Earned Value Analysis） |
| `category` | `earned_value` |
| `when_to_use` | 项目执行阶段需要量化进度与成本偏差时 |
| `steps` | 1. 计算 PV（Planned Value，计划价值）；2. 计算 EV（Earned Value，挣值）；3. 计算 AC（Actual Cost，实际成本）；4. 计算 SV = EV − PV（进度偏差）；5. 计算 CV = EV − AC（成本偏差）；6. 计算 SPI = EV / PV（进度绩效指数）；7. 计算 CPI = EV / AC（成本绩效指数）；8. 记录数据来源与计算时点 |
| `inputs` | 工作包计划价值、完成百分比、实际成本 |
| `outputs` | SV、CV、SPI、CPI、预测（EAC、ETC） |
| `scale_applicability` | `medium` / `large`（小项目数据粒度可能不足） |
| `grounding_ref` | `PMBOK8-2025`（仅原则层交叉验证） |
| `provenance_note` | 挣值分析为通用项目管理方法；本条目登记其公式与步骤。**待补充更精确的来源锚定**（登记于 `TODO.md`）。 |

#### M-PROC-01 采购流程

| 字段 | 内容 |
|---|---|
| `method_id` | `M-PROC-01` |
| `method_name` | 采购流程（Procurement Process） |
| `category` | `procurement` |
| `when_to_use` | 项目需要外部采购商品或服务时 |
| `steps` | 1. 制定采购计划（自制或外购分析）；2. 编制采购文档（SOW、RFQ/RFP）；3. 获取卖方响应；4. 选择卖方（评估标准与权重）；5. 签订合同（关联 G-F3 的 Contract 节点）；6. 管理合同履行（验收、变更、支付）；7. 合同收尾 |
| `inputs` | 项目范围、预算、采购需求 |
| `outputs` | 采购计划、合同、验收记录 |
| `scale_applicability` | `small` / `medium` / `large` |
| `grounding_ref` | `ISO21502-2020`（采购主题组的领域无关表述） |
| `provenance_note` | ISO 21502:2020 将采购作为项目管理主题之一；本条目登记其步骤，具体步骤的细化程度为技能自身贡献。**待核验 ISO 21502:2020 采购主题组的具体过程要素**（登记于 `TODO.md`）。 |

### 待填充类别

| 类别 | 待填充方法 | 登记于 |
|---|---|---|
| `estimation` | 类比估算、参数估算、自下而上估算 | `TODO.md` |
| `decomposition` | 按阶段分解、按地理分解 | `TODO.md` |
| `risk` | 蒙特卡洛模拟、决策树 | `TODO.md` |
| `earned_value` | 燃尽图、累积流量图 | `TODO.md` |
| `procurement` | 合同类型选择（固定价/成本补偿/工料合同） | `TODO.md` |
| `stakeholder` | 干系人分析（权力-利益矩阵） | `TODO.md` |
| `communication` | 沟通计划编制 | `TODO.md` |
| `quality` | 质量审计、因果图 | `TODO.md` |

### 检索接口

方法条目的检索按 `category`、`method_name`、`scale_applicability` 三个键进行。检索结果为条目全文（结构化字段）。检索不依赖嵌入相似度，不依赖生成模型的参数记忆。
