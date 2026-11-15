# 复核索引：G-018 `actors[].type` 封闭枚举归一化（批次 0071–0072）

**性质：非权威索引，不构成 G-018 的关闭依据。** 本记录只用于规格区段绑定的机械核对；G-018 在 `GAP_LEDGER.md` 中维持 `open`，关闭依据留空，等针对修复提交的非同源复核。

- 非同源复核：G-018 第一轮复核（基线 `0b88547`）
- 复核产物：`/home/wgz/projects/skills/2026-11-14/pm-governance-review/verify-g018/REPORT.md`
- sha256：4a72e5a12cfa8795342762e539a4b3108988a2411588a0f9056fc7497e59fb21
- 复核基线：0b88547
- 结论：认可（“认可”指接受报告列出的阻断项与次要项作为本批修复清单；**覆盖范围缺失**：该报告审查的是批次 0071，不覆盖批次 0072 的修复，本记录与 `spec-pins`/`checker-pins` 的 basis 只作指纹登记，不作验收依据）
- 区段：`spec/methods/deterministic-checker.md#A.1`
- 区段：`spec/methods/deterministic-checker.md#A.2`
- 区段：`spec/CHECKER_INPUT_SCHEMA.md#3`
- 区段：`spec/CHECKER_INPUT_SCHEMA.md#4`
- 区段：`validation/checker-prototype/coverage.json`

## 批次 0071 的改动（已被复核）

1. `CHECKER_INPUT_SCHEMA.md` §1.11 增列 `actors[].type`，§2 同步必填性，§3 三行补 `undefined_enum_value`，§4 新增 `actor_type` 枚举。
2. A.1 新增 5 个样例（A.1.1-8/9/10、A.1.5-5、A.1.10-6）。
3. `coverage.json` 为上述样例补 `expected_failed_clauses`。

## 批次 0072 的修复（本轮，待复核）

1. **非字符串 `type` 不再崩溃**：`enum_results()` 用 `isinstance(value, str)` 守卫，对象、数组、数字、布尔一律给 `undefined_enum_value`；E1/E2 的 `accountable_not_human` 也只在字符串类型下判定。
2. **A.2 同步**：`G-A1#1`、`G-E1#1`、`G-E2#1` 原因码列补 `undefined_enum_value`，A 表由 `check_three_table.py --write` 重建；`clause_of()` 对四个归属子句均返回正确 id。
3. **F 类输入覆盖**：`PROJECT_CHARTER_EXISTENCE` 的 `actors[].type` 归属 `G-F1#2`，`G-F1#2` 原因码补 `undefined_enum_value`；新增数组型负例 A.1.11-4。
4. **对象型负例** A.1.1-11；`failed_clauses()` 在必需键缺失/为 `null` 时返回空集，不再抛 `KeyError`。
5. **覆盖闸门措辞**：`coverage.json` 的 note 改为实际检查项，并写明 A.1.10-6 走入口归一化、其子句归属只用于取证。
6. **pins**：本批按用户裁定重冻，basis 指向上述报告并显式标注“覆盖范围缺失”；正确重冻时机为本次修复提交 + 针对该提交的新一轮复核。

## 待复核项

- 非字符串值（对象、数组、数字、布尔）是否全部产出子句级 `undefined_enum_value` 且无异常，含 F/G 类输入。
- `clause_of()` 对 `G-A1#1`/`G-E1#1`/`G-E2#1`/`G-F1#2` 的 `undefined_enum_value` 是否返回正确子句。
- A.1.10-6 的说明是否与生产 `evaluate()` 路径一致。
- 覆盖闸门 note 与实际实现是否一致。
