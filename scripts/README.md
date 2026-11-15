## 辅助脚本

**性质**：本目录存放技能的辅助检查脚本及其规格。除 `check_glossary_sync` 仍为规格（实现登记于 `TODO.md` T-090）外，本目录列出的检查器均已实现且可直接运行。

### 脚本清单

| 脚本 | 用途 | 规格文件 | 实现状态 |
|---|---|---|---|
| `check_state.py` | 以 `git ls-files` 核对 `STATE.md`：漏登、登了不存在的文件、状态值非法；并核对 `manifest.json` 的 `package_version` / `release_tag` 与最新 annotated tag 一致，且该 tag 指向 `HEAD`；`release_state=development` 时仅把“HEAD 领先于 tag”降为警告；`v0.5.2` 起发布提交必须携带 `Hook-Bypass` 三项 trailer | 无独立规格（规则见 `STATE.md`、`AGENTS.md` 3.5 / 3.5.1 与本文件“脚本的定位”） | 已实现 |
| `check_ledger_landings.py` | 核对 `SOURCE_LEDGER.md` 每个 active 来源条目是否声明编译落点，且落点在 `GRAMMAR.md`、`knowledge/`、方法条目或检查项中真实存在 | 无独立规格（规则见 `CONSTITUTION.md` 第 2.6 条） | 已实现 |
| `check_anchors.py` | 解析并校验全仓锚点：禁止行号 locator、文件/稳定 ID/章节号/标题路径可解析、规则 `grounding_ref` 与知识条目 `evidence.source_id` 指向 active 来源、规则与来源文本块指纹未漂移 | `spec/ANCHOR_SPEC.md` | 已实现 |
| `anchor_baseline.json` | `check_anchors.py` 的指纹基线（`rule:*` 与 `source:*`），内容变更后重冻 | `spec/ANCHOR_SPEC.md` 第 5 节 | 数据文件 |
| `check_glossary_sync` | 检查 `GLOSSARY.md` 的 A 类条目与 `knowledge/anchored-entries.jsonl` 的定义一致性 | `check_glossary_sync.md` | 未实现（T-090） |
| `check_no_raw_material.py` | 按目录分区执行原始资料准入（`CONSTITUTION.md` 第 13.3 条）：未归类路径 fail-closed；数据区必须过 schema 与字段配额；散文区只执行硬约束；本体区按 13.6 的谓词分档。形态推断判据（行长/行数/句末标点/空格比例）已退役 | `CONSTITUTION.md` 第 13 条、`spec/ACCESS_ZONES.md` | 已实现 |
| `check_gap_ledger.py` | 核查 `GAP_LEDGER.md`：字段枚举、核查矩阵与附录 A 全覆盖、`open` 缺口被矩阵引用、TODO 交叉引用、按里程碑计算到期；`closed` 的关闭依据必须是 `外部复核：<路径>；sha256：<64hex>`，机械核对路径存在、是文件、哈希一致（`--self-test` 的 E01–E05 为正负例）；`--staged` 要求规则/判定文件与台账同批更新。到期未裁定退出 1 | `AGENTS.md` 3.6 / 3.6.6、`adr/0012-gap-ledger-and-adjudication.md` | 已实现 |
| `check_three_table.py` | 三表机械对照：正文（规则 → 条款与子句范围）、判定列（`check_id` → 子句与原因码）、输入 schema（`check_id` → 输入域、具名枚举、原因码）。覆盖“正文 ↔ 判定列”“判定列 ↔ schema”“正文 ↔ schema”三对关系，核对子句闭合、枚举封闭、判定列不含叙述性短语、G-B1/G-B2 条件归属、原因码与子句映射。**深度边界**：它保证结构一致与已列举的语义短语规则，不保证规则正文与子句表的全文语义等价 | `adr/0013-unified-adjudication-of-check-semantics.md`、`spec/CHECKER_INPUT_SCHEMA.md` | 已实现 |
| `check_coverage_gate.py` | 覆盖闸门：`validation/checker-prototype/coverage.json` 登记 A.2 每个子句的正例与负例，负例必须声明单一 `expected_clause`，闸门用生产 `evaluate_trace()` 核对 verdict/reason 与子句归属（“归属是真的”，不是“归属非空”），并核对样例 reason 已登记在 A.2 该子句的原因码列。入口归一化与无子句的全局枚举样例登记在 `global_normalization` 分区（`expected_clause: null`），不挂子句但必须被消费。缺正/负例、负例改成正例、负例指错子句、全局样例挂子句、样例未被引用均阻断。负例测试见 `test_coverage_gate.py` | `adr/0014-validation-chain-self-attestation.md`、`GAP_LEDGER.md` G-018 | 已实现 |
| `check_checker_pins.py` | 检查器绑定：比对 `scripts/checker-pins.json` 登记哈希与工作区脚本（**含本脚本自身、`.githooks/pre-commit`、验收原型**），改动须 `--write --basis "<非同源复核记录>"`。`basis` 默认模式即校验：`复核产物：` 必须在仓库外真实存在、`sha256：` 实算一致、`复核基线：` 必须是仓库内存在的提交、`区段：` 精确等值且只一条、结论词精确匹配（`不予/未/无法` 前缀无效）；“无复核声明”只对代码内冻结的 `UNREVIEWED_KEYS` 成立，历史基文须**逐字**相等，本批改动须为结构化 `待复核：批次 NNNN …；无复核声明，不构成认可`，前缀文本一律拒绝；`--write` 不接受冻结的旧状态。同时校验验收快照 `validation/pinned/checker.py` 与工作区副本一致（漂移检测，不是权限分离）。负例见 `test_checker_pins.py`（17 项） | `adr/0014-validation-chain-self-attestation.md`、`AGENTS.md` 3.6.8 | 已实现 |
| `check_dependency_pins.py` | 外部校验依赖指纹：`scripts/dependency-pins.json` 登记 `jsonschema`、`rdflib`、`pyshacl` 的版本、分发产物 sha256 与安装树计数；**三重均为强制项**。安装树按 wheel 内 `RECORD` 逐文件重算内容哈希核对，并断言导入路径落在分发目录内（影子包、`PYTHONPATH` 劫持、保留原 `RECORD` 的改动均阻断）。wheel 默认从仓库外持久路径 `~/.local/share/pm-governance/wheels/` 读取（`<包名>_WHEEL` 或 `--artifact <包名>=<wheel>` 可覆盖）；产物缺失、版本或安装树不符一律阻断。**威胁模型**：能发现误装与非恶意不一致，不构成对有权写本机 Python 环境者的防护（ADR-0019、G-022）。负例见 `test_dependency_pins.py`（16 项） | ADR-0019 | 已实现 |
| `check_spec_pins.py` | 规格区段绑定：登记 `GRAMMAR.md` 全文、方法 A.2/A.1、schema §1.11/§2bis/§3/§4、`coverage.json`，以及 `contracts/schema/` 下**全部** schema（自动发现：目录里出现未登记文件即阻断，取代人工清单）。区段新增或改动须 `--write --basis`，`basis` 与 `check_checker_pins` 同一标准——`复核产物：` 必须指向仓库外文件、`sha256：` 与之一致、`复核基线：` 必须是仓库内存在的提交、`区段：` 唯一且等值、结论词精确匹配，仓库内转录件只作索引；区段相对 `HEAD` 改动时同批还须附同样标准的复核记录。“无复核声明”只对冻结白名单成立（历史基文逐字相等，本批改动须为结构化 `待复核：批次 NNNN …`），复核记录永不接受该状态。负例见 `test_spec_pins.py`（18 项） | `adr/0014-validation-chain-self-attestation.md`、`AGENTS.md` 3.6.8 | 已实现 |
| `check_glossary_usage.py` | 从 `git ls-files` 的 Markdown / JSONL 生成每条术语的使用位置基线 `knowledge/glossary-usage.json`，并在 `GLOSSARY.md` 第 4 节生成位置表；默认模式校验位置存在、行号有效、该行含术语、生成块未被手改、术语集合一致。`--write` 重生成 | `AGENTS.md` 5bis.1 | 已实现 |
| `validate_ontology.py` | 用 `rdflib` + `pyshacl` 校验 `ontology/` 本体与 24 条 SHACL 形状；`--matrix` 逐条运行违规 fixture，确认每条形状能判出违规 | 无独立规格（边界见 `CONSTITUTION.md` 第 13.6 条与 `ontology/README.md`） | 已实现（可选依赖） |

### 测试脚本与执行入口

`scripts/test_*.py` 是检查器的负例/正例测试。**自批次 0074（2026-11-15）起**，以下测试明确列入 `.githooks/pre-commit`，与对应检查器并列执行，任一失败即阻断提交：

| 测试 | 对应检查器 | 接入情况 |
|---|---|---|
| `test_checker_pins.py` | `check_checker_pins.py` | 批次 0074 接入（此前从未被钩子或 CI 执行） |
| `test_dependency_pins.py` | `check_dependency_pins.py` | 批次 0074 之前已接入 |
| `test_spec_pins.py` | `check_spec_pins.py` | 批次 0074 接入（此前从未被钩子或 CI 执行） |
| `test_coverage_gate.py` | `check_coverage_gate.py` | 批次 0075 接入 |
| `test_check_table_mutations.py` | `check_three_table.py` | 批次 0075 接入 |
| `validate_ontology.py --matrix` | 本体与负例样例 | 批次 0075 接入（缺 `rdflib`/`pyshacl` 时退出 2，按“无法评估”阻断） |

**尚未接入**：无。本仓库无 CI 配置，钩子是唯一的自动执行入口。`validate_ontology.py --matrix` 的依赖按 `scripts/dependency-pins.json` 登记版本、wheel sha256 与逐文件安装树；缺依赖不是“跳过”，而是阻断。

### 运行方式

```
python3 scripts/check_state.py
python3 scripts/check_ledger_landings.py
python3 scripts/check_anchors.py
python3 scripts/check_no_raw_material.py
python3 scripts/check_gap_ledger.py
python3 scripts/check_gap_ledger.py --self-test
python3 scripts/check_three_table.py
python3 scripts/check_coverage_gate.py
python3 scripts/check_checker_pins.py
python3 scripts/check_dependency_pins.py
python3 scripts/check_spec_pins.py
python3 scripts/check_glossary_usage.py
python3 scripts/validate_ontology.py --matrix
```

**外部依赖**：仅数据区 schema 校验使用 `jsonschema`（ADR-0019）。安装、取 wheel 与核对：

```
python3 -m pip install --user jsonschema==4.26.0
python3 -m pip download --no-deps --no-cache-dir jsonschema==4.26.0 -d ~/.local/share/pm-governance/wheels
python3 scripts/check_dependency_pins.py
```

`check_dependency_pins.py` 退出码：`0` 通过；`1` 版本、安装树或分发产物指纹不符；`2` 依赖缺失、分发产物缺失、分发产物存在但不可读取或逐文件数据不可核对，或 `scripts/dependency-pins.json` 不可解析——按“无法评估”处理，不得视为通过（同一次运行既命中“指纹不符”又无法核对逐文件数据时，按 `2` 处理）。wheel 不提交进 git；`JSONSCHEMA_WHEEL=<wheel>` 可覆盖默认目录。升级依赖必须同批 `--write --artifact <wheel>` 记录新 sha256。

`check_gap_ledger.py` 退出码：`0` 通过；`1` 结构非法或存在到期未裁定（含规则/判定文件与台账未同批暂存）；`2` 台账或方法注册表无法解析。输出首行给出总数、`open`/`closed`、按级与到期计数、核查矩阵 `consistent` 比例。`--staged` 用于 pre-commit；独立运行时省略该参数。只有 `open` 缺口必须被核查矩阵引用——`closed` 缺口已记录处置出口，不再锚定矩阵，否则矩阵永远无法达到撤除条件要求的 17/17 `consistent`。

`check_three_table.py` 退出码：`0` 通过；`1` 对照失败（规则未映射到 `check_id`、`check_id` 无判定行或无 schema 输入域、子句未被引用、机制术语未定义、判定列含叙述性短语、G-B1 写了枚举条件、G-B2#1 未写枚举、原因码未在 schema 定义或与子句不一致）；`2` 三张表之一无法解析。输出首行给出规则数、`check_id` 数、子句数与 schema 输入域数；失败时逐条列出关系与对象。它是 ADR-0013 的交付物，pre-commit 与 `check_state.py` 双重调用，失败即阻断提交与发布。**它不保证语义闭合**：绿字只表示结构、枚举、子句归属与原因码映射一致；规则正文是否被子句忠实表达，仍须由非同源复核或人工逐条签收（`AGENTS.md` 3.6.6）。

`check_glossary_usage.py` 退出码：`0` 通过（零使用术语只输出警告）；`1` 校验失败（基线中的位置不存在、行号越界、该行不含术语、生成块被手改、术语集合与 `GLOSSARY.md` 不一致）；`2` 无法解析 `GLOSSARY.md` 或基线。`--write` 重生成基线与生成块，位置按 `path:line` 排序且幂等。新增、删除、移动文件或改行后必须 `--write` 并与改动同批提交；该检查器与缺口台账不是平行机制——它只做引用完整性核对，不承担语义裁定。

`validate_ontology.py` 退出码：`0` 通过；`1` 出现非预期结果（本体不通过或某条形状未被 fixture 判出）；`2` 缺少 `rdflib`/`pyshacl` 或结构无法解析——此时必须报“无法评估”，不得视为通过。

`check_state.py` 退出码：`0` 通过（开发态下“HEAD 领先于 tag”只输出警告）；`1` 存在错误（逐条列出）；`2` `STATE.md` 或 `manifest.json` 结构无法解析、缺少字段、`release_state` 非法，或不在 git 仓库中。`release_state` 缺失按 `released` 严格处理；`development` 不豁免 tag 名、版本号、annotated 与祖先关系判断。

发布引导提交的留痕：git 不记录 `--no-verify`，因此 `check_state.py` 改为核查 commit message 中的 `Hook-Bypass: release-bootstrap`、`Hook-Bypass-Reason:`、`Hook-Bypass-Verified:` 三项 trailer。`v0.5.2` 及以后的发布提交缺任一项即错误；非发布提交携带即错误。规则见 `AGENTS.md` 3.5.1，撤除条件见 3.5.2 与 `TODO.md` T-129。

`check_ledger_landings.py` 退出码：`0` 通过（可有待落点警告）；`1` 存在错误；`2` 登记表结构无法解析。

`check_anchors.py` 退出码：`0` 通过（可有警告/提示）；`1` 存在错误；`2` 结构或基线无法解析。规则/来源被有意修改后，用 `--write-baseline` 重冻基线，并把基线变更与内容变更同批提交。`--root` 可指向副本，用于插行负例演练。

`check_no_raw_material.py` 退出码：`0` 通过；`1` 发现违规（逐条列出规则码与位置，提交应被阻断）；`2` 无法评估——不在 git 仓库中，或 `spec/ACCESS_ZONES.md` 的归区表/准入登记表缺失、不可解析，或 `jsonschema` 无法导入。导入成功但运行时行为探测失败不属于退出 2：它按逐文件 `RM-SCHEMA`/`RM-SCHEMA-LINT` 报错并整体退出 1（实测 24 条），两者都不视为通过。`--self-test` 只返回 `0/1`：全部用例为合成数据，不依赖本地 PDF 资源，不存在“无法评估”分支，也不存在把“无法评估”当成通过的路径。判定按目录分区执行（`CONSTITUTION.md` 13.3，归区表 `spec/ACCESS_ZONES.md`）：

| 规则码 | 判定 |
|---|---|
| `RM-ZONE` | 路径未归区（fail-closed，D-1）；或区的扩展名与文件形态不符（O 区非本体序列化、P 区非散文、C 区非代码/配置） |
| `RM-MAGIC` | 文件头是 PDF/ZIP/GZIP/PNG/JPEG/GIF/TIFF/RAR/7Z/PostScript/OLE/DjVu（先于扩展名判断，改名无效） |
| `RM-EXT` | 被跟踪文件扩展名属于文档/电子书/扫描件/压缩包 |
| `RM-BINARY` | 出现 NUL 字节或无法按 UTF-8 解码 |
| `RM-SIZE` | 单文件超过 512 KiB |
| `RM-CONTROL` | 出现除制表符/换行外的 C0 控制字符 |
| `RM-MOJIBAKE` | 出现 U+FFFD 替换字符 |
| `RM-BASE64` | 出现 256 字符以上的 base64 形态长串，或 64 字符以上且解码后是已知二进制魔数（全区分） |
| `RM-SCHEMA` | 数据区文件未在准入登记表登记；解析失败；未知键、必填/类型/枚举不通过；schema 文件缺 `$schema`/`type`；schema 未通过官方元 schema；schema 内含无法解析的本地 `$ref`；缺少 `jsonschema`（导入失败）时按“无法评估”退出 2，导入成功但运行时行为探测失败时逐文件报本码、整体退出 1，不降级为跳过。**指针由本仓库恢复**（`additionalProperties` → `$.x`、`$.a.x`；`propertyNames` → `$.m.<键>`），**消息文本取自库的英文诊断**（`oneOf` 另加中文前缀） |
| `RM-FIELD` | 数据区字段超长或模式不符；按 schema 的 `x-prose-fields` 逐路径计量超上限（数组元素按出现值分别计量）；单条散文字段总和超过 `x-prose-budget`；单文件散文字段合计超过 32 KiB；集合字段超过 `maxItems`；`relations` 超过 `maxProperties` |
| `RM-SCHEMA-LINT` | schema 自身不完整：数组缺 `maxItems`/`items`（`items` 不接受 `true`/`false` 或元组）、字符串缺 `maxLength`（`enum`/`const` 不豁免）、对象缺 `additionalProperties: false`（或 `maxProperties` + `propertyNames` 映射）、关键字不在支持白名单、使用未支持的关键字、`$ref` 与同级断言关键字并用、`$ref` 指向不存在的 `$defs`、`pattern` 超过 512 字符（只限长度，不做回溯形态启发式）、嵌套超过 64 层（深嵌套 RecursionError）、`x-prose-fields` 路径在 schema 结构中解析不到、未通过官方元 schema |
| `RM-ONTO-HEADER` | 本体文件（`.ttl`/`.nt`/`.n3`/`.owl`/`.rdf`/`.jsonld`）前 40 行缺少 `self-authored`、`source_id:` 或 `source_pages:` 头注释（`source_pages` 取页码范围或 `n/a`；声明 `n/a` 时还须有 `source_pages_basis:`，缺该项同样按本码阻断） |
| `RM-ONTO-LITERAL` | 本体文件的 `skos:definition`/`rdfs:comment`/`dcterms:description` 字面量超过 2000 字符，或其他字面量超过 400 字符 |
| `RM-ONTO-COMMENT` | 本体文件的单行 `#` 注释超过 800 字符 |
| `RM-ONTO-PAGESEQ` | 页码序列转储：连续 12 行以上页码三元组（`ex:pN pm:page N .`）、12 个以上逗号分隔页码、或 12 个以上裸页码数字。真实 TTL 的最长连续三元组为 1 行，故对 5 份真实文件召回 0；299 行三元组转储与裸数字转储均命中（实测见 `spec/ACCESS_ZONES.md` 第 6 节） |
| `RM-ONTO-PROVENANCE` | 按块核对：含定义谓词、页码定位或 `dcterms:source` 的块必须交代来源与页码——术语级（`dcterms:source` / `pm:sourcePage` 等）或文件头统一声明（`source_id` / `source_pages`）。头注释写 `source_pages: n/a` 但正文含页码值 → 声明矛盾，阻断；`n/a` 未附可机械核验的 `source_pages_basis:`（非空、非占位符、含仓库内真实存在的 `adr/NNNN-*.md` 引用且另有自写理由）→ 视为页码未交代，阻断 |
| `RM-LONGLINE` | P/C 区单行超过 8192 字符 |
| `RM-QUOTE` | P 区单条引用超过 400 字符，或连续引用块超过 800 字符 |
| `RM-DOTLEADER` | P/O 区单行出现 30 个以上连续点（目录转储） |

**分区与准入**：D 区（数据）只收 `ACCESS_ZONES.md` 第 2 节登记的结构化文件，按 `contracts/schema/*.schema.json` 校验（`jsonschema==4.26.0`，ADR-0019；依赖缺失即“无法评估”，不跳过），并把 schema 的 `x-prose-fields`（逐路径上限，按出现值计量）与 `x-prose-budget`（单条总和兜底）用于配额；schema 自身先过完整性 lint 与官方元 schema，数组缺 `maxItems`/`items`（`items` 不接受 `true`/元组）、字符串缺 `maxLength`（`enum`/`const` 不豁免）、对象缺 `additionalProperties: false`、出现白名单外或未支持的关键字、`$ref` 带同级断言关键字或指向不存在的 `$defs`、`pattern` 超过 512 字符、嵌套超过 64 层、`x-prose-fields` 路径解析不到，均报 `RM-SCHEMA-LINT`。`contracts/schema/` 的发现是**递归**的，子目录里的 schema 同样 lint、同样要求登记为规格区段。未登记的数据区文件直接 `RM-SCHEMA`，不降级为文本扫描（D-1）。O 区按 13.6 执行谓词分档字面量与注释上限。P 区只执行与 13.1/13.2 直接对应的硬约束，不做页形态推断。C 区执行同一组硬约束（不含引证与目录点线两项散文判据）。未归类路径一律 `RM-ZONE` 阻断；新增顶层目录不会获得默认放行。

**已退役判据**：`RM-PROSEBLOCK`、`RM-PAGEDUMP`、`RM-PAGESEQ` 已删除，自测中也不保留依赖它们的样例。退役理由与实测数字见 `spec/RAW_MATERIAL_ADMISSION.md` 第 1 节；替代保护是数据区 schema + 配额、散文区硬约束、仓库外指纹与人工评审。**未命中不等于合规。**

**结构化数据边界**：JSONL 逐行解析、JSON 数组逐元素过 schema；解析前先剥 UTF-8 BOM；`.yaml` 用安全加载后过同一份契约 schema。键白名单改由 schema 的 `additionalProperties: false` 表达，不再在检查器里维护手写键表。配额只挡“单条整页”与最明显的滥用，不证明来源；均分切块仍可能落在配额内，这是已登记的残余风险。

**自测**：`python3 scripts/check_no_raw_material.py --self-test` 覆盖 83 项合成用例——合法 15 条 JSONL 与 BOM、退役启发式不再误杀长散文/硬换行/中文页/长定义、对象包裹的 `text`/`content`/`chunk` 被 schema 拦下、未知键/缺必填/超长字段/单文件配额、30 万字符单行、base64 PDF 头、单条长引用、PDF/gzip 魔数改名、禁止扩展名、未归类与未登记 fail-closed、本体定义分档与注释上限、页码序列与来源存在性、全本体扩展名头注释、归区最长前缀与全仓覆盖；复核补漏的 13 项覆盖 300 KB 散文塞 manifest、5 万字符契约字段与 statement、200 键 `relations`、100 条 `evidence`/`claim_mapping`、非法 `definitionStatus`、合法 2800 字符定义不被误杀、归区表与契约 schema 已在规格指纹内；r3 补漏的 12 项覆盖仓库内 7 份 schema 的完整性 lint、`package-manifest` 削弱为 `additionalProperties: true` 的 lint 与 fail-closed、三类缺上限各报一条、拼错与未实现关键字、`$ref` 同级关键字、`oneOf` 排他、3 条假设 × 1400 与 12 条 `notes`（6200）不被误杀、`positions` 300×400 与 `recorded_fields` 200×120 被拦；`source_pages: n/a` 的 7 项覆盖“只写 n/a 无依据”“依据为空串”“占位符”“指向不存在的 ADR”均阻断，附自写理由与仓库内 ADR 引用放行，`n/a` 与正文页码值矛盾仍阻断；r4 补漏的 11 项覆盖 `items: true` 与元组 `items` 被 lint 拦下、`enum`/`const` 不跳过 `maxLength`、`x-prose-fields` 路径拼错即报错、子目录 schema 同样被 lint、schema 未过官方元 schema 即失败、依赖缺失 fail-closed 并给出安装命令、20 条假设（28,000）与 8 条 `positions`（3,200）不再被单文件配额与路径预算误杀；r5 补漏的 6 项覆盖缺失本地 `$ref` 报错而不抛 `_WrappedReferencingError`、1500 层嵌套转为可诊断失败、空实现校验器被运行时探测拦下（`sitecustomize` 类替换）、`additionalProperties` 指针恢复为 `$.x`/`$.a.x`、`propertyNames` 指针恢复为 `$.m.<键>`；r6 改写 1 项、新增 1 项：撤掉 `pattern` 嵌套量词启发式后，官方 semver、dotted-id、dotted-version、list-of-pairs 与 `^(a|aa)+$` 五种写法全部放行，仍只按 512 字符上限拒绝超长 `pattern`。全部用例不依赖外部资源。

提交前接入：每个克隆需自行执行 `git config core.hooksPath .githooks`（只对当前克隆生效）。钩子依次运行全套检查器、准入自测与原型快检，任一失败即阻断提交：

```
python3 scripts/check_no_raw_material.py
python3 scripts/check_no_raw_material.py --self-test
python3 scripts/check_anchors.py
python3 scripts/check_ledger_landings.py
python3 scripts/check_gap_ledger.py --staged
python3 scripts/check_three_table.py
python3 scripts/check_coverage_gate.py
python3 validation/checker-prototype/checker.py --quiet
python3 validation/checker-prototype/checker.py --aggregation-order
python3 validation/checker-prototype/checker.py --missing-key-sweep --quiet
python3 validation/checker-prototype/checker.py --null-sweep --quick
python3 validation/checker-prototype/checker.py --nested-missing-sweep --quiet
python3 validation/checker-prototype/checker.py --enum-sweep --quiet
python3 scripts/check_checker_pins.py
python3 scripts/check_spec_pins.py
python3 scripts/check_glossary_usage.py
python3 scripts/check_state.py
```

未启用钩子时，在 `git add` 前手工按上述顺序运行，效果等价。检查器命中时不得用 `--no-verify` 绕过；唯一例外是 `AGENTS.md` 第 3.5 条规定的发布引导提交（tag 只能指向已存在提交），该提交后必须立即打 tag 并复跑全套检查器。新增其他例外须走 ADR 并在脚本中登记路径豁免。

### 脚本的定位

- 脚本是**辅助工具**，不是技能的核心规范。它们的缺失不构成技能不完备（`CHARTER.md` 承诺 C4 的延伸）。
- 脚本的执行结果是**证据工件**，可用于 `spec/GROUNDING_CRITERIA.md` G4 的验证。
- 脚本的规格（如 `check_glossary_sync.md`）是**规范性的**——脚本实现必须与规格一致；规格与实现冲突时以规格为准。
