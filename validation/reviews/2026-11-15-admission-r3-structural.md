# 复核索引：G-019 r3 结构性修法（批次 0060）

**性质：非权威、不构成关闭依据、不构成 basis。** 本文件只是索引与转录，记录批次 0060 改动的出处与范围；任何依据判定都必须回到仓库外的复核产物本身。权威依据为下面路径指向的文件，其内容不在本仓库内、不可由本仓库改写。

- 非同源复核：G-019 第三轮复核（基线 `3664b64`）
- 复核产物：`/home/wgz/projects/skills/2026-11-14/pm-governance-review/verify-g019-r3/REPORT.md`
- sha256：`877047e8f825ad905f560fc27bd6b94dd19277edd80a6d44a0912cd6c707f0b0`
- 复核基线：`3664b64`
- 结论：认可（按报告第五节 P0/P1 项执行结构性修法）

## 区段

- 区段：`contracts/schema/knowledge-entry.schema.json`
- 区段：`contracts/schema/pilot-conflict.schema.json`
- 区段：`contracts/schema/pm-slot-contract.schema.json`
- 区段：`contracts/schema/package-manifest.schema.json`
- 区段：`contracts/schema/ontology-fixtures-manifest.schema.json`
- 区段：`contracts/schema/pilot-artifact.schema.json`
- 区段：`contracts/schema/pilot-id-map.schema.json`
- 区段：`spec/ACCESS_ZONES.md`

## 转录要点（只作索引，判定以复核产物为准）

1. 复核指出校验器存在静默降级：`oneOf` 被当 `anyOf`、`$ref` 忽略同级关键字、`contracts/schema/` 未全量入指纹。
2. 复核指出现行配额按整条求和，误杀 3 条假设（3×1400）与 12 条 notes（6200）等合法内容。
3. 复核指出 `pilot-conflicts` 的 `positions` 与 `recorded_fields` 无上限，300×400 与 200×120 可整页进入。

## 本批次改动范围

- schema 完整性 lint（`RM-SCHEMA-LINT`）与关键字白名单；`oneOf` 排他；`$ref` 同级关键字显式失败。
- 散文配额改为按路径上限 + 单条总和兜底；`pilot-conflicts` 补 `maxItems`。
- 7 份 schema 全部通过 lint；新增 12 项自测（含两个正向例与削弱 schema 的负例）。

**不构成**：G-019、G-021 的关闭依据；也不证明任何提交者身份。
