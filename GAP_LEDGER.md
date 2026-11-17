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
| `PROJECT_MINIMAL_EXISTENCE` | G-A1 | `G-002`、`G-007`、`G-008`、`G-009`、`G-014`、`G-016`、`G-017`、`G-019`、`G-020`、`G-021`、`G-023`、`G-024`、`G-025`、`G-026`、`G-027`、`G-028` | M1 |
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

> 矩阵说明：缺口编号替代 `consistent` 表示该 `check_id` 截至 2026-11-14 的复核仍受该缺口影响，不得判为一致。G-008 是表示层合并条目，G-010/G-011/G-012 等为其拆分后的可执行项；G-014、G-016、G-017 为全局项，锚定在首行。
> G-019 是仓库级“形态判据退役与准入制落地”，不归属单一 `check_id`，锚定首行；2026-11-15 按 r7 复判以 `check-change` 关闭。G-020 是仓库级“子模块、外部生成物与未登记路径的扫描范围”，锚定首行；文件枚举一半已不再保留，形态分类一半并入 G-019，边界见 G-020 说明。G-021 是仓库级内容层残余风险（`representation-defect`/L3，2026-11-15 按 r5 复判以 `accepted` 关闭），锚定首行；G-022 是依赖指纹的信任边界（`representation-defect`/L3，同批以 `accepted` 关闭并指向 ADR-0015 的外部承接），不并入 G-019。

> G-023/G-024/G-025 是 D6 验收侧在公开案例批次 0104–0105 暴露的运行时契约缺口（状态与挣值工件无币种字段、`due_day` 上限装不下长周期、风险类别闭集），不归属 A 表任一 `check_id`，按 G-014/G-016/G-017 的既有做法锚定首行；三者均 `open`，未改动受钉扎 schema 与检查器。G-026 是 D6 验收侧的模型档位口径缺口（本地权重口径已移出主档位、改走外部 API，本地线独立待定），同属仓库级、锚定首行。G-027/G-028 是 D6 验收侧在 S2 变体运行（批次 0109）暴露的**配置可观测性覆盖缺口**，均不归 A 表任一 `check_id`，同样锚定首行。G-027：CFG-03 无任何消费题与契约绑定；G-028：CFG-14 的分档标签无法观测，刻度尺寸现有题取值覆盖不到。

## 缺口账

| 编号 | 状态 | 成因 | 等级 | 影响面 | 是否阻断 | 待裁定方 | 登记里程碑 | 处置出口 | 关联 T | 说明 | 关闭依据 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| G-001 | closed | undefined-object | L3 | G-A2、G-D2、G-E1 | 否 | 架构负责人 | M1 | check-change | T-136 | 2026-11-14 复核重开：P2（封闭枚举）只部分解决——`subject_group` 仅物化 2/17 项，`management_node_type` 等枚举未覆盖判定列全部引用；原以 `check-change` 关闭的依据是同源重跑，不成立。剩余项由 G-013 承接。 2026-11-14 非同源复核（基线 `d8bf413`）：判 partly。残留：`subject_group` 17 项已物化，但判定列引用的其他枚举（`management_node_type`、`applicability.state`、`assumption.status`）尚未全部纳入统一枚举强制；本轮清单第 6 项承接，维持 open。 2026-11-14 非同源复核（基线 `9519b82`，报告 §三 G-001 行）：`management_items[].node_type` 非法值在 B1/B2 均判 `cannot_evaluate/undefined_enum_value`，`orthogonal_to` 正确 pass，`subject_group` 17/17；原残留已消，判 closed。新观察 `actors[].type=Bogus` 另登记为 G-018。 | 外部复核：/home/wgz/projects/skills/2026-11-14/pm-governance-review/verify-g014/REPORT_9519b82.md；sha256：791050d5062d6202afb877ba7508b43c9685b1ad03110d3296fd814031f446bf；基线：9519b82；报告章节：§三（G-001） |
| G-002 | closed | rule-stricter | L2 | G-A1 | 否 | 架构负责人 | M1 | check-change | T-130 | 2026-11-14 复核重开：P1（子句压缩）只部分解决——A 表判定列仍写叙述性短语，子句未完全下沉 A.2；原关闭依据是同源重跑，不成立。待 G-015/G-016 修正后由非同源复核关闭。 | 外部复核：/home/wgz/projects/skills/2026-11-14/pm-governance-review/verify-4812/REPORT_48128a8.md；sha256：d0f8275f9931f36da93c640ad8a070c8af7200929d0a4a685e5309268356c4e7；基线：48128a8 |
| G-003 | closed | rule-stricter | L2 | G-E2 | 否 | 架构负责人 | M1 | check-change | T-131 | 2026-11-14 复核重开：P1/P5 只部分解决——`assumption.pending` 分支未检查 `approved_by`，且路径仍与扁平字符串双轨；原关闭依据不成立。由 G-011/G-012 承接。 2026-11-14 非同源复核（基线 `d8bf413`）：判 partly。残留：`pending` 分支已补 `approved_by`，但 `delegated_from` 的扁平字符串兼容入口仍与路径对象双轨；本轮清单第 6/7 项只部分覆盖，维持 open。 2026-11-14 非同源复核（基线 `9519b82`，报告 §三 G-003 行）：`assertion.assumption={}` → `cannot_evaluate/missing_input`；端点 `AIActor` → `fail/accountable_not_human`；扁平 grant → `cannot_evaluate/invalid_path`；双轨与空对象残留已消，判 closed。 | 外部复核：/home/wgz/projects/skills/2026-11-14/pm-governance-review/verify-g014/REPORT_9519b82.md；sha256：791050d5062d6202afb877ba7508b43c9685b1ad03110d3296fd814031f446bf；基线：9519b82；报告章节：§三（G-003） |
| G-004 | closed | severity-mismatch | L1 | G-E1 | 否 | 架构负责人 | M1 | check-change | T-100 | 2026-11-14 复核重开：severity 拆分本身已落地，但 P1 表示层只部分解决，且判定列格式与原因码映射未定义，不能维持 `check-change` 关闭。由 G-015/G-016 承接。 2026-11-14 非同源复核（基线 `d8bf413`）：判此项已收敛。 | 外部复核：/home/wgz/projects/skills/2026-11-14/pm-governance-review/verify-4812/REPORT_48128a8.md；sha256：d0f8275f9931f36da93c640ad8a070c8af7200929d0a4a685e5309268356c4e7；基线：48128a8 |
| G-005 | closed | rule-stricter | L1 | G-C1 | 否 | 架构负责人 | M1 | check-change | T-134 | 2026-11-14 复核重开：C1 内容与 `about` 已纳入，但引用完整性只在 C1 局部生效（P4 未全局化），原关闭依据不成立。由 G-010 承接。 2026-11-14 非同源复核（基线 `d8bf413`）：判此项已收敛。 | 外部复核：/home/wgz/projects/skills/2026-11-14/pm-governance-review/verify-4812/REPORT_48128a8.md；sha256：d0f8275f9931f36da93c640ad8a070c8af7200929d0a4a685e5309268356c4e7；基线：48128a8 |
| G-006 | closed | rule-stricter | L1 | G-D1 | 否 | 架构负责人 | M1 | check-change | T-135 | 2026-11-14 复核重开：`target.type` 已纳入，但引用完整性未全局生效，且 `reason` 与聚合优先级矛盾未定稿。由 G-010/G-014 承接。 2026-11-14 非同源复核（基线 `d8bf413`）：判此项已收敛。 2026-11-14 证据措辞更正（报告 §二 G-006 行）：原报告“缺 constraint 均 fail”不成立；实测 `constraint=null` 走 `cannot_evaluate/missing_input`，用 `48128a8` 旧基线复跑同样如此，属原报告写错而非本次回归。按“非 pass”口径关闭仍成立，不改写批次 0043 历史记录，来由记于本条与批次 0046。 | 外部复核：/home/wgz/projects/skills/2026-11-14/pm-governance-review/verify-g014/REPORT_9519b82.md；sha256：791050d5062d6202afb877ba7508b43c9685b1ad03110d3296fd814031f446bf；基线：9519b82；报告章节：§二（G-006 证据措辞更正） |
| G-007 | closed | undefined-object | L1 | G-A1、G-A2、G-C1、G-D1 | 否 | 架构负责人 | M1 | check-change | T-136 | 2026-11-14 复核重开：P2/P3/P4/P5 只部分解决——引用完整性仅 C1、路径表示缺目标 id 且与扁平字符串双轨、`assumption.pending` 未校验批准者、17 处 `null` 崩溃。由 G-009–G-012 承接。 2026-11-14 非同源复核（基线 `d8bf413`）：判 partly。残留：顶层 `null` 已归一化，但嵌套对象缺键与封闭枚举尚未全局强制；本轮清单第 5/6 项承接，修后仍待非同源复核，维持 open。 2026-11-14 非同源复核（基线 `9519b82`，报告 §三 G-007 行）：`status` 缺失、仅 `{status}`、`{}` 三者均 `cannot_evaluate/missing_input`（`G-D2#3`），嵌套缺 id 亦 `cannot`；残留已消，判 closed。 | 外部复核：/home/wgz/projects/skills/2026-11-14/pm-governance-review/verify-g014/REPORT_9519b82.md；sha256：791050d5062d6202afb877ba7508b43c9685b1ad03110d3296fd814031f446bf；基线：9519b82；报告章节：§三（G-007） |
| G-008 | closed | representation-defect | L2 | 表示层（全局） | 否 | 架构负责人 | M1 | check-change | T-133 | 2026-11-14 复核重开：P1–P8 的合并条目中，P4（引用完整性）、P6（路径表示）未解决，P1/P2/P3/P5 只部分解决；上一轮以 `check-change` 全部关闭的裁定被非同源复核推翻。 2026-11-14 非同源复核（基线 `d8bf413`）：判 partly。残留：P4（引用完整性）已全局化，P6（路径表示）已统一；覆盖矩阵已绑定，但“覆盖 ≠ 充分”的结构风险仍在，维持 open。 2026-11-14 非同源复核（基线 `9519b82`，报告 §三 G-008 行）：覆盖闸门已把 `expected_failed_clauses: []` 直接判错，不再算负例，闸门 0；通道已堵，判 closed。方法论残留“覆盖 ≠ 充分”仍由复核负责，已不是可复现缺陷。 | 外部复核：/home/wgz/projects/skills/2026-11-14/pm-governance-review/verify-g014/REPORT_9519b82.md；sha256：791050d5062d6202afb877ba7508b43c9685b1ad03110d3296fd814031f446bf；基线：9519b82；报告章节：§三（G-008） |
| G-009 | closed | implementation-defect | L1 | 全部 17 个 `check_id` | 否 | 架构负责人 | M1 | check-change | T-133 | 原型对必需顶层键只判 `key not in data`；键存在但值为 `null` 时进入迭代并抛 `TypeError`（17 处 check 函数同一缺陷）。按 schema §1.2/§1.3 应输出 `cannot_evaluate` / `missing_input`。 本次已修正：入口 `evaluate()` 同时拦截“键不存在”与“值为 `null`”，不依赖 check 内守卫；`--missing-key-sweep` 43/43 返回 `cannot_evaluate/missing_input`（偏离 0）、`--null-sweep` 138/138（崩溃 0），对照实验 `{}` 直入 check 仍 17/17 抛 `KeyError`。 | 外部复核：/home/wgz/projects/skills/2026-11-14/pm-governance-review/verify-4812/REPORT_48128a8.md；sha256：d0f8275f9931f36da93c640ad8a070c8af7200929d0a4a685e5309268356c4e7；基线：48128a8 |
| G-010 | closed | representation-defect | L1 | 全部引用字段；重点 G-C1 之外 | 否 | 架构负责人 | M1 | check-change | T-133 | 引用完整性（P4）只在 `DELIVERABLE_ASSERTION_LINK` 与 `AI_AUTONOMY_DELEGATION_AUDITABLE` 局部实现；`commitments.by/to`、`constraints.constrains`、`changes.target.id`、`charters.project` 等悬空引用未统一报 `dangling_reference`。本次已把全局校验扩展到上述字段、`contracts.constrained_by/accountable_signature`、`tailoring_records.approver`、`assertions.about/deliverable/subject/accountable_confirmation`；A.1.11-2、A.1.12-2、A.1.13-2、A.1.15-2 的输入已按 schema §1.5 补齐，期望输出未变。 | 外部复核：/home/wgz/projects/skills/2026-11-14/pm-governance-review/verify-4812/REPORT_48128a8.md；sha256：d0f8275f9931f36da93c640ad8a070c8af7200929d0a4a685e5309268356c4e7；基线：48128a8；caveat：F1.charter.project→missing_charter；E2.assertions→assertion_incomplete |
| G-011 | closed | representation-defect | L1 | G-D2、G-E2 | 否 | 架构负责人 | M1 | check-change | T-133 | `assumption` 的 `pending` 分支只检查 `expired`，未检查 `approved_by`；schema §1.9 要求 `pending` 且缺 `approved_by` → `cannot_evaluate` / `assumption_unclosed`。 本次已修正：D2/E2 的 pending 分支均检查 `approved_by`。 | 外部复核：/home/wgz/projects/skills/2026-11-14/pm-governance-review/verify-4812/REPORT_48128a8.md；sha256：d0f8275f9931f36da93c640ad8a070c8af7200929d0a4a685e5309268356c4e7；基线：48128a8 |
| G-012 | closed | representation-defect | L2 | G-E2、schema §1.10/§3bis | 否 | 架构负责人 | M1 | check-change | T-133 | 路径结构 `{start, steps, reach}` 的 `steps[]` 缺目标 `id`，无法定位下一节点；同时 schema 保留 `delegated_from` 扁平字符串写法，形成双轨。 本次已修正：路径对象补 `steps[].target_id`，扁平字符串返回 invalid_path。 | 外部复核：/home/wgz/projects/skills/2026-11-14/pm-governance-review/verify-4812/REPORT_48128a8.md；sha256：d0f8275f9931f36da93c640ad8a070c8af7200929d0a4a685e5309268356c4e7；基线：48128a8 |
| G-013 | closed | representation-defect | L1 | G-B1、G-B2 | 否 | 架构负责人 | M1 | check-change | T-133 | `subject_group` 只物化 `planning`、`lessons-learned` 两项；ISO 21502:2020 第 7 章的 17 项管理实践未完整物化，合法标签会被判 `dimension_value_out_of_enum`。 本次已修正：17 项完整物化，原型同步。 | 外部复核：/home/wgz/projects/skills/2026-11-14/pm-governance-review/verify-4812/REPORT_48128a8.md；sha256：d0f8275f9931f36da93c640ad8a070c8af7200929d0a4a685e5309268356c4e7；基线：48128a8 |
| G-014 | closed | representation-defect | L1 | 全部 `check_id` 的 verdict/reason 聚合 | 否 | 架构负责人 | M1 | check-change | T-133 | schema §1.14 规定 `reason` 优先级 `cannot_evaluate > fail`，A.2 又规定 verdict 聚合“任一 `fail` → `fail`，否则 `cannot_evaluate`”；两处对“同时存在 fail 与 cannot_evaluate”的结论相反。 本次已修正：§1.14 与 A.2 统一为 fail > cannot_evaluate > pass；17 个 check 改为返回子句级结果列表，由 `aggregate()` 顺序无关聚合（verdict 取最高级、reason 按 A.2 行序、severity 取胜出子句最高级）。证据：A2/E2 各 6 种排列均收敛为 1 个结论（A2 = fail/unanchored_management_item，E2 = fail/delegation_chain_not_accountable），34/34 不变。 2026-11-14 复核基线 `48128a8`：原关闭依据（转录件与同源重跑）失效，重开；入口枚举短路已改为参与 `aggregate()`，修后仍需外部复核才能关闭。 2026-11-14 非同源复核（基线 `9519b82`，报告 §一）：四组场景（枚举+unanchored、枚举+真 fail、三 verdict 混合、E2 端点+缺 status）全排列顺序无关、唯一收敛到 `fail`；`failed_clauses()` 同时可见 `G-A2#1`/`G-A2#2`；无关子句 G-A1#1、G-C1#1、G-D1#2、G-E1#1、G-G1#1 各自 fail/cannot 正常，未被牵连；判 closed。 | 外部复核：/home/wgz/projects/skills/2026-11-14/pm-governance-review/verify-g014/REPORT_9519b82.md；sha256：791050d5062d6202afb877ba7508b43c9685b1ad03110d3296fd814031f446bf；基线：9519b82；报告章节：§一（G-014） |
| G-015 | closed | representation-defect | L2 | 附录 A 判定列 | 否 | 架构负责人 | M1 | check-change | T-133 | A 表“判定”列仍写叙述性短语（如 G-B1 写“且值在枚举内”），子句 id 只在“子句”列；同一条件又划给 B2，造成 B1/B2 口径冲突。 本次已修正：A 表判定列只留子句 id，叙述下沉 A.2；B1/B2 条件归属已分离。 | 外部复核：/home/wgz/projects/skills/2026-11-14/pm-governance-review/verify-4812/REPORT_48128a8.md；sha256：d0f8275f9931f36da93c640ad8a070c8af7200929d0a4a685e5309268356c4e7；基线：48128a8 |
| G-016 | closed | representation-defect | L2 | 附录 A.2、schema §3 | 否 | 架构负责人 | M1 | check-change | T-133 | A.2 子句表无“原因码”列；原因码与实际子句的映射未定义，`reason` 只能靠原型实现反向推断。 本次已修正：A.2 增加原因码列（41 条子句，不是 40 条），A 表原因码与子句原因码集合机械一致。 2026-11-14 更正：共用原因码组为 **6 组**（B1、C2、E2 两处、F2、G3），不是 7 组。 | 外部复核：/home/wgz/projects/skills/2026-11-14/pm-governance-review/verify-4812/REPORT_48128a8.md；sha256：d0f8275f9931f36da93c640ad8a070c8af7200929d0a4a685e5309268356c4e7；基线：48128a8 |
| G-017 | open | implementation-defect | L2 | `scripts/check_three_table.py`、M2 出口 1 | 否 | 架构负责人 | M1 |  | T-133 | 三表检查器只做存在性/集合一致/词级定义，不做语义短语检查：G-B1 判定列写“值在枚举内”与 A.2 划给 B2 的冲突仍报通过，绿字被误读为语义闭合。 本次已修正：三表检查器增加判定列叙述检测、B1/B2 条件归属、原因码定义与映射检查；仍不保证全文语义等价， 2026-11-14 非同源复核（基线 `d8bf413`）：判 partly。残留：三表检查器可抓判定列叙述、B1/B2 归属与原因码映射，但仍不保证规则正文与子句表的全文语义等价；该残留只能由非同源复核承接，维持 open。 2026-11-14 非同源复核（基线 `9519b82`，报告 §三 G-017 行）：三表与规格闸门均 0，仍无全文语义等价机器证明，维持 open。 |  |
| G-018 | closed | representation-defect | L1 | 全部含 `actors[]` 的 `check_id`；重点 G-A1、G-E1、G-E2 | 否 | 架构负责人 | M1 | check-change | T-137 | 2026-11-14 复核发现：`actors[].type=Bogus` 仍判 `pass`。`CHECKER_INPUT_SCHEMA.md` §2 已把 `actor_type` 声明为枚举，但 §1.11 的封闭枚举全局归一化未列 `actor_type`，原型 `enum_results()` 亦未校验。合法值应限 §2 枚举，非法值应判 `cannot_evaluate/undefined_enum_value`，不得 `pass`。建议处置出口 `check-change`（改 §1.11 与 `enum_results()`，加负例）。**2026-11-15 批次 0071 按 `check-change` 实施（状态仍 `open`，等非同源复核关闭）**：`CHECKER_INPUT_SCHEMA.md` §1.11 增列 `actors[].type`，写明必填与三个出口（键缺失 → 子句级 `missing_input`；值为 `null` → 入口 `missing_input`；非法值、大小写变体、空字符串 → 子句级 `undefined_enum_value`）及子句归属；§2 同步必填性，§3 三行补 `undefined_enum_value`，§4 新增 `actor_type` 具名枚举。原型 `enum_results()` 对每个 `actors[]` 元素校验 `type`，结果带 `G-A1#1` / `G-E1#1` / `G-E2#1`（其余 `check_id` 无子句）并参与 `aggregate()`，未做入口短路；`ROLE_MINIMAL_COMPLETENESS` 与 `AI_AUTONOMY_DELEGATION_AUDITABLE` 不再用未定义类型推导 `accountable_not_human`，避免 `fail` 盖掉 `cannot_evaluate`。负例新增 A.1.1-8（非法值）、A.1.1-9（大小写变体）、A.1.1-10（空字符串）、A.1.5-5（缺失键）、A.1.10-6（`null`），覆盖矩阵对应 5 条；`--enum-sweep` 4 → 5 项，A.1 样例 61 → 66。**批次 0072 按复核报告（基线 `0b88547`）修复**：`enum_results()` 用 `isinstance(value, str)` 守卫，对象、数组、数字、布尔等非字符串 `type` 一律给子句级 `undefined_enum_value`，不再抛 `TypeError`；A.2 为 `G-A1#1`/`G-E1#1`/`G-E2#1` 补 `undefined_enum_value`，并新增 `PROJECT_CHARTER_EXISTENCE` → `G-F1#2` 的 F 类归属，A 表由 `check_three_table.py --write` 重建，`clause_of()` 对四个归属均返回正确子句；`failed_clauses()` 在必需顶层键缺失或为 `null` 时返回空集，不再抛 `KeyError`；覆盖闸门 note 改为实际检查项，并写明 A.1.10-6 走入口归一化、其子句归属只用于取证。新增对象型 A.1.1-11 与数组型 A.1.11-4 两条负例，样例 66 → 68、负例 47 → 49。`spec-pins`/`checker-pins` 本批按裁定重冻，basis 指向该报告并显式标注“覆盖范围缺失：未审查本批修复，仅作指纹登记”。状态仍 `open`，等针对修复提交的非同源复核。**批次 0073 按 r2 报告（基线 `ea9b674`）整改（状态仍 `open`）**：① `missing_input` 子句级出口补齐——A.2 的 `G-A1#1`/`G-E1#1`/`G-E2#1` 原因码列增列 `missing_input`，子句条件写明 `type` 必填、键缺失按 §1.11 判定；schema §3 三行同步，A 表由 `--write` 重建，`clause_of()` 对三者返回正确子句。② 撤回 `G-F1#2` 归属：`PROJECT_CHARTER_EXISTENCE` 不承接“任意 actor 类型合法”，A.2 该行、schema §3、§1.11 归属同步复原；F 类数组型样例 A.1.11-4 移入覆盖矩阵新增的 `global_normalization` 分区，不再挂子句；不补 ADR（撤回即恢复原判定逻辑）。③ 覆盖闸门规则 6 语义变更：从“每条样例必须被至少一个子句引用”改为“被子句或 `global_normalization` 分区之一引用”；新增生产 `evaluate_trace()` 取证，子句负例必须 verdict/reason 与子句归属均命中声明，并核对样例 reason 已登记在 A.2 该子句原因码列；删除 `failed_clauses()` 这条绕过入口归一化的取证路径。该变更只改验证工具、不改任何 `check_id` 判定逻辑，按方法 §9 不需要 ADR。④ **更正 0072 记述**：F 类 `G-F1#2` 归属是本批自行扩展，既不属复核“阻断项 1”（对象/数组崩溃），也不属“阻断项 2（A.2 未同步）”，已撤回。**2026-11-15 r3 非同源复核（基线 `a9ff5bb`）判可关闭**：上一轮两条阻断项均已消除，`missing_input` 五处一致、`G-F1#2` 归属已撤回、覆盖闸门以生产 `evaluate_trace()` 取证；两条 caveat 一并记录——① `global_normalization` 分区只核对 verdict/reason 与 `expected_clause: null`，不限制无子句原因码集合；② `G-A1#1`/`G-E2#1` 的 `missing_input` 无专用样例，该分支由 A.1.5-5 间接守卫（删掉键缺失分支会被闸门阻断，但仅 A1/E2 的原因码标注错误这类局部回归无法被样例发现）。 | 外部复核：/home/wgz/projects/skills/2026-11-14/pm-governance-review/verify-g018-r3/REPORT.md；sha256：2ce8107766068643d83a94bbbe1844c2c415d6e6c4f39f059f8a8851419602c6；基线：a9ff5bb；报告章节：§一（守卫与四条路径）、§二（闸门与五处一致）、§三（测试约束力）；caveat：global_normalization 不限制无子句原因码集合；G-A1#1/G-E2#1 的 missing_input 无专用样例（分支由 A.1.5-5 间接守卫） |
| G-019 | closed | implementation-defect | L1 | 原始资料防线：形态判据（已退役）与分区准入实现；`scripts/check_no_raw_material.py`、`scripts/check_spec_pins.py`、`spec/ACCESS_ZONES.md`、`contracts/schema/` 全部 schema | 否 | 架构负责人 | M1 | check-change | T-140、T-144 | 形态判据退役与准入制落地。2026-11-14 试点发现 `RM-PROSEBLOCK` 把连续 ≥15 行、每行 ≥100 字符的结构化 JSONL 判为文本层转储；批次 0049 收窄为“每行一个 JSON 对象”豁免，批次 0050 按外部复核补值级上限、键白名单、base64、魔数与段落判据，仍被 r2 复核（基线 `58641d0`）证明双向失准且不收敛：整页单条 0 命中、390 字符切块 0 命中、`RM-PAGEDUMP` 真实召回 4/15、合法 450–1500 字符定义被误杀、中文正文页 0 命中。批次 0051 出换轴方案；用户 2026-11-15 批准全部 10 条 D 项。批次 0052 修订 `CONSTITUTION.md` 13.3/13.5 并将 ADR-0018 转 `accepted`；批次 0053 新增 `spec/ACCESS_ZONES.md` 与 2 份 schema，重写检查器为“归区 + 硬约束 + schema”，删除 `RM-PROSEBLOCK`/`RM-PAGEDUMP`/`RM-PAGESEQ`，新增 `RM-ZONE`/`RM-SCHEMA`/`RM-FIELD`，自测按新轴重建为 30 项；批次 0054 全仓 138 个跟踪文件一次过检 0 违规，D-6 收敛为不设豁免期。**2026-11-15 r2 复核（基线 `deaac46`）**：旧判据退役与负例新轴成立，但“新准入生效”只部分成立——13/18 个数据区文件不受内容 schema 或字段配额约束，schema 本身另有键空间、集合长度与配额矛盾孔隙；同批复核另判第 5 条程序未闭合、13.5 裁定句回避。批次 0056 补全受影响对象并改写裁定句为“承认降低、显式接受”；批次 0057 为 5 个人工维护文件补内容 schema、收紧 `relations`/`evidence`/`claim_mapping`、统一单条配额 2800、落地 13.6 三项检查、把归区表纳入 `spec-pins`。数据区现为 22 个文件：10 个受内容 schema 约束、7 个 schema 自身、5 个生成器。**r3 复核后结构性修法（批次 0059–0061，基线 `3664b64`）**：批次 0059 把规格钉扎改为目录自动发现——`contracts/schema/` 下任一文件未登记为区段即阻断，4 份漏钉 schema 由自动发现兜住，`basis` 抬到与检查器绑定同一标准（仓库外产物 + 64 位 sha256 + 基线）；批次 0060 新增 `RM-SCHEMA-LINT`，对全部 schema 强制数组 `maxItems`+`items`、字符串 `maxLength`、对象 `additionalProperties: false`（或 `maxProperties`+`propertyNames` 映射），建关键字白名单与未实现关键字集合（白名单外与 `patternProperties` 等未实现关键字直接失败），`oneOf` 改为恰好命中 1 个分支、`$ref` 同级断言关键字显式拒绝；配额由整条求和改为 `x-prose-fields` 逐路径 + `x-prose-budget` 单条总和兜底，`pilot-conflicts` 的 `positions`/`recorded_fields` 加 `maxItems: 40`；批次 0061 按真实 TTL 形态重写 `RM-ONTO-PAGESEQ`/`RM-ONTO-PROVENANCE`，真实 TTL 5 文件、349 个页码值、501 个义务块 0 命中，299 行三元组转储与“两项都缺”术语均命中（统计见 `spec/ACCESS_ZONES.md` 第 6 节）。自测 43 → 58 项，覆盖 r3 全部攻击输入（`positions` 300×400、`recorded_fields` 200×120、3 条假设契约、12 条 `notes` 的 id-map、`package-manifest` 削弱为 `additionalProperties: true` 应失败）；批次 0063 收紧 `source_pages: n/a`：声明 `n/a` 必须附 `source_pages_basis:`（非空、非占位符、含仓库内真实存在的 ADR 引用与自写理由），缺项由 `RM-ONTO-HEADER` 阻断、不可核验由 `RM-ONTO-PROVENANCE` 阻断且不解除页码义务，两份标 `n/a` 的 TTL 已补齐依据，自测 65 项。**r4 复核后换用成熟实现（批次 0064–0066，基线 `11c5d92`）**：批次 0064 选定 `jsonschema==4.26.0` 并登记分发产物 sha256（`d489f15263b8d200f8387e64b4c3a75f06629559fb73deb8fdfb525f2dab50ce`）与安装树摘要（`scripts/dependency-pins.json`），新增 ADR-0019；批次 0065 用库替换自写 `validate()` 而输出契约不变（仍走 `RM-SCHEMA` 等 reason code，消息带文件与 JSON 指针，退出码保持），schema 自身过官方元 schema，`x-prose-fields` 路径按 schema 结构严格解析（拼错即报错）、`contracts/schema/` 自动发现改递归、依赖缺失 fail-closed，自测 65 → 76 项；批次 0066 用 r4 四类攻击面逐项确认（`items: true`/元组、`enum`/`const` 跳过 `maxLength`、散文路径拼错静默失效、`contracts/schema/sub/` 逃过 lint 与钉扎），并修正 G-021 口径（见该条）。**r5 复核（基线 `3d7211c`）与批次 0067–0068**：r5 确认 r4 四类缺陷已由结构消除，但列出四项仍成立的问题：① 校验语义可被本机路径静默替换——`PYTHONPATH`、`sitecustomize`、改安装树保留 `RECORD` 三种方式下 `check_dependency_pins.py` 仍退 0；② 输出契约并非未变——`additionalProperties` 与 `propertyNames` 的指针丢失具体键；③ 缺失本地 `$ref` 抛未捕获的 `_WrappedReferencingError`，不是 `RM-SCHEMA`；④ schema 自身可造成灾难性 `pattern` 回溯与 1500 层嵌套 `RecursionError`。**本轮已修**：批次 0067 让分发产物核对真正执行（wheel 置于仓库外持久目录，`DP-ARTIFACT` 缺失按“无法评估”退出 2，负例 10 项）；批次 0068 把依赖核对改为按 wheel 内 `RECORD` **逐文件重算内容哈希**核对实际安装树，并断言 `jsonschema.__file__` 落在分发目录内（`DP-IMPORT`），上述三种非针对性替换与同名假 wheel 均阻断（负例 13 项）；指针恢复 `$.x`、`$.a.x`、`$.m.<键>`，消息口径统一为“指针由本仓库恢复、文本取自库的英文诊断”并写入 ADR-0019 与 README；缺失本地 `$ref` 转 `RM-SCHEMA`；`pattern` 512 字符上限（当时另含嵌套量词启发式，r6 已撤）、schema 嵌套 64 层上限，`RecursionError` 捕获为带 reason code 与指针的失败；新增运行时行为探测，空实现校验器 fail-closed；自测 76 → 82 项。**残留**：有权写本机 Python 环境者仍可同时改写安装树、wheel 与登记表，逐文件哈希只能提高干扰成本、不构成防护——按用户裁定移出威胁模型，由 G-022 承接（与 ADR-0015 同一信任模型），不由本条关闭覆盖。**r6 复核（基线 `bafcb04`）与批次 0069**：r6 判本条只剩三处口径对齐，均在本轮修完——① **撤掉 `pattern` 的嵌套量词启发式，只保留 512 字符上限**：schema 是仓库自写的可信资产、不是外部输入，正则回溯不在威胁模型内，该结论已写入 ADR-0019 威胁模型一节，文档不再保留“已用启发式覆盖”的说法；实测该启发式误拒 4 个合法常见写法（官方 semver 正则 179 字符、dotted-id、dotted-version、list-of-pairs，均由 `(?:\.\w+)*` 类“分隔符 + 段 + 重复”触发），又漏拒 `a`/`aa` 交替重复这类真正呈指数行为的写法，撤除后 5 个写法全部放行；依赖它的负例已删除并改写为“常见写法放行 + 只按长度拒绝”，自测 82 → 83 项。② **退出码表述与实现对齐**：`jsonschema` 导入失败才退出 2；导入成功但运行时探测失败是逐文件 24 条 `RM-SCHEMA`/`RM-SCHEMA-LINT` 后退出 1，`scripts/README.md` 与 ADR-0019 的“不改变失败方向”已按此改写。③ **替换范围表述与实测对齐**：`sitecustomize` 只替换 `validator_for`、保留 `Draft202012Validator` 时不阻断，属 G-022 声明的信任边界（有权写本机 Python 环境者的针对性替换），故“三种替换均阻断”改为“非针对性替换均阻断”。剩余项：r6 三处已完成；r7 另有一处退出码文档缺口（分发产物存在但不可读取/逐文件数据不可核对应退 2，README、ADR-0019 与 `check_dependency_pins.py` docstring 均未列），已同批勘误。**r7 复判（基线 `7300283`）与批次 0070**：r7 确认 `pattern` 撤除干净、无回归（5 个指定写法全部放行、512 通过 / 513 拒绝、代码无 `NESTED_QUANTIFIER_RE` 或死分支、自测无空壳、ADR 威胁模型一节与裁定一致）；退出码实测矩阵六种情形全部与实现一致，仅文档少列“不可读产物退 2”一种，已补入 `scripts/README.md`、ADR-0019 两处与 `check_dependency_pins.py` docstring。按 3.6.6 以 r7 报告 §1、§2、§4 关闭：旧判据退役、新准入覆盖全部数据区文件、负例不依赖退役启发式、无静默降级均由本轮证据支撑。 | 外部复核：/home/wgz/projects/skills/2026-11-14/pm-governance-review/verify-g019-r7/REPORT.md；sha256：65e319da5b5e3a511b5d8dbf6b3f45f1ddbc9f86e8a4a86c17b4121cea20dacb；基线：7300283；报告章节：§1（pattern 撤除）、§2（退出码）、§4（裁定） |
| G-020 | closed | representation-defect | L1 | 第 13 条防线的覆盖范围与准入口径：子模块、外部生成物、未登记路径；`scripts/check_no_raw_material.py` 的 `git ls-files` 枚举面 | 否 | 架构负责人 | M1 | accepted | T-142、T-144 | 子模块、外部生成物与未登记路径的扫描范围。2026-11-15 批次 0050 登记时包含“文件枚举”与“形态分类”两半；批次 0053 换轴后按以下口径收敛：① **文件枚举一半不再保留**——未知扩展名与魔数改名已由批次 0050 的 `RM-MAGIC`/`RM-BINARY`/fail-closed 覆盖，不再是独立缺口；② **形态分类一半并入 G-019**——准入形态由 `spec/ACCESS_ZONES.md` 与 schema 决定，退役判据与准入实现统一在 G-019 复核；③ 本条只保留扫描范围：`git ls-files` 之外的未跟踪文件（由 `.gitignore` 与提交纪律承接）、外部生成物、子模块。**D-8 子模块口径**：按“显式声明不纳入”处理——本期防线不扫描子模块内容；当前仓库实测 0 个 gitlink、无 `.gitmodules`，该声明是口径预留而非现存盲区，若将来引入子模块须在本条与 `spec/ACCESS_ZONES.md` 同批重新裁定。**D-7 外部指纹**：方向为仓库外常驻的来源指纹比对，与 ADR-0015 同批外置，承接方与时点见 T-145。批次 0058 把 gitlink、符号链接与缺失路径在检查器中显式判为 `RM-ZONE`，使“声明式排除”机械可见。**理由**：复核确认拆分成立、剩余范围表述完整，未跟踪文件、外部生成物与子模块均属经批准的声明式排除，不存在可复现的漏扫缺陷；据此按 `accepted` 关闭。**关闭备注（必须同时成立）**：① 子模块不纳入是**声明式排除**，不是“已扫描无违规”；② 引入子模块时必须在 `spec/ACCESS_ZONES.md` 与本台账同批重新裁定；③ 现状事实为 0 gitlink、无 `.gitmodules`，可复算。本报告不构成 G-019/G-021 的关闭依据。 | 外部复核：/home/wgz/projects/skills/2026-11-14/pm-governance-review/verify-admission/REPORT.md；sha256：905cf234539cccb916f9096e3e137f12876e24b2fb9c1960a034157ac33aff06；基线：deaac46；报告章节：§6（G-020） |
| G-021 | closed | representation-defect | L3 | 散文区与数据区 `x-prose-fields` / `x-prose-budget` 的内容层原创性；`CONSTITUTION.md` 13.3 第 5 项承接的残余风险 | 否 | 架构负责人 | M1 | accepted | T-145 | 2026-11-15 批次 0055 按 D-10 登记，批次 0058 按 r2 复核改写，批次 0062 按 r3 复核改为真实量级，批次 0066 按 r4 复核（基线 `11c5d92`）以实测口径重写并更正 0062 的错误表述。**已剥离的可修缺陷（不属于本条）**：`relations` 键空间无白名单、`evidence`/`claim_mapping` 无上限、配额 2500 与 2800 矛盾——批次 0057 已修（键白名单 + `maxProperties`、`maxItems`、配额统一）；schema 静默降级与漏钉（`oneOf` 当 `anyOf`、`$ref` 忽略同级、4 份 schema 未入指纹、`items: true` 与元组 `items`、`enum`/`const` 跳过 `maxLength`、散文路径拼错静默失效、`contracts/schema/sub/` 逃过 lint 与钉扎）——批次 0059–0066 已修（自动发现并递归、关键字白名单、`oneOf` 排他、`$ref` 同级拒绝、官方元 schema、成熟校验器、路径严格解析）。**本条只保留真正不可机械化的残余**：散文区正文与 `x-prose-fields` 内的“改写、翻译、合理切块”是否实质替代原作，仓库内无判据可断。**实测口径（r4 按 schema 上限求和，非实存量；批次 0066 更正）**：批次 0062 写的“`relations`/`evidence`/`positions` 均计入总量口径”与实测相反——`relations` 上限 28,800（12 键 × 20 值 × 120 字符）与 `evidence` 上限 9,120（12 条 × 约 760 字符）**不在任何 `x-prose-fields`**，`claim_mapping` 2,400 同样未计入；`positions[].stance` 的单值路径上限是 2,400 字符（每个值的上限，不是预算；同段 16,800 才是 `pilot-conflict` 的单条总和预算，两者不是同一口径）、`recorded_fields` 4,800 未登记；`pilot-id-map` 的 12 条 `notes`（4,800）与 `rule_bindings.*.note`（20 × 800 = 16,000）由路径上限与预算兜底。按各 schema 的字符串总容量减去计入额（批次 0065 把预算抬到 schema 合法上限后的值）：knowledge-entry 45,136 − 2,800 = 42,336；pm-slot-contract 69,060 − 28,000 = 41,060；pilot-conflict 27,240 − 16,800 = 10,440；pilot-id-map 329,910 − 22,200 = 307,710；pilot-artifact 82,165 − 0 = 82,165；ontology-fixtures-manifest 40,800 − 0 = 40,800；package-manifest 791 − 0 = 791。这些未计入字符串仍受单字段 `maxLength` 与单文件 512 KiB 约束，但不受散文配额约束，“通过检查”只证明结构合规。**8 条未登记通道（r4 §3.2/§3.5，逐条）**：① `pilot-id-map.entries`/`reverse_rule_index`——40 条，仅 `candidate_iri_reason` 即 16,000，整条 0 命中；② `pilot-artifact.clauses`——200 条、正文总量 103,126 字节，该 schema 无 `x-prose-fields`，单文件散文上限不生效；③ `ontology/fixtures/manifest.json`——40,800，无散文配额；④ 跨文件拆分——`contracts/examples/` 10 个文件各 2,800，无跨文件总量；⑤ 键名散文——`reverse_index` 60 个 101 字符键 = 6,060（容量上界 12,000），不计入；⑥ 无魔数的 base64 正文——15 段 × 120 字符，每段 < 256 且解码后无魔数，0 命中；⑦ `schema-doc` 形态——schema 自身的 `description` 文本不经数据配额（批次 0065 起 `schema-doc` 也过 lint 与官方元 schema，但内容层仍无配额）；⑧ 13.6.5 的文件头替代——文件头 `source_id`/`source_pages` 统一声明可替代术语级来源，声明本身不校验内容原创性。**反向误杀处置（r4 §3.3，批次 0065）**：Q04（20 条假设合计 28,000）与 Q06（8 条 `positions` 合计 3,200）被“路径上限按整条合并”拦下——已改为按出现值分别计量，`x-prose-budget` 上调至 schema 合法上限（pm-slot 28,000、pilot-conflict 16,800、pilot-id-map 22,200），单文件上限由 20 KiB 提到 32 KiB；20 条假设、8 条 `positions`、12 条 `notes`（6,200）、id-map 6,200 均放行，`positions` 300×400 与 `recorded_fields` 200×120 仍被拦（自测 76 项）。成因记 `representation-defect`、等级 L3：不是某条规则的条件缺失，而是表示层对“来源原创性”的表达缺失。**D-7**：承接方为外部指纹（维护方，M4 来源收口前）与人工评审（人类责任方，来源/知识/规则变更同批），降级方式见 T-145；与 ADR-0015 同批外置。**处置出口 `accepted`（2026-11-15 按 r5 复判关闭）**：接受“仓库内不做来源层判定”。**理由：**本条剩余部分不可机械化——散文区正文与 `x-prose-fields` 内的改写、翻译、合理切块是否实质替代原作，仓库内没有判据可断；r5 复算确认七项容量差额与 8 条通道逐项吻合、反向误杀已放行而超限仍被拦，可修部分已在此前批次剥离，继续挂 `open` 只会把“无法机械判定”误表示为“待修代码缺陷”。**批准依据：**用户 2026-11-15 定“收紧威胁模型 + 修可机械修的部分”，并指示按复核条件以 `accepted` 关闭本条（依据见右列）。**承接方与时点：**外部指纹（维护方）在 M4 来源收口前、不晚于 M4 关闭；人工评审（人类责任方）在 `SOURCE_LEDGER` 变更、`knowledge/` 批量新增、规则或裁定修订的同一批次；降级方式见 T-145，与 ADR-0015 同批外置。 | 外部复核：/home/wgz/projects/skills/2026-11-14/pm-governance-review/verify-g019-r5/REPORT.md；sha256：5373a537d05870dcf4f52756bf7e0012bc0128879e22df92cb85d86007258108；基线：3d7211c；报告章节：§4（G-021）、§5.2 |
| G-022 | closed | representation-defect | L3 | 依赖指纹与校验层的信任边界；`scripts/check_dependency_pins.py`、`scripts/dependency-pins.json`、`adr/0019-mature-json-schema-validator.md` | 否 | 架构负责人 | M1 | accepted | T-146 | 依赖指纹的信任边界，2026-11-15 按 r5 复核 §2.1 单列登记（不并入 G-019）。**成因**：`check_dependency_pins.py` 核对的全部对象——wheel 的 sha256、安装树逐文件内容哈希、导入路径与登记表——都在同一台机器、同一权限域内；r5 实测 `PYTHONPATH` 注入、`sitecustomize`、改安装树保留 `RECORD` 三种方式可让实际运行的校验器变为空实现。**本轮已做**：批次 0068 将核对改为按 wheel 内 `RECORD` 逐文件重算内容哈希、断言 `jsonschema.__file__` 落在分发目录内，并加运行时行为探测；非针对性替换与同名假 wheel 均被阻断（负例 13 项），但这只提高干扰成本。**影响**：能发现误装、版本漂移、安装树被改动与非针对性运行时替换；**不构成对有权写本机 Python 环境者的防护**——同时改写安装树、wheel 与 `scripts/dependency-pins.json` 可保持一致，指纹不是签名，登记表没有外部锚点。**理由：**与 ADR-0015 同一信任模型——本机无 CI、无受保护分支，权限分离只能在仓库外基础设施上实现；把“本机同权限者可同时改写”当作本条要防护的对象，是永远无法满足的条件。**批准依据：**用户 2026-11-15 定“收紧威胁模型 + 修可机械修的部分”，明确 `PYTHONPATH` 注入、`sitecustomize`、直接改 `site-packages` 移出威胁模型，并要求单列本条、不并入 G-019（ADR-0019 已同步改写“替换可被发现”的表述）。**承接方与时点：**外部基础设施（真 CI + 受保护分支 + 复核方独立持有工具链）在 M4 前承接，方向与 ADR-0015 同批；承接前若发生依赖替换，只能按“本机环境不可信”处理，不得声称指纹提供安全保证。**边界**：本条不覆盖 G-019 的准入与归区实现，也不构成 G-019 的关闭依据。 | 外部复核：/home/wgz/projects/skills/2026-11-14/pm-governance-review/verify-g019-r5/REPORT.md；sha256：5373a537d05870dcf4f52756bf7e0012bc0128879e22df92cb85d86007258108；基线：3d7211c；报告章节：§2.1、§5.1 |
| G-023 | open | representation-defect | L2 | G-023：`status-snapshot` 与 `evm-record` 的全部金额字段（状态件的 AC/PV/EV 指标、挣值件的 `bac`、`measurements` 的 pv/ev/ac、`work_packages.budget`）；`CFG-09` 仅由 `budget.currency_match` 消费 | 否 | 架构负责人 | M1 |  | T-150 | 批次 0104–0105 连续两批公开案例暴露：状态与挣值工件没有币种字段，`CFG-09` 只在 `budget.currency_match` 被消费，因此这两类工件的金额无论用什么币种记录都不会被拦。**影响面**：状态 4 项检查（`status.dictionary_fields`、`status.no_implicit_zero`、`status.sample_grid`、`status.account_registered`）与挣值 4 项检查（`evm.budget_consistent`、`evm.ev_measurement`、`evm.formulas`、`evm.eac_method`）均不读 `CFG-09`；工件契约也未定义 `currency`，没有字段可核；状态 AC 与成本预算合计之间也没有跨工件一致性检查。**为什么机械校验漏掉**：不是检查逻辑漏写——`_check_budget_currency` 已按 `CFG-09` 比对——而是表示层缺字段，另两种工件里不存在可比对象。**不修的后果**：跨币种不可比的数字会被当作合规通过；D6 的金额类结论与 S2 的 `CFG-09` 变体只覆盖预算侧，接受度报告中的金额比对失去意义。修复前，公开案例的状态与挣值件一律标注来源币种，不得与他币种工件拼比。**处置方向**：`check-change`（状态与挣值契约增加币种字段并扩展货币核对），待非同源复核。 |  |
| G-024 | open | representation-defect | L2 | G-024：`runtime/artifacts/dependency-graph.schema.json` 的 `activities[].due_day`（上限 3650 天）；`schedule.critical_path` 的期限判定 | 否 | 架构负责人（受钉扎 schema 变更需裁定） | M1 |  | T-150 | 批次 0105 暴露：`due_day` 上限 3650 天，装不下 2013→2028 的十五年周期；期限一旦超过上限，`schedule.critical_path` 的“按期/超期”就没有合法输入可表达。**待裁定**：是否扩展上限、改日期或相对期限、或在规则中声明“仅支持十年内期限”。本台账不自行改受钉扎 schema，也不为让题目通过而缩放年限；D6-PUB-07 已改为不设里程碑期限，局限写入运行记录与案例台账。**登记里程碑**：M1；到期仍未裁定将阻断发布。 |  |
| G-025 | open | representation-defect | L3 | G-025：`runtime/artifacts/risk-register.schema.json` 的 `risks[].category` 闭集；`risk.required_fields`、`risk.owner_registered`、`risk.band_consistent` 的类别语义 | 否 | 架构负责人 | M1 |  | T-150 | 批次 0105 暴露：风险类别是闭集（technical/resource/external/organizational/scope），公开案例中的“治理”类问题无对应类别，只能落 `organizational`。**登记即可，不扩枚举**——扩展会改动受钉扎 schema 并影响既有正负例。后续题目按现有五类就近归类，并在案例台账注明改写方式。 |  |
| G-026 | open | representation-defect | L3 | 全部 32 题的模型臂（S0/S1）、`validation/d6/acceptance.json` 的档位定义、任何“本地可部署”类结论 | 否（不阻断编译主流程与最终发布） | 验收负责人 | M1 |  | T-179 | 批次 0110 按裁定把三档改走外部 API；原本地权重口径（`Qwen2.5-Instruct` 7B/72B、`Q4_K_M` 4-bit、`32768` tokens）移出主档位，打包为独立待定任务 T-179。**受影响下游**：① 全部 32 题的模型臂（S0、S1）从未运行，故无运行记录依赖该口径；② `acceptance.json` 档位定义已改为 `external_api`，本地口径仅作历史字段保留；③ 当前不存在依赖该口径的对比结论。**边界**：本地权重可用时作为独立任务推进，不阻断编译主流程与最终发布，主流程不等待该任务。**拟处置方向**：`doc-only`（仅作历史口径文档化）；关闭须非同源复核或人工签收，不得以本文自证，故关闭前不填处置出口列。 |  |
| G-027 | open | representation-defect | L2 | CFG-03（偏差分档）的配置敏感性；`deviation.thresholds_configured`、`deviation.dimensions`、`deviation.custom_metric`、`compute_deviation`；S2 变体 V-CFG03 | 否 | 架构负责人（受钉扎 schema 变更需裁定） | M1 |  | T-150 | 批次 0109 暴露：S2 变体 V-CFG03 零题可跑。**性质判定**：① **不是检查缺口**——三项 `deviation.*` 检查与 `compute_deviation` 均已实现（`scripts/pm_caps.py` 的 `_check_deviation_config`/`_check_deviation_dimensions`/`_check_deviation_unsupported` 与 `COMPUTE_REGISTRY["deviation.map"]`）；② **不是“敏感性为 0”**，而是覆盖缺口，且根因有两层：**契约未绑定**——没有任何工件 schema 在 `x-checks` 中声明 `deviation.*`（对 `runtime/artifacts/*.schema.json` 的检索结果为 0），而 `pm_check` 只执行工件 schema 声明的检查，故只加题不加绑定也不会跑到这些检查；**题集缺题**——32 题无一题覆盖偏差分档。**补一题的最小代价（两选一，均需裁定，不得自行改受钉 schema）**：A. 在既有 `runtime/artifacts/cost-budget.schema.json` 的 `x-checks` 增加三项（成本最低：复用现有 cost-budget 输入与工作包字段 `wbs_ref`，仅需 1 条任务卡；但会改变全部既有成本题的检查集合，须整批重跑并复核）；B. 新建 deviation 工件契约（新 schema + 钉扎登记 + 1 份输入 + 1 条任务卡），成本更高但不改既有题。**2026-11-17 按裁定取 B（已实现，待复核）**：新增 `runtime/artifacts/deviation-report.schema.json`，并在 `scripts/check_spec_pins.py` 的 `SECTIONS` 登记为规格区段、重冻指纹；`x-checks` 绑定三项既有检查并新增 `deviation.band_consistent`，由后者消费 CFG-03.boundaries 与 CFG-02.labels；配套输入 `validation/cases/NAO-UNIVERSAL-CREDIT/inputs/deviation-report.json` 与任务卡 D6-PUB-23。主配置实际结果：退出码 0，四项全部通过；V-CFG03 下 `deviation.band_consistent` 违规（SPI 0.88 由 amber 落入 red），为已声明翻转。既有 32 题未改动，期望未改。 |  |
| G-028 | open | representation-defect | L3 | CFG-14（风险刻度与分档）的配置敏感性；`risk.scale_in_range`、`risk.band_consistent`、`compute_risk`；S2 变体 V-CFG14 | 否 | 架构负责人（受钉扎 schema 变更需裁定） | M1 |  | T-150 | 批次 0109 暴露：S2 变体 V-CFG14 下 5 题结论全部不变。**性质判定（分开两层）**：① **分档标签不可观测，属“契约未要求比对标签”，不是检查实现漏写**——`risk-register.schema.json` 的风险条目没有 `band`/`band_order` 字段（必填为 id、category、probability、impact、trigger、response_strategy、owner_role、status、residual_score、objective_refs），`_check_risk_band` 只验证“评分能落入 CFG-14.bands 的某个连续区间”，工件没有声明值可比对，故 3×3→5×5 改标签不会产生差异；② **刻度尺寸并非完全不可观测**——`risk.scale_in_range` 以 CFG-14 的刻度上限判定，若题中出现取值 4–5，3×3 会违规而 5×5 通过；现有 5 题取值均为 1–3，两种刻度都通过，故本轮无差异。**两种修法不同**：契约变更（schema 增 `band` 字段 + `band_consistent` 比对声明值与计算值，动受钉 schema、检查器与既有 5 题工件）；或只补一道取值 4–5 的风险题（只动题集，最小代价约 1 条任务卡 + 1 份输入，可观测刻度尺寸但标签仍不可观测）；或 `doc-only` 声明“档位标签仅用于展示、不参与判定”。最小的是补题，但**不能**据此宣称 CFG-14 已获敏感性覆盖。**2026-11-17 按裁定取“补题 + 标签 doc-only”（已实现，待复核）**：新增任务卡 D6-PUB-24 与输入 `validation/cases/NAO-HS2/inputs/risk-register-scale45.json`（概率 4、影响 1，初始评分 4）；主配置实际退出码 1，仅 `risk.scale_in_range` 违规；V-CFG14 下全部通过（violation→pass，已在任务卡声明）。`band` 标签仅展示、不参与判定的声明写入 `runtime/artifacts/CONTRACTS.md`：生产者可任意填写或省略标签而仍通过，展示层可贴任意标签而不被检查发现，CFG-14.bands 的标签变更不可验证；可验证的只有刻度尺寸与连续分档。未改动 `risk-register.schema.json`；仍不能据此宣称 CFG-14 已获完整敏感性覆盖（标签仍不可观测）。 |  |

**共同成因**：G-002、G-003、G-004、G-005、G-006 同属 **规则正文严于判定列** 这一大类——判定列只覆盖了规则正文的一部分条件，或把不同严重度的条件压在同一级别。它们不是彼此独立的偶发问题，而是同一口径缺陷的不同表现。对应的独立工作项 T-130、T-131、T-100、T-134、T-135 保留原编号，不合并。

**与 G-007 的关系**：G-007 是另一类——不是“判定列漏了正文条件”，而是“判定列本身存在未定明的语义”，因此成因记为 `undefined-object`。2026-11-14 复核后，其剩余语义缺陷拆为 G-009–G-012 四个可执行项。

**与 G-008 的关系**：G-008 登记独立复核报出的八条**表示层**问题（P1–P8）。2026-11-14 复核重跑确认 P4（引用完整性不统一）与 P6（路径表示）未解决，P1/P2/P3/P5 只部分解决，故重开；拆分项为 G-009–G-017。

## 需求缺口（RG）与配置改判（批次 0082；RG-07/RG-08 的配置编号于批次 0084 补齐）

**依据**：`spec/D6_REBASELINE_PROPOSAL.md` 第 9 节（配置层设计）与 9.6 反向审查；用户已批准以第 9 节为配置层设计基准。**本节不关闭任何缺口**：改判只回答“原来被当成技能常量的那部分参数去了哪里”，判据部分仍留在缺口内。

**改判规则**：满足 9.1 的 C1–C3（随项目变、只改刻度不改通过语义、可由责任方声明并复现）的部分 → 配置项；其余留作判据。**配置化不等于解决**：参数有了落点，缺口只因“判据部分仍缺”而保持 `open`。

**编号口径**：本表的 `RG-NN` 与第 2 节缺口主表的 `G-NNN` **两套编号不同源**（RG 来自 D6 第 8 节，G 来自“规则正文 ↔ 判定列”缺口）；未在“关联”列显式引用 `G-NNN` 时，两者不构成对应关系，不得据本表推断 G 条目状态或反向补齐编号。

| 编号 | 状态 | 等级 | 原判（第 2 节） | 被配置吸收的部分 | 仍是缺口的部分 | 剩余关闭出口 | 关联 |
|---|---|---|---|---|---|---|---|
| RG-10 偏差阈值（CAP-16） | `open` | L2 | 无法替代（D）；阈值由责任方另行设定 | **全量**：阈值表结构与取值 → CFG-01（分档维度）、CFG-02（档数与标签）、CFG-03（边界与偏差点定义）；“无默认、缺失即 `cannot_evaluate`”由 schema 与 9.3 承担 | **数值该取多少**仍无权威来源（政府指南只要求“设阈值并复核”）；技能不能替项目定值，也不能判断项目取值是否合理——只能校验结构、可复现性与变更留痕 | `doc-only`：明文写“技能只校验结构与可比性，不判断数值合理性”，或由非同源复核确认“配置化 + 校验 + 留痕”已尽到技能义务。**不得以“已改为配置”关闭** | CFG-01/02/03；T-150 |
| RG-09 状态采集字典（CAP-35） | `open` | L2 | 无法替代（D）；只能由责任方设定最小集 | 采什么、多久采、口径如何换算 → CFG-04（采样口径）、CFG-05（周期分数集）、CFG-06（周期基准）、CFG-07（固定间隔）、CFG-08（日历） | **数据字典本身**（字段集、口径一致性规则、缺数处理）仍无通用权威来源；“缺数不得默认通过”是判据，不可配置 | `rule-change` / `check-change`：定义最小采集字典与缺数判据，并由非同源复核 | CFG-04–08；T-151 |
| RG-08 风险登记册（CAP-25） | `open` | L2 | 公开可得，刻度需自定 | 概率-影响刻度（3×3 / 5×5 的刻度尺寸、概率与影响标签、评分规则、分档边界）→ **CFG-14（风险刻度）**，判定性、无默认、缺失即 `cannot_evaluate`；编号由责任方于批次 0084 裁定补齐 | **字段集**（ID/类别/概率/影响/触发/应对/责任人/状态/残余）仍是判据；刻度与字段的可判关系（如“残余风险必须有对应应对”）未定义 | `check-change`：字段集 schema 化 + 刻度与字段的可判关系落地；非同源复核 | CFG-14；T-157（已关闭） |
| RG-07 成本科目（CAP-19） | `open` | L2 | 公开可得，科目表需自定 | **组织成本科目表**（科目编码、名称、上级科目）→ **CFG-15（成本科目表）**，项目参数、判定性、无默认、缺失即 `cannot_evaluate`；编号由责任方于批次 0084 裁定补齐 | **WBS—成本映射守恒**（父节点 = 子节点之和、科目汇总与 WBS 交叉一致）仍是判据；科目表与 WBS 的对应口径、编码唯一性/无环/父科目存在性未定义 | `check-change`：守恒校验与科目表引用完整性落地；非同源复核 | CFG-15；T-151；T-157（已关闭） |
| RG-05 关口证据 | `open` | L2 | 公开可得但需自定 | `approver_role` 映射 → CFG-12（人审关口） | **`must_see` 证据清单**（每类关口必须看到什么）仍是判据；现仅要求存在 Accountable | `rule-change` / `check-change`：按工件裁剪 `must_see` 清单并逐项判定 | CFG-12 |
| RG-04 口径判定规则 | `open` | L2 | 公开可得但需自定 | **阈值类参数** → CFG-01/02/03 与 CFG-13；量纲与刻度改为配置读取 | **定义、枚举、区间、优先级**仍缺：现有条目多为一句话定义，A 表无法据此判定 | `check-change`：逐条下沉判定规则并标“技能自设”，非同源复核 | CFG-01/02/03/13 |
| RG-02 工件字段集 | `open` | L2 | 公开可得（A） | **命名与版本约定** → CFG-11 | **字段集与必填性**（章程、WBS、风险登记册、进度、成本、状态报告）仍是判据；字段级枚举与引用关系未定义 | `check-change`：工件字段集 schema 化（工件契约）；非同源复核 | CFG-11 |
| RG-11 挣值口径 | `open` | L2 | 付费不可得，有公开替代（C） | **计量规则**（0/100、50/50、百分比完成、加权里程碑）→ CFG-13 | **PV/EV/AC 定义、偏差与绩效指数、EAC 三法、术语别名**仍是判据；且须固定单一主源（第 8 节、T-155） | `rule-change`：按 T-155 落公式与单一主源，非同源复核 | CFG-13；T-155 |

**未改判的 8 条**（RG-01 工序映射、RG-03 算子语义、RG-06 依赖类型、RG-12 审计字段、RG-13 案例素材、RG-14 改造规范、RG-15 rubric、RG-16 领域裁剪）：理由见 9.6——步骤顺序、算子语义、四类逻辑关系、审计字段集、验收装置、判据与任务卡声明都**不满足 C2**（改动即改变“什么算通过”），保持原判与 `open`。

**统计**：16 条中 8 条改判（1 条全量、7 条部分）、8 条不改判；**本批关闭 0 条**，8 条改判条目的“仍是缺口的部分”与“剩余关闭出口”均不得为空。

**编号补齐（批次 0084）**：RG-08 的风险刻度与 RG-07 的成本科目表原在 9.2 中无 CFG 编号，由责任方裁定新增 **CFG-14（风险刻度）** 与 **CFG-15（成本科目表）**，按 CFG-01～13 的既有体例落盘（判定性、无默认、缺失即 `cannot_evaluate`）；T-157 随之关闭。原“按未注册配置项报 `config_invalid`”的临时口径作废。两项的判据部分仍为缺口，状态保持 `open`。

## 批次 0095 实施进展（不关闭任何条目）

**性质**：本段只记录“缺口的判据部分被机械化到什么程度”，**不构成任何条目的关闭依据**，也不改变第 2 节任何 `G-NNN` 的状态与核查矩阵。新增脚本均已在 `scripts/no-review-declarations.json` 登记无复核声明（T-167）。

| 编号 | 本批机械化部分 | 仍未机械化（缺口成立的原因） |
|---|---|---|
| RG-02 工件字段集 | 6 份工件 schema（依赖图、成本预算、风险登记册、状态快照、EVM 记录、审计留痕）以 JSON Schema 子集落地，含字段集、必填性与引用关系；工件信封强制 `x-checks`/`x-provenance` | 章程、WBS、进度计划、状态报告四类工件未落 schema；字段级枚举仍只覆盖本批六类 |
| RG-07 成本科目 | `CFG-15` 求值（编码唯一、父科目存在、无环）；`budget.total_conserved` 校验总额守恒，并逐节点比对子树合计（旧实现只保证总数、不保证每个节点，本批已改为逐节点）；科目汇总与 WBS 交叉一致 | 科目表与 WBS 的对应口径未定义；守恒只在本批 schema 的字段形态内可判，跨工件口径缺判据 |
| RG-08 风险登记册 | `CFG-14` 刻度求值（尺寸、标签、评分规则、分档边界）；`risk.residual_response` 校验残余风险须有对应应对；`score_rule=matrix` 无矩阵取值时判 `cannot_evaluate` | 字段集的完整枚举与“刻度取值的合理性”仍无判据；矩阵评分规则缺可求值的取值表（本批按 `cannot_evaluate` 处理，不猜） |
| RG-09 状态采集 | `CFG-04`–`CFG-08` 采样网格求值（口径、周期分数、基准、固定间隔、日历/时区/节假日）；采样点缺失判 `cannot_evaluate`，不默认通过 | 最小采集字典（字段集、口径一致性规则、缺数处理的业务判据）仍缺；本批只保证“没采到不许判过” |
| RG-10 偏差阈值 | `CFG-01/02/03` 求值（分档维度、档数与标签、边界与偏差点）；越界值判 `cannot_evaluate` | 数值该取多少仍无权威来源；技能不判断项目取值是否合理（同原判） |
| RG-11 挣值 | `CFG-13` 计量规则求值；SV/CV/SPI/CPI 与 EAC 三法按工件显式声明的方法计算；方法未声明判 `cannot_evaluate` | 单一主源仍未固定（T-155）；**扩大缺口**：EAC 三法未在 CFG 注册编号，方法选择目前由工件字段承载而非配置项，与“可复现”要求存在张力，需裁定是否新增 CFG 编号 |
| RG-12 审计字段 | `audit.append` 生成 `prev_digest` 摘要链；跨配置记录判不可比 | 摘要链只证“未被改动”，不构成外部锚定；谁写入、何时写入仍不可验，**扩大缺口**：审计仅摘要链、无外部时间戳/签名锚定 |
| RG-05 关口证据 | `human_approve` 读取 `must_see` 清单，未看到指定项判 `1`；无签字记录判 `3`；拒绝判 `1`；角色与 `CFG-12` 映射不符判 `1` | `must_see` 内容按工件裁剪的判据仍缺；**扩大缺口**：签字人的自然人身份不可验，本批只能校验“有记录、角色匹配、看过指定字段” |
| RG-01 工序映射 | 5 张工序卡落地 6 算子闭集，步骤 `needs` 依赖与算子必填字段机械校验 | 工序到能力的映射判据未定；闭集只保证“不越界”，不保证“映射正确” |
| RG-03 算子语义 | 六算子语义按第 6 节落地，未注册算子判 `2` | 算子的业务语义（何时该用哪个算子）仍不是机械判据 |

**本批新增/扩大缺口（不合并进既有 RG 编号，待裁定编号）**：

- `EAC-无配置编号`：EAC 三法选择由工件字段承载，未进 CFG 注册表；与“判定性项无默认、可复现”存在张力。
- `风险矩阵取值`：`CFG-14.score_rule=matrix` 时无矩阵取值来源，本批判 `cannot_evaluate`，不提供默认矩阵。
- `签字人身份不可验`：`human_approve` 只能校验记录/角色/`must_see`，不能证明签字人是自然人。
- `审计无外部锚定`：摘要链可自证连续性，不能证明时间与写入者。

## 批次 0096 实施进展（不关闭任何条目）

**性质**：批次 0095 落地完成后，外复核对 `ef54b63` 判 3 项认可、7 项不认可、2 条阻断；本段记录按复核清单修复后的机械化状态，**不构成任何条目的关闭依据**，也不改变第 2 节任何 `G-NNN` 的状态。修复本身尚未经复核，仍按 T-167 登记。

| 复核项 | 修复后的机械化部分 | 仍未机械化（缺口成立的原因） |
|---|---|---|
| 阻断 1 预算上卷 | 按 parent 链计算深度、深度降序上卷；`budget.total_conserved` 逐节点比对子树合计，不再以总数相等代替单节点正确 | 科目表与 WBS 的对应口径仍缺；本批只保证“同一张科目表内逐节点自洽” |
| 阻断 2 退出码契约 | 步骤内输入非法统一记 `invalid`（2）；非对象工件与深嵌套 JSON 归 `2`；`human_approve` 无配置归 `3` | 退出码只覆盖已注册工件与六算子；新算子或新工件类型的边界仍须复核 |
| 严重 3 聚合优先级 | `4 > 2 > 3 > 1 > 0`；配置 finding 在聚合前并入报告 | 优先级本身是约定，非可外部验证的判据 |
| 严重 4 无配置放行 | 工件缺 `--config` 一律 `cannot_evaluate`（3），删除跳过 `config_ref` 比对的分支 | 无配置时无法建立跨配置可比性，这是缺口而非可补全项 |
| 严重 5 逐项摘要 | `item_digests` 逐项重算；篡改或缺失判 `config_drift`（1） | 逐项摘要仍由执行方生成，无外部锚定 |
| 严重 6 CFG-12 为空 | 角色映射缺失或为空即 `cannot_evaluate`（3），不再整段跳过 | 签字人自然人身份仍不可验 |
| 严重 7 render 越界 | `render.out` 以 realpath 前缀限制在 `--out-dir` 内，越界判 `2` | 符号链接竞态（检查与写入之间）未做原子化，属残余边界 |
| 严重 8 库层默认 | 删除 `metric="SPI"`、`percent_complete=0`、固定周表三处默认，缺失即 `3` | 无默认后，配置供给责任完全落在使用方，验收配置须随任务集保存（T-150） |
| 严重 9 采样口径 | 固定间隔与里程碑共用 CFG-06 的 workday/calendar 基准，基准无配置即拒绝 | 节假日日历本身来自配置，其权威性不在技能内 |
| 严重 10 schema 关键字 | `validate()` 入口全树预扫描，未实现关键字在任意分支都拒绝 | schema 子集仍是有意裁剪的闭集，新增关键字须显式实现并复核 |

## 批次 0097 实施进展（不关闭任何条目）

**性质**：第二轮外复核对基线 `cff825b` 判零阻断、8 项认可、4 项不认可；本段记录四项修复与三条“只登记不修”残余的机械化状态，**不构成任何条目的关闭依据**，也不改变第 2 节任何 `G-NNN` 的状态。修复本身尚未经复核，仍按 T-167 登记。

| 复核项 | 修复后的机械化部分 | 仍未机械化（缺口成立的原因） |
|---|---|---|
| 一 工件逐项摘要 | `validate_artifact()` 调 `pm_config.comparability()` 与 `snapshot["item_digests"]` 比对；单条篡改/缺项/键序不符判 `1`，多余键判 `2` | 逐项摘要仍由执行方生成，无外部锚定；键序判定是“按快照生成”的代理信号 |
| 二 模板读取 | `_render()` 捕获 `OSError`/`UnicodeDecodeError` → `4`；绝对路径或 `..` 越出 `TEMPLATE_DIR` → `2` | 模板内容本身未做语法或安全性检查；工序校验阶段仍不前置拒绝非法模板路径 |
| 三 库层残留默认 | `lag` 缺失 → `cannot_evaluate`；缺 `CFG-01`/`CFG-03` 的 `deviation.*` → `cannot_evaluate`；`_ev_rule` 缺 rule 给出原因 | 配置供给责任仍在使用方；`weighted_milestone` 缺权重仍用固定文案 |
| 四 引用失实 | 测试依据改指 `GAP_LEDGER.md` 外复核派生条；`CHANGELOG` 改为“因配置问题退 1 时必带 `config.*`” | 引用正确性仍靠人写，本批起由条款登记与检查器承接（见批次 0098） |

**只登记不修的三条残余（均为 0096 之前引入）**：

| 编号 | 残余 | 状态 |
|---|---|---|
| R-0097-01 | `render.template` 在工序校验阶段未受约束（绝对路径可读任意文件）；运行期路径约束已由本批二补上 | 登记，不修 |
| R-0097-02 | `--procedure` 不受任务目录约束，可指向任意工序文件 | 登记，不修 |
| R-0097-03 | `_ev_rule` 空理由；本批三已让缺 rule 时返回原因，其他调用方仍可能丢弃该原因 | 登记，不修（重叠部分已按第三条修） |

---

## 批次 0098 实施进展（不关闭任何条目）

**性质**：条款依据的机械检查装置（登记表 + 检查器 + 用例标记）。新增对象均未经非同源复核，**不构成任何认可**，也不构成第 2 节任何 `G-NNN` 的关闭依据。

| 新增对象 | 位置 | 准入与钉扎 | 仍不机械化（缺口成立的原因） |
|---|---|---|---|
| 条款登记表 | `spec/clause-registry.json`：38 条，`quote` 由 `check_clause_basis.py --write` 从源文件逐字提取 | `spec/ACCESS_ZONES.md` 第 1/2 节登记为 D 区，生成器登记；**未钉扎**（0098 原写“`checker-pins.json` 钉扎”不实，0099 纳入 `spec-pins.json`） | 手写部分只剩 `(source, locator, section, anchor, kind)`；`kind` 的判定性/文字性分类由人判断 |
| 条款依据检查器 | `scripts/check_clause_basis.py`：三查（引用存在、判定性条款有覆盖、源文件/章节/原文一致）+ 五条 `--self-test` | `checker-pins.json`、`no-review-declarations.json`、pre-commit、`scripts/README.md` | 只认 `条款：<id>` 标记；不判断用例断言是否真的检验了该条款语义 |
| 用例标记 | `scripts/test_pm_runtime.py` 由 66 项增至 68 项，全部 `依据：` 行改带条款标记；新增未注册配置项、配置项相互矛盾两例 | — | 标记可被贴在任意断言上，检查器无法核对标记与断言的对应关系 |

**新增欠账（登记，不修）**：

| 编号 | 残余 | 状态 |
|---|---|---|
| R-0098-01 | 登记表 `quote` 与源文件的一致性由生成器自证：源文件与登记表同批改动即可同步漂移，无外部锚定（与 G-021/G-022 同属信任边界） | 登记，不修 |
| R-0098-02 | 覆盖判定只要求“至少一条用例引用”，不判断断言是否真的检验该条款；“覆盖 ≠ 充分”的方法论残留仍在 | 登记，不修 |
| R-0098-03 | `条款：` 标记与测试断言的对应关系无法机械核验，只能由外复核抽查 | 登记，不修 |

---

## 批次 0099 实施进展（不关闭任何条目）

**性质**：第三轮外复核五项修复。新增钉扎与判定规则均未经非同源复核，**不构成任何认可**，也不构成任何 `G-NNN` 的关闭依据。

| 修复 | 位置 | 后果 | 仍不机械化 |
|---|---|---|---|
| 一 钉扎缺口 | `scripts/check_spec_pins.py` 的 `SECTIONS` + `scripts/spec-pins.json` + `no-review-declarations.json`：提案整篇、`AGENTS.md#1bis`、`GLOSSARY.md#T-F-015`、`spec/clause-registry.json` 整篇 | 改源必留失效痕迹；改源 + 改 anchor + `--write` 会使登记表指纹失效 | 纳入时的现行文本没有复核产物，只有声明（R-0099-01） |
| 二 三处虚报更正 | `CHANGELOG.md` 0098 条目、`GAP_LEDGER.md` 0098 表、`TODO.md` T-168 | 三处均改为“当时未钉扎/未登记”并注明由 0099 补正 | 无（文字更正） |
| 三 textual 引文 | `spec/clause-registry.json` 5 条改取正文句；`check_clause_basis.py` 增 `section_digest` 与“textual 禁取标题” | 改标题外正文也报“章节正文已变动” | 摘要仍由同源生成器计算（R-0099-02） |
| 四 硬链接 | `scripts/pm_check.py` 的 `_render()` 按 `st_nlink` 拒绝 | 模板目录内硬链接指向外部 → 2，不写出 | 同 inode 的 bind mount 等未覆盖（R-0099-03） |
| 五 聚合与默认 | `pm_check.validate_artifact()` 逐项摘要并入聚合；`pm_caps.compute_risk/compute_status` 缺配置改不可判定 | 配置不可判定不再被工件违规掩盖；键序不再判违规 | 各 `compute_*` 调用点是否都把 `cannot_evaluate` 正确上抛未逐点核验（R-0099-04） |

**新增欠账（登记，不修）**：

| 编号 | 残余 | 状态 |
|---|---|---|
| R-0099-01 | 提案、`AGENTS.md#1bis`、`GLOSSARY.md#T-F-015`、`clause-registry.json` 纳入钉扎时只有无复核声明，没有对“纳入了正确版本”的外部确认 | 登记，不修 |
| R-0099-02 | `quote`/`section_digest` 与源文件的一致性仍由同一生成器自证；同批改源、改 anchor、`--write`、重冻钉扎可以自洽推进 | 登记，不修 |
| R-0099-03 | 硬链接按 `st_nlink` 拒绝，bind mount / overlay 等同 inode 的其他形态未覆盖 | 登记，不修 |
| R-0099-04 | `compute_risk`、`compute_status` 已改判不可判定，但其他 `compute_*` 的缺配置路径与调用方上抛未逐点核验。**批次 0101 补列两处库层默认**：`scripts/pm_config.py` 的 `sample_points()` 用 `config.get("CFG-05", [])` 静默取空列表（`milestone_fraction` 模式下会得到零采样点而不报错）；`scripts/pm_caps.py` 的 `compute_budget` 用 `config.get("CFG-15") or {}` 静默取空科目表 | 登记，不修 |

---

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
| 2026-11-14 | 批次 0042：按非同源复核清单机械化（非同源复核基线 `d8bf413`） | 12 条按复核结论关闭（`关闭依据` 均为 `非同源复核：`，见各条）；5 条维持 `open` 并写明残留。机械化项：根检查器与 pre-commit 纳入哈希保护、`--basis` 必须是复核记录、`coverage.json`/A.1 纳入指纹、覆盖闸门改子句级取证、pre-commit 跑 60 条样例与关键扫描、嵌套缺键 53 项入口归一化、四类封闭枚举统一 `undefined_enum_value`、E2 终点限人类/法人、A.2 条数更正为 41。M2 出口改为“清单清零 + 非同源复核判实质收敛”，两项残余风险外置到真 CI/受保护分支。 |
| 2026-11-14 | 批次 0046：非同源复核（基线 `9519b82`，产物 `/home/wgz/projects/skills/2026-11-14/pm-governance-review/verify-g014/REPORT_9519b82.md`） | 关闭 G-014、G-001、G-003、G-007、G-008，依据均带 `报告章节`；G-006 证据措辞更正为“`constraint=null` → cannot/missing_input，非 fail”，按非 pass 口径仍关闭；G-017 维持 `open`（无全文语义等价机器证明）；新登记 G-018（`actors[].type=Bogus` 仍 `pass`）。台账 18 条：`open` 2（G-017、G-018）/ `closed` 16。 |
| 2026-11-14 | 批次 0048：T-123 放宽与 T-139 拆分（用户裁定） | `PMBOK8-2025` 的 `allowed_uses` 放宽到概念层（仍禁成段摘录、原文替代定义、未核页批量引用、规则直接锚定）；10 条 `anchored-entries.jsonl` 的来源迁入 `evidence[]`，`grounding_ref` 只用于规则/本体到条目的绑定，试点 15 条同步对齐；F-07 定性为检查器过度匹配，新登记 G-019（`RM-PROSEBLOCK` 误伤 ≥15 条长 JSONL）。台账 19 条：`open` 3（G-017、G-018、G-019）/ `closed` 16。 |
| 2026-11-15 | 批次 0050：G-019 二次加固与 G-020 登记（用户授权，基线 `dcd2240`，复核 `/home/wgz/projects/skills/2026-11-14/pm-governance-review/verify-g019/REPORT.md`） | `check_no_raw_material.py` 补六条：值级上限、顶层键白名单与子结构校验、全局单行上限与 base64 识别、magic bytes 与未知扩展名 fail-closed、段落级 `RM-PAGEDUMP`、解析前剥 BOM；扩展名扫描面纳入 `.log/.csv/.html/.xml/.tex/.rst/.tsv/.dat`；`--self-test` 18/18 通过（T-NRM-03 改取真实正文第 6 页，`RM-PAGEDUMP` 独立命中且无 `RM-DOTLEADER`）；全仓 130 个跟踪文件 0 新命中；15/20/20 条 JSONL 均 0 报。新登记 G-020（防线覆盖面与准入形态，`representation-defect`、L1、登记 M1、到期 M2、关联 T-142，与 G-019 的边界见该条说明）。G-019 维持 `open`，关闭依据留空，待非同源复核。台账 20 条：`open` 4（G-017、G-018、G-019、G-020）/ `closed` 16。 |
| 2026-11-15 | 批次 0051：原始资料防线换轴方案（用户批准只出方案，基线 `58641d0`，r2 复核 `/home/wgz/projects/skills/2026-11-14/pm-governance-review/verify-g019-r2/REPORT.md`） | 新增 `spec/RAW_MATERIAL_ADMISSION.md` 与 `adr/0018-raw-material-admission-control.md`（`proposed`）：以分区准入替代形态推断，D/O/P/C 四区、131 文件逐条判定、数据区 schema 与字段配额、`RM-*` 逐条留改删、第 13 条修订草案、迁移与残余风险、待批 D 清单。G-019 建议改写为“形态判据退役与准入制落地”、G-020 建议拆分改写为“子模块、外部生成物与未登记路径的扫描范围”，两条均维持 `open`，不自行关闭。本批不改实现、不改 `CONSTITUTION.md`。台账仍 20 条（`open` 4 / `closed` 16）。 |
| 2026-11-15 | 批次 0052–0053：准入制落地（用户批准 D1–D10，基线 `58641d0`） | `CONSTITUTION.md` 13.3/13.5 修订、ADR-0018 转 `accepted`；新增 `spec/ACCESS_ZONES.md` 与 2 份内容 schema；检查器改为“归区 + 硬约束 + schema”，退役 `RM-PROSEBLOCK`/`RM-PAGEDUMP`/`RM-PAGESEQ`，新增 `RM-ZONE`/`RM-SCHEMA`/`RM-FIELD`，自测按新轴重建为 30 项。G-019/G-020 维持 `open`。 |
| 2026-11-15 | 批次 0054：全仓一次性过检（`git ls-files` 138 文件） | 0 违规；D-6 收敛为**不设豁免期**，未创建 `validation/exemptions/`；过检只证明已登记的区与结构条件成立，不证明内容不是原文。 |
| 2026-11-15 | 批次 0055–0056：r2 复核后处置（基线 `deaac46`） | G-019/G-020 按复核改写、G-021 按 D-10 登记；第 5 条受影响对象补齐、13.5 裁定句改为“承认降低、显式接受”、13.6 结尾表述更正。 |
| 2026-11-15 | 批次 0057：五份人工维护文件补 schema 与 13.6 三项检查 | 数据区 22 个文件（10 受 schema、7 schema 自身、5 生成器）；`relations`/`evidence`/`claim_mapping` 收紧；单条配额统一 2800；13.6 三项检查落地；归区表纳入 `spec-pins`；自测 43 项。 |
| 2026-11-15 | 批次 0058：G-020 关闭（复核 `verify-admission`，sha256 `905cf2…`，基线 `deaac46`） | G-020 以 `accepted` 关闭并登记三条备注（子模块为声明式排除、引入须同批重新裁定、现状 0 gitlink 可复算）；G-019/G-021 维持 `open`；gitlink/符号链接/缺失路径显式判 `RM-ZONE`。 |
| 2026-11-15 | 批次 0059：规格钉扎自动发现与依据标准对齐（r3 复核，基线 `3664b64`） | `check_spec_pins.py` 枚举 `contracts/schema/`，未登记即阻断（区段 11 → 15，补 4 份漏钉 schema）；`basis` 改为仓库外产物 + 64 位 sha256 + 基线，与检查器绑定同一标准；`test_spec_pins` 8/8。 |
| 2026-11-15 | 批次 0060：schema 完整性 lint 与按路径配额 | 新增 `RM-SCHEMA-LINT`（数组 `maxItems`、字符串 `maxLength`、对象 `additionalProperties: false`、关键字白名单、未实现关键字、`oneOf` 排他、`$ref` 同级拒绝）；配额改 `x-prose-fields` 逐路径 + `x-prose-budget` 兜底；`pilot-conflicts` 的 `positions`/`recorded_fields` 加 `maxItems: 40`；自测 55 项，含 300×400、200×120、3 条假设契约、12 条 `notes` 的正负例。 |
| 2026-11-15 | 批次 0061：两条零召回本体规则重写 | `RM-ONTO-PAGESEQ` 认连续页码三元组 / 逗号页码表 / 裸数字串；`RM-ONTO-PROVENANCE` 按块核对来源与页码并识别 `n/a` 矛盾；真实 TTL 5 文件、349 页码值、501 义务块 0 命中，攻击输入全部命中（统计见 `spec/ACCESS_ZONES.md` 第 6 节）；自测 58 项。 |
| 2026-11-15 | 批次 0062：台账同步（本批） | G-021 按真实量级改写（`relations` 28.8K、`evidence` 9K、`positions` 修复前 12 万 / 修复后 1.6 万，均计入总量口径）并维持 `open`；G-019 补 0059–0061 落地、维持 `open`；G-020 三条备注未改。台账 21 条：`open` 4（G-017、G-018、G-019、G-021）/ `closed` 17。 |
| 2026-11-15 | 批次 0063–0068：r4/r5 复判后的修复与处置（r5 基线 `3d7211c`） | 0063 收紧 `source_pages: n/a` 依据；0064–0066 换用成熟 `jsonschema` 并按 r4 四类攻击面验收；0067 让分发产物核对真正执行（`DP-ARTIFACT` 缺失退出 2）；0068 依赖核对改为按 wheel 内 `RECORD` 逐文件重算内容哈希并断言导入路径（`DP-IMPORT`），影子包/`PYTHONPATH`、空实现型 `sitecustomize`、改安装树保留 `RECORD`、同名假 wheel 均阻断（负例 13 项），指针恢复 `$.x`/`$.a.x`/`$.m.<键>`，缺失本地 `$ref` 转 `RM-SCHEMA`，`pattern` 512 字符上限（当时另含嵌套量词启发式，r6 已撤）、schema 嵌套 64 层上限、`RecursionError` 归一，自测 76 → 82 项。G-021 按 r5 条件以 `accepted` 关闭（“2,400 预算”更正为单值路径上限）；新增 G-022（依赖指纹信任边界）并以 `accepted` 关闭；G-019 维持 `open`；G-020 未改。台账 22 条：`open` 3（G-017、G-018、G-019）/ `closed` 19。 |
| 2026-11-15 | 批次 0069：r6 复判三处口径对齐（r6 基线 `bafcb04`） | 撤掉 `pattern` 嵌套量词启发式、只留 512 字符上限（schema 为自写可信资产、非外部输入，回溯不在威胁模型内，ADR-0019 已写明）；官方 semver 正则、dotted-id、dotted-version、list-of-pairs 与 `^(a|aa)+$` 全部放行，依赖启发式的负例删除并改写为“常见写法放行 + 只按长度拒绝”，自测 82 → 83 项；`check_no_raw_material.py` 退出码表述对齐实现——导入失败退 2，导入成功但运行时探测失败为逐文件 24 条 `RM-SCHEMA`/`RM-SCHEMA-LINT` 后退出 1；`sitecustomize` 只替换 `validator_for` 而不阻断属 G-022 声明的信任边界，G-019 改“非针对性替换均阻断”。台账 22 条：`open` 3（G-017、G-018、G-019）/ `closed` 19。 |
| 2026-11-15 | 批次 0070：G-019 关闭（复核 `verify-g019-r7`，sha256 `65e319da…`，基线 `7300283`） | G-019 补最后一处文档口径：`scripts/README.md`、ADR-0019 两处与 `check_dependency_pins.py` docstring 均写明“分发产物存在但不可读取/逐文件数据不可核对应退 2”（同时命中指纹不符与无法核对时按 2；实测同名 `not a wheel` 文件退 2、可读但 sha 不符退 1）；台账改“r6 三处已完成；r7 另有一处退出码文档缺口，已同批勘误”；以 r7 报告 §1/§2/§4 关闭为 `check-change`。G-021、G-022 未动。台账 22 条：`open` 2（G-017、G-018）/ `closed` 20。 |
| 2026-11-15 | 批次 0071：G-018 `actors[].type` 封闭枚举（同源实现，不关闭） | `CHECKER_INPUT_SCHEMA.md` §1.11 增列 `actors[].type` 并写明必填与三个出口（键缺失 → 子句级 `missing_input`；`null` → 入口 `missing_input`；非法值/大小写变体/空字符串 → 子句级 `undefined_enum_value`）及归属 `G-A1#1`/`G-E1#1`/`G-E2#1`；§2 同步必填性，§3 三行补 `undefined_enum_value`，§4 新增 `actor_type` 具名枚举。原型 `enum_results()` 对每个 `actors[]` 元素校验 `type`，结果参与 `aggregate()`、无入口短路；E1/E2 不再用未定义类型推导 `accountable_not_human`。新增负例 A.1.1-8/9/10、A.1.5-5、A.1.10-6（覆盖矩阵 5 条），`--enum-sweep` 4 → 5 项，A.1 样例 61 → 66，`validation/pinned/checker.py` 同步。G-018 维持 `open`，关闭依据留空等非同源复核。台账 22 条：`open` 2（G-017、G-018）/ `closed` 20。 |
| 2026-11-15 | 批次 0072：G-018 按复核报告修复（同源实现，不关闭） | 报告判不可关闭（基线 `0b88547`）。阻断项 1：非字符串 `type`（对象、数组、数字、布尔）改为 `isinstance(value, str)` 守卫后统一给 `undefined_enum_value`，E1/E2 的 `accountable_not_human` 同样只在字符串类型下判定；新增对象型 A.1.1-11、数组型 A.1.11-4（F 类）。阻断项 2：A.2 为 `G-A1#1`/`G-E1#1`/`G-E2#1` 补 `undefined_enum_value`，并把 F 类归属到 `G-F1#2`；A 表 `--write` 重建，`clause_of()` 四个归属均正确。次要项：`failed_clauses()` 缺键/`null` 返回空集；覆盖闸门 note 改为实际检查项并写明 A.1.10-6 走入口归一化。样例 66 → 68、负例 47 → 49。pins 重冻 basis 显式标注覆盖范围缺失。G-018 维持 `open`。台账 22 条：`open` 2（G-017、G-018）/ `closed` 20。 |
| 2026-11-15 | 批次 0073：G-018 r2 复判整改（同源实现，不关闭） | 报告基线 `ea9b674`（`verify-g018-r2`，sha256 `17f63114…`）认可运行时行为，列表示层/归属问题。① `missing_input` 补齐：A.2 `G-A1#1`/`G-E1#1`/`G-E2#1` 原因码列与子句条件、schema §3 三行同步，A 表 `--write` 重建；`clause_of()` 三者返回正确子句，F1 返回 `None`。② 撤回 `G-F1#2` 归属：A.2/schema §3/§1.11 复原，`ACTOR_TYPE_CLAUSES` 删 F1；A.1.11-4 移入 `global_normalization`。③ 覆盖闸门规则 6 改为“被子句或全局分区之一引用”，新增生产 `evaluate_trace()`、删除 `failed_clauses()`、子句负例须真实违反、新增 `(reason, clause)` 登记检查；只改验证工具，按方法 §9 不需 ADR。④ pins 仅 `#4` 用 r2 报告重冻，其余保持“未审查本批”占位待 r3。覆盖矩阵：子句 41、正例 43、负例 47、全局归一化 2、样例 68。G-018 维持 `open`。台账 22 条：`open` 2（G-017、G-018）/ `closed` 20。 |

## 临时性与撤除

本台账是过渡机制，不是永久治理结构。**撤除条件**（全部满足）：

1. 连续两个发布点，`python3 scripts/check_gap_ledger.py` 报告 `open=0`，且核查矩阵 17/17 为 `consistent`；
2. 第二个发布周期内没有新增缺口；
3. 裁定方完成一次全量“规则正文 ↔ 判定列”对照，确认无 `rule-stricter` 遗留。

**硬约束**：不晚于 M3 关闭前评估撤除；若 M3 关闭时仍有 `open` 缺口，机制冻结——新增缺口须经 ADR，所有 `open` 缺口必须在 M4 前裁定。

**撤除动作**：删除本文件与 `scripts/check_gap_ledger.py`；移除 `AGENTS.md` 3.6、7bis 的钩子项与 `check_state.py` 的调用；`TODO.md` T-132 标 `done` 并记 CHANGELOG。
