# 复核索引：G-018 `actors[].type` 封闭枚举归一化（批次 0071–0075）

**性质：非权威索引，不构成 G-018 的关闭依据。** 本记录只用于规格区段绑定的机械核对；关闭依据以 `GAP_LEDGER.md` 的 G-018 行为准。

- 非同源复核：G-018 第三轮复核（verify-g018-r3，基线 `a9ff5bb`）
- 复核产物：`/home/wgz/projects/skills/2026-11-14/pm-governance-review/verify-g018-r3/REPORT.md`
- sha256：2ce8107766068643d83a94bbbe1844c2c415d6e6c4f39f059f8a8851419602c6
- 复核基线：a9ff5bb
- 结论：认可（r3 逐条核对 `missing_input` 登记、`G-F1#2` 撤回与覆盖闸门，判 G-018 可关闭）
- 区段：`spec/methods/deterministic-checker.md#A.1`
- 区段：`spec/methods/deterministic-checker.md#A.2`
- 区段：`spec/CHECKER_INPUT_SCHEMA.md#3`
- 区段：`validation/checker-prototype/coverage.json`

**r2 重冻区段（本批未改）**：

- 区段：`spec/CHECKER_INPUT_SCHEMA.md#4`（r2 报告 §二确认 §4 的 `actor_type` 与实现一致）

## 批次 0071–0072 的改动（已由 r1/r2 复核）

1. §1.11 增列 `actors[].type`，§2 同步必填性，§3 三行补 `undefined_enum_value`，§4 新增 `actor_type` 枚举。
2. 非字符串 `type` 用 `isinstance(value, str)` 守卫，对象、数组、数字、布尔统一为 `undefined_enum_value`；E1/E2 不再用未定义类型推导 `accountable_not_human`。
3. A.1 新增 A.1.1-8/9/10/11、A.1.5-5、A.1.10-6、A.1.11-4，样例 61 → 68。

## 批次 0073 的修复（已由 r3 复核）

1. **`missing_input` 登记**：A.2 的 `G-A1#1`/`G-E1#1`/`G-E2#1` 原因码列补 `missing_input`，子句条件写明 `type` 必填；schema §3 三行同步；A 表 `--write` 重建；`clause_of()` 三者返回正确子句。
2. **撤回 `G-F1#2` 归属**：删除 `ACTOR_TYPE_CLAUSES` 的 F1 项，A.2/schema §3/§1.11 复原；A.1.11-4 移入 `global_normalization` 分区。
3. **覆盖闸门规则 6**：改为“被子句或 `global_normalization` 分区之一引用”；新增生产 `evaluate_trace()`，删除 `failed_clauses()`；子句负例须真实违反；新增 `(reason, clause)` 登记检查。
4. **pins**：`spec/CHECKER_INPUT_SCHEMA.md#4` 用 r2 报告重冻；其余改动区段在批次 0075 用 r3 报告统一重冻。

## 批次 0075（本批）

1. 按 r3 报告关闭 G-018（`status=closed`，处置出口 `check-change`，附两条 caveat）。
2. 10 条 pins 用 r3 报告重冻；A.2 签收行改指 r3，子句表指纹保持 `b14854847668`。
3. ADR-0014 §4 字段名 `expected_failed_clauses` 更正为 `expected_clause`（doc-only）。
4. pins 默认读取模式改为校验 basis（仓库外产物、sha256、基线、区段、结论词）；`test_coverage_gate.py`、`test_check_table_mutations.py` 与 `validate_ontology.py --matrix` 接入 pre-commit；`rdflib`/`pyshacl` 纳入依赖指纹。
