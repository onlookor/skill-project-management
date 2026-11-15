# 原始资料防线换轴授权记录（批次 0052）

- 非同源复核：用户授权（parent session `6af45947fead009e7bdd1e76`，批次 0052），2026-11-15；依据 r2 复核 `/home/wgz/projects/skills/2026-11-14/pm-governance-review/verify-g019-r2/REPORT.md` 与方案 `spec/RAW_MATERIAL_ADMISSION.md`
- 区段：`CONSTITUTION.md` 第 13.3/13.5 条
- 复核产物：`CONSTITUTION.md`；`adr/0018-raw-material-admission-control.md`；`scripts/check_no_raw_material.py`
- 复核基线：`2d0c0ea`
- 结论：认可

## 授权内容

用户批准 `spec/RAW_MATERIAL_ADMISSION.md` 第 13.2 节的全部 10 条待批决策，按方案建议执行：

- **D-1**：未归类路径 fail-closed；数据区未登记文件同样阻断，不降级为按文本扫描。
- **D-2**：撤销散文区形态判据，写入第 13 条与 ADR。
- **D-3**：认定删去的形态判据不构成实质性降低——`RM-PROSEBLOCK` 与 `RM-PAGEDUMP` 实测漏杀与误杀并存，`RM-PAGEDUMP` 真实召回 4/15，整页单条与切块均 0 命中；按第 5 条特殊程序在 13.5 增补裁定句。
- **D-4**：字段配额按方案第 4.3 节（`definition` 2000 / `provenance_note` 800 / 单条 2500 / 单文件 20 KiB / 身份键 120 / `relations` 120 / `evidence` 200 / `candidate_iri_reason` 400）。
- **D-5**：schema 放 `contracts/schema/*.schema.json`，纳入 `spec-pins`。
- **D-6**：一次性全仓过检；0 违规即收敛为“不设豁免期”，有违规才登记 `validation/exemptions/<批次>.md`，且不得用于原始资料。
- **D-7**：外部指纹方案只记方向不定时点，与 ADR-0015 同批外置。
- **D-8**：子模块按“显式声明不纳入”写入 G-020，注明当前 0 gitlink、无 `.gitmodules`。
- **D-9**：`ontology/` 归 O，`ontology/fixtures/manifest.json` 归 D。
- **D-10**：登记 G-021（`representation-defect` / L3 / 出口倾向 `accepted`）。

## 边界

本记录是用户授权与裁定的转录，用于检查器哈希绑定与规格区段绑定核对；它不构成 G-019、G-020、G-021 的关闭依据（`AGENTS.md` 3.6.6），也不代表复核方对实现做了逐行代码审查。三条缺口均维持 `open`，关闭依据留空，待非同源复核。
