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
| `PROJECT_MINIMAL_EXISTENCE` | G-A1 | `G-002` | M1 |
| `CONSTRAINT_ANCHOR_REQUIRED` | G-A2 | `G-001` | M1 |
| `DUAL_DIMENSION_ANNOTATION` | G-B1 | `consistent` | M1 |
| `DIMENSION_VALUE_CLOSED` | G-B2 | `consistent` | M1 |
| `DELIVERABLE_ASSERTION_LINK` | G-C1 | `consistent` | M1 |
| `ASSERTION_MUTUAL_EXCLUSION` | G-C2 | `consistent` | M1 |
| `CHANGE_CONSTRAINT_LINK` | G-D1 | `consistent` | M1 |
| `ALL_IMPROVEMENT_ASSUMPTION` | G-D2 | `G-001` | M1 |
| `ROLE_MINIMAL_COMPLETENESS` | G-E1 | `G-001`, `G-004` | M1 |
| `AI_AUTONOMY_DELEGATION_AUDITABLE` | G-E2 | `G-003` | M1 |
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
| G-001 | open | undefined-object | L3 | G-A2、G-D2、G-E1 | 否 | 架构负责人 | M1 |  | — | 规则引用了注册表未定义的判定对象：G-A2 的“管理活动/产物”节点类型、G-D2 的“批准依据”关系、G-E1 的“决策类 `Commitment`”筛选谓词均未在输入 schema 中定义。原型可按输入约定实现，但不得宣称全保真。 |
| G-002 | open | rule-stricter | L2 | G-A1 | 是（全保真） | 架构负责人 | M1 |  | T-130 | G-A1 正文的“`Constraint` 作用于该 `Outcome` 或 `Commitment`”未进入 `PROJECT_MINIMAL_EXISTENCE` 判定列。 |
| G-003 | open | rule-stricter | L2 | G-E2 | 是（全保真） | 架构负责人 | M1 |  | T-131 | G-E2 正文的“该 `Assertion` 以 `assumption` 形式存在并附带验证条件”未进入 `AI_AUTONOMY_DELEGATION_AUDITABLE` 判定列。 |
| G-004 | open | severity-mismatch | L1 | G-E1 | 是 | 架构负责人 | M1 |  | T-100 | `ROLE_MINIMAL_COMPLETENESS` 把“角色合并声明缺失”与“问责结构根本性缺失”混为同一 severity，可能把合法产物判为失败。 |

**共同成因**：G-002、G-003、G-004 同属 **规则正文严于判定列** 这一大类——判定列只覆盖了规则正文的一部分条件，或把不同严重度的条件压在同一级别。G-002、G-003 的成因记为 `rule-stricter`（漏判条件）；G-004 的成因记为 `severity-mismatch`（判定列未区分两种情形，导致合法产物可能被判失败），但三者不是彼此独立的偶发问题，而是同一口径缺陷的不同表现。对应的独立工作项 T-130、T-131、T-100 保留原编号，不合并。

## 临时性与撤除

本台账是过渡机制，不是永久治理结构。**撤除条件**（全部满足）：

1. 连续两个发布点，`python3 scripts/check_gap_ledger.py` 报告 `open=0`，且核查矩阵 17/17 为 `consistent`；
2. 第二个发布周期内没有新增缺口；
3. 裁定方完成一次全量“规则正文 ↔ 判定列”对照，确认无 `rule-stricter` 遗留。

**硬约束**：不晚于 M3 关闭前评估撤除；若 M3 关闭时仍有 `open` 缺口，机制冻结——新增缺口须经 ADR，所有 `open` 缺口必须在 M4 前裁定。

**撤除动作**：删除本文件与 `scripts/check_gap_ledger.py`；移除 `AGENTS.md` 3.6、7bis 的钩子项与 `check_state.py` 的调用；`TODO.md` T-132 标 `done` 并记 CHANGELOG。
