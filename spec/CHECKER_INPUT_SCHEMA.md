# 确定性校验器输入 schema

**性质**：执行层规范文件（`STATE.md` 的 `spec/` 默认 `active`）。它固定 `spec/methods/deterministic-checker.md` 附录 A 各 `check_id` 的**谓词快照输入字段**。T-011 的 34 个样例是该 schema 的首批实例；**此后新增或修改的样例必须遵循本文件**。

**边界**：只定义输入字段与判定前提，不改变附录 A 的判定列，不新增谓词，不改变任何 `severity` / `rule_status`。schema 与判定列冲突时以附录 A 为准，并登记缺口（`GAP_LEDGER.md`，`AGENTS.md` 3.6）。

**基线**：本文件不写版本号（ADR-0003）。每次修改记 `CHANGELOG.md`，并重跑 `validation/checker-prototype/checker.py`；34 个样例必须仍为 34/34。

## 1. 通用约定

1. 一个输入是一份 YAML 谓词快照，顶层为映射。顶层键即该 `check_id` 的**量化域**（例如 `deliverables` 表示“每个 `Deliverable`”）。
2. **缺键即不可判定**：判定所需的顶层键缺失，或键的值为 `null`，原型输出 `cannot_evaluate` / `missing_input`，不得当作 `pass`。
3. **空列表是事实**：键存在且值为 `[]`，表示“量化域为空”或“引用集为空”，按判定列判 `fail` 或 `pass`，不得当作缺失输入。
4. **已按适用范围筛选**：输入只含该规则的适用对象。已筛选的范围包括：G-E1 的决策类 `Commitment`、G-A2 的管理活动/产物、G-F1 的执行阶段 `Project`、G-F2 的收尾阶段 `Deliverable`、G-F3 的外部采购承诺。检查本身不再做类型筛选。
5. **标识符与引用**：`id` 为字符串，同一输入内唯一。引用字段（`by`、`to`、`constrained_by`、`asserted_by`、`accountable_by`、`responsible_by`、`delegated_from`、`contract`、`record` 等）必须指向同快照中已出现的 `id`；指向不存在者按判定列判 `fail`，原因码见第 3 节。
6. **结论与原因**：`verdict ∈ {pass, fail, cannot_evaluate}`；`reason` 为稳定原因码，`pass` 时为 `null`。原因码只用于样例断言，不是新的规范词汇。
7. **severity / rule_status**：由附录 A 与 `validation/CHECKLIST.md` 决定，不由输入携带；`assumption` 组按 P6 输出 `advisory`。

## 2. 共享字段

| 对象 | 键 | 类型 | 说明 |
|---|---|---|---|
| `project` / `projects[]` | `id`, `stage` | 字符串 | `stage` 至少识别 `executing` |
| `actors[]` | `id`, `type`, `accountable`, `delegated_from` | 字符串 / 布尔 | `type ∈ {HumanActor, LegalEntity, AIActor}`；`accountable: true` 表示委托链终点 |
| `outcomes[]` | `id` | 字符串 | |
| `commitments[]` | `id`, `by`, `to`, `constrained_by`, `accountable_by`, `responsible_by`, `role_merge_declaration`, `procurement`, `contract`, `deadline`, `milestone`, `evidence_assertions` | 见各 `check_id` | `responsible_by` 为字符串列表 |
| `constraints[]` | `id`, `constrains` | 字符串 | |
| `deliverables[]` | `id`, `constrained_by`, `asserted_by`, `assertions` | 列表 / 对象 | 两种断言表示：C1 用 `asserted_by` 引用，F2 内嵌 `assertions` |
| `assertions[]` | `id`, `about`, `deliverable`, `subject`, `property`, `value`, `state`, `covers`, `basis`, `source`, `statement`, `accountable_confirmation` | 见各 `check_id` | `state ∈ {active, ...}`；`covers` 为字符串列表 |
| `changes[]` | `id`, `constraint`, `relation`, `relations`, `assumption`, `verification_condition` | 见各 `check_id` | D1 用单数 `relation`；D2 用复数 `relations` |
| `management_items[]` | `id`, `process_group`, `subject_group` | 字符串 | |
| `autonomy_grants[]` | `id`, `actor`, `delegated_from`, `assertions` | 字符串 / 列表 | |
| `charters[]` | `id`, `project`, `outcomes`, `constraints`, `accountable`, `authorizing_assertion` | 见 F1 | |
| `contracts[]` | `id`, `deliverable_form`, `acceptance_criteria`, `constrained_by`, `accountable_signature` | 见 F3 | |
| `tailoring_actions[]` | `id`, `record` | 字符串 | `record` 指向 `tailoring_records[].id` |
| `tailoring_records[]` | `id`, `trimmed_rule`, `rationale`, `scope`, `approver`, `reassessment_condition`, `permanent`, `reason` | 见 G 组 | |

## 3. 各 check_id 的输入域

| check_id | 必需顶层键 | 判定所需字段 | 失败原因码 |
|---|---|---|---|
| `PROJECT_MINIMAL_EXISTENCE` | `project`, `actors`, `outcomes`, `commitments`, `constraints` | `commitments[].by/to` | `missing_actor` / `missing_outcome` / `missing_commitment` / `missing_constraint` / `broken_commitment_endpoint` |
| `CONSTRAINT_ANCHOR_REQUIRED` | `commitments`, `deliverables`, `constraints` | 每项的 `constrained_by` | `unanchored_management_item` |
| `DUAL_DIMENSION_ANNOTATION` | `management_items` | `process_group`, `subject_group` | `missing_dimension` |
| `DIMENSION_VALUE_CLOSED` | `management_items`（可选 `subject_group_extension`） | 同左 | `dimension_value_out_of_enum` |
| `DELIVERABLE_ASSERTION_LINK` | `deliverables`, `assertions` | `asserted_by` | `deliverable_without_assertion` |
| `ASSERTION_MUTUAL_EXCLUSION` | `assertions` | `subject`, `property`, `value`, `state` | `mutually_exclusive_active_assertions` |
| `CHANGE_CONSTRAINT_LINK` | `changes`, `constraints` | `constraint`, `relation` | `missing_constraint_link` / `invalid_change_relation` |
| `ALL_IMPROVEMENT_ASSUMPTION` | `changes` | `relations`, `assumption`, `verification_condition` | `all_improvement_without_verification` |
| `ROLE_MINIMAL_COMPLETENESS` | `actors`, `commitments` | `accountable_by`, `responsible_by`, `role_merge_declaration` | `missing_accountable` / `multiple_accountable` / `unknown_accountable` / `accountable_not_human` / `missing_responsible` / `missing_role_merge_declaration` |
| `AI_AUTONOMY_DELEGATION_AUDITABLE` | `actors`, `autonomy_grants`, `assertions` | `delegated_from`, `accountable`, `covers` | `delegation_chain_not_accountable` / `assertion_incomplete` |
| `PROJECT_CHARTER_EXISTENCE` | `projects`, `charters` | `stage`, `project`, 四项声明 | `missing_charter` / `incomplete_charter` |
| `CLOSURE_ACCEPTANCE_LINK` | `deliverables` | 内嵌 `assertions[].statement/accountable_confirmation` | `missing_acceptance_assertion` |
| `PROCUREMENT_CONTRACT_ANCHOR` | `commitments`, `contracts` | `procurement`, `contract`, 四项声明 | `missing_contract` / `incomplete_contract` |
| `SCHEDULE_EVIDENCE_LINK` | `commitments` | `deadline` / `milestone`, `evidence_assertions[].basis` | `missing_schedule_evidence` |
| `TAILORING_RECORD_EXISTENCE` | `tailoring_actions`, `tailoring_records` | `record`, 四项声明 | `missing_tailoring_record` / `incomplete_tailoring_record` |
| `TAILORING_NON_TRIMMABLE_SET` | `tailoring_records` | `trimmed_rule` | `non_trimmable_rule` |
| `TAILORING_REASSESSMENT_CONDITION` | `tailoring_records` | `reassessment_condition` / `permanent` + `reason` | `missing_reassessment_condition` |

## 4. 枚举

| 枚举 | 值 |
|---|---|
| `process_group` | `pre-project`、`overseeing`、`directing`、`initiating`、`controlling`、`managing-delivery`、`closing`、`post-project` |
| `subject_group` | ISO 21502:2020 第 7 章的 17 项管理实践；当前原型只物化样例用到的 `planning`、`lessons-learned`，其余值须在 `subject_group_extension[].value` 中声明 |
| `relation` | `mitigates`、`exacerbates`、`trades_off` |
| 不可裁剪规则 | `G-A1`、`G-A2`、`G-C1`、`G-D1`、`G-E1` |
| 验收/移交陈述 | `已验收`、`已移交` |

`subject_group` 的 17 项完整枚举依赖来源正文；原型只保证“样例值 + 契约扩展”两条路径，不宣称覆盖全部合法值。

## 5. 原型未覆盖的规则正文

下列条件不在附录 A 判定列内，原型**不实现**，并在运行输出中逐条声明“未覆盖规则正文”：

| check_id | 未覆盖条件 | 缺口 / 工作项 |
|---|---|---|
| `PROJECT_MINIMAL_EXISTENCE` | `Constraint` 须作用于该 `Outcome` 或 `Commitment` | G-002 / T-130 |
| `CONSTRAINT_ANCHOR_REQUIRED` | “管理活动/产物”节点类型未枚举 | G-001 / G-A2 |
| `ROLE_MINIMAL_COMPLETENESS` | “决策类 `Commitment`”筛选未定义；两种情形的 severity 未拆分 | G-001 / G-E1、G-004 / T-100 |
| `ALL_IMPROVEMENT_ASSUMPTION` | “验证条件满足前不得作为批准依据”无关系载体 | G-001 / G-D2 |
| `AI_AUTONOMY_DELEGATION_AUDITABLE` | `Assertion` 须以 `assumption` 形式存在并附验证条件 | G-003 / T-131 |

## 6. 后续样例的遵循规则

1. 新样例的顶层键与字段名必须来自第 2、3 节；需要新字段时，先改本文件并记 `CHANGELOG.md`，再改样例。
2. 新样例仍须成组：一个触发 `fail`、一个不触发 `pass`；`warn` / `assumption` 组须在期望输出中写 `severity` 与 `rule_status`。
3. 任何样例不得固化第 5 节的未覆盖条件；裁定改变判定列后，先改附录 A 与本文件，再补样例。
4. 修改后必须运行 `python3 validation/checker-prototype/checker.py`，全部样例通过才可提交；失败时按 `AGENTS.md` 3.6 判断是否新增缺口。
