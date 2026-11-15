# 复核索引：G-018 `actors[].type` 封闭枚举归一化（批次 0071）

**性质：非权威索引，不构成 G-018 的关闭依据。** 本记录只用于规格区段绑定的机械核对；G-018 在 `GAP_LEDGER.md` 中维持 `open`，关闭依据留空，等针对本次改动的非同源复核。

- 非同源复核：G-019 第七轮复核（基线 `7300283`），本批在其确认的基线上实施 G-018；该报告未审查本批改动，其结论不外推到 `actors[].type`
- 复核产物：`/home/wgz/projects/skills/2026-11-14/pm-governance-review/verify-g019-r7/REPORT.md`
- sha256：65e319da5b5e3a511b5d8dbf6b3f45f1ddbc9f86e8a4a86c17b4121cea20dacb
- 复核基线：7300283
- 结论：认可（“认可”指接受 r7 报告确定的基线口径；本批改动的验收仍待 G-018 非同源复核）
- 区段：`spec/methods/deterministic-checker.md#A.1`
- 区段：`spec/CHECKER_INPUT_SCHEMA.md#3`
- 区段：`spec/CHECKER_INPUT_SCHEMA.md#4`
- 区段：`validation/checker-prototype/coverage.json`

## 改动摘要

1. `CHECKER_INPUT_SCHEMA.md` §1.11 增列 `actors[].type`，写明必填与缺失/非法两个出口；§2 同步必填性。
2. §3 的 `PROJECT_MINIMAL_EXISTENCE`、`ROLE_MINIMAL_COMPLETENESS`、`AI_AUTONOMY_DELEGATION_AUDITABLE` 三行补 `undefined_enum_value`。
3. §4 新增 `actor_type` 具名枚举（`HumanActor`、`LegalEntity`、`AIActor`）。
4. A.1 新增 5 个样例：A.1.1-8（非法值）、A.1.1-9（大小写变体）、A.1.1-10（空字符串）、A.1.5-5（缺失键）、A.1.10-6（`null`）。
5. `coverage.json` 为上述 5 条补 `expected_failed_clauses`：三条指向 `G-A1#1`，一条指向 `G-E1#1`，一条指向 `G-E2#1`。

## 待复核项

- `enum_results()` 是否确实以子句级结果参与 `aggregate()`，且未用入口归一化短路（对照 G-014 的教训）。
- 缺失键 / `null` / 非法值三类输入的 reason code 是否分别为 `missing_input` / `missing_input` / `undefined_enum_value`，与 G-001/G-003/G-007 口径一致。
- `ROLE_MINIMAL_COMPLETENESS` 与 `AI_AUTONOMY_DELEGATION_AUDITABLE` 是否不再用未定义类型推导 `fail`。
- A.1 样例与覆盖矩阵是否互相闭合，A 表由 `check_three_table.py --write` 生成且无手改。
