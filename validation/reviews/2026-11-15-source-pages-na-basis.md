# 复核索引：`source_pages: n/a` 依据收紧（批次 0063）

**性质：非权威、不构成关闭依据、不构成 basis。** 本文件只是索引；权威依据是下面路径指向的仓库外复核产物与用户裁定。

- 非同源复核：G-019 第三轮复核（基线 `3664b64`）——第四节第 4 项要求 `source_pages` 头字段
- 复核产物：`/home/wgz/projects/skills/2026-11-14/pm-governance-review/verify-g019-r3/REPORT.md`
- sha256：`877047e8f825ad905f560fc27bd6b94dd19277edd80a6d44a0912cd6c707f0b0`
- 复核基线：`3664b64`
- 结论：认可（`n/a` 依据要求本身来自用户 2026-11-15 裁定，不由复核报告单独推出）

## 区段

- 区段：`spec/ACCESS_ZONES.md`

## 本批次改动范围

- `source_pages: n/a` 须同时给出 `source_pages_basis:`：非空、非占位符、含仓库内真实存在的 `adr/NNNN-*.md` 引用，并在 ADR 引用之外另有自写理由。
- 缺 `source_pages_basis:` 由 `RM-ONTO-HEADER` 阻断；写了但不可核验由 `RM-ONTO-PROVENANCE` 阻断，且该 `n/a` 不解除逐块页码义务。`n/a` 与正文页码值矛盾的旧判据保留。
- `ontology/pmbok8-vocab.ttl`、`ontology/pmbok8-shapes.ttl` 补齐依据（引用 `adr/0010-self-authored-ontology-in-git.md`）。
- 自测 58 → 65 项：无依据、空串、占位符、ADR 不存在均阻断；有依据放行；矛盾仍阻断。

**不构成**：G-019、G-021 的关闭依据；也不证明任何提交者身份。
