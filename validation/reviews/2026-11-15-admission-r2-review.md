# 准入制 r2 复核转录索引（批次 0057–0058）

**性质**：非同源复核报告的**仓库内索引件**，非权威、不构成依据、不构成缺口关闭证据；任何 `basis` 只指向下方仓库外产物路径 + sha256 + 基线。本文件可被改写，因此不能被用来自证。

- 非同源复核：`2026-11-14/pm-governance-review/verify-admission`（复核方独立于本仓库实现，按 `CONSTITUTION.md` 第 13 条与 `spec/RAW_MATERIAL_ADMISSION.md` 逐项比对）
- 复核产物：`/home/wgz/projects/skills/2026-11-14/pm-governance-review/verify-admission/REPORT.md`；sha256 `905cf234539cccb916f9096e3e137f12876e24b2fb9c1960a034157ac33aff06`
- 复核基线：`deaac46`
- 结论：认可（换轴方向成立；同时判出程序未闭合、裁定句回避、八项实现缺陷与三处台账口径问题）

## 区段

- 区段：spec/ACCESS_ZONES.md
  - 改动：补 5 个人工维护数据文件的内容 schema；新增 4 份 schema 的登记；本体区检查补页码序列、来源存在性、全扩展名头注释；§6 更正“全部通过 schema”的不成立表述。
  - 改动依据：报告要求归区表与准入登记必须可机械核对，且“只在表里插一行就能换区”必须留痕——本批将本表纳入 `spec-pins` 指纹。
- 区段：contracts/schema/knowledge-entry.schema.json
  - 改动：`relations` 改为 41 键白名单 + `maxProperties: 12`；`evidence` 加 `maxItems: 12` 与 `page` 下界；`claim_mapping` 加 `maxItems: 20`；`definitionStatus` 按 D8 落枚举；`sourcePage` 加下界 1。
  - 改动依据：报告判出键空间与集合长度无限，200 键 `relations`、100 条 `evidence`/`claim_mapping` 均不被阻断。
- 区段：contracts/schema/pm-slot-contract.schema.json
  - 改动：全部字段补 `maxLength` 与 `maxItems`；新增 `x-prose-fields`（`assumption_refs[].statement`、`assumption_refs[].verification.alignment_criterion`）；允许试点契约的 `authoritative`、`evidence_forms`、条目级 `grounding_ref`。
  - 改动依据：报告要求契约 schema 具备值级上限，且 5 万字符 statement 必须被阻断。

## 边界

- 本转录不证明签收人身份，也不关闭 G-019/G-021；`spec-pins` 指纹只证明区段内容一致。
- 报告原文的逐条结论以仓库外文件为准；本文件不复述其证据。
