# 自建本体

**状态**：`active`（目录级默认值见 `STATE.md`）。全量本体已落盘，形状与负例校验通过。

**性质**：自建本体是**派生工件**，不是来源。它不得作为 `grounding_ref`，也不得直接充当规则依据；`validation/CHECKLIST.md` 仍是人类可读的权威投影。

## 文件

| 文件 | 内容 | 规模 |
|---|---|---|
| `pmbok8-vocab.ttl` | 类、对象属性、数据类型属性；定义自写，英中标签 | 92 类 / 35 对象属性 / 7 数据类型属性 |
| `pmbok8-processes.ttl` | 绩效域、焦点区、过程与 I/O 链接 | 7 域 / 5 焦点区 / 40 过程 |
| `pmbok8-artifacts.ttl` | 工件个体，按计划、基线、登记册、报告、数据、文档分类 | 124 |
| `pmbok8-tools.ttl` | 工具与技术条目，按用途分类 | 185 |
| `pmbok8-shapes.ttl` | SHACL 形状，约束本体自身的结构 | 24 |
| `fixtures/valid.ttl` | 通过全部形状的最小图 | 1 |
| `fixtures/invalid-*.ttl` | 每条形状一个违规图 | 24 |
| `ontology/fixtures/manifest.json` | 形状到 fixture 与报告消息的映射 | — |

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
- **写不出定义时**：只保留术语名与页码，标 `definition_status: "pending"`，不要用原文改写凑数。当前工件与工具个体为 `taxonomy-only`，补全工作见 `TODO.md` T-126。
- **判定问题**：删去原作后，读者能否仅凭本体重建该来源的表达？能则不合法。

## 检查

提交前运行：

```bash
python3 scripts/check_no_raw_material.py
python3 scripts/validate_ontology.py --matrix
```

本目录下的文件仍受体积、二进制、乱码、控制字符、点线、页码序列检查，并额外受以下规则约束：

| 规则码 | 判定 |
|---|---|
| `RM-ONTO-HEADER` | `.ttl` 缺少 `self-authored` 或 `source_id` 头注释 |
| `RM-ONTO-LITERAL` | 单个字符串/三引号字面量超过 400 字符 |
| `RM-ONTO-COMMENT` | 单行 `#` 注释超过 400 字符 |
| `RM-PROSEBLOCK` | 连续 12 行以上注释每行不少于 80 字符（PDF 文本换行后的段落形态） |

`validate_ontology.py` 是可选校验：缺少 `rdflib` 或 `pyshacl` 时以退出码 2 报“无法评估”，不静默通过；本体不是项目的运行前提。

## 定位

本体只约束自身的结构，不改 `GRAMMAR.md` 的 `grounding_ref`，不改任何 `check_id` 的绑定。若将来要接成 `grounding_ref`，候选规则与知识条目见 `TODO.md` T-125；接入前须先做“形状 ↔ 规则文本”的逐条对照（P1c）。
