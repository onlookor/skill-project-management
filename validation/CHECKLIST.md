## 检查清单

**生成依据**：`spec/COMPILATION_META.md`（编译元框架，P1–P6 与准入条件）+ `spec/methods/deterministic-checker.md`（CM-DET-CHECKER 方法的 check_id 注册表与翻译规范）。
**性质**：本清单是检查项规格的人类可读投影，**不是检查执行器**。执行由确定性校验器按 `spec/methods/deterministic-checker.md` 的注册表执行。清单与注册表不一致时以注册表为准，重建本清单。
**source_commit**：`0669a4b031f02dc6045c6b2696c5c9f3eb427a4b`（生成基线；源文件为 `GRAMMAR.md`、`SOURCE_LEDGER.md`、`spec/methods/deterministic-checker.md` 与 `knowledge/` 谓词定义，见 ADR-0004）

### 规则组 A

| check_id | 规则 | severity | 规则状态 | 输入摘要 | 判定摘要 |
|---|---|---|---|---|---|
| `PROJECT_MINIMAL_EXISTENCE` | G-A1 | `block` | `active` | Project / Actor / Outcome / Commitment / Constraint 节点 | 四类节点均存在且 Commitment 的 by→Actor、to→Outcome |
| `CONSTRAINT_ANCHOR_REQUIRED` | G-A2 | `block` | `active` | 管理活动/产物节点、Constraint 节点 | 每个管理活动/产物有 constrained_by 边指向已登记 Constraint |

### 规则组 B

> 规则组 B 整体状态 `active`（ADR-0008）；以下检查项 `severity` 保持 `advisory`，升级为 `block` 需样例契约证据（T-118）。

| check_id | 规则 | severity（实际） | 规则状态 | 输入摘要 | 判定摘要 |
|---|---|---|---|---|---|
| `DUAL_DIMENSION_ANNOTATION` | G-B1 | `advisory` | `active` | 管理项节点 | 每个管理项携带 process_group 与 subject_group 两标签 |
| `DIMENSION_VALUE_CLOSED` | G-B2 | `advisory` | `active` | 管理项的标签值 | 标签值 ∈ 枚举 ∪ 契约声明的 subject_group_extension |

### 规则组 C

| check_id | 规则 | severity | 规则状态 | 输入摘要 | 判定摘要 |
|---|---|---|---|---|---|
| `DELIVERABLE_ASSERTION_LINK` | G-C1 | `block` | `active` | Deliverable 节点、Assertion 节点 | 每个 Deliverable 有 asserted_by 边指向 Assertion |
| `ASSERTION_MUTUAL_EXCLUSION` | G-C2 | `warn` | `active` | 同一 Deliverable 的多条 Assertion | 不存在两条 active 断言对同一 Subject 同一属性不相容 |

### 规则组 D

| check_id | 规则 | severity | 规则状态 | 输入摘要 | 判定摘要 |
|---|---|---|---|---|---|
| `CHANGE_CONSTRAINT_LINK` | G-D1 | `block` | `active` | 变更提议、Constraint 节点 | 每个变更提议有边指向 Constraint，关系类型 ∈ {mitigates, exacerbates, trades_off} |
| `ALL_IMPROVEMENT_ASSUMPTION` | G-D2 | `warn` | `active` | 变更提议的关系类型集合 | 全为 mitigates 时标记为 assumption 并附验证条件 |

### 规则组 E

| check_id | 规则 | severity | 规则状态 | 输入摘要 | 判定摘要 |
|---|---|---|---|---|---|
| `ROLE_MINIMAL_COMPLETENESS` | G-E1 | `block` | `active` | Commitment、Accountable/Responsible 关系 | 唯一 accountable_by 指向 HumanActor/LegalEntity，至少一个 responsible_by；重合时有 role_merge_declaration |
| `AI_AUTONOMY_DELEGATION_AUDITABLE` | G-E2 | `warn` | `active` | AIActor 自治权、delegated_from 链 | 链终至 Accountable，链上有 Assertion 声明范围/边界/撤销条件 |

### 规则组 F

> 规则组 F 整体状态 `assumption`；以下检查项仅输出 `advisory`，输出附验证条件。

| check_id | 规则 | severity（实际） | 规则状态 | 输入摘要 | 判定摘要 |
|---|---|---|---|---|---|
| `PROJECT_CHARTER_EXISTENCE` | G-F1 | `advisory` | `assumption` | Project、ProjectCharter 节点 | 进入执行阶段的 Project 有 ProjectCharter 且关联四要素 |
| `CLOSURE_ACCEPTANCE_LINK` | G-F2 | `advisory` | `assumption` | 收尾阶段 Deliverable、Assertion | 每个 Deliverable 有验收/移交断言且关联 Accountable 确认 |
| `PROCUREMENT_CONTRACT_ANCHOR` | G-F3 | `advisory` | `assumption` | 外部采购 Commitment、Contract 节点 | 每个外部采购承诺有 Contract 节点且声明四要素 |
| `SCHEDULE_EVIDENCE_LINK` | G-F4 | `advisory` | `assumption` | 带 deadline/milestone 的 Commitment、Assertion | 每个时间承诺关联至少一条依据断言 |

### 规则组 G

> 规则组 G 整体状态 `assumption`；以下检查项仅输出 `advisory`，输出附验证条件。

| check_id | 规则 | severity（实际） | 规则状态 | 输入摘要 | 判定摘要 |
|---|---|---|---|---|---|
| `TAILORING_RECORD_EXISTENCE` | G-G1 | `advisory` | `assumption` | 裁剪动作、TailoringRecord | 每次裁剪有 TailoringRecord 且声明四要素 |
| `TAILORING_NON_TRIMMABLE_SET` | G-G2 | `advisory` | `assumption` | TailoringRecord 的目标规则 | 目标规则 ∉ {G-A1, G-A2, G-C1, G-D1, G-E1} |
| `TAILORING_REASSESSMENT_CONDITION` | G-G3 | `advisory` | `assumption` | TailoringRecord | 每条记录关联重新评估条件断言或显式声明永久并附理由 |

### 执行纪律

1. 校验器按本表逐项执行，输出 `pass` / `fail` / `cannot_evaluate`（`spec/methods/deterministic-checker.md` 第 4.2 节）。
2. `cannot_evaluate` 不等于 `pass`；缺失输入必须报告。
3. 规则状态为 `assumption`（或将来出现的 `pending_reanchor`）的检查项，校验器输出携带 `rule_status`；宿主据此仅记录而不阻断。
4. 生成模型只消费校验器的输出，不消费本清单本身（`CONSTITUTION.md` 第 1 条）。
5. 本清单由 `spec/methods/deterministic-checker.md` 附录 A 的注册表机械生成；不一致时重建。
