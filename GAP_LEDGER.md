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
| `PROJECT_MINIMAL_EXISTENCE` | G-A1 | `G-002`, `G-007` | M1 |
| `CONSTRAINT_ANCHOR_REQUIRED` | G-A2 | `G-001`, `G-007` | M1 |
| `DUAL_DIMENSION_ANNOTATION` | G-B1 | `consistent` | M1 |
| `DIMENSION_VALUE_CLOSED` | G-B2 | `consistent` | M1 |
| `DELIVERABLE_ASSERTION_LINK` | G-C1 | `G-005`, `G-007` | M1 |
| `ASSERTION_MUTUAL_EXCLUSION` | G-C2 | `consistent` | M1 |
| `CHANGE_CONSTRAINT_LINK` | G-D1 | `G-006`, `G-007` | M1 |
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
| G-005 | open | rule-stricter | L1 | G-C1 | 是 | 架构负责人 | M1 |  | T-134 | G-C1 正文要求“`Assertion` 的内容必须是关于该交付物‘是什么、处于什么状态、满足什么条件’的明确陈述”，判定列只检查 `asserted_by` 边存在，未检查断言内容，也未检查 `about` 是否指向该交付物。证据：样例 A.1.3-2 的断言只有 `id`、无任何内容，仍期望 `pass`；按正文应判 `fail`。 |
| G-006 | open | rule-stricter | L1 | G-D1 | 是 | 架构负责人 | M1 |  | T-135 | G-D1 正文限定“对 `Commitment` 或 `Deliverable` 的变更提议”，判定列对任何变更提议生效，缺少 `target` 对象类型谓词。证据：变更带 `target: some_deliverable`（非 `Commitment`/`Deliverable`）时，原型与复核实现都判 `pass`。 |
| G-007 | open | undefined-object | L1 | G-A1、G-A2、G-C1、G-D1 | 是 | 架构负责人 | M1 |  | T-136 | 判定列语义未定明（合并登记，避免五条同源条目重复占用裁定带宽）：(1) 端点量词——`Commitment` 的 `by`/`to` 是“每个”还是“存在一个”；(2) 空对象语义——`{}` 与缺键、空列表的区分；(3) 悬空引用的原因码——是 `fail` 还是 `cannot_evaluate`；(4) 多违规时 `reason` 的优先级；(5) `about` 反向引用是否构成 C1 的“出边”。复核已观察到两套实现在这些点上的分歧，按 L1 计（存在错判并阻断独立复核）。 |

**共同成因**：G-002、G-003、G-004、G-005、G-006 同属 **规则正文严于判定列** 这一大类——判定列只覆盖了规则正文的一部分条件，或把不同严重度的条件压在同一级别。G-002、G-003、G-005、G-006 的成因记为 `rule-stricter`（漏判条件：G-002 漏“约束作用边”、G-003 漏“assumption 形式与验证条件”、G-005 漏“断言内容与 `about` 相关性”、G-006 漏“变更对象的类型谓词”）；G-004 的成因记为 `severity-mismatch`（判定列未区分两种情形，导致合法产物可能被判失败）。它们不是彼此独立的偶发问题，而是同一口径缺陷的不同表现。对应的独立工作项 T-130、T-131、T-100、T-134、T-135 保留原编号，不合并——每条有各自的规则条款与判定列行，可分别裁定。

**与 G-007 的关系**：G-007 是另一类——不是“判定列漏了正文条件”，而是“判定列本身存在未定明的语义”，因此成因记为 `undefined-object`，并合并登记（取舍理由见该行说明）。

## 核查记录

| 日期 | 事件 | 结论 |
|---|---|---|
| 2026-11-14 | T-107 最小原型跑通 34/34 个样例 | 核查矩阵不变；G-001–G-004 仍为 `open`，原型只在输出中声明“未覆盖规则正文”，不关闭任何缺口 |
| 2026-11-14 | T-133 独立复核（非同源，只读验收包，覆盖 G-A1 / G-C1 / G-D1 共 3 个 `check_id`、6 个样例） | 6/6 判定与预期一致，但一致不等于一致于规则正文：复核指出 G-C1 漏“断言内容与 `about` 相关性”、G-D1 漏“变更对象类型谓词”，并报告 5 处判定列语义未定明。据此登记 G-005、G-006、G-007；核查矩阵由 12/17 降为 10/17 consistent。剩余 14 个 `check_id` 尚未复核，T-133 保持 `in-progress` |

## 临时性与撤除

本台账是过渡机制，不是永久治理结构。**撤除条件**（全部满足）：

1. 连续两个发布点，`python3 scripts/check_gap_ledger.py` 报告 `open=0`，且核查矩阵 17/17 为 `consistent`；
2. 第二个发布周期内没有新增缺口；
3. 裁定方完成一次全量“规则正文 ↔ 判定列”对照，确认无 `rule-stricter` 遗留。

**硬约束**：不晚于 M3 关闭前评估撤除；若 M3 关闭时仍有 `open` 缺口，机制冻结——新增缺口须经 ADR，所有 `open` 缺口必须在 M4 前裁定。

**撤除动作**：删除本文件与 `scripts/check_gap_ledger.py`；移除 `AGENTS.md` 3.6、7bis 的钩子项与 `check_state.py` 的调用；`TODO.md` T-132 标 `done` 并记 CHANGELOG。
