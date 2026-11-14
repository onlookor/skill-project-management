## 辅助脚本

**性质**：本目录存放技能的辅助检查脚本及其规格。除 `check_glossary_sync` 仍为规格（实现登记于 `TODO.md` T-090）外，本目录列出的检查器均已实现且可直接运行。

### 脚本清单

| 脚本 | 用途 | 规格文件 | 实现状态 |
|---|---|---|---|
| `check_state.py` | 以 `git ls-files` 核对 `STATE.md`：漏登、登了不存在的文件、状态值非法；并核对 `manifest.json` 的 `package_version` / `release_tag` 与最新 annotated tag 一致，且该 tag 指向 `HEAD`；`release_state=development` 时仅把“HEAD 领先于 tag”降为警告；`v0.5.2` 起发布提交必须携带 `Hook-Bypass` 三项 trailer | 无独立规格（规则见 `STATE.md`、`AGENTS.md` 3.5 / 3.5.1 与本文件“脚本的定位”） | 已实现 |
| `check_ledger_landings.py` | 核对 `SOURCE_LEDGER.md` 每个 active 来源条目是否声明编译落点，且落点在 `GRAMMAR.md`、`knowledge/`、方法条目或检查项中真实存在 | 无独立规格（规则见 `CONSTITUTION.md` 第 2.6 条） | 已实现 |
| `check_anchors.py` | 解析并校验全仓锚点：禁止行号 locator、文件/稳定 ID/章节号/标题路径可解析、`grounding_ref` 指向 active 来源、规则与来源文本块指纹未漂移 | `spec/ANCHOR_SPEC.md` | 已实现 |
| `anchor_baseline.json` | `check_anchors.py` 的指纹基线（`rule:*` 与 `source:*`），内容变更后重冻 | `spec/ANCHOR_SPEC.md` 第 5 节 | 数据文件 |
| `check_glossary_sync` | 检查 `GLOSSARY.md` 的 A 类条目与 `knowledge/anchored-entries.jsonl` 的定义一致性 | `check_glossary_sync.md` | 未实现（T-090） |
| `check_no_raw_material.py` | 阻断式检查：已跟踪文件中不得出现原始资料（PDF/EPUB/扫描件等）、文本层/OCR 转储与成段原文；允许受控的自建本体（`CONSTITUTION.md` 第 13.6 条） | `CONSTITUTION.md` 第 13 条 | 已实现 |
| `check_gap_ledger.py` | 核查 `GAP_LEDGER.md`：字段枚举、核查矩阵与附录 A 全覆盖、`open` 缺口被矩阵引用、TODO 交叉引用、按里程碑计算到期；`--staged` 要求规则/判定文件与台账同批更新。到期未裁定退出 1 | `AGENTS.md` 3.6、`adr/0012-gap-ledger-and-adjudication.md` | 已实现 |
| `check_three_table.py` | 三表机械对照：正文（规则 → 条款与子句范围）、判定列（`check_id` → 子句与原因码）、输入 schema（`check_id` → 输入域、具名枚举、原因码）。覆盖“正文 ↔ 判定列”“判定列 ↔ schema”“正文 ↔ schema”三对关系，核对子句闭合、枚举封闭、判定列不含叙述性短语、G-B1/G-B2 条件归属、原因码与子句映射。**深度边界**：它保证结构一致与已列举的语义短语规则，不保证规则正文与子句表的全文语义等价 | `adr/0013-unified-adjudication-of-check-semantics.md`、`spec/CHECKER_INPUT_SCHEMA.md` | 已实现 |
| `check_glossary_usage.py` | 从 `git ls-files` 的 Markdown / JSONL 生成每条术语的使用位置基线 `knowledge/glossary-usage.json`，并在 `GLOSSARY.md` 第 4 节生成位置表；默认模式校验位置存在、行号有效、该行含术语、生成块未被手改、术语集合一致。`--write` 重生成 | `AGENTS.md` 5bis.1 | 已实现 |
| `validate_ontology.py` | 用 `rdflib` + `pyshacl` 校验 `ontology/` 本体与 24 条 SHACL 形状；`--matrix` 逐条运行违规 fixture，确认每条形状能判出违规 | 无独立规格（边界见 `CONSTITUTION.md` 第 13.6 条与 `ontology/README.md`） | 已实现（可选依赖） |

### 运行方式

```
python3 scripts/check_state.py
python3 scripts/check_ledger_landings.py
python3 scripts/check_anchors.py
python3 scripts/check_no_raw_material.py
python3 scripts/check_gap_ledger.py
python3 scripts/check_three_table.py
python3 scripts/check_glossary_usage.py
python3 scripts/validate_ontology.py --matrix
```

`check_gap_ledger.py` 退出码：`0` 通过；`1` 结构非法或存在到期未裁定（含规则/判定文件与台账未同批暂存）；`2` 台账或方法注册表无法解析。输出首行给出总数、`open`/`closed`、按级与到期计数、核查矩阵 `consistent` 比例。`--staged` 用于 pre-commit；独立运行时省略该参数。只有 `open` 缺口必须被核查矩阵引用——`closed` 缺口已记录处置出口，不再锚定矩阵，否则矩阵永远无法达到撤除条件要求的 17/17 `consistent`。

`check_three_table.py` 退出码：`0` 通过；`1` 对照失败（规则未映射到 `check_id`、`check_id` 无判定行或无 schema 输入域、子句未被引用、机制术语未定义、判定列含叙述性短语、G-B1 写了枚举条件、G-B2#1 未写枚举、原因码未在 schema 定义或与子句不一致）；`2` 三张表之一无法解析。输出首行给出规则数、`check_id` 数、子句数与 schema 输入域数；失败时逐条列出关系与对象。它是 ADR-0013 的交付物，pre-commit 与 `check_state.py` 双重调用，失败即阻断提交与发布。**它不保证语义闭合**：绿字只表示结构、枚举、子句归属与原因码映射一致；规则正文是否被子句忠实表达，仍须由非同源复核或人工逐条签收（`AGENTS.md` 3.6.6）。

`check_glossary_usage.py` 退出码：`0` 通过（零使用术语只输出警告）；`1` 校验失败（基线中的位置不存在、行号越界、该行不含术语、生成块被手改、术语集合与 `GLOSSARY.md` 不一致）；`2` 无法解析 `GLOSSARY.md` 或基线。`--write` 重生成基线与生成块，位置按 `path:line` 排序且幂等。新增、删除、移动文件或改行后必须 `--write` 并与改动同批提交；该检查器与缺口台账不是平行机制——它只做引用完整性核对，不承担语义裁定。

`validate_ontology.py` 退出码：`0` 通过；`1` 出现非预期结果（本体不通过或某条形状未被 fixture 判出）；`2` 缺少 `rdflib`/`pyshacl` 或结构无法解析——此时必须报“无法评估”，不得视为通过。

`check_state.py` 退出码：`0` 通过（开发态下“HEAD 领先于 tag”只输出警告）；`1` 存在错误（逐条列出）；`2` `STATE.md` 或 `manifest.json` 结构无法解析、缺少字段、`release_state` 非法，或不在 git 仓库中。`release_state` 缺失按 `released` 严格处理；`development` 不豁免 tag 名、版本号、annotated 与祖先关系判断。

发布引导提交的留痕：git 不记录 `--no-verify`，因此 `check_state.py` 改为核查 commit message 中的 `Hook-Bypass: release-bootstrap`、`Hook-Bypass-Reason:`、`Hook-Bypass-Verified:` 三项 trailer。`v0.5.2` 及以后的发布提交缺任一项即错误；非发布提交携带即错误。规则见 `AGENTS.md` 3.5.1，撤除条件见 3.5.2 与 `TODO.md` T-129。

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

提交前接入：每个克隆需自行执行 `git config core.hooksPath .githooks`（只对当前克隆生效）。钩子依次运行七个检查器，任一失败即阻断提交：

```
python3 scripts/check_no_raw_material.py
python3 scripts/check_anchors.py
python3 scripts/check_ledger_landings.py
python3 scripts/check_gap_ledger.py --staged
python3 scripts/check_three_table.py
python3 scripts/check_glossary_usage.py
python3 scripts/check_state.py
```

未启用钩子时，在 `git add` 前手工按上述顺序运行，效果等价。检查器命中时不得用 `--no-verify` 绕过；唯一例外是 `AGENTS.md` 第 3.5 条规定的发布引导提交（tag 只能指向已存在提交），该提交后必须立即打 tag 并复跑七个检查器。新增其他例外须走 ADR 并在脚本中登记路径豁免。

### 脚本的定位

- 脚本是**辅助工具**，不是技能的核心规范。它们的缺失不构成技能不完备（`CHARTER.md` 承诺 C4 的延伸）。
- 脚本的执行结果是**证据工件**，可用于 `spec/GROUNDING_CRITERIA.md` G4 的验证。
- 脚本的规格（如 `check_glossary_sync.md`）是**规范性的**——脚本实现必须与规格一致；规格与实现冲突时以规格为准。
