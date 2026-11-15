# 复核索引：以成熟 JSON Schema 实现替换自写子集（批次 0064，第一段）

**性质：非权威、不构成关闭依据、不构成 basis。** 本文件只是索引；权威依据是下面路径指向的仓库外复核产物与用户裁定。

- 非同源复核：G-019 第四轮复核（基线 `f049f28`）第 3.1–3.2 节指出自写子集的语义失真
- 复核产物：`/home/wgz/projects/skills/2026-11-14/pm-governance-review/verify-g019-r4/REPORT.md`
- sha256：`47b0be71a05d726a690278f2075efb13ed54ee79582176a373e8fb6dd7f74fbb`
- 复核基线：`f049f28`
- 结论：认可（改用成熟实现与依赖指纹由用户 2026-11-15 裁定，复核报告提供失效证据）

## 区段

- 区段：`spec/ACCESS_ZONES.md`

## 本批次改动范围

- 新增 `adr/0019-mature-json-schema-validator.md`：放弃自写子集、两个被否方案、例外范围与撤销条件。
- 新增 `scripts/dependency-pins.json`、`scripts/check_dependency_pins.py`、`scripts/test_dependency_pins.py`：锁定 `jsonschema` 4.26.0、分发产物 sha256（`d489f15263b8d200f8387e64b4c3a75f06629559fb73deb8fdfb525f2dab50ce`）与安装树摘要；负例 9/9。
- `spec/ACCESS_ZONES.md` §2 登记 `scripts/dependency-pins.json`；根 `README.md` 与 `scripts/README.md` 写依赖安装步骤。
- `.githooks/pre-commit` 增加依赖指纹与负例两道检查。

**不构成**：G-019、G-021 的关闭依据；也不证明任何提交者身份。
