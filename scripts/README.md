## 辅助脚本

**性质**：本目录存放技能的辅助检查脚本及其规格。`check_state.py`、`check_ledger_landings.py` 与 `check_anchors.py` 已实现且可直接运行；`check_glossary_sync` 仍为规格，实现登记于 `TODO.md` T-090。

### 脚本清单

| 脚本 | 用途 | 规格文件 | 实现状态 |
|---|---|---|---|
| `check_state.py` | 以 `git ls-files` 核对 `STATE.md`：漏登、登了不存在的文件、状态值非法；并核对 `manifest.json` 的 `package_version` / `release_tag` 与最新 annotated tag 一致，且该 tag 指向 `HEAD` | 无独立规格（规则见 `STATE.md` 与本文件“脚本的定位”） | 已实现 |
| `check_ledger_landings.py` | 核对 `SOURCE_LEDGER.md` 每个 active 来源条目是否声明编译落点，且落点在 `GRAMMAR.md`、`knowledge/`、方法条目或检查项中真实存在 | 无独立规格（规则见 `CONSTITUTION.md` 第 2.6 条） | 已实现 |
| `check_anchors.py` | 解析并校验全仓锚点：禁止行号 locator、文件/稳定 ID/章节号/标题路径可解析、`grounding_ref` 指向 active 来源、规则与来源文本块指纹未漂移 | `spec/ANCHOR_SPEC.md` | 已实现 |
| `anchor_baseline.json` | `check_anchors.py` 的指纹基线（`rule:*` 与 `source:*`），内容变更后重冻 | `spec/ANCHOR_SPEC.md` 第 5 节 | 数据文件 |
| `check_glossary_sync` | 检查 `GLOSSARY.md` 的 A 类条目与 `knowledge/anchored-entries.jsonl` 的定义一致性 | `check_glossary_sync.md` | 未实现（T-090） |
| `check_no_raw_material.py` | 阻断式检查：已跟踪文件中不得出现原始资料（PDF/EPUB/扫描件等）、文本层/OCR 转储与成段原文；允许受控的自建本体（`CONSTITUTION.md` 第 13.6 条） | `CONSTITUTION.md` 第 13 条 | 已实现 |
| `validate_ontology.py` | 用 `rdflib` + `pyshacl` 校验 `ontology/` 本体与 24 条 SHACL 形状；`--matrix` 逐条运行违规 fixture，确认每条形状能判出违规 | 无独立规格（边界见 `CONSTITUTION.md` 第 13.6 条与 `ontology/README.md`） | 已实现（可选依赖） |

### 运行方式

```
python3 scripts/check_state.py
python3 scripts/check_ledger_landings.py
python3 scripts/check_anchors.py
python3 scripts/check_no_raw_material.py
python3 scripts/validate_ontology.py --matrix
```

`validate_ontology.py` 退出码：`0` 通过；`1` 出现非预期结果（本体不通过或某条形状未被 fixture 判出）；`2` 缺少 `rdflib`/`pyshacl` 或结构无法解析——此时必须报“无法评估”，不得视为通过。

`check_state.py` 退出码：`0` 通过；`1` 存在错误（逐条列出）；`2` `STATE.md` 或 `manifest.json` 结构无法解析、缺少字段，或不在 git 仓库中。

`check_ledger_landings.py` 退出码：`0` 通过（可有待落点警告）；`1` 存在错误；`2` 登记表结构无法解析。

`check_anchors.py` 退出码：`0` 通过（可有警告/提示）；`1` 存在错误；`2` 结构或基线无法解析。规则/来源被有意修改后，用 `--write-baseline` 重冻基线，并把基线变更与内容变更同批提交。`--root` 可指向副本，用于插行负例演练。

`check_no_raw_material.py` 退出码：`0` 通过；`1` 发现违规（逐条列出规则码与位置，提交应被阻断）；`2` 不在 git 仓库中。判定规则：

| 规则码 | 判定 |
|---|---|
| `RM-EXT` | 被跟踪文件扩展名属于文档/电子书/扫描件/压缩包 |
| `RM-BINARY` | 文本扩展名下出现 NUL 字节或无法按 UTF-8 解码 |
| `RM-SIZE` | 单文件超过 512 KiB |
| `RM-QUOTE` | 单条引用超过 400 字符，或连续引用块超过 800 字符 |
| `RM-PROSEBLOCK` | 连续 15 行以上每行不少于 100 字符（PDF 文本转储的行形态） |
| `RM-PAGESEQ` | 连续 5 行以上为页码或纯数字 |
| `RM-DOTLEADER` | 单行出现 30 个以上连续点（目录转储） |
| `RM-MOJIBAKE` | 出现 U+FFFD 替换字符 |
| `RM-CONTROL` | 出现除制表符/换行外的 C0 控制字符 |
| `RM-ONTO-HEADER` | `.ttl` 前 40 行缺少 `self-authored` 或 `source_id` 头注释 |
| `RM-ONTO-LITERAL` | 本体文件中的字符串/三引号字面量超过 400 字符 |
| `RM-ONTO-COMMENT` | 本体文件中的单行 `#` 注释超过 400 字符 |

**本体的受控放行**（`CONSTITUTION.md` 第 13.6 条）：`.ttl`、`.shacl.ttl`、`.owl`、`.rdf`、`.nt`、`.n3`、`.jsonld` 允许入库，但**不豁免**体积、二进制、乱码、控制字符、点线、页码序列与长文本检查。本体文件的连续长注释行按 `RM-PROSEBLOCK` 处理（本体适用更严阈值：连续 12 行、每行 80 字符，以覆盖 PDF 换行后的段落形态）；头注释与 provenance 要求见 `ontology/README.md`。放行只针对“自写定义 + 标准术语标签”的本体，不针对原文转录。

提交前接入：`git config core.hooksPath .githooks`（只对当前克隆生效）。未启用钩子时，在 `git add` 前手工运行该脚本，效果等价。检查器命中时不得用 `--no-verify` 绕过；新增例外须走 ADR 并在脚本中登记路径豁免。

### 脚本的定位

- 脚本是**辅助工具**，不是技能的核心规范。它们的缺失不构成技能不完备（`CHARTER.md` 承诺 C4 的延伸）。
- 脚本的执行结果是**证据工件**，可用于 `spec/GROUNDING_CRITERIA.md` G4 的验证。
- 脚本的规格（如 `check_glossary_sync.md`）是**规范性的**——脚本实现必须与规格一致；规格与实现冲突时以规格为准。
