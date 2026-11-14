# 缺口台账

**用途**：登记“规则正文与 `check_id` 判定列不一致”的缺口，给出分级、到期与处置出口。本文件是缺口的唯一台账；变更历史见 `CHANGELOG.md`，工作项状态见 `TODO.md`。

**当前里程碑**：M1

**性质**：临时治理机制，撤除条件见文末；规则出处 `AGENTS.md` 3.6，决策记录 `adr/0012-gap-ledger-and-adjudication.md`。

## 入口条件

满足任一条件即**必须**登记为缺口，不得只留在讨论或提交信息里：

- `undefined-object`：规则或判定列引用了输入 schema 未定义的节点类型、关系或字段。
- `rule-stricter`：规则正文包含判定列未覆盖的规范性条件（例如“且”“附带”“不得”引出的条件）。
- `severity-mismatch`：判定列的实际 severity 与 `validation/CHECKLIST.md` 不一致。
- `representation-defect`：判定层的表示规范自身有缺陷（路径、枚举、格式、聚合、封闭性），不对应某一条规则的具体条款。
- `implementation-defect`：原型或检查器的实现与其声明口径不一致（崩溃、漏检、只做结构不做语义）。

**机械保证**：下方的核查矩阵必须逐行覆盖 A 表全部 `check_id`，结论只能是 `consistent` 或缺口编号；任何对 `GRAMMAR.md` 或 `spec/methods/deterministic-checker.md` 判定列的改动，必须在同一提交更新本文件，否则 `scripts/check_gap_ledger.py --staged` 退出 1。`rule-stricter` 与 `severity-mismatch` 的语义判断仍由人工复核，但“未复核”不再可能静默通过。

## 关闭判据（硬要求，2026-11-14 起）

**缺口不得以同源运行结果关闭。** 以下依据不构成关闭证据，`scripts/check_gap_ledger.py` 会直接报错：

- 自家原型对自家样例全部通过；
- 自家脚本退出 0（包括本台账的检查器、三表检查器、术语检查器）；
- 在同一提交内同时修改样例与实现后，用修改后的样例自证；
- 任何以“同源自查”“自家脚本通过”“退出 0”为唯一依据的说明。

**合法关闭依据**只有两类，必须写入缺口行的“关闭依据”列：

| 值 | 要求 |
|---|---|
| `非同源复核：<复核者/会话>，<日期>` | 复核方未参与被复核内容的实现；附复核范围、样例/条款清单与差异结论 |
| `人工签收：<签收人>，<日期>` | 签收人按规则正文逐条比对判定列与实现，附比对清单与逐条结论 |

关闭时 `status` 改为 `closed`，`处置出口` 只能取 `rule-change` / `check-change` / `doc-only` / `accepted`；`accepted` 仍须写“理由：”。检查器对“关闭依据缺失”“依据不是上述两类”“说明中出现同源自证措辞”均退出 1。

## 分级与停留上限

| 等级 | 含义 | 最长停留 | 默认处置 |
|---|---|---|---|
| L1 | 阻断错判：合法产物被判失败或非法产物被判通过，且阻断工作 | 1 个里程碑 | `check-change` |
| L2 | 漏判：规则正文的条件未进入判定列 | 2 个里程碑 | `check-change` |
| L3 | 语义不可判定：规则引用未定义的判定对象，无法机械判定 | 2 个里程碑 | `doc-only` |

到期里程碑 = 登记里程碑 + 最长停留。到期仍未裁定（`status=open` 且当前里程碑 ≥ 到期里程碑）时，`check_gap_ledger.py` 退出 1，`check_state.py` 随之报错，发布被阻断。

## 处置出口

每条缺口关闭时只能落到以下四种之一，不允许“沉默”：

- `rule-change`：改规则正文，使其与判定列或输入 schema 一致。
- `check-change`：改判定列，使其覆盖规则正文。
- `doc-only`：降为文档约束，并在规则状态中明确注明“不检查”。
- `accepted`：接受现状，说明中必须写“理由：”并附批准依据。

## 核查矩阵

| check_id | 规则 | 结论 | 复核里程碑 |
|---|---|---|---|
| `PROJECT_MINIMAL_EXISTENCE` | G-A1 | `G-002`、`G-007`、`G-008`、`G-009`、`G-014`、`G-016`、`G-017` | M1 |
| `CONSTRAINT_ANCHOR_REQUIRED` | G-A2 | `G-001`、`G-007`、`G-009`、`G-010` | M1 |
| `DUAL_DIMENSION_ANNOTATION` | G-B1 | `G-013`、`G-015` | M1 |
| `DIMENSION_VALUE_CLOSED` | G-B2 | `G-013`、`G-015` | M1 |
| `DELIVERABLE_ASSERTION_LINK` | G-C1 | `G-005`、`G-009`、`G-010` | M1 |
| `ASSERTION_MUTUAL_EXCLUSION` | G-C2 | `G-009`、`G-010` | M1 |
| `CHANGE_CONSTRAINT_LINK` | G-D1 | `G-006`、`G-009`、`G-010` | M1 |
| `ALL_IMPROVEMENT_ASSUMPTION` | G-D2 | `G-009`、`G-011` | M1 |
| `ROLE_MINIMAL_COMPLETENESS` | G-E1 | `G-004`、`G-009`、`G-010` | M1 |
| `AI_AUTONOMY_DELEGATION_AUDITABLE` | G-E2 | `G-003`、`G-010`、`G-011`、`G-012` | M1 |
| `PROJECT_CHARTER_EXISTENCE` | G-F1 | `G-009`、`G-010` | M1 |
| `CLOSURE_ACCEPTANCE_LINK` | G-F2 | `G-009`、`G-010` | M1 |
| `PROCUREMENT_CONTRACT_ANCHOR` | G-F3 | `G-009`、`G-010` | M1 |
| `SCHEDULE_EVIDENCE_LINK` | G-F4 | `G-009` | M1 |
| `TAILORING_RECORD_EXISTENCE` | G-G1 | `G-009`、`G-010` | M1 |
| `TAILORING_NON_TRIMMABLE_SET` | G-G2 | `G-009` | M1 |
| `TAILORING_REASSESSMENT_CONDITION` | G-G3 | `G-009` | M1 |

> 矩阵说明：缺口编号替代 `consistent` 表示该 `check_id` 截至 2026-11-14 的复核仍受该缺口影响，不得判为一致。G-008 是表示层合并条目，G-010/G-011/G-012 等为其拆分后的可执行项；G-014、G-016、G-017 为全局项，锚定在首行，但其影响覆盖全部 `check_id`。

## 缺口账

| 编号 | 状态 | 成因 | 等级 | 影响面 | 是否阻断 | 待裁定方 | 登记里程碑 | 处置出口 | 关联 T | 说明 | 关闭依据 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| G-001 | open | undefined-object | L3 | G-A2、G-D2、G-E1 | 否 | 架构负责人 | M1 |  | — | 2026-11-14 复核重开：P2（封闭枚举）只部分解决——`subject_group` 仅物化 2/17 项，`management_node_type` 等枚举未覆盖判定列全部引用；原以 `check-change` 关闭的依据是同源重跑，不成立。剩余项由 G-013 承接。 |  |
| G-002 | open | rule-stricter | L2 | G-A1 | 否 | 架构负责人 | M1 |  | T-130 | 2026-11-14 复核重开：P1（子句压缩）只部分解决——A 表判定列仍写叙述性短语，子句未完全下沉 A.2；原关闭依据是同源重跑，不成立。待 G-015/G-016 修正后由非同源复核关闭。 |  |
| G-003 | open | rule-stricter | L2 | G-E2 | 否 | 架构负责人 | M1 |  | T-131 | 2026-11-14 复核重开：P1/P5 只部分解决——`assumption.pending` 分支未检查 `approved_by`，且路径仍与扁平字符串双轨；原关闭依据不成立。由 G-011/G-012 承接。 |  |
| G-004 | open | severity-mismatch | L1 | G-E1 | 否 | 架构负责人 | M1 |  | T-100 | 2026-11-14 复核重开：severity 拆分本身已落地，但 P1 表示层只部分解决，且判定列格式与原因码映射未定义，不能维持 `check-change` 关闭。由 G-015/G-016 承接。 |  |
| G-005 | open | rule-stricter | L1 | G-C1 | 否 | 架构负责人 | M1 |  | T-134 | 2026-11-14 复核重开：C1 内容与 `about` 已纳入，但引用完整性只在 C1 局部生效（P4 未全局化），原关闭依据不成立。由 G-010 承接。 |  |
| G-006 | open | rule-stricter | L1 | G-D1 | 否 | 架构负责人 | M1 |  | T-135 | 2026-11-14 复核重开：`target.type` 已纳入，但引用完整性未全局生效，且 `reason` 与聚合优先级矛盾未定稿。由 G-010/G-014 承接。 |  |
| G-007 | open | undefined-object | L1 | G-A1、G-A2、G-C1、G-D1 | 否 | 架构负责人 | M1 |  | T-136 | 2026-11-14 复核重开：P2/P3/P4/P5 只部分解决——引用完整性仅 C1、路径表示缺目标 id 且与扁平字符串双轨、`assumption.pending` 未校验批准者、17 处 `null` 崩溃。由 G-009–G-012 承接。 |  |
| G-008 | open | representation-defect | L2 | 表示层（全局） | 否 | 架构负责人 | M1 |  | T-133 | 2026-11-14 复核重开：P1–P8 的合并条目中，P4（引用完整性）、P6（路径表示）未解决，P1/P2/P3/P5 只部分解决；上一轮以 `check-change` 全部关闭的裁定被非同源复核推翻。 |  |
| G-009 | open | implementation-defect | L1 | 全部 17 个 `check_id` | 否 | 架构负责人 | M1 |  | T-133 | 原型对必需顶层键只判 `key not in data`；键存在但值为 `null` 时进入迭代并抛 `TypeError`（17 处 check 函数同一缺陷）。按 schema §1.2/§1.3 应输出 `cannot_evaluate` / `missing_input`。 本次已修正：入口 `evaluate()` 同时拦截“键不存在”与“值为 `null`”，不依赖 check 内守卫；`--missing-key-sweep` 43/43 返回 `cannot_evaluate/missing_input`（偏离 0）、`--null-sweep` 138/138（崩溃 0），对照实验 `{}` 直入 check 仍 17/17 抛 `KeyError`；待非同源复核关闭。 |  |
| G-010 | open | representation-defect | L1 | 全部引用字段；重点 G-C1 之外 | 否 | 架构负责人 | M1 |  | T-133 | 引用完整性（P4）只在 `DELIVERABLE_ASSERTION_LINK` 与 `AI_AUTONOMY_DELEGATION_AUDITABLE` 局部实现；`commitments.by/to`、`constraints.constrains`、`changes.target.id`、`charters.project` 等悬空引用未统一报 `dangling_reference`。本次已把全局校验扩展到上述字段、`contracts.constrained_by/accountable_signature`、`tailoring_records.approver`、`assertions.about/deliverable/subject/accountable_confirmation`；A.1.11-2、A.1.12-2、A.1.13-2、A.1.15-2 的输入已按 schema §1.5 补齐，期望输出未变。待非同源复核关闭。 |  |
| G-011 | open | representation-defect | L1 | G-D2、G-E2 | 否 | 架构负责人 | M1 |  | T-133 | `assumption` 的 `pending` 分支只检查 `expired`，未检查 `approved_by`；schema §1.9 要求 `pending` 且缺 `approved_by` → `cannot_evaluate` / `assumption_unclosed`。 本次已修正：D2/E2 的 pending 分支均检查 `approved_by`；待非同源复核关闭。 |  |
| G-012 | open | representation-defect | L2 | G-E2、schema §1.10/§3bis | 否 | 架构负责人 | M1 |  | T-133 | 路径结构 `{start, steps, reach}` 的 `steps[]` 缺目标 `id`，无法定位下一节点；同时 schema 保留 `delegated_from` 扁平字符串写法，形成双轨。 本次已修正：路径对象补 `steps[].target_id`，扁平字符串返回 invalid_path；待非同源复核关闭。 |  |
| G-013 | open | representation-defect | L1 | G-B1、G-B2 | 否 | 架构负责人 | M1 |  | T-133 | `subject_group` 只物化 `planning`、`lessons-learned` 两项；ISO 21502:2020 第 7 章的 17 项管理实践未完整物化，合法标签会被判 `dimension_value_out_of_enum`。 本次已修正：17 项完整物化，原型同步；待非同源复核关闭。 |  |
| G-014 | open | representation-defect | L1 | 全部 `check_id` 的 verdict/reason 聚合 | 否 | 架构负责人 | M1 |  | T-133 | schema §1.14 规定 `reason` 优先级 `cannot_evaluate > fail`，A.2 又规定 verdict 聚合“任一 `fail` → `fail`，否则 `cannot_evaluate`”；两处对“同时存在 fail 与 cannot_evaluate”的结论相反。 本次已修正：§1.14 与 A.2 统一为 fail > cannot_evaluate > pass；17 个 check 改为返回子句级结果列表，由 `aggregate()` 顺序无关聚合（verdict 取最高级、reason 按 A.2 行序、severity 取胜出子句最高级）。证据：A2/E2 各 6 种排列均收敛为 1 个结论（A2 = fail/unanchored_management_item，E2 = fail/delegation_chain_not_accountable），34/34 不变；待非同源复核关闭。 |  |
| G-015 | open | representation-defect | L2 | 附录 A 判定列 | 否 | 架构负责人 | M1 |  | T-133 | A 表“判定”列仍写叙述性短语（如 G-B1 写“且值在枚举内”），子句 id 只在“子句”列；同一条件又划给 B2，造成 B1/B2 口径冲突。 本次已修正：A 表判定列只留子句 id，叙述下沉 A.2；B1/B2 条件归属已分离；待非同源复核关闭。 |  |
| G-016 | open | representation-defect | L2 | 附录 A.2、schema §3 | 否 | 架构负责人 | M1 |  | T-133 | A.2 子句表无“原因码”列；原因码与实际子句的映射未定义，`reason` 只能靠原型实现反向推断。 本次已修正：A.2 增加原因码列（40 条子句），A 表原因码与子句原因码集合机械一致；待非同源复核关闭。 |  |
| G-017 | open | implementation-defect | L2 | `scripts/check_three_table.py`、M2 出口 1 | 否 | 架构负责人 | M1 |  | T-133 | 三表检查器只做存在性/集合一致/词级定义，不做语义短语检查：G-B1 判定列写“值在枚举内”与 A.2 划给 B2 的冲突仍报通过，绿字被误读为语义闭合。 本次已修正：三表检查器增加判定列叙述检测、B1/B2 条件归属、原因码定义与映射检查；仍不保证全文语义等价，待非同源复核关闭。 |  |

**共同成因**：G-002、G-003、G-004、G-005、G-006 同属 **规则正文严于判定列** 这一大类——判定列只覆盖了规则正文的一部分条件，或把不同严重度的条件压在同一级别。它们不是彼此独立的偶发问题，而是同一口径缺陷的不同表现。对应的独立工作项 T-130、T-131、T-100、T-134、T-135 保留原编号，不合并。

**与 G-007 的关系**：G-007 是另一类——不是“判定列漏了正文条件”，而是“判定列本身存在未定明的语义”，因此成因记为 `undefined-object`。2026-11-14 复核后，其剩余语义缺陷拆为 G-009–G-012 四个可执行项。

**与 G-008 的关系**：G-008 登记独立复核报出的八条**表示层**问题（P1–P8）。2026-11-14 复核重跑确认 P4（引用完整性不统一）与 P6（路径表示）未解决，P1/P2/P3/P5 只部分解决，故重开；拆分项为 G-009–G-017。

## 核查记录

| 日期 | 事件 | 结论 |
|---|---|---|
| 2026-11-14 | T-107 最小原型跑通 34/34 个样例 | 核查矩阵不变；G-001–G-004 仍为 `open`，原型只在输出中声明“未覆盖规则正文”，不关闭任何缺口 |
| 2026-11-14 | T-133 独立复核（非同源，只读验收包，覆盖 G-A1 / G-C1 / G-D1 共 3 个 `check_id`、6 个样例） | 6/6 判定与预期一致，但一致不等于一致于规则正文：复核指出 G-C1 漏“断言内容与 `about` 相关性”、G-D1 漏“变更对象类型谓词”，并报告 5 处判定列语义未定明。据此登记 G-005、G-006、G-007；核查矩阵由 12/17 降为 10/17 consistent。 |
| 2026-11-14 | 起草 `adr/0013-unified-adjudication-of-check-semantics.md`（`draft`） | G-001、G-002、G-003、G-005、G-006、G-007 并入同一次裁定范围；G-004（`severity-mismatch`）不并入，仍按 T-100 单独裁定。 |
| 2026-11-14 | ADR-0013 扩范围为“判定层表示规范”并一次性裁定（`accepted`） | D0–D9 与 P1–P8 同批出结论；G-001–G-007 全部以 `check-change` 关闭；P1–P8 合并登记为 G-008 并关闭。核查矩阵 17/17 `consistent`。**该裁定已于同日被非同源复核重跑推翻，见下一行。** |
| 2026-11-14 | 裁定后单次重验（同源，非独立复核） | 原型 34/34、三表检查器退出 0。**按本文件“关闭判据”，同源重验不构成关闭证据**；上一轮把该结果当作关闭依据是错误。 |
| 2026-11-14 | 独立复核重跑（非同源） | 推翻上一轮裁定：P4 引用完整性仍只在 C1 局部生效、P6 路径表示仍有扁平字符串双轨且缺目标 id；P1/P2/P3/P5 只部分解决；G-B1 判定列仍写“值在枚举内”、A.2 又划给 B2；原型 17 处 `null` 崩溃。据此重开 G-001–G-008，登记 G-009–G-017，ADR-0013 回到修订状态。 |
| 2026-11-14 | 追溯性修正：A.1.11-2、A.1.12-2、A.1.13-2、A.1.15-2 的悬空引用 | 这四个样例自 T-107 起一直带悬空引用：A.1.11-2 的章程指向未提供的 Outcome/Constraint/Actor/Assertion；A.1.12-2 的验收确认指向未提供的 Actor；A.1.13-2 的契约约束与签署指向未提供的 Constraint/Actor；A.1.15-2 的裁剪批准者指向未提供的 Actor。此前多次“34/34 通过”中包含这 4 条**未被发现的无效验证**。本轮按 schema §1.5（所有引用必须解析到同一快照）补齐输入块，4 个样例的期望输出均未改动。这不是新缺陷，是对既有绿色数字的追溯性降级：此前的 34/34 不能按“全部有效”引用。 |
| 2026-11-14 | 四层修订第一、二层（同源） | `run_case` 入口统一 null 归一化（顶层/嵌套/数组元素），`--null-sweep` 138/138 无崩溃；引用字段清单改由 schema §2bis 生成，补齐 `accountable_signature` 与 `assumption.approved_by`；§3 输入域与 `REQUIRED_KEYS` 同步，`--input-domain` 0 缺口；34/34、七检查器退出 0。**这是同源修订结果，不关闭任何缺口**；G-001–G-017 仍为 `open`，第三、四层完成后只重跑一次非同源复核。 |
| 2026-11-14 | 四层修订第三层（同源） | A 表改由 A.2 派生（7 列 + 子句指纹），`--write` 为唯一生成路径，默认模式逐格比较生成结果与提交内容；新增固定变异集脚本，11/11 变异抓到（子句语义 1、量词 1、原因码删除/篡改 2、枚举归属 2、承接规则 1、子句 id 1、severity 1、规则状态 1、子句删除 1），全部退出 1。样例基线锚定提交 `1a42b8b`（34 例，输入块 7 处改动、期望输出零改动），跨轮通过率可按基线横比。34/34、null-sweep 138/138、input-domain 0 缺口、三表退出 0。**同源结果，仍不关闭任何缺口**；G-001–G-017 保持 `open`。 |
| 2026-11-14 | 四层修订第四层（同源） | `subject_group_extension` 补 `relation ∈ {specializes, cross_cuts}` 与 `base`（须 ∈ 17 项基础枚举、`value` 不得重名），A.2 新增 `G-B2#2`，只写 `{value}` 被拒。悬空引用选“规则子句原因优先”：A.2 归属表固定 A2/C1/D1/E1/E2 的返回码，仅 C1#1、E2#1、E2#3 可返回 `dangling_reference`。`violations[]` 选择撤除，§1.14 与 `run_case` 输出一致。`G-A2#2` 通过 `commitments[]`/`deliverables[]` 的可选 `node_type` 变为可达（非法值 → `cannot_evaluate`/`undefined_object_type`）。负例逐项命中预期；34/34、null-sweep 138/138、input-domain 0 缺口、三表退出 0、变异 11/11、七检查器退出 0。**同源结果，仍不关闭任何缺口**；G-001–G-017 保持 `open`，待一次非同源复核。 |
| 2026-11-14 | A.2 签收纪律补漏（同源） | 新增 AGENTS 3.6.7、ADR 决策表 `A2-SIGNOFF`、A.2 区头“复核签收”行与 `check_three_table.py` 规则 8：只改 A.2 不更新签收 → 退出 1；改 A.2 并更新签收 → 通过。S01/S02 正负例固定于变异脚本。这是对派生检查绕过的补漏，不改变任何缺口状态；G-001–G-017 仍为 `open`。 |
| 2026-11-14 | 批次 0040：覆盖闸门上线（同源） | A.1 增补 23 个负例（34 → 57），A.2 与判定列未改；`scripts/check_coverage_gate.py` 登记 41 子句 × 正负例矩阵，N01–N03 三条负例全部阻断。本批次只补覆盖，不改判定语义；17 条缺口状态与核查矩阵不变。 |
| 2026-11-14 | 批次 0041：四道绑定上线（同源） | 检查器哈希 + `basis`、规格区段指纹 + 同批复核记录、验收快照漂移检测、ADR-0014；快照漂移检测明确不是权限分离（本机无 CI，做不到真正分离）。不改判定语义；17 条缺口仍为 `open`，核查矩阵不变。 |

## 临时性与撤除

本台账是过渡机制，不是永久治理结构。**撤除条件**（全部满足）：

1. 连续两个发布点，`python3 scripts/check_gap_ledger.py` 报告 `open=0`，且核查矩阵 17/17 为 `consistent`；
2. 第二个发布周期内没有新增缺口；
3. 裁定方完成一次全量“规则正文 ↔ 判定列”对照，确认无 `rule-stricter` 遗留。

**硬约束**：不晚于 M3 关闭前评估撤除；若 M3 关闭时仍有 `open` 缺口，机制冻结——新增缺口须经 ADR，所有 `open` 缺口必须在 M4 前裁定。

**撤除动作**：删除本文件与 `scripts/check_gap_ledger.py`；移除 `AGENTS.md` 3.6、7bis 的钩子项与 `check_state.py` 的调用；`TODO.md` T-132 标 `done` 并记 CHANGELOG。
