# 原始资料防线改造方案：从形态推断转为分区准入

**性质**：改造方案与待批决策，不是现行规范。本文不改变 `CONSTITUTION.md`、`GRAMMAR.md` 或任何检查器；批准后的落地项登记于 `TODO.md`，决策记录见 `adr/0018-raw-material-admission-control.md`（`proposed`）。

**基线**：`58641d0`。失效证据：`/home/wgz/projects/skills/2026-11-14/pm-governance-review/verify-g019-r2/REPORT.md`（下称 r2 报告）。

## 1. 为什么形态启发式不收敛

r2 报告用 67 项探针复判了批次 0050 的加固。上轮确实堵住了对象包裹键、嵌套值、超长行、未知扩展名与魔数改名；但只要判据依赖“文本看起来像不像原文”，绕过与误杀会同时出现，且无法靠调阈值收敛。

关键实测数字：

| 现象 | r2 实测 |
|---|---|
| 整页正文放进一条 JSONL 记录 | 0 命中（第 6 页 3986 字符放进 `definition`，单行、低于 8192 行上限） |
| 真实正文按 390 字符切块、每块补句号 | 0 命中（15 条同构记录，低于每行 100 字符的连续判据） |
| base64 按 60 字符切块 | 0 命中（低于 64 探测阈值与 256 直判） |
| `RM-PAGEDUMP` 真实召回 | 4/15 页；剥离 C0 控制字符后 10/15 页零命中 |
| 合法 450–1500 字符自写定义 | 一律 `RM-PROSEBLOCK`；309 条落盘时前 15 条超限即封锁整文件 |
| 本体 `skos:definition` 450/600 字符 | 一律 `RM-ONTO-LITERAL` |
| 中文正文页（25 行 × 90 字，无 ASCII 空格） | 0 命中 |
| 80 列硬换行的英文 `.md`（41 行） | 误报 `RM-PAGEDUMP` |
| 表格行（20 行 × 110 字符） | 0 命中（Markdown 表格被排除） |

这些不是“阈值没调好”，而是三类结构性缺陷：

1. **判据变量与目标变量不同**：判据用“行长、行数、句末标点、空格比例”推断“是否原文”，而原文与自写文本在这几个维度上可以完全一致。
2. **双向失准无法同时修**：收紧会误杀长定义与硬换行文档，放宽会放过整页单条记录与均分切块；任何阈值都只能移动误判点，不能消除误判面。
3. **豁免语义自相矛盾**：值级上限 400 只决定“是否给整文件豁免”，不决定“单条是否合法”，于是出现“合法长定义被拦、单条超长原文被放”的同一文件内的反向错误。

结论：**继续加启发式不收敛。** 防线必须换轴：不再推断内容像不像原文，改为按目录角色规定“什么形态可以进入哪个区”，用准入条件代替形态推断。

## 2. 主轴：分区准入

三条原则：

1. **按目录角色管辖**。每个路径属于且只属于一个区；区决定允许的文件形态与检查强度，内容本身的“样子”不再是判据。
2. **数据区只收结构化数据**。数据区文件必须可解析、必须通过 schema；任何未声明的自由文本都是 schema 违规，不进入“像不像原文”的判断。
3. **散文区承认散文**。README、ADR、规范正文、报告本来就是散文；对它们只保留与第 13.1/13.2 条直接对应的硬约束（原始文件、成段引证、体积、乱码、控制字符），不再做页形态推断。

由此，`RM-PROSEBLOCK` 与 `RM-PAGEDUMP` 退役；它们承担的保护由“数据区 schema + 散文区硬约束 + 外部指纹比对（外置方案）”承接。

## 3. 分区模型

### 3.1 四个区

| 区 | 名称 | 允许形态 | 主判据 |
|---|---|---|---|
| D | 数据区 | `.json`、`.jsonl`、`.yaml`/`.yml`、`.csv`/`.tsv`（仅限已登记 schema 的文件） | 解析成功 + schema 通过 + 字段配额 |
| O | 本体区 | `.ttl`、`.shacl.ttl`、`.owl`、`.rdf`、`.nt`、`.n3`、`.jsonld` | 第 13.6 条 + 本体专用上限 |
| P | 散文区 | `.md`、`.txt`、`.rst`、`.html`、`.tex`、`.svg`、`LICENSE`、无扩展名文本 | 硬约束（原始文件、引证长度、体积、乱码、控制字符） |
| C | 代码与配置区 | `.py`、`.sh`、`.json` 配置登记、`.gitignore` | 硬约束 + 键/值配额；不做散文判据 |

**D 与 C 的 `.json` 区别**：D 区的 `.json` 承载知识数据，必须有 schema；C 区的 `.json` 是检查器登记/基线（如 `scripts/checker-pins.json`），由生成脚本自校验。区由路径决定，不由扩展名决定。

### 3.2 归区规则

1. **路径前缀优先**。`spec/ACCESS_ZONES.md`（落地时新增，尚未创建）登记“路径前缀 → 区/级别”的封闭表；匹配取最长前缀。
2. **文件级覆盖**。前缀表之外的单个文件可在同表登记例外；例外必须写明理由与到期里程碑。
3. **STATE 登记辅助**。新文件在 `STATE.md` 登记时同步给出区；`check_state.py` 只核对“已跟踪文件都有状态”，区由准入检查器核对。
4. **未归类默认 fail-closed**。路径不属于任何已登记前缀或例外时，阻断并报 `RM-ZONE`，提示先登记区。理由：准入制的前提是“只放行已声明的形态”；若未归类默认放行，新增一个顶层目录就等于新增一块无人管辖的盲区，这正是 G-020 记录的问题。
5. **数据区内未登记文件同样 fail-closed**。D 区新增文件必须在 schema 登记表中出现，否则报 `RM-SCHEMA`，不降级为“按文本扫描”。

### 3.3 现有 131 个跟踪文件的判定表

统计：D 16、O 30、C 19、P 66（P0 16 / P1 39 / P2 11）。逐文件判定见附录 A。

## 4. 数据区准入条件

### 4.1 允许的扩展名与解析器

| 扩展名 | 解析器 | 说明 |
|---|---|---|
| `.json` | `json.load` | 顶层必须是对象或对象数组；数组逐元素过 schema |
| `.jsonl` | 逐行 `json.loads` | 每行一个对象；空行允许；BOM 先剥 |
| `.yaml` / `.yml` | YAML 安全加载 | 仅限 `contracts/examples/` 与 `spec/pilot/` 的契约样例 |
| `.csv` / `.tsv` | 分隔符解析 | 必须有表头与列 schema；无 schema 不准入 |

解析失败即 `RM-SCHEMA`，不进入任何内容判断。

### 4.2 schema 从哪来

schema 是**单一事实源**，不再由检查器手写常量维护：

| 数据文件 | schema 来源 | 现状 |
|---|---|---|
| `knowledge/anchored-entries.jsonl` | 新增 `contracts/schema/knowledge-entry.schema.json`（尚未创建），字段集由 D2 已定字段（`term`/`definition`/`entry_type`/`status`/`relations`/`evidence` 等）+ D3 的 `grounding_ref` + D7 的 `claim_mapping` + M3-E1 的 `pending_reason` 合并 | 当前检查器用 `JSONL_TOP_KEYS` 手写常量，且不含 D3/D7/M3-E1 字段，必须替换 |
| `spec/pilot/pilot-entries.json` | 同一份 `contracts/schema/knowledge-entry.schema.json`（尚未创建），`authoritative: false` 分支 | 试点 15 条已符合 D2 |
| `spec/pilot/pilot-conflicts.jsonl` | 新增 `contracts/schema/pilot-conflict.schema.json`（尚未创建） | 现有 3 条；扩到 15 条即会撞旧判据 |
| `contracts/examples/*.yaml` | 既有 `contracts/schema/pm-slot-contract.schema.json` | 已有 |
| `scripts/*.json`、`ontology/fixtures/manifest.json`、`validation/checker-prototype/coverage.json` | 由生成脚本自校验，不进入知识 schema | 已有生成逻辑 |

schema 文件本身纳入 `spec-pins` 指纹绑定；改 schema 必须同批更新复核记录。未知键报“schema 未登记”，不再报“疑似原文”。

### 4.3 字段配额

配额是**硬上限**，超限即 `RM-FIELD`，不再有“超限只取消豁免”的双重语义：

| 字段类 | 上限 | 理由 |
|---|---|---|
| 身份键（`term`/`id`/`draft_id`/`label_*`/`status`/`entry_type`/`candidate_iri*`） | 120 字符 | 标识符，不应承载句子 |
| `relations` 子值 | 120 字符 | 关系名或目标 id |
| `evidence` 字符串 | 200 字符 | 定位串 |
| `definition` | 2000 字符 | 覆盖 1500 字符的真实定义，同时低于整页正文常见体量 |
| `provenance_note` | 800 字符 | 形式化边界说明 |
| `candidate_iri_reason` | 400 字符 | 解释性文本，不再按身份键 120 |
| 单条记录散文字段合计 | 2500 字符 | `definition` + `provenance_note` 的组合上限 |
| 单文件散文字段合计 | 20 KiB | 粗粒度总量闸门；超出转人工裁定 |

**配额不能证明来源。** 均分切块（15 × 390 字符）可以落在所有配额内。配额的作用是挡住“单条整页”和最明显的滥用，不承担“是否原文”的判定；后者交给第 8 节的外部指纹方案与人工评审。

### 4.4 散文残留怎么判

数据区里的“散文”按**字段位置**定义，不按内容形状定义：

1. **文件级**：D 区出现扩展名不在准入表、或内容不可解析的文件 → `RM-SCHEMA`；这就是“散文文件进数据区”的唯一判定方式。
2. **记录级**：出现 schema 未声明的键 → `RM-SCHEMA`（未知键），不猜测该键是否像原文。
3. **字段级**：未声明为 `prose_fields` 的字符串必须匹配声明模式（ID、IRI、关系 token、页码定位、枚举值）；不匹配 → `RM-FIELD`。
4. **配额级**：`prose_fields` 超第 4.3 节上限 → `RM-FIELD`。

任一情形都不使用句长、句末标点、行宽、空格比例、连续行数。这样“散文残留”是一个**结构位置问题**，可以机械判定；它是否抄袭原文，不是本层能回答的问题。

## 5. 本体区

本体继续受 `CONSTITUTION.md` 第 13.6 条约束，只调整与定义长度相关的误杀：

- `RM-ONTO-HEADER`：保留，头注释三件套不变。
- `RM-ONTO-LITERAL`：按谓词分档。`skos:definition`、`rdfs:comment`、`dcterms:description` 的上限提到 2000 字符；其他字符串字面量维持 400 字符。依据：13.6 要求“自写一句话”，但一句话没有长度上限，450–1500 字符的中文定义是正常形态。
- `RM-ONTO-COMMENT`：上限从 400 提到 800 字符，与 `provenance_note` 对齐。
- 本体文件的体积、二进制、乱码、控制字符、页码序列、目录点线检查不变。
- 本体定义仍不得与原文逐句对应；这一条无法由长度判据机械验证，列入第 11 节残余风险。

## 6. 散文区分级

散文区不再做页形态推断，但按目录分三级，差别在**复核义务**与**转录件标识**，不在内容形状：

| 级别 | 范围 | 机器检查 | 复核义务 |
|---|---|---|---|
| P0 | 根级治理与说明文档、`LICENSE` | 硬约束 + `RM-QUOTE` | 随规则/来源变更复核 |
| P1 | `adr/`、`spec/` 正文、`contracts/*.md`、`ontology/README.md`、`scripts/README.md`、`scripts/check_glossary_sync.md`、`knowledge/methods/`、`validation/CHECKLIST.md`、`validation/independent-review-package.md` | 同 P0 | 结构性变更走 ADR/CHANGELOG |
| P2 | 报告、复核转录、试点报告与用例（`validation/reviews/`、`validation/test-cases/`、`spec/pilot/*.md`） | 同 P0；复核转录必须带“非权威、不构成关闭依据”头 | 为非权威记录，不得作为缺口关闭依据 |

P0/P1/P2 的机器检查相同，是因为“散文区长短”没有可靠判别式；分级的实际作用是明确哪类文档可以承载规范性表述、哪类只能作为证据转录。

## 7. 规则清单变更

| 规则码 | 处置 | 新口径 / 替代保护 |
|---|---|---|
| `RM-MAGIC` | 保留（全区分） | 文件头识别先于一切分区判断 |
| `RM-EXT` | 保留（全区分） | 原始资料/压缩包扩展名，作为 D/P/O/C 之外的硬拦 |
| `RM-BINARY` | 保留（全区分） | NUL、非 UTF-8 |
| `RM-SIZE` | 保留（全区分） | 单文件 512 KiB；D 区另受 schema 与配额 |
| `RM-CONTROL` | 保留（全区分） | C0 控制字符 |
| `RM-MOJIBAKE` | 保留（全区分） | U+FFFD |
| `RM-BASE64` | 保留（全区分） | 256 直判 + 64 解码认魔数；D 区值内同样适用 |
| `RM-DOTLEADER` | 保留（P/O） | 30 个连续点在散文与本体中无合法用途 |
| `RM-LONGLINE` | 保留（P/C） | 单行 8192 字符；D 区由 schema 与字段配额取代，O 区由本体上限取代 |
| `RM-QUOTE` | 保留（P） | 对应第 13.2 条“单条不超过一行或一句”；D 区由字段配额取代 |
| `RM-PAGESEQ` | 删除 | 无独立保护价值：D 区由 schema 拒绝纯数字行，P 区的编号列表应被允许 |
| `RM-PROSEBLOCK` | 删除 | 双向失准（第 1 节）；替代：D 区 schema + 配额，P 区硬约束，外部指纹 |
| `RM-PAGEDUMP` | 删除 | 召回 4/15、误杀 80 列文档与中文页漏判；替代同上 |
| `RM-ONTO-HEADER` | 保留（O） | 第 13.6 条头注释 |
| `RM-ONTO-LITERAL` | 修改（O） | 定义类谓词 2000，其他字面量 400 |
| `RM-ONTO-COMMENT` | 修改（O） | 400 → 800 |
| `RM-ZONE` | 新增 | 路径未归区或数据区未登记；fail-closed |
| `RM-SCHEMA` | 新增 | D 区解析失败、未知键、schema 不通过 |
| `RM-FIELD` | 新增 | D 区字段模式不符或配额超限 |

**删除后的保护真空**：`RM-PROSEBLOCK` 与 `RM-PAGEDUMP` 原本试图在散文区识别“整页粘贴”，但它们既漏判又误杀。删除后，散文区的整页粘贴不再由仓库内判据拦截，改由第 8 节外部指纹与人工评审承接；这是本方案明确接受并登记的残余风险，不是隐性削弱。

## 8. 第 13 条修订草案（建议稿，本次不修改 `CONSTITUTION.md`）

> **第 13 条 原始资料与提取产物的入库禁令**
>
> **13.1 禁止入库的内容**（实质范围不变）
>
> 本仓库是公开仓库。下列内容不得以任何形式进入 git 跟踪范围：
>
> 1. **原始资料**：PDF、EPUB、MOBI、扫描件、图片型页面、受版权保护的文档副本，以及包含它们的压缩包；
> 2. **提取产物**：PDF 文本层转储、OCR 全文或整页输出、逐页转录、围绕同一来源的连续摘录；
> 3. **成段原文**：整段、整节或成篇的原文摘录，无论是否标注引用；
> 4. **可替代原作的实质内容**：即使经过改写或翻译，只要达到“读者无需原作即可获得该来源实质内容”的程度，同样禁止。
>
> **13.2 允许的形态**（不变）
>
> 页码定位、来源标识与元数据、最短引证、自己的转述与摘要、满足 13.6 的自建本体。

13.3 的改写文本如下，核心变化是判定依据从内容形态改为目录分区：

> **13.3 合规判定与执行**
>
> 合规判定按目录角色执行，不按内容形态推断：
>
> 1. **数据区**：只允许结构化文件。文件必须可解析、必须通过登记的 schema、必须满足字段配额；散文只能出现在 schema 声明的 `prose_fields` 中。数据区出现未声明的自由文本文件或未声明字段，即阻断。
> 2. **散文区**：允许散文。该区只执行与 13.1/13.2 直接对应的硬约束——原始文件扩展名与文件头、体积、二进制、乱码、控制字符、目录点线、单条引证长度；不再以行长、行数、句末标点或空格比例推断“是否原文”。
> 3. **本体区**：按 13.6 与本体专用上限执行。
> 4. **未归类路径**：阻断，直至登记区。
> 5. **不构成合规证据**：任何形态判据的“命中”只表示需要人工复核，“未命中”不表示合规。仓库内检查器的通过只证明已登记的结构条件成立，不证明内容不是原文；来源层面的比对由仓库外指纹方案与复核承接。

13.4–13.6 保持现行条文，仅 13.5 的张力与 13.6 的谓词分档需要在批准时确认：

> **13.4 与来源治理的关系**（不变）
>
> **13.5 修改程序**（保留，需同步评估）
>
> 本条的修改适用第 5 条的特殊程序。原“不得降低 13.3 的阻断强度”与本次换轴的张力见待批决策 D-3：数据区的阻断强度上升，散文区的形态阻断被撤销并由外部方案承接，是否构成“降低”需要人类责任方明确裁定。
>
> **13.6 自建本体的边界**（不变，仅 `RM-ONTO-LITERAL` 按谓词分档）

修订后的变化一句话概括：**从“禁止仓库里出现某类内容”变为“规定每个区允许什么形态，并承认内容层面的来源比对不在仓库内完成”**。仍禁止的：原始文件、提取产物、成段原文、可替代原作的实质内容；新增的明确项：数据区不得出现未声明的自由文本，未归类路径不得通过。

## 9. ADR 提案

完整草稿见 `adr/0018-raw-material-admission-control.md`（`proposed`）。要点：

- 决定：以分区准入替代形态推断；退役 `RM-PROSEBLOCK`/`RM-PAGEDUMP`/`RM-PAGESEQ`。
- 被否方案：继续加启发式（r2 双向失准、无可收敛阈值）；纯人工评审（不可机械阻断、无留痕）；只做文件白名单（`RM-PROSEBLOCK` 误杀与整页单条仍无解）；仅上外部指纹（干净克隆无法运行，且对数据区结构无约束）。
- 后果：数据区可机械验收；散文区依赖评审与外部指纹；需要一次迁移与一条 CONSTITUTION 修订。

## 10. 迁移路径

### 10.1 四步

1. **本批（方案）**：出本文与 ADR 提案、G-019/G-020 处置建议；不改实现、不改 `CONSTITUTION.md`。
2. **批准与修法**：用户逐条裁定第 13 节的 D 清单；按第 5 条特殊程序修订第 13 条；ADR 转 `accepted`。
3. **实现批次**：新增 `spec/ACCESS_ZONES.md`、`contracts/schema/knowledge-entry.schema.json`、`contracts/schema/pilot-conflict.schema.json`（均尚未创建）；重写 `check_no_raw_material.py` 为“归区 + 硬约束 + schema”；同批删除三条旧判据与 18 项自测中的形态用例；同步 `.githooks/pre-commit`、`scripts/README.md`、`check_state.py`、`checker-pins.json`。
4. **一次性过检与复核**：按附录 A 的 131 条判定逐文件跑新检查器；全部通过后由非同源复核确认“旧判据已退役、新准入生效、G-019/G-020 改写成立”。

### 10.2 一次性过检

- 预检：`knowledge/anchored-entries.jsonl`（10 条，最长 678 字符）与试点 15 条（最长 998 字符）在新配额内，预计 0 违规；本体当前无 `skos:definition`，`RM-ONTO-LITERAL` 改动不产生存量影响。
- 逐文件：附录 A 的区与级别即为过检清单；D 区文件过 schema，O 区过 13.6 + 本体上限，P/C 过硬约束。
- 预计存量违规：0。若出现，按 10.3 处理，不修改判据迁就存量。

### 10.3 豁免期

- **原则上不设豁免期**。准入制要求“存量先合规，再切闸门”；一次性过检不通过的文件先修正或移出，而不是带着例外上线。
- 若确有暂时无法修正的合法文件，登记 `validation/exemptions/<批次>.md`：路径、原因、责任人、到期里程碑、复核人。检查器对豁免文件输出**警告并计数**，不静默放行；到期仍未移除即阻断。
- 豁免最长停留 1 个里程碑，且不得用于原始资料或提取产物；此类内容只能移除，不能豁免。

## 11. 残余风险

| 风险 | 能否机械化 | 承接方 |
|---|---|---|
| 数据区 `prose_fields` 内的均分切块（15 × 390 字符） | 否；配额只能挡单条整页 | 外部指纹比对 + 非同源复核 |
| 散文区整页粘贴（无形态特征） | 否；已明确不再做形态推断 | 人工评审 + 外部指纹 |
| 自写定义与原文逐句对应（语义抄袭） | 否 | 人工评审；13.6 的语义约束保留 |
| 外部指纹方案无法在干净克隆运行 | 依赖仓库外资源常驻 | 与 ADR-0015 同类：承认仓库内无法自保，由外部基础设施承接 |
| 子模块 gitlink 不扫描 | 否，需显式递归 | G-020 改写后承接 |
| 豁免文件被长期挂账 | 可机械到期 | 豁免登记 + 到期阻断 |

与 ADR-0015 的关系：ADR-0015 的结论是“仓库内不存在能保护自己的信任根，验证权必须外置”。本方案沿用同一判断——内容层面的“是否原文”无法由仓库内判据可靠回答，只能由分区准入把可机械化的部分做实，把不可机械化的部分显式外置。两者是同一信任模型在内容防线上的应用，不新增仓库内自证层。

## 12. G-019 与 G-020 的处置建议

两条都**不自行关闭**；换轴后按下述方式改写，待方案批准与实现批次完成、非同源复核后再关闭。

| 缺口 | 建议处置 | 改写后的内容 | 关闭条件 |
|---|---|---|---|
| G-019 | **改写，保持 `open`** | 从“`RM-PROSEBLOCK` 未识别结构化 JSONL”改为“形态推断判据退役、分区准入落地”：数据区 schema 与配额、散文区硬约束、旧判据删除、自测改用准入正负例 | 实现批次完成 + 非同源复核确认旧判据已删、新准入可复现 |
| G-020 | **拆分并改写，保持 `open`** | 文件枚举一半（未知扩展名、魔数改名）已由批次 0050 解决，不再保留；剩余改写为“子模块、外部生成物与未登记路径的扫描范围”。形态分类一半并入 G-019 的准入实现，不再单列 | 子模块与未登记路径口径裁定并实现后，非同源复核 |

建议另立 **G-021（待批准后登记）**：散文区与数据区 `prose_fields` 内的原文抄袭缺乏仓库内机械判据，属 `representation-defect`/L3，处置出口倾向 `accepted`（理由：依赖外部指纹与人工评审，见 ADR-0015 同类边界）。在方案批准前不登记，避免用未定方案占号。

## 13. 成本量级与待批决策

### 13.1 成本量级

| 项 | 量级 |
|---|---|
| 新增文档/规格 | 3 个：`spec/ACCESS_ZONES.md`、2 个 JSON Schema（均尚未创建） |
| 检查器改造 | `check_no_raw_material.py` 约 600–900 行重写；删除 3 条判据、新增 3 条 |
| 自测改造 | 18 项形态用例替换为准入正负例，预计 12–16 项 |
| 存量过检 | 131 个文件，其中 D 16、O 30 需逐文件校验 |
| 联动文件 | `.githooks/pre-commit`、`scripts/README.md`、`check_state.py`、`checker-pins.json`、`spec-pins.json`、`GAP_LEDGER.md`、`TODO.md`、`CHANGELOG.md` |

### 13.2 待批决策 D 清单

| 编号 | 待定问题 | 建议 | 不定的后果 |
|---|---|---|---|
| D-1 | 未归类路径默认 fail-closed 还是放行 | fail-closed | 放行则新增顶层目录成为盲区，G-020 原样复发 |
| D-2 | 是否整体撤销散文区形态判据 | 撤销 | 保留则继续双向失准，方案无法收敛 |
| D-3 | 第 13.5 条“不得降低阻断强度”是否允许本次换轴 | 明确裁定“数据区增强 + 散文区外置”不构成降低，或按特殊程序修订该句 | 不裁定则修订草案与 13.5 冲突，无法合法落地 |
| D-4 | 数据区配额数值（`definition` 2000 / `provenance_note` 800 / 单条 2500 / 单文件 20 KiB） | 按第 4.3 节 | 不定则实现无阈值，或沿用被证明双向失准的 400 |
| D-5 | schema 单一事实源的位置与生成方式 | `contracts/schema/*.schema.json`，纳入 `spec-pins` | 不定则继续手写白名单，D3/D7/M3-E1 字段扩展即误杀 |
| D-6 | 是否需要豁免期 | 不需要；确有例外按 10.3 登记，最长 1 个里程碑 | 不定的后果是切闸门时无处置路径，可能被迫放宽判据 |
| D-7 | 外部指纹方案的启用时点与资源常驻方式 | 与 ADR-0015 同批外置，不阻塞准入制落地 | 不定则残余风险无人承接，散文区保护出现空档 |
| D-8 | 子模块是否纳入扫描 | 纳入或显式声明不纳入并写入 G-020 | 不定则 G-020 无法改写，且子模块仍是盲区 |
| D-9 | `ontology/` 归 O 还是 D | 归 O（13.6 专用规则），`ontology/fixtures/manifest.json` 归 D | 归 D 会用知识 schema 误判本体文件 |
| D-10 | 是否新登记 G-021（散文区语义抄袭不可机械判定） | 批准后登记，出口倾向 `accepted` | 不登记则该残余风险无处挂账，复核时会被重新报为缺口 |

## 附录 A：现有 131 个跟踪文件判定表

区代码：D 数据区、O 本体区、C 代码/配置区、P0/P1/P2 散文区分级。

| 路径 | 区 | 级别 | 依据 |
|---|---|---|---|
| `.githooks/pre-commit` | C | — | 钩子脚本 |
| `.gitignore` | C | — | 配置 |
| `AGENTS.md` | P | P0 | 根级治理 |
| `CHANGELOG.md` | P | P0 | 根级治理 |
| `CHARTER.md` | P | P0 | 根级治理 |
| `CONSTITUTION.md` | P | P0 | 根级治理 |
| `ERRATA.md` | P | P0 | 根级治理 |
| `GAP_LEDGER.md` | P | P0 | 根级治理 |
| `GLOSSARY.md` | P | P0 | 根级治理 |
| `GRAMMAR.md` | P | P0 | 根级治理 |
| `LICENSE` | P | P0 | 法律文本，非知识数据 |
| `QUICKSTART.md` | P | P0 | 根级说明 |
| `README.en.md` | P | P0 | 根级说明 |
| `README.md` | P | P0 | 根级说明 |
| `ROADMAP.md` | P | P0 | 根级治理 |
| `SOURCE_LEDGER.md` | P | P0 | 根级治理 |
| `STATE.md` | P | P0 | 根级治理 |
| `TODO.md` | P | P0 | 根级治理 |
| `manifest.json` | D | — | 包元数据，键值封闭 |
| `adr/0001-separate-grammar-from-governance.md` | P | P1 | 决策记录 |
| `adr/0002-compilation-meta-vs-methods.md` | P | P1 | 决策记录 |
| `adr/0003-version-and-state-governance.md` | P | P1 | 决策记录 |
| `adr/0004-artifact-baseline-by-commit.md` | P | P1 | 决策记录 |
| `adr/0005-source-ledger-scope.md` | P | P1 | 决策记录 |
| `adr/0006-knowledge-sources-vs-normative-basis.md` | P | P1 | 决策记录 |
| `adr/0007-anchor-discipline.md` | P | P1 | 决策记录 |
| `adr/0008-reanchor-dimension-rules.md` | P | P1 | 决策记录 |
| `adr/0009-no-raw-material-in-git.md` | P | P1 | 决策记录 |
| `adr/0010-self-authored-ontology-in-git.md` | P | P1 | 决策记录 |
| `adr/0011-schedule-layer-and-plan.md` | P | P1 | 决策记录 |
| `adr/0012-gap-ledger-and-adjudication.md` | P | P1 | 决策记录 |
| `adr/0013-unified-adjudication-of-check-semantics.md` | P | P1 | 决策记录 |
| `adr/0014-validation-chain-self-attestation.md` | P | P1 | 决策记录 |
| `adr/0015-trust-root-external-infrastructure.md` | P | P1 | 决策记录 |
| `adr/0016-pmbok8-concept-layer-use.md` | P | P1 | 决策记录 |
| `adr/0017-grounding-ref-vs-evidence.md` | P | P1 | 决策记录 |
| `adr/ADR-TEMPLATE.md` | P | P1 | 模板 |
| `adr/README.md` | P | P1 | 决策记录说明 |
| `contracts/examples/construction.pm-contract.yaml` | D | — | 契约样例，YAML 解析 + 槽位 schema |
| `contracts/examples/software-engineering.pm-contract.yaml` | D | — | 契约样例，YAML 解析 + 槽位 schema |
| `contracts/resolver.md` | P | P1 | 解析规范 |
| `contracts/schema/pm-slot-contract.schema.json` | D | — | 契约 schema 本体 |
| `knowledge/anchored-entries.jsonl` | D | — | 知识条目，按 `contracts/schema/knowledge-entry.schema.json`（尚未创建） |
| `knowledge/glossary-usage.json` | D | — | 生成的使用位置基线 |
| `knowledge/methods/registry-skeleton.md` | P | P1 | 方法注册表骨架 |
| `ontology/README.md` | P | P1 | 本体说明 |
| `ontology/fixtures/invalid-s01_process_domain_cardinality.ttl` | O | — | 负例本体 |
| `ontology/fixtures/invalid-s02_process_focus_area.ttl` | O | — | 负例本体 |
| `ontology/fixtures/invalid-s03_process_input.ttl` | O | — | 负例本体 |
| `ontology/fixtures/invalid-s04_process_output.ttl` | O | — | 负例本体 |
| `ontology/fixtures/invalid-s05_process_domain_class.ttl` | O | — | 负例本体 |
| `ontology/fixtures/invalid-s06_process_focus_class.ttl` | O | — | 负例本体 |
| `ontology/fixtures/invalid-s07_process_label_en.ttl` | O | — | 负例本体 |
| `ontology/fixtures/invalid-s08_process_label_zh.ttl` | O | — | 负例本体 |
| `ontology/fixtures/invalid-s09_process_code.ttl` | O | — | 负例本体 |
| `ontology/fixtures/invalid-s10_process_source_page.ttl` | O | — | 负例本体 |
| `ontology/fixtures/invalid-s11_process_io_status.ttl` | O | — | 负例本体 |
| `ontology/fixtures/invalid-s12_domain_definition.ttl` | O | — | 负例本体 |
| `ontology/fixtures/invalid-s13_domain_process.ttl` | O | — | 负例本体 |
| `ontology/fixtures/invalid-s14_focus_definition.ttl` | O | — | 负例本体 |
| `ontology/fixtures/invalid-s15_focus_process.ttl` | O | — | 负例本体 |
| `ontology/fixtures/invalid-s16_artifact_category.ttl` | O | — | 负例本体 |
| `ontology/fixtures/invalid-s17_artifact_label.ttl` | O | — | 负例本体 |
| `ontology/fixtures/invalid-s18_artifact_source_page.ttl` | O | — | 负例本体 |
| `ontology/fixtures/invalid-s19_artifact_definition_status.ttl` | O | — | 负例本体 |
| `ontology/fixtures/invalid-s20_technique_category.ttl` | O | — | 负例本体 |
| `ontology/fixtures/invalid-s21_technique_label.ttl` | O | — | 负例本体 |
| `ontology/fixtures/invalid-s22_class_definition.ttl` | O | — | 负例本体 |
| `ontology/fixtures/invalid-s23_property_domain.ttl` | O | — | 负例本体 |
| `ontology/fixtures/invalid-s24_property_range.ttl` | O | — | 负例本体 |
| `ontology/fixtures/manifest.json` | D | — | fixture 清单 |
| `ontology/fixtures/valid.ttl` | O | — | 正例本体 |
| `ontology/pmbok8-artifacts.ttl` | O | — | 自建本体 |
| `ontology/pmbok8-processes.ttl` | O | — | 自建本体 |
| `ontology/pmbok8-shapes.ttl` | O | — | 自建本体 |
| `ontology/pmbok8-tools.ttl` | O | — | 自建本体 |
| `ontology/pmbok8-vocab.ttl` | O | — | 自建本体 |
| `scripts/README.md` | P | P1 | 脚本说明 |
| `scripts/anchor_baseline.json` | D | — | 锚点指纹基线 |
| `scripts/check_anchors.py` | C | — | 检查器 |
| `scripts/check_checker_pins.py` | C | — | 检查器 |
| `scripts/check_coverage_gate.py` | C | — | 检查器 |
| `scripts/check_gap_ledger.py` | C | — | 检查器 |
| `scripts/check_glossary_sync.md` | P | P1 | 检查规格 |
| `scripts/check_glossary_usage.py` | C | — | 检查器 |
| `scripts/check_ledger_landings.py` | C | — | 检查器 |
| `scripts/check_no_raw_material.py` | C | — | 本方案的改造对象 |
| `scripts/check_spec_pins.py` | C | — | 检查器 |
| `scripts/check_state.py` | C | — | 检查器 |
| `scripts/check_three_table.py` | C | — | 检查器 |
| `scripts/checker-pins.json` | D | — | 检查器哈希登记 |
| `scripts/spec-pins.json` | D | — | 规格指纹登记 |
| `scripts/test_check_table_mutations.py` | C | — | 测试脚本 |
| `scripts/test_checker_pins.py` | C | — | 测试脚本 |
| `scripts/test_coverage_gate.py` | C | — | 测试脚本 |
| `scripts/test_spec_pins.py` | C | — | 测试脚本 |
| `scripts/validate_ontology.py` | C | — | 本体校验 |
| `spec/ANCHOR_SPEC.md` | P | P1 | 规范正文 |
| `spec/ASSUMPTION_PROTOCOL.md` | P | P1 | 规范正文 |
| `spec/CHECKER_INPUT_SCHEMA.md` | P | P1 | 规范正文 |
| `spec/COMPILATION_META.md` | P | P1 | 规范正文 |
| `spec/COMPILATION_METHODS.md` | P | P1 | 规范正文 |
| `spec/CONTEXT_ASSEMBLY.md` | P | P1 | 规范正文 |
| `spec/GOVERNANCE_RESTRUCTURE.md` | P | P1 | 规范正文 |
| `spec/GROUNDING_CRITERIA.md` | P | P1 | 规范正文 |
| `spec/INTERFACE_CONTRACT_SPEC.md` | P | P1 | 规范正文 |
| `spec/M3_M4_DECISIONS.md` | P | P1 | 决策记录 |
| `spec/M3_M4_PLAN.md` | P | P1 | 规划 |
| `spec/ONTOLOGY_FEASIBILITY.md` | P | P1 | 评估报告 |
| `spec/methods/deterministic-checker.md` | P | P1 | 方法声明 |
| `spec/pilot/M3_M4_PILOT_REPORT.md` | P | P2 | 试点报告 |
| `spec/pilot/pilot-artifact.json` | D | — | 产物样例（结构化） |
| `spec/pilot/pilot-artifact.md` | P | P2 | 产物人类可读投影 |
| `spec/pilot/pilot-conflicts.jsonl` | D | — | 冲突样例（结构化） |
| `spec/pilot/pilot-contract.yaml` | D | — | 试点契约（结构化） |
| `spec/pilot/pilot-entries.json` | D | — | 试点条目（结构化） |
| `spec/pilot/pilot-id-map.json` | D | — | ID 映射（结构化） |
| `validation/CHECKLIST.md` | P | P1 | 检查清单 |
| `validation/checker-prototype/checker.py` | C | — | 检查器原型 |
| `validation/checker-prototype/coverage.json` | D | — | 覆盖矩阵 |
| `validation/independent-review-package.md` | P | P1 | 复核包说明 |
| `validation/pinned/checker.py` | C | — | 只读快照 |
| `validation/reviews/2026-11-14-48128a8-external.md` | P | P2 | 复核转录 |
| `validation/reviews/2026-11-14-d8bf413-review.md` | P | P2 | 复核转录 |
| `validation/reviews/2026-11-14-g019-user-authorization.md` | P | P2 | 授权转录 |
| `validation/reviews/2026-11-14-t139-user-adjudication.md` | P | P2 | 裁定转录 |
| `validation/reviews/2026-11-15-g019-hardening-user-authorization.md` | P | P2 | 授权转录 |
| `validation/test-cases/README.md` | P | P2 | 用例说明 |
| `validation/test-cases/TC-A1-02.md` | P | P2 | 反例用例 |
| `validation/test-cases/TC-C1-03.md` | P | P2 | 反例用例 |
| `validation/test-cases/TC-E1-04.md` | P | P2 | 反例用例 |
