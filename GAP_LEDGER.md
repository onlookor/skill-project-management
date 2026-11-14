# 缺口台账

**用途**：登记“规则正文与 `check_id` 判定列不一致”的缺口，给出分级、到期与处置出口。本文件是缺口的唯一台账；变更历史见 `CHANGELOG.md`，工作项状态见 `TODO.md`。

**当前里程碑**：M1

**性质**：临时治理机制，撤除条件见文末；规则出处 `AGENTS.md` 3.6，决策记录 `adr/0012-gap-ledger-and-adjudication.md`。

## 入口条件

满足任一条件即**必须**登记为缺口，不得只留在讨论或提交信息里：

- `undefined-object`：规则或判定列引用了输入 schema 未定义的节点类型、关系或字段。
- `rule-stricter`：规则正文包含判定列未覆盖的规范性条件（例如“且”“附带”“不得”引出的条件）。
- `severity-mismatch`：判定列的实际 severity 与 `validation/CHECKLIST.md` 不一致。

**机械保证**：下方的核查矩阵必须逐行覆盖 A 表全部 `check_id`，结论只能是 `consistent` 或缺口编号；任何对 `GRAMMAR.md` 或 `spec/methods/deterministic-checker.md` 判定列的改动，必须在同一提交更新本文件，否则 `scripts/check_gap_ledger.py --staged` 退出 1。`rule-stricter` 与 `severity-mismatch` 的语义判断仍由人工复核，但“未复核”不再可能静默通过。

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
| `PROJECT_MINIMAL_EXISTENCE` | G-A1 | `consistent` | M1 |
| `CONSTRAINT_ANCHOR_REQUIRED` | G-A2 | `consistent` | M1 |
| `DUAL_DIMENSION_ANNOTATION` | G-B1 | `consistent` | M1 |
| `DIMENSION_VALUE_CLOSED` | G-B2 | `consistent` | M1 |
| `DELIVERABLE_ASSERTION_LINK` | G-C1 | `consistent` | M1 |
| `ASSERTION_MUTUAL_EXCLUSION` | G-C2 | `consistent` | M1 |
| `CHANGE_CONSTRAINT_LINK` | G-D1 | `consistent` | M1 |
| `ALL_IMPROVEMENT_ASSUMPTION` | G-D2 | `consistent` | M1 |
| `ROLE_MINIMAL_COMPLETENESS` | G-E1 | `consistent` | M1 |
| `AI_AUTONOMY_DELEGATION_AUDITABLE` | G-E2 | `consistent` | M1 |
| `PROJECT_CHARTER_EXISTENCE` | G-F1 | `consistent` | M1 |
| `CLOSURE_ACCEPTANCE_LINK` | G-F2 | `consistent` | M1 |
| `PROCUREMENT_CONTRACT_ANCHOR` | G-F3 | `consistent` | M1 |
| `SCHEDULE_EVIDENCE_LINK` | G-F4 | `consistent` | M1 |
| `TAILORING_RECORD_EXISTENCE` | G-G1 | `consistent` | M1 |
| `TAILORING_NON_TRIMMABLE_SET` | G-G2 | `consistent` | M1 |
| `TAILORING_REASSESSMENT_CONDITION` | G-G3 | `consistent` | M1 |

## 缺口账

| 编号 | 状态 | 成因 | 等级 | 影响面 | 是否阻断 | 待裁定方 | 登记里程碑 | 处置出口 | 关联 T | 说明 |
|---|---|---|---|---|---|---|---|---|---|---|
| G-001 | closed | undefined-object | L3 | G-A2、G-D2、G-E1 | 否 | 架构负责人 | M1 | check-change | — | ADR-0013 D0 / D2 / D5 / D9 已把原“未定义的判定对象”全部落为具名字段：G-A2 的管理活动/产物 = `management_items[].node_type`；G-D2 的批准依据 = `approval_basis`；G-E1 的决策类筛选 = `commitments[].decision_class`（输入已筛选，schema §1.4）。 |
| G-002 | closed | rule-stricter | L2 | G-A1 | 否 | 架构负责人 | M1 | check-change | T-130 | ADR-0013 D9：G-A1 正文的“`Constraint` 作用于该 `Outcome` 或 `Commitment`”以追加子句 `G-A1#6` 纳入 `PROJECT_MINIMAL_EXISTENCE`，失败原因码 `constraint_not_applied`。 |
| G-003 | closed | rule-stricter | L2 | G-E2 | 否 | 架构负责人 | M1 | check-change | T-131 | ADR-0013 D9 + P5：`G-E2#3` 要求 `assertion.kind = assumption` 且 `verification_condition` 非空；缺失分别报 `assertion_incomplete` / `assumption_unclosed`。 |
| G-004 | closed | severity-mismatch | L1 | G-E1 | 否 | 架构负责人 | M1 | check-change | T-100 | ADR-0013 §2.2：改用 A.2 子句级 severity——`G-E1#3`（角色合并声明缺失）为 `warn`，其余 `G-E1` 子句保持 `block`；原型以三元组返回 `missing_role_merge_declaration` / `warn`。 |
| G-005 | closed | rule-stricter | L1 | G-C1 | 否 | 架构负责人 | M1 | check-change | T-134 | ADR-0013 D6：`G-C1#2` 断言内容（`statement` + `statement_kind`）与 `G-C1#3` 的 `about` 反向边纳入判定；原样例 A.1.3-2 的空断言期望被推翻，改为 `fail / assertion_without_content`。 |
| G-006 | closed | rule-stricter | L1 | G-D1 | 否 | 架构负责人 | M1 | check-change | T-135 | ADR-0013 D7：`G-D1` 增加 `target.type ∈ {Commitment, Deliverable}`；缺 `target` 报 `missing_change_target`，类型非法报 `invalid_change_target`。 |
| G-007 | closed | undefined-object | L1 | G-A1、G-A2、G-C1、G-D1 | 否 | 架构负责人 | M1 | check-change | T-136 | ADR-0013 D1–D5 + P2–P7：端点量词（默认全称，引用“存在且全部解析”）、空值三态（缺键/`null` / `{}` / `[]`）、悬空引用 `fail` 与类型未定义 `cannot_evaluate`、`reason` 优先级 `cannot_evaluate > fail`、`about` 构成 C1 出边；并补齐表示规范（封闭枚举、关系路径、assumption 时效、路径可达、适用性状态机）。 |
| G-008 | closed | undefined-object | L2 | 表示层（全局） | 否 | 架构负责人 | M1 | check-change | T-136 | 独立复核报出的八条上层设计问题的合并登记（P1–P8），ADR-0013 同批裁定：P1 子句被压缩 → A.2 子句表；P2 未封闭枚举/自然语言值 → schema §4；P3 跨对象全称/相关性 → schema §1.6–1.7 与 §3bis；P4 引用完整性分散 → schema §1.5 统一策略；P5 assumption 时效与批准资格 → schema §1.9 `assumption` 对象；P6 链/路径/可达性 → schema §1.10；P7 适用性状态机与 `not_applicable` → 方法 §4.4 与 schema §1.11；P8 三表无机械对照 → `scripts/check_three_table.py`。 |

**共同成因**：G-002、G-003、G-004、G-005、G-006 同属 **规则正文严于判定列** 这一大类——判定列只覆盖了规则正文的一部分条件，或把不同严重度的条件压在同一级别。G-002、G-003、G-005、G-006 的成因记为 `rule-stricter`（漏判条件：G-002 漏“约束作用边”、G-003 漏“assumption 形式与验证条件”、G-005 漏“断言内容与 `about` 相关性”、G-006 漏“变更对象的类型谓词”）；G-004 的成因记为 `severity-mismatch`（判定列未区分两种情形，导致合法产物可能被判失败）。它们不是彼此独立的偶发问题，而是同一口径缺陷的不同表现。对应的独立工作项 T-130、T-131、T-100、T-134、T-135 保留原编号，不合并——每条有各自的规则条款与判定列行，可分别裁定。

**与 G-007 的关系**：G-007 是另一类——不是“判定列漏了正文条件”，而是“判定列本身存在未定明的语义”，因此成因记为 `undefined-object`，并合并登记（取舍理由见该行说明）。

**与 G-008 的关系**：G-008 登记的是独立复核报出的八条**表示层**问题（P1–P8），它们不指向某一条规则的具体条款，而是指向“判定层如何被表示”这一层；因此不进入核查矩阵的逐 `check_id` 行，单独成条。P1–P8 与已有关口的对应关系：P1（子句被压缩）与 P2（枚举未封闭）、P3（量词/相关性）、P4（引用完整性）、P5（assumption 时效）、P6（路径表示）、P7（适用性状态机）分别覆盖 G-001–G-007 的语义面；P8（三表无机械对照）是新增机制，由 `scripts/check_three_table.py` 承接。所有九条缺口在 ADR-0013 `accepted` 时以 `check-change` 一次性关闭。

## 核查记录

| 日期 | 事件 | 结论 |
|---|---|---|
| 2026-11-14 | T-107 最小原型跑通 34/34 个样例 | 核查矩阵不变；G-001–G-004 仍为 `open`，原型只在输出中声明“未覆盖规则正文”，不关闭任何缺口 |
| 2026-11-14 | T-133 独立复核（非同源，只读验收包，覆盖 G-A1 / G-C1 / G-D1 共 3 个 `check_id`、6 个样例） | 6/6 判定与预期一致，但一致不等于一致于规则正文：复核指出 G-C1 漏“断言内容与 `about` 相关性”、G-D1 漏“变更对象类型谓词”，并报告 5 处判定列语义未定明。据此登记 G-005、G-006、G-007；核查矩阵由 12/17 降为 10/17 consistent。剩余 14 个 `check_id` 尚未复核，T-133 保持 `in-progress` |
| 2026-11-14 | 起草 `adr/0013-unified-adjudication-of-check-semantics.md`（状态 `draft`） | G-001、G-002、G-003、G-005、G-006、G-007 并入同一次裁定范围；G-004（`severity-mismatch`）不并入，仍按 T-100 单独裁定。裁定门为 T-133 的 17/17 复核完成；裁定门达成前，台账条目的等级、到期与状态均不变 |
| 2026-11-14 | ADR-0013 扩范围为“判定层表示规范”并一次性裁定（`accepted`） | D0–D9 与独立复核报出的 P1–P8 同批出结论：G-001–G-007 全部以 `check-change` 关闭；P1–P8 合并登记为 G-008 并关闭。核查矩阵 17/17 `consistent`，到期 0 |
| 2026-11-14 | 裁定后单次重验（同源，非独立复核） | 原型对改动后的判定列/schema 重跑：34/34 样例、17/17 `check_id` 通过，`COVERAGE_GAPS` 为空；`check_three_table.py` 覆盖三对关系与子句/枚举闭合，退出 0。独立复核会话对同一版本的单次重跑仍待执行，其结论另记 |

## 临时性与撤除

本台账是过渡机制，不是永久治理结构。**撤除条件**（全部满足）：

1. 连续两个发布点，`python3 scripts/check_gap_ledger.py` 报告 `open=0`，且核查矩阵 17/17 为 `consistent`；
2. 第二个发布周期内没有新增缺口；
3. 裁定方完成一次全量“规则正文 ↔ 判定列”对照，确认无 `rule-stricter` 遗留。

**硬约束**：不晚于 M3 关闭前评估撤除；若 M3 关闭时仍有 `open` 缺口，机制冻结——新增缺口须经 ADR，所有 `open` 缺口必须在 M4 前裁定。

**撤除动作**：删除本文件与 `scripts/check_gap_ledger.py`；移除 `AGENTS.md` 3.6、7bis 的钩子项与 `check_state.py` 的调用；`TODO.md` T-132 标 `done` 并记 CHANGELOG。
