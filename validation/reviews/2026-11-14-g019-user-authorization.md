# G-019 / T-140 修复授权记录

- 非同源复核：用户授权（parent session `6af45947fead009e7bdd1e76`，批次 0049），2026-11-14
- 区段：scripts/check_no_raw_material.py（`RM-PROSEBLOCK`）
- 复核产物：scripts/check_no_raw_material.py；scripts/README.md；GAP_LEDGER.md（G-019）
- 复核基线：`851809f`
- 结论：认可

## 授权内容

用户批准先修 G-019：让按条目铺开的 `knowledge/anchored-entries.jsonl`（15 条以上、每行一条长 JSON）正常通过，同时不放行真正的文本层转储；补“15 条长 JSONL 不报”与“15 行长文本转储仍报”双向负例；修复后不自行关闭 G-019，关闭等非同源复核或人工签收。

## 边界

本记录是用户授权的转录，用于检查器哈希绑定核对；它不构成 G-019 的关闭依据（`AGENTS.md` 3.6.6），也不代表复核方对实现做了逐行代码审查。
