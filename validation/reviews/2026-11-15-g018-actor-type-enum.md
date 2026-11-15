# 复核索引：G-018 `actors[].type` 封闭枚举归一化（批次 0071–0073）

**性质：非权威索引，不构成 G-018 的关闭依据。** 本记录只用于规格区段绑定的机械核对；G-018 在 `GAP_LEDGER.md` 中维持 `open`，关闭依据留空，等针对修复提交的非同源复核（r3）。

- 非同源复核：G-018 第二轮复核（基线 `ea9b674`）
- 复核产物：`/home/wgz/projects/skills/2026-11-14/pm-governance-review/verify-g018-r2/REPORT.md`
- sha256：17f631140bc700bf5826a7468f6919e7fc7f65da56302aef9d152b7fd1c1232d
- 复核基线：ea9b674
- 结论：认可（指接受 r2 报告列出的缺陷清单作为本批修复范围；**覆盖范围缺失**：该报告审查的是批次 0072（基线 `ea9b674`），不覆盖批次 0073 的修复，本记录与 `spec-pins`/`checker-pins` 的 basis 只作指纹登记，不作验收依据）
- 区段：`spec/CHECKER_INPUT_SCHEMA.md#4`（r2 报告 §二确认 §4 的 `actor_type` 与实现一致，本批未改该区段；按用户裁定用 r2 报告重冻）

**仅作占位、待 r3 重冻的区段**（r2 报告明确 G-018 不可关闭，本批改动不在其审查范围内，故不预写结论词）：

- 区段：`spec/methods/deterministic-checker.md#A.1`
- 区段：`spec/methods/deterministic-checker.md#A.2`
- 区段：`spec/CHECKER_INPUT_SCHEMA.md#3`
- 区段：`validation/checker-prototype/coverage.json`

## 批次 0071–0072 的改动（已由 r1/r2 复核）

1. §1.11 增列 `actors[].type`，§2 同步必填性，§3 三行补 `undefined_enum_value`，§4 新增 `actor_type` 枚举。
2. 非字符串 `type` 用 `isinstance(value, str)` 守卫，对象、数组、数字、布尔统一为 `undefined_enum_value`；E1/E2 不再用未定义类型推导 `accountable_not_human`。
3. A.1 新增 A.1.1-8/9/10/11、A.1.5-5、A.1.10-6、A.1.11-4，样例 61 → 68。

## 批次 0073 的修复（本轮，待 r3 复核）

1. **`missing_input` 登记**：A.2 的 `G-A1#1`/`G-E1#1`/`G-E2#1` 原因码列补 `missing_input`，子句条件写明 `type` 必填；schema §3 三行同步；A 表 `--write` 重建；`clause_of()` 三者返回正确子句。
2. **撤回 `G-F1#2` 归属**：删除 `ACTOR_TYPE_CLAUSES` 的 F1 项，A.2/schema §3/§1.11 复原；A.1.11-4 移入 `global_normalization` 分区。
3. **覆盖闸门规则 6**：改为“被子句或 `global_normalization` 分区之一引用”；新增生产 `evaluate_trace()`，删除 `failed_clauses()`；子句负例须真实违反；新增 `(reason, clause)` 登记检查。
4. **pins**：`spec/CHECKER_INPUT_SCHEMA.md#4` 用 r2 报告重冻；其余改动区段保持“未审查本批”占位，待 r3。

## 待 r3 复核项

- `clause_of()` 对 `G-A1#1`/`G-E1#1`/`G-E2#1` 的 `missing_input` 是否返回正确子句，`PROJECT_CHARTER_EXISTENCE` 是否返回 `None`。
- `G-F1#2` 是否已不再承接任意 `actors[].type`；A.1.11-4 是否只由 `global_normalization` 消费。
- 覆盖闸门是否以 `evaluate_trace()` 取证、负例是否真实违反、全局分区计数是否与样例一致。
- pins 是否在 r3 报告上完成统一重冻。
