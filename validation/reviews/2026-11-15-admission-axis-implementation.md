# 原始资料防线换轴实现记录（批次 0053）

- 非同源复核：用户授权（parent session `6af45947fead009e7bdd1e76`，批次 0053），2026-11-15；授权范围见 `validation/reviews/2026-11-15-admission-axis-authorization.md`
- 区段：contracts/schema/knowledge-entry.schema.json
- 区段：contracts/schema/pilot-conflict.schema.json
- 复核产物：`spec/ACCESS_ZONES.md`；`contracts/schema/knowledge-entry.schema.json`；`contracts/schema/pilot-conflict.schema.json`；`scripts/check_no_raw_material.py`
- 复核基线：`debe35b`
- 结论：认可

## 实现内容

按已批准的 D-1–D-10 落地阶段二，不扩大授权范围：

1. 新增 `spec/ACCESS_ZONES.md`：路径前缀归区表（D/O/P/C 与 P0–P2 分级）与数据区准入登记表；未归类路径 fail-closed，数据区未登记文件报 `RM-SCHEMA`，不降级为文本扫描。
2. 新增 `contracts/schema/knowledge-entry.schema.json`（anchored 与 pilot 共用，含 D2/D3/D7/M3-E1 字段）与 `contracts/schema/pilot-conflict.schema.json`；两者纳入 `spec-pins`。
3. 重写 `scripts/check_no_raw_material.py`：按区执行硬约束、schema 与字段配额；删除 `RM-PROSEBLOCK`、`RM-PAGEDUMP`、`RM-PAGESEQ`；新增 `RM-ZONE`、`RM-SCHEMA`、`RM-FIELD`；`RM-ONTO-LITERAL` 对 `skos:definition`/`rdfs:comment`/`dcterms:description` 放宽到 2000，其他字面量 400；`RM-ONTO-COMMENT` 放宽到 800。
4. 自测按新轴重建为 30 项合成用例，不保留已退役启发式的样例；`--self-test` 只返回 0/1，不依赖 PDF 资源，不存在“无法评估即通过”的路径。
5. `.githooks/pre-commit` 增加 `--self-test`；`scripts/README.md` 同步新规则表、退出码与归区说明。

## 边界

本记录是把用户授权转写为实现批次依据，供检查器指纹与规格区段绑定核对；它不是对实现的逐行审查，也不构成 G-019、G-020、G-021 的关闭依据。三条缺口维持 `open`，待非同源复核。全仓过检与豁免判定在阶段三单独记录。
