# 确定性校验器输入 schema

**性质**：执行层规范文件（`STATE.md` 的 `spec/` 默认 `active`）。它固定 `spec/methods/deterministic-checker.md` 附录 A 各 `check_id` 的**谓词快照输入字段**，并定义判定列的表示规范（量词、空值、关系路径、值域封闭、引用完整性、假设时效、路径可达性、适用性状态）。T-011 的 34 个样例是该 schema 的首批实例；**此后新增或修改的样例必须遵循本文件**。

**边界**：本文件定义输入字段与表示规范，不改变附录 A 的判定逻辑本身；判定逻辑以附录 A 为准。schema 与判定列冲突时登记缺口（`GAP_LEDGER.md`，`AGENTS.md` 3.6）。

**基线**：本文件不写版本号（ADR-0003）。每次修改记 `CHANGELOG.md`，并重跑 `validation/checker-prototype/checker.py`；34 个样例必须仍为 34/34。

## 1. 通用约定

1. 一个输入是一份 YAML 谓词快照，顶层为映射。顶层键即该 `check_id` 的**量化域**（例如 `deliverables` 表示“每个 `Deliverable`”）。
2. **缺键即不可判定**：判定所需的顶层键缺失，或键的值为 `null`，原型输出 `cannot_evaluate` / `missing_input`，不得当作 `pass`。归一化在 `run_case` 入口一次完成，覆盖**顶层键、嵌套对象键、数组元素**三种 `null` 情形；各 `check` 函数不再单独兜底。嵌套归一化规则：第 3 节登记的实体集合（`actors`、`outcomes`、`commitments`、`constraints`、`deliverables`、`assertions`、`changes`、`projects`、`charters`、`contracts`、`tailoring_actions`、`tailoring_records`、`management_items`、`autonomy_grants`）中，每个元素必须带 `id`；缺 `id` 与顶层缺键同出口。内嵌对象（如 `deliverables[].assertions[]`、`evidence_assertions[]`）不要求 `id`。
3. **空值三态**（D2）：
   - 缺键或 `null` → `cannot_evaluate`（输入缺失）；
   - `{}` → 对象存在但无字段，按字段必填判定 `fail`；
   - `[]` → 集合为空，按量词判定：全称下为真，存在下为假，不得当作缺失输入。
4. **已按适用范围筛选**：输入只含该规则的适用对象。已筛选的范围包括：G-E1 的决策类 `Commitment`（`decision_class: true`）、G-A2 的管理活动/产物、G-F1 的执行阶段 `Project`、G-F2 的收尾阶段 `Deliverable`、G-F3 的外部采购承诺。检查本身不再做类型筛选。
5. **引用完整性（统一策略，P4）**：所有引用字段必须指向同快照中已出现的 `id`。引用字段清单由第 2bis 节的标注表生成，不在代码中另维护。
   - **规则子句原因优先**：悬空引用落在某规则子句的判定对象内时，返回该子句在 A.2 中登记的原因码；只有该子句的原因码列显式包含 `dangling_reference`（当前仅 `G-E2#1`、`G-E2#3`），才返回 `dangling_reference`。A.2 的“悬空引用原因归属”表是消费方的判别依据。
   - **全局兜底**：`validate_references()` 只在全部子句 `pass` 后运行，处理没有规则子句承接的悬空引用，返回 `fail` / `dangling_reference`。它不覆盖已命中的规则原因码。
   - 引用对象类型未在第 2 节定义 → `cannot_evaluate` / `undefined_object_type`（不得判 `fail`，因为缺的是表示能力而非事实）。
   - 判 `fail` 时仍须给出确定原因码；消费方按“check_id + 原因码”判别，不得只凭 `dangling_reference` 推断规则语义。
6. **量词显式化（P3）**：
   - 顶层键默认**全称**：每个元素都必须满足判定列；
   - 对象内引用字段默认**存在且全部解析**：字段存在至少一个合法取值，且每个列出的引用都必须解析；
   - 需要“存在一个”的跨对象条件必须写成关系路径（第 3bis 节），不得用自然语言“某个/至少一个”隐含。
7. **跨对象相关性（P3）**：判定列中的“该交付物”“其 `Outcome`”等指代必须落为关系路径，例如 `deliverables[].asserted_by[].about`。第 3bis 节列出各 `check_id` 使用的关系路径；新增路径先改本节。
8. **值域封闭（P2）**：判定列中出现的枚举集合必须引用第 4 节的具名枚举；不得出现自然语言值（如“已验收或已移交”须写成枚举名 `acceptance_statement`）。
9. **assumption 时效与批准资格（P5）**：`assumption` 表示为对象 `{verification_condition, status, verified_at, expires_at, approved_by, approval_basis}`；`status ∈ {pending, satisfied, expired}`。`expired`、或 `pending` 且缺 `approved_by` → `cannot_evaluate` / `assumption_unclosed`，不得判 `pass`。
10. **路径与可达性（P6）**：链式条件表示为 `{start, steps: [{relation, direction, target_type, target_id}], reach}`。`steps[]` 必须带 `target_id`，它是路径解析到下一节点的唯一依据；`direction` 当前只允许 `out`。判定列写路径表达式，不得写“终至”“链上有”这类自然语言，也不得再使用 `delegated_from: "<id>"` 的扁平字符串写法（该写法已删除）。
11. **封闭枚举全局归一化**：`applicability.state`、`assumption.status`、`node_type`、`subject_group_extension[].relation` 的取值必须在第 4 节具名枚举内。出现非法值一律以子句结果参与聚合（`("cannot_evaluate", "undefined_enum_value", <clause>)`），不得判 `pass` 或 `fail`。**不做入口短路**：枚举结果与各 `check` 函数的结果一并交给 `aggregate()`，按第 15 条的 `fail > cannot_evaluate > pass` 与 A.2 行序判定，保证结论与违规被发现顺序无关。`node_type` 非法归属 `G-A2#2`、`relation` 非法归属 `G-B2#2`，`assumption.status` 归属 `G-D2#3` / `G-E2#3`，`applicability.state` 与 `management_items[].node_type` 无独立 A.2 子句。
12. **适用性（P7）**：输入可携带 `applicability: {state}`，`state ∈ {applicable, inapplicable, pending}`。`inapplicable` → `not_applicable`；`pending` → `cannot_evaluate` / `applicability_pending`；`applicable` 或未提供 → 正常判定。
13. **结论与原因**：`verdict ∈ {pass, fail, cannot_evaluate, not_applicable}`；`reason` 为稳定原因码，`pass` / `not_applicable` 时为 `null`。原因码只用于样例断言，不是新的规范词汇。
14. **severity / rule_status**：由附录 A 与 `validation/CHECKLIST.md` 决定，不由输入携带；`assumption` 组按 P6 输出 `advisory`。子句级 severity 覆盖见附录 A.2。
15. **多违规优先级（D4）**：`reason` 单值；聚合顺序为 **`fail` > `cannot_evaluate` > `pass`**——任一子句 `fail` 即判 `fail`，不存在 `fail` 时才由 `cannot_evaluate` 决定；同一 verdict 内按附录 A.2 的子句行序取第一条命中，`reason` 即该子句的原因码。**原型不输出 `violations[]`**：四值结论与单一 `reason` 是唯一承诺；需要逐子句明细的消费方按 A.2 行序自行复算。旧表述“全部子句结果以 `violations[]` 输出”已撤除，“`cannot_evaluate` 优先于 `fail`”已废止。
16. **`grounding_ref` 与知识条目来源的分工（T-139，2026-11-14）**：本 schema 的检查输入不携带 `grounding_ref`。知识条目（`knowledge/anchored-entries.jsonl`）的来源归属写在 `evidence[]`，每项至少含 `source_id`，可附 `locator` / `page` / `precision`；`grounding_ref` 只用于规则或本体到知识条目的绑定，取 `knowledge:<term>`。规则正文的 `grounding_ref` 仍按 `GRAMMAR.md` 字段表指向 `SOURCE_LEDGER.md` 的条目 ID。两类意图不得混用同一字段。

## 2. 共享字段

| 对象 | 键 | 类型 | 说明 |
|---|---|---|---|
| `project` / `projects[]` | `id`, `stage` | 字符串 | `stage` 至少识别 `executing` |
| `actors[]` | `id`, `type`, `accountable`, `delegated_from` | 字符串 / 布尔 | `type ∈ {HumanActor, LegalEntity, AIActor}`；`accountable: true` 表示委托链终点 |
| `outcomes[]` | `id` | 字符串 | |
| `commitments[]` | `id`, `by`, `to`, `constrained_by`, `accountable_by`, `responsible_by`, `role_merge_declaration`, `procurement`, `contract`, `deadline`, `milestone`, `evidence_assertions`, `decision_class`, `node_type` | 见各 `check_id` | `responsible_by` 为字符串列表；`decision_class: true` 标识决策类承诺（G-E1 输入已按此筛选）；`node_type` 可选，提供时须 ∈ `management_node_type`（G-A2#2） |
| `constraints[]` | `id`, `constrains` | 字符串 | `constrains` 指向 `outcomes[].id` 或 `commitments[].id`；`{}` 视为未填 → `fail` |
| `deliverables[]` | `id`, `constrained_by`, `asserted_by`, `assertions`, `form`, `node_type` | 列表 / 对象 | 两种断言表示：C1 用 `asserted_by` 引用，F2 内嵌 `assertions`；`node_type` 可选，提供时须 ∈ `management_node_type`（G-A2#2） |
| `assertions[]` | `id`, `about`, `deliverable`, `subject`, `property`, `value`, `state`, `covers`, `basis`, `source`, `statement`, `statement_kind`, `kind`, `verification_condition`, `accountable_confirmation`, `assumption` | 见各 `check_id` | `state ∈ {active, ...}`；`covers` 为字符串列表；`statement_kind ∈ statement_kind`；`kind ∈ assertion_kind` |
| `changes[]` | `id`, `constraint`, `relation`, `relations`, `target`, `assumption`, `verification_condition`, `approval_basis` | 见各 `check_id` | D1 用单数 `relation`；D2 用复数 `relations`；`target` 为 `{type, id}`；`approval_basis` 为被当作批准依据的产物 `id` 列表 |
| `management_items[]` | `id`, `node_type`, `process_group`, `subject_group` | 字符串 | `node_type ∈ management_node_type` |
| `subject_group_extension[]` | `value`, `relation`, `base` | 字符串 | 领域特化项：`relation ∈ subject_group_extension_relation`；`specializes` / `cross_cuts` 的 `base` 必须是 17 项基础 `subject_group` 之一，`orthogonal_to` 可不写 `base`；`value` 不得与基础枚举重名。只写 `{value}` → `fail` / `invalid_subject_group_extension`；`relation` 非法值 → `cannot_evaluate` / `undefined_enum_value` |
| `autonomy_grants[]` | `id`, `actor`, `delegated_from`, `assertions` | 对象 / 列表 | `delegated_from` 为第 1.10 条路径对象；禁止扁平字符串。终点须 `accountable: true` 且类型 ∈ `{HumanActor, LegalEntity}`；`AIActor` 标 `accountable: true` 仍按 `accountable_not_human` 判 `fail` |
| `charters[]` | `id`, `project`, `outcomes`, `constraints`, `accountable`, `authorizing_assertion` | 见 F1 | |
| `contracts[]` | `id`, `deliverable_form`, `acceptance_criteria`, `constrained_by`, `accountable_signature` | 见 F3 | |
| `tailoring_actions[]` | `id`, `record` | 字符串 | `record` 指向 `tailoring_records[].id` |
| `tailoring_records[]` | `id`, `trimmed_rule`, `rationale`, `scope`, `approver`, `reassessment_condition`, `permanent`, `reason` | 见 G 组 | |
| `assumption` | `verification_condition`, `status`, `verified_at`, `expires_at`, `approved_by`, `approval_basis` | 见 §1.9 | 变更或断言携带的假设对象；`pending` 且缺 `approved_by` → `assumption_unclosed` |

## 2bis. 引用字段标注（生成源）

> 本节的 2bis.1 是原型 `REFERENCE_RULES` 的**唯一生成源**；`validation/checker-prototype/checker.py` 启动时解析该表，代码中不得另写引用字段清单。2bis.2 显式登记第 2 节中**不是引用**的字段。第 2 节出现的每个字段必须落在 2bis.1（引用）或 2bis.2（非引用）之一；新增字段未登记时 `scripts/check_three_table.py` 退出 1，样例不得提交。

### 2bis.1 引用字段

路径语法：`对象[]` 表示逐元素展开，`.` 表示对象嵌套；`字段` 是路径末端的键。`形态`：`scalar`（单值）、`list`（id 列表）、`type`（按同对象的 `type` 选择目标集合）、`any`（任意已登记产物集合）。

| 源路径 | 字段 | 目标集合 | 形态 |
|---|---|---|---|
| `commitments[]` | `by` | `actors` | scalar |
| `commitments[]` | `to` | `outcomes` | scalar |
| `commitments[]` | `accountable_by` | `actors` | scalar |
| `commitments[]` | `responsible_by` | `actors` | list |
| `commitments[]` | `contract` | `contracts` | scalar |
| `commitments[]` | `constrained_by` | `constraints` | list |
| `constraints[]` | `constrains` | `outcomes` ∪ `commitments` | scalar |
| `deliverables[]` | `asserted_by` | `assertions` | list |
| `deliverables[]` | `constrained_by` | `constraints` | list |
| `deliverables[].assertions[]` | `about` | `deliverables` | scalar |
| `deliverables[].assertions[]` | `deliverable` | `deliverables` | scalar |
| `deliverables[].assertions[]` | `subject` | `deliverables` | scalar |
| `deliverables[].assertions[]` | `accountable_confirmation` | `actors` | scalar |
| `assertions[]` | `about` | `deliverables` | scalar |
| `assertions[]` | `deliverable` | `deliverables` | scalar |
| `assertions[]` | `subject` | `deliverables` | scalar |
| `assertions[]` | `accountable_confirmation` | `actors` | scalar |
| `assertions[].assumption` | `approved_by` | `actors` | scalar |
| `changes[]` | `constraint` | `constraints` | scalar |
| `changes[].target` | `id` | `Commitment→commitments`、`Deliverable→deliverables` | type |
| `changes[]` | `approval_basis` | `any` | list |
| `changes[].assumption` | `approved_by` | `actors` | scalar |
| `charters[]` | `project` | `projects` | scalar |
| `charters[]` | `outcomes` | `outcomes` | list |
| `charters[]` | `constraints` | `constraints` | list |
| `charters[]` | `accountable` | `actors` | scalar |
| `charters[]` | `authorizing_assertion` | `assertions` | scalar |
| `tailoring_actions[]` | `record` | `tailoring_records` | scalar |
| `autonomy_grants[]` | `actor` | `actors` | scalar |
| `autonomy_grants[].delegated_from.steps[]` | `target_id` | `actors` | scalar |
| `autonomy_grants[]` | `assertions` | `assertions` | list |
| `contracts[]` | `constrained_by` | `constraints` | list |
| `contracts[]` | `accountable_signature` | `actors` | scalar |
| `tailoring_records[]` | `approver` | `actors` | scalar |

### 2bis.2 非引用字段

本表显式登记第 2 节中不参与引用解析的字段（标量、枚举、自由文本、容器或局部 id）。容器字段的引用在 2bis.1 中按内部路径另行标注。

| 非引用字段 | 说明 |
|---|---|
| `id` | 对象自身标识，不是引用 |
| `stage` | 阶段枚举 |
| `type` | 类型判别值，不是引用 |
| `accountable` | 布尔标记（`actors[]`） |
| `delegated_from` | 容器；引用在 `steps[].target_id`（2bis.1） |
| `role_merge_declaration` | 声明文本 |
| `procurement` | 采购标记 |
| `deadline` | 日期 |
| `milestone` | 里程碑标识（文本） |
| `evidence_assertions` | 内嵌依据对象，局部 `id` 不进入全局解析 |
| `decision_class` | 布尔标记 |
| `form` | 交付物形态描述 |
| `property` | 属性名 |
| `value` | 属性值 |
| `state` | 断言状态 |
| `covers` | 覆盖范围字符串列表 |
| `basis` | 依据类型 |
| `source` | 来源文本 |
| `statement` | 陈述文本 |
| `statement_kind` | 陈述类型枚举 |
| `kind` | 断言类型枚举 |
| `verification_condition` | 验证条件文本 |
| `assumption` | 容器；引用在 `approved_by`（2bis.1） |
| `relation` | 关系枚举（D1） |
| `relations` | 关系枚举列表（D2） |
| `target` | 容器；引用在 `id`（2bis.1，按 `type` 判别） |
| `node_type` | 节点类型枚举 |
| `process_group` | 过程组枚举 |
| `subject_group` | 主题组枚举 |
| `base` | `subject_group_extension[]` 指向的基础主题组（枚举值，不是跨集合引用） |
| `deliverable_form` | 形态声明 |
| `acceptance_criteria` | 验收判据文本 |
| `trimmed_rule` | 规则号 |
| `rationale` | 理由文本 |
| `scope` | 适用范围文本 |
| `reassessment_condition` | 重新评估条件文本 |
| `permanent` | 布尔标记 |
| `reason` | 原因文本 |
| `status` | 假设状态枚举 |
| `verified_at` | 验证时间 |
| `expires_at` | 失效时间 |

## 2ter. 嵌套必需键全表（入口归一化）

第 2 节列出的 14 个实体集合（`actors`、`outcomes`、`commitments`、`constraints`、`deliverables`、`assertions`、`changes`、`projects`、`charters`、`contracts`、`tailoring_actions`、`tailoring_records`、`management_items`、`autonomy_grants`）的每个元素都必须带 `id`。删除任一元素的 `id` 与删除顶层必需键同出口：`cannot_evaluate` / `missing_input`，由入口 `evaluate()` 归一化，不依赖各 `check` 函数自守。内嵌数组（`deliverables[].assertions[]`、`commitments[].evidence_assertions[]`、`autonomy_grants[].assertions[]`）的局部 `id` 不参与全局解析，不在本表内。

下表是 `--nested-missing-sweep` 的固定清单（按样例实际出现的元素逐项列出，共 53 项，全部实测 53/53 返回 `cannot_evaluate/missing_input`）：

| check_id | 嵌套必需键（逐元素删除） |
|---|---|
| `PROJECT_MINIMAL_EXISTENCE` | `actors[0].id`、`outcomes[0].id`、`commitments[0].id`、`constraints[0].id` |
| `CONSTRAINT_ANCHOR_REQUIRED` | `commitments[0].id`、`constraints[0].id`、`deliverables[0].id`、`constraints[1].id` |
| `DELIVERABLE_ASSERTION_LINK` | `deliverables[0].id`、`assertions[0].id`、`deliverables[1].id`、`assertions[1].id`、`assertions[2].id` |
| `CHANGE_CONSTRAINT_LINK` | `constraints[0].id`、`deliverables[0].id`、`changes[0].id`、`commitments[0].id`、`constraints[1].id`、`changes[1].id` |
| `ROLE_MINIMAL_COMPLETENESS` | `actors[0].id`、`actors[1].id`、`commitments[0].id` |
| `DUAL_DIMENSION_ANNOTATION` | `management_items[0].id`、`management_items[1].id` |
| `DIMENSION_VALUE_CLOSED` | `management_items[0].id`、`management_items[1].id` |
| `ASSERTION_MUTUAL_EXCLUSION` | `deliverables[0].id`、`assertions[0].id`、`assertions[1].id` |
| `ALL_IMPROVEMENT_ASSUMPTION` | `changes[0].id`、`actors[0].id` |
| `AI_AUTONOMY_DELEGATION_AUDITABLE` | `actors[0].id`、`actors[1].id`、`assertions[0].id`、`autonomy_grants[0].id` |
| `PROJECT_CHARTER_EXISTENCE` | `projects[0].id`、`actors[0].id`、`outcomes[0].id`、`constraints[0].id`、`assertions[0].id`、`charters[0].id` |
| `CLOSURE_ACCEPTANCE_LINK` | `deliverables[0].id`、`actors[0].id` |
| `PROCUREMENT_CONTRACT_ANCHOR` | `commitments[0].id`、`actors[0].id`、`constraints[0].id`、`contracts[0].id` |
| `SCHEDULE_EVIDENCE_LINK` | `commitments[0].id` |
| `TAILORING_RECORD_EXISTENCE` | `tailoring_actions[0].id`、`actors[0].id`、`tailoring_records[0].id` |
| `TAILORING_NON_TRIMMABLE_SET` | `tailoring_records[0].id` |
| `TAILORING_REASSESSMENT_CONDITION` | `tailoring_records[0].id` |

## 3. 各 check_id 的输入域

| check_id | 必需顶层键 | 判定所需字段 | 失败原因码 |
|---|---|---|---|
| `PROJECT_MINIMAL_EXISTENCE` | `project`, `actors`, `outcomes`, `commitments`, `constraints` | `commitments[].by/to`、`constraints[].constrains` | `missing_actor` / `missing_outcome` / `missing_commitment` / `missing_constraint` / `broken_commitment_endpoint` / `constraint_not_applied` |
| `CONSTRAINT_ANCHOR_REQUIRED` | `commitments`, `deliverables`, `constraints` | 每项的 `constrained_by`；可选 `node_type`（提供时须 ∈ `management_node_type`，否则 G-A2#2 不可达） | `unanchored_management_item` / `undefined_enum_value` |
| `DUAL_DIMENSION_ANNOTATION` | `management_items` | `process_group`, `subject_group` | `missing_dimension` |
| `DIMENSION_VALUE_CLOSED` | `management_items`（可选 `subject_group_extension`） | `process_group`、`subject_group`、`subject_group_extension[].value/relation/base` | `dimension_value_out_of_enum` / `invalid_subject_group_extension` / `undefined_enum_value` |
| `DELIVERABLE_ASSERTION_LINK` | `deliverables`, `assertions` | `asserted_by` / `about`、`statement`, `statement_kind` | `deliverable_without_assertion` / `assertion_without_content` / `assertion_about_mismatch` |
| `ASSERTION_MUTUAL_EXCLUSION` | `assertions`, `deliverables` | `subject`, `property`, `value`, `state` | `mutually_exclusive_active_assertions` |
| `CHANGE_CONSTRAINT_LINK` | `changes`, `constraints`, `commitments`, `deliverables` | `constraint`, `relation`, `target.type/id` | `missing_constraint_link` / `invalid_change_relation` / `missing_change_target` / `invalid_change_target` |
| `ALL_IMPROVEMENT_ASSUMPTION` | `changes`, `actors` | `relations`, `assumption`, `verification_condition`, `approval_basis` | `all_improvement_without_verification` / `approval_basis_before_verification` / `assumption_unclosed` |
| `ROLE_MINIMAL_COMPLETENESS` | `actors`, `commitments` | `accountable_by`, `responsible_by`, `role_merge_declaration` | `missing_accountable` / `multiple_accountable` / `unknown_accountable` / `accountable_not_human` / `missing_responsible` / `missing_role_merge_declaration` |
| `AI_AUTONOMY_DELEGATION_AUDITABLE` | `actors`, `autonomy_grants`, `assertions` | `delegated_from` 路径（第 1.10 条）、`accountable`、`covers`, `kind`, `verification_condition` | `delegation_chain_not_accountable` / `accountable_not_human` / `assertion_incomplete` / `assumption_unclosed` / `invalid_path` / `dangling_reference` |
| `PROJECT_CHARTER_EXISTENCE` | `projects`, `charters`, `outcomes`, `constraints`, `actors`, `assertions` | `stage`, `project`, 四项声明 | `missing_charter` / `incomplete_charter` |
| `CLOSURE_ACCEPTANCE_LINK` | `deliverables`, `actors` | 内嵌 `assertions[].statement/accountable_confirmation` | `missing_acceptance_assertion` |
| `PROCUREMENT_CONTRACT_ANCHOR` | `commitments`, `contracts`, `constraints`, `actors` | `procurement`, `contract`, 四项声明 | `missing_contract` / `incomplete_contract` |
| `SCHEDULE_EVIDENCE_LINK` | `commitments` | `deadline` / `milestone`, `evidence_assertions[].basis` | `missing_schedule_evidence` |
| `TAILORING_RECORD_EXISTENCE` | `tailoring_actions`, `tailoring_records`, `actors` | `record`, 四项声明 | `missing_tailoring_record` / `incomplete_tailoring_record` |
| `TAILORING_NON_TRIMMABLE_SET` | `tailoring_records` | `trimmed_rule` | `non_trimmable_rule` |
| `TAILORING_REASSESSMENT_CONDITION` | `tailoring_records` | `reassessment_condition` / `permanent` + `reason` | `missing_reassessment_condition` |

## 3bis. 跨对象相关性表示（P3）

判定列中的跨对象指代必须落到下表路径；未列出的 `check_id` 不使用跨对象相关性。

| check_id | 关系路径 | 量词 | 说明 |
|---|---|---|---|
| `PROJECT_MINIMAL_EXISTENCE` | `commitments[].by → actors[].id`、`commitments[].to → outcomes[].id` | 全称（每个引用解析） | 端点必须已登记 |
| `PROJECT_MINIMAL_EXISTENCE` | `constraints[].constrains → outcomes[].id ∪ commitments[].id` | 存在且全部解析 | 约束须作用于本项目的 `Outcome` 或 `Commitment` |
| `DELIVERABLE_ASSERTION_LINK` | `deliverables[].asserted_by → assertions[].id` ∪ `assertions[].about → deliverables[].id` | 存在 | 正向边与反向 `about` 任一成立即可（D5） |
| `DELIVERABLE_ASSERTION_LINK` | `assertions[].about → deliverables[].id` | 全称（每条被引用断言） | 断言内容的相关性锚点（D6） |
| `CHANGE_CONSTRAINT_LINK` | `changes[].target.type ∈ {Commitment, Deliverable}` 且 `target.id` 解析到对应集合 | 全称 | 变更对象的类型谓词（D7） |
| `AI_AUTONOMY_DELEGATION_AUDITABLE` | `autonomy_grants[].delegated_from` 路径（`start` → `steps[].target_id` → … → `reach: accountable`） | 存在一条路径 | 路径对象见第 1.10 条；每步 `target_id` 必须解析到 `actors[].id` |

## 4. 枚举

| 枚举 | 值 |
|---|---|
| `process_group` | `pre-project`、`overseeing`、`directing`、`initiating`、`controlling`、`managing-delivery`、`closing`、`post-project` |
| `subject_group` | `planning`（7.2）、`benefits-management`（7.3）、`scope-management`（7.4）、`resources-management`（7.5）、`schedule-management`（7.6）、`cost-management`（7.7）、`risk-management`（7.8）、`issues-management`（7.9）、`change-control`（7.10）、`quality-management`（7.11）、`stakeholder-engagement`（7.12）、`communication-management`（7.13）、`organizational-and-societal-change`（7.14）、`reporting`（7.15）、`information-and-documentation-management`（7.16）、`procurement`（7.17）、`lessons-learned`（7.18） |
| `relation` | `mitigates`、`exacerbates`、`trades_off` |
| `statement_kind` | `what`、`state`、`condition`（对应“是什么 / 处于什么状态 / 满足什么条件”） |
| `assertion_kind` | `fact`、`assumption`、`decision` |
| `change_target_type` | `Commitment`、`Deliverable` |
| `assumption.status` | `pending`、`satisfied`、`expired` |
| `applicability.state` | `applicable`、`inapplicable`、`pending` |
| `management_node_type` | `ManagementActivity`、`ManagementArtifact` |
| `subject_group_extension_relation` | `specializes`、`cross_cuts`、`orthogonal_to` |
| 不可裁剪规则 | `G-A1`、`G-A2`、`G-C1`、`G-D1`、`G-E1` |
| 验收/移交陈述 | `acceptance_statement`：`已验收`、`已移交` |

`subject_group` 的 17 项已完整物化，取值来源为 ISO 21502:2020 第 7 章 7.2–7.18（本地副本印刷页 26–45）。原型直接以这 17 项为封闭集；`subject_group_extension` 只用于领域特化（`specializes` / `cross_cuts` / `orthogonal_to`），不再是“补全基础枚举”的通道。`orthogonal_to` 与实现对齐：正交扩展**不要求** `base` 归属，声明了则必须属于 17 项基础枚举；`specializes` / `cross_cuts` 仍必须有合法 `base`。

## 5. 表示层覆盖状态（ADR-0013 后）

原第 5 节列出的 5 处“原型未覆盖规则正文”已全部消解；下表保留为变更记录。判定列与本节不一致时，以附录 A 为准并登记缺口。

| 原未覆盖项 | 处置 | 承接 check_id |
|---|---|---|
| G-A1 `Constraint` 须作用于该 `Outcome` 或 `Commitment` | 纳入判定列（`constraint_not_applied`） | `PROJECT_MINIMAL_EXISTENCE` |
| G-A2 “管理活动/产物”节点类型未枚举 | 第 4 节定义 `management_node_type` | `CONSTRAINT_ANCHOR_REQUIRED` |
| G-E1 “决策类 `Commitment`”未定义、severity 未拆分 | 第 2 节定义 `decision_class`；A.2 拆分 severity | `ROLE_MINIMAL_COMPLETENESS` |
| G-D2 “验证条件满足前不得作为批准依据”无载体 | 第 2 节定义 `approval_basis`；纳入判定列 | `ALL_IMPROVEMENT_ASSUMPTION` |
| G-E2 `Assertion` 须以 `assumption` 形式存在并附验证条件 | 第 2 节定义 `kind` / `verification_condition`；纳入判定列 | `AI_AUTONOMY_DELEGATION_AUDITABLE` |

## 6. 后续样例的遵循规则

1. 新样例的顶层键、字段名与枚举值必须来自第 2、3、3bis、4 节；需要新字段时，先改本文件并记 `CHANGELOG.md`，再改样例。
2. 新样例仍须成组：一个触发 `fail`、一个不触发 `pass`；`warn` / `assumption` 组须在期望输出中写 `severity` 与 `rule_status`。
3. 样例必须声明它覆盖的子句（附录 A.2 的 clause id）；一个子句至少被一个样例覆盖，未覆盖须在 A.2 记 `not-checked` 并写理由。
4. 判定列中的枚举、关系路径、量词必须能在本文件找到定义；`scripts/check_three_table.py` 负责机械对照，失败即阻断提交。
5. 修改后必须运行 `python3 validation/checker-prototype/checker.py`，全部样例通过才可提交；失败时按 `AGENTS.md` 3.6 判断是否新增缺口。
