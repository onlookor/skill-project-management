# 自建本体

**状态**：`skeleton`（目录级默认值见 `STATE.md`）。本目录当前只有本说明，尚无本体文件。

**性质**：自建本体是**派生工件**，不是来源。它不得作为 `grounding_ref`，也不得直接充当规则依据；`validation/CHECKLIST.md` 仍是人类可读的权威投影。

## 允许的形态

| 项 | 规定 |
|---|---|
| 主格式 | Turtle：`*.ttl`、`*.shacl.ttl` |
| 生成导出 | `.owl`、`.rdf`、`.nt`、`.n3`、`.jsonld` 可入库，但受同一内容检查；发生冲突时以 `.ttl` 为准 |
| 存放位置 | 只放本目录；不得散落到 `spec/`、`knowledge/` 或其他目录 |
| 头注释 | 每个 `.ttl` 前 40 行必须含 `# self-authored: true`、`# source_id: <id>`、`# source_pages: <定位>` |
| 术语 provenance | 每个类/属性/个体带 `dcterms:source` 与 `pm:sourcePage` |

## 内容边界

依据 `CONSTITUTION.md` 第 13.6 条：

- **可写**：标准术语名作标签；层级、归属、输入/输出等结构事实；印刷页/章节定位；自写的一句话定义。
- **不可写**：逐句对应原文的改写或同义替换；原文段落、项目符号列表、表格行、图注；整页转储、OCR 全文、页码序列、目录点线。
- **写不出定义时**：只保留术语名与页码，标 `definition_status: "pending"`，不要用原文改写凑数。
- **判定问题**：删去原作后，读者能否仅凭本体重建该来源的实质内容？能则不合法。

## 检查

提交前运行 `python3 scripts/check_no_raw_material.py`。本目录下的文件仍受体积、二进制、乱码、控制字符、点线、页码序列检查，并额外受以下规则约束：

| 规则码 | 判定 |
|---|---|
| `RM-ONTO-HEADER` | `.ttl` 缺少 `self-authored` 或 `source_id` 头注释 |
| `RM-ONTO-LITERAL` | 单个字符串/三引号字面量超过 400 字符 |
| `RM-ONTO-COMMENT` | 单行 `#` 注释超过 400 字符 |
| `RM-PROSEBLOCK` | 连续 12 行以上注释每行不少于 80 字符（PDF 文本换行后的段落形态） |

## 当前计划

最小原型（概念骨架 + 8–12 条 SHACL 形状 + 3 个 fixture + 包装脚本）登记于 `TODO.md`；评估结论见 `spec/ONTOLOGY_FEASIBILITY.md`。在原型通过“形状 ↔ 规则文本”逐条对照前，本目录不承载任何规范性内容。
