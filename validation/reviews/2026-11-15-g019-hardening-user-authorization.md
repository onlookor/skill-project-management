# G-019 / T-141 二次加固授权记录

- 非同源复核：用户授权（parent session `6af45947fead009e7bdd1e76`，批次 0050），2026-11-15；依据外部复核 `/home/wgz/projects/skills/2026-11-14/pm-governance-review/verify-g019/REPORT.md`
- 区段：scripts/check_no_raw_material.py（`RM-PROSEBLOCK` 豁免、值级判据、键白名单、单行/base64、magic bytes、段落判据、BOM）
- 复核产物：scripts/check_no_raw_material.py；scripts/README.md；GAP_LEDGER.md（G-019、G-020）
- 复核基线：`dcd2240`
- 结论：认可

## 授权内容

用户批准按外部复核拆法继续修 G-019：补齐值级长度上限并复用段落/句长启发式；键白名单或 JSON Schema；全局单行上限与 base64 形态识别；magic bytes 识别、未知扩展名 fail-closed、`.log/.csv/.html/.xml/.tex/.rst/.tsv` 纳入扫描；段落级正文判据；先剥 BOM 再解析。负例按复核最小集补齐，`T-NRM-03` 改为取正文页并排除 `RM-DOTLEADER` 干扰，新增 T-NRM-05/06/07。放宽扫描面前先全仓实测新命中，逐条列误报再处置。另新立 G-020 承接覆盖范围与形态识别层；G-019 修完不自行关闭。

## 边界

本记录是用户授权与外部复核结论的转录，用于检查器哈希绑定核对；它不构成 G-019 的关闭依据（`AGENTS.md` 3.6.6），也不代表复核方对实现做了逐行代码审查。G-019 仍 `open`，关闭依据留空。
