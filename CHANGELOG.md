## 变更历史

**登记规则**：见 `AGENTS.md` 第 3.1 条。按批次追加，禁止改写已登记批次。

### 批次 0001 — 2026-11-11 — 初始交付

- **涉及文件**：`README.md`、`AGENTS.md`、`CHARTER.md`、`CONSTITUTION.md`、`GRAMMAR.md`、`SOURCE_LEDGER.md`、`spec/COMPILATION_SPEC.md`、`spec/ASSUMPTION_PROTOCOL.md`、`spec/INTERFACE_CONTRACT_SPEC.md`、`contracts/schema/pm-slot-contract.schema.json`、`contracts/resolver.md`、`contracts/examples/construction.pm-contract.yaml`、`contracts/examples/software-engineering.pm-contract.yaml`、`knowledge/anchored-entries.jsonl`、`knowledge/methods/registry-skeleton.md`、`adr/ADR-TEMPLATE.md`、`adr/0001-separate-grammar-from-governance.md`、`validation/CHECKLIST.md`、`CHANGELOG.md`、`TODO.md`
- **变更摘要**：技能 v0.1 初始交付。四层结构（意图/治理/立法/执行）建立；成文法规则组 A–G 定义（A/C/D/E 为 `active`，B 为 `pending_reanchor`，F/G 为 `assumption`）；来源登记表封闭枚举 8 个条目（含 1 个 `deprecated`）；接口契约 v1 单层解析启用，多层合并语义定义但不启用；方法注册表骨架与 5 条首批方法条目入库；治理 ADR-0001 记录规范层与执行层物理分离决策。
- **关联 ADR**：ADR-0001（accepted）
- **状态**：`pending-adr` 解除（ADR-0001 已 accepted）

---

### 批次 0002 — 2026-11-11 — 编译域拆分

- **涉及文件**：
  - 新建：`spec/COMPILATION_META.md`、`spec/COMPILATION_METHODS.md`、`spec/methods/deterministic-checker.md`
  - 删除：`spec/COMPILATION_SPEC.md`（内容上收至 META、下沉至 deterministic-checker.md）
  - 修改：`CONSTITUTION.md`（第 5 条保护清单新增项、新增第 10 条）、`README.md`（文件地图、阅读路径、状态与版本）、`AGENTS.md`（第 4 条目录结构）、`validation/CHECKLIST.md`（文件头生成依据）、`TODO.md`（新增工作项、更新引用）
  - 新建：`adr/0002-compilation-meta-vs-methods.md`
- **变更摘要**：将编译域拆分为“元框架（方法无关）/ 方法注册表 / 具体方法声明”三层，与“项目管理元框架 / 领域技能”同构。原 `spec/COMPILATION_SPEC.md` 的方法无关部分上收至 `COMPILATION_META.md`，方法有关部分下沉至 `spec/methods/deterministic-checker.md`。`CONSTITUTION.md` 新增第 10 条（编译治理总纲），第 5 条保护清单覆盖编译域基础约束。方法注册表当前启用 `CM-DET-CHECKER`，登记四个候选方法（技能卡片、人类检查单、PACT 规则、神经符号编译）。
- **关联 ADR**：ADR-0002（accepted）
- **状态**：生效

---

### 批次 0003 — 2026-11-11 — 术语表与术语治理

- **涉及文件**：
  - 新建：`GLOSSARY.md`（术语表，首批约 80 条）、`CONSTITUTION.md` 新增第 11 条（术语治理与引用规则）
  - 修改：`AGENTS.md`（新增第 5bis 条术语引用纪律；第 4 条目录结构加入 `GLOSSARY.md`）、`README.md`（文件地图加入 `GLOSSARY.md`；阅读路径补术语查询）、`TODO.md`（新增术语表相关工作项）
- **变更摘要**：新增 `GLOSSARY.md` 作为立法层的支撑文件，覆盖 A 领域无关核心概念（16 条）、B 框架自创机制术语（20 条）、C 编译域术语（15 条）、D 治理术语（13 条）、E 行业缩写（10 条）、F 接口契约术语（8 条）。`CONSTITUTION.md` 新增第 11 条，规定术语准入条件、引用纪律、废弃与合并、与 `anchored-entries.jsonl` 的同步、与 `SOURCE_LEDGER.md` 的关系、版本纪律。`AGENTS.md` 新增第 5bis 条，规定输出中的术语引用纪律。
- **关联 ADR**：无（术语表的建立是 CHANGELOG 级变更；术语治理条款的加入是 `CONSTITUTION.md` 的实质变更，但因其不降低第 5 条保护清单中的任何约束，且由本批次记录，不单独设 ADR。若未来某术语的定义变更影响规则理解，则需 ADR。）
- **状态**：生效

---

### 批次 0004 — 2026-11-11 — 状态台账与仓库初始化

- **涉及文件**：
  - 新建：`STATE.md`、`.gitignore`
  - 修改：`README.md`（移除状态与版本段及修订标记，文件地图加入 `STATE.md`）、`AGENTS.md`（目录结构与维护责任表加入 `STATE.md`）、`GLOSSARY.md`、`GRAMMAR.md`、`SOURCE_LEDGER.md`、`spec/ASSUMPTION_PROTOCOL.md`、`spec/COMPILATION_META.md`、`spec/COMPILATION_METHODS.md`、`spec/INTERFACE_CONTRACT_SPEC.md`、`contracts/resolver.md`、`knowledge/methods/registry-skeleton.md`、`validation/CHECKLIST.md`（删除文件头版本行、文件级状态行与变更记录）
- **变更摘要**：将各文件的版本与文件级状态元信息移出正文，集中登记于 `STATE.md`；`CHANGELOG.md` 继续记录批次历史，`TODO.md` 继续记录待办与任务状态。在 `project-management/` 内初始化 Git 仓库并完成初始提交。
- **关联 ADR**：无（不改变任何规范语义）
- **状态**：生效

---

### 批次 0005 — 2026-11-11 — 上下文装配、接地判据与反例用例

- **涉及文件**：
  - 新建：`QUICKSTART.md`、`ERRATA.md`、`spec/CONTEXT_ASSEMBLY.md`、`spec/GROUNDING_CRITERIA.md`、`scripts/README.md`、`scripts/check_glossary_sync.md`、`validation/test-cases/README.md`、`validation/test-cases/TC-A1-02.md`、`validation/test-cases/TC-C1-03.md`、`validation/test-cases/TC-E1-04.md`
  - 修改：`CONSTITUTION.md`（第 11.5 条末尾补同步检查的执行方式；新增第 12 条接地治理）、`AGENTS.md`（第 4 条目录结构与维护责任表；新增第 6bis 条与 QUICKSTART、装配、接地的衔接）、`README.md`（文件地图、阅读路径、`CONSTITUTION.md` 行）、`STATE.md`（新增 10 个文件登记）、`TODO.md`（新增工作项）、`CHANGELOG.md`（本批次）
- **变更摘要**：依据分享链接 2 的内容，补齐“上下文装配（`spec/CONTEXT_ASSEMBLY.md`）”“接地完成判据（`spec/GROUNDING_CRITERIA.md`）”“最小走查样例（`QUICKSTART.md`）”“幻觉更正台账（`ERRATA.md`）”“反例检验用例库（`validation/test-cases/`）”“术语同步检查规格（`scripts/`）”六个缺口；`CONSTITUTION.md` 新增第 12 条（接地治理），与第 10 条（编译治理）、第 11 条（术语治理）并列。分享链接 1 的诊断项中，装配规范、走查样例、反例库、ERRATA、接地判据、LLM 接合示例、术语同步机制已由本批次覆盖；ADR 拒绝记录、检查回放机制等未覆盖项登记于 `TODO.md`。
- **取舍说明**：
  1. **批次号顺延**：分享原文标注的批次号为 0004，与已发布的批次 0004（状态台账与仓库初始化）冲突；按第 3.1 条“批次号一经发布永不复用”，本批记为 0005。
  2. **版本头未采用**：分享原文各新文件含 `**版本**：v0.1` 行，`README.md` 含“状态与版本（修订）”段及 `v0.4` 等表述；按现行口径（文件不携带版本头与文件级状态元信息），一律不写入，文件当前状态统一登记于 `STATE.md`，版本历史由本文件批次承载。
  3. **反例用例只落正文**：分享原文表格列 13 个用例，仅 3 个提供完整正文；本批只落这 3 个，其余 10 个登记 `TODO.md` T-101，不补写推断内容。
  4. **接地判据改写**：`GROUNDING_CRITERIA` 的 G2/G3 原依赖产物版本头与版本对齐检查，现行仓库已无版本头，故改为基于 `STATE.md` 与部署配置判定；改动点登记 `ERRATA.md` E-008。
  5. **ID 冲突修复**：`QUICKSTART` 中 assumption 与 HumanActor 共用 `A-001`，assumption 改用 `AS-001`；登记 `ERRATA.md` E-009。
  6. **`partially_grounded` 的保留范围**：该词仅作为接地判定的三值结论之一保留于 `spec/GROUNDING_CRITERIA.md` 第 4 节与 `CONSTITUTION.md` 第 12.3 条，不用于声明本包当前状态。
- **关联 ADR**：无（新增文件不改变既有规则语义；`CONSTITUTION.md` 第 12 条为新增治理条款，未降低第 5 条保护清单中的任何约束，理由同批次 0003）
- **状态**：生效

---

### 批次 0006 — 2026-11-11 — 版本与状态治理决策

- **涉及文件**：
  - 新建：`adr/0003-version-and-state-governance.md`
  - 修改：`STATE.md`（登记 ADR-0003）、`TODO.md`（新增 T-109、T-110）、`CHANGELOG.md`（本批次）
- **变更摘要**：记录版本与状态治理决策：文件层不承载版本与状态、包层以 annotated tag 声明单一版本、`STATE.md` 为唯一状态来源且按目录给默认值、版本号按 major/minor/patch 递增、首个包版本取 `v0.4.0`。ADR 同时登记了由该决策引出的两项待办：产物版本链重构（T-109）与 `manifest.json` 与 tag 的一致性检查（T-110）。
- **关联 ADR**：ADR-0003（accepted）
- **状态**：生效

---

### 批次 0007 — 2026-11-11 — 落地包层版本与产物基线

- **涉及文件**：
  - 新建：`adr/0004-artifact-baseline-by-commit.md`、`manifest.json`
  - 修改：`CONSTITUTION.md`（第 9 条、第 11.7 条）、`spec/COMPILATION_META.md`（第 3.6 节、第 7 条编译产物段、第 7.5 节、第 10 条、方法声明模板第 9 节）、`spec/methods/deterministic-checker.md`（第 9 节）、`AGENTS.md`（第 3.1 条、第 4 条目录树与维护责任表）、`README.md`（文件地图、版本与发布、阅读路径）、`ERRATA.md`（E-011）、`TODO.md`（T-108、T-109 关闭；T-110 更新；新增 T-111）、`STATE.md`、`CHANGELOG.md`（本批次）
- **变更摘要**：把“版本号在文件头声明”改为“版本在包层以 annotated tag 声明，文件不承载版本”；新增根目录 `manifest.json` 记录包版本 `0.4.0` 与 `pm_contract_version`；把编译域的“产物版本 = 源文件版本函数”改为“产物记录生成基线的 `source_commit`，装配时比对当前源提交，脏工作区直接判定过期”，拒绝语义保留（ADR-0004）。
- **取舍说明**：
  1. 改动范围超出原计划的 `CONSTITUTION`/`AGENTS`/`README`/`ERRATA`/`TODO`：`spec/COMPILATION_META.md` 与 `spec/methods/deterministic-checker.md` 同样以文件版本为前提，不改会与新第 9 条直接矛盾；经用户确认后一并修改。
  2. 产物基线单立 ADR-0004 而非并入 ADR-0003：前者是运行时机制变更（改变 `validation/` 产物的生成与装配校验方式），后者是版本载体决策；两者的被否方案与代价不同，分列便于日后追溯。
  3. `manifest.json` 的包版本与 tag 可能漂移，登记 T-110 做一致性检查；`validation/CHECKLIST.md` 尚未写入 `source_commit`，登记 T-111，在此之前按“基线未记录”处理为过期。
- **关联 ADR**：ADR-0003（accepted）、ADR-0004（accepted）
- **状态**：生效

---

### 批次 0008 — 2026-11-11 — 状态台账改为目录默认值并对账

- **涉及文件**：
  - 新建：`scripts/check_state.py`
  - 修改：`STATE.md`（由逐文件登记改为“目录默认值 + 例外”）、`scripts/README.md`（脚本清单与运行方式）、`AGENTS.md`（第 4 条目录树）、`CHANGELOG.md`（本批次）
- **变更摘要**：`STATE.md` 不再逐文件登记 40 个文件，改为八条目录默认值（`./`、`spec/`、`contracts/`、`contracts/examples/`、`knowledge/`、`adr/`、`scripts/`、`validation/`）加两条例外（`adr/ADR-TEMPLATE.md` 为 `template`、`knowledge/methods/registry-skeleton.md` 为 `skeleton`）。新增 `scripts/check_state.py`，以 `git ls-files` 为准校验：漏登、登了未被跟踪的文件、状态值非法、例外重复均报错，退出码 0/1/2。
- **取舍说明**：状态默认值按最长前缀匹配，避免逐文件维护；例外表只允许承载“目录默认值不足以描述”的文件，防止例外表退化为第二份逐文件清单。`scripts/README.md` 中 `check_glossary_sync` 的实现待办原指向 `T-102`（该编号已用于 ADR 拒绝记录），一并更正为 `T-090`。
- **关联 ADR**：ADR-0003（accepted）
- **状态**：生效

---

### 批次 0009 — 2026-11-12 — 来源表收缩、本地资料入表与三空间清理

- **涉及文件**：
  - 新建：`adr/0005-source-ledger-scope.md`、`adr/README.md`
  - 修改：`SOURCE_LEDGER.md`（整体重写）、`CONSTITUTION.md`（第 2.3、2.4、3.6、4、6、8、10.3、10.7 条）、`CHARTER.md`（C4）、`GRAMMAR.md`（规则组 B 状态说明与汇总表）、`GLOSSARY.md`（T-B-006、T-B-020、T-C-012、T-D-005、T-E-001、T-E-003、T-E-005、T-E-007）、`README.md`（文件地图与定位）、`AGENTS.md`（第 4 条目录树、第 7 节）、`ERRATA.md`（删除原 E-001；E-002、E-003 改写去悬空引用）、`adr/ADR-TEMPLATE.md`、`spec/ASSUMPTION_PROTOCOL.md`、`spec/COMPILATION_META.md`、`spec/CONTEXT_ASSEMBLY.md`、`spec/methods/deterministic-checker.md`、`contracts/examples/construction.pm-contract.yaml`、`knowledge/anchored-entries.jsonl`、`knowledge/methods/registry-skeleton.md`、`TODO.md`（新增 T-112、T-113）、`CHANGELOG.md`（本批次）
- **变更摘要**：删除过期来源 `ISO21500-2012`、`PMBOK7-2021`；将 ADR 记法与 RFC 2119 移出来源表，ADR 格式移入新建的 `adr/README.md`，规范性措辞改引 BCP 14（RFC 2119 + RFC 8174，写入 `CONSTITUTION.md` 第 3.6 条）；把 `resources/pm/` 下实际存在的本地资料登记为正式来源并写明 `local_path`；新增 `SPRINGER-PMBOK-2024`（仅元数据，正文未获取）；OWL 候选保留并标注“有可靠来源但尚未获取”；删除 Jarke 三世界候选，并清理非软件工程语境的三空间叙述；放宽 `CONSTITUTION.md` 第 2.3 条的入表口径、将第 2.4 条改为允许删除并以 git 历史追溯。
- **取舍说明**：
  1. 软件工程语境（`spec/INTERFACE_CONTRACT_SPEC.md` 第 7 节与 `contracts/examples/software-engineering.pm-contract.yaml`）中的“三空间”作为该领域技能的专有概念保留，其余文档一律改为“外部领域本体”。
  2. `ERRATA.md` 原 E-001 随 Jarke 条目一并删除，条目编号不再复用；E-002、E-003 因引用已删除的来源 ID 而改写表述，事实与处置结论未变。
  3. `PRINCE2® 7th Edition（无水印）.pdf` 不作为核对依据，内容以官方水印版为准；排除的是副本，不是文献。
- **关联 ADR**：ADR-0005（accepted）
- **状态**：生效

---

### 批次 0010 — 2026-11-12 — 区分知识来源与规范依据并强制编译落点

- **涉及文件**：
  - 新建：`adr/0006-knowledge-sources-vs-normative-basis.md`、`scripts/check_ledger_landings.py`
  - 修改：`CONSTITUTION.md`（第 2 条新增两类文献区分与 `compilation_landing` 字段；第 2.1 条接第 2.6 条；新增第 2.6 条）、`SOURCE_LEDGER.md`（字段说明与 7 个 active 条目的编译落点）、`scripts/README.md`、`AGENTS.md`（第 4 条目录树）、`README.md`（文件地图）、`TODO.md`（新增 T-114、T-115）、`CHANGELOG.md`（本批次）
- **变更摘要**：把“知识来源”与“规范依据”拆为两类；来源表新增正向准入测试（领域无关 + 编译落点），每条 active 来源必须能指向 `GRAMMAR.md` 规则、`knowledge/` 条目、方法条目或检查项；新增 `check_ledger_landings.py` 机械核对落点存在性，`SPRINGER-PMBOK-2024` 因正文未获取记 `pending:T-112`。
- **取舍说明**：`compilation_landing` 与 `claim_mapping` 保留并存——前者用于机械检查、后者保留论断级的自然语言说明；两者漂移风险登记为后续缺口，未在本批次引入额外校验。
- **关联 ADR**：ADR-0006（accepted）
- **状态**：生效

---

### 批次 0011 — 2026-11-12 — 开源化：MIT 许可证与英文 README

- **涉及文件**：新增 `LICENSE`、`README.en.md`；修改 `README.md`（顶部语言互链、治理阅读路径补 ADR-0005/0006）、`CHANGELOG.md`（本批次）
- **变更摘要**：加入 MIT 许可证（版权人 `onlookor`，年份 2026）；新增与中文版结构对应的英文 README，并在两版顶部互相链接；中文版保持为默认入口，未被覆盖。
- **取舍说明**：英文版按现有中文 README 逐节翻译，未新增任何未实现的能力描述；文件地图中增加 `README.en.md` 一行以保持两版导航对称。
- **关联 ADR**：无（不改变规范语义）
- **状态**：生效

---

### 批次 0012 — 2026-11-12 — Zenodo 候选条目核查结论

- **涉及文件**：`SOURCE_LEDGER.md`（候选条目改记为已核实存在、领域不符）、`ERRATA.md`（新增 E-012）、`README.md`（文件地图补 `README.en.md`）、`CHANGELOG.md`（本批次）
- **变更摘要**：实际检索 Zenodo 与搜索引擎，确认该论文存在（Jennifer Evans，2025-12-24 预印本，DOI `10.5281/zenodo.18039274`；同日另有 `10.5281/zenodo.18043672`）。结论：**不是幻觉**，但主题为 RAG 与幻觉机制，不满足通用项目管理领域测试，仍不入表。
- **取舍说明**：两项记录题名不同、作者与日期相同，无法仅凭页面判断哪一项是评审当初所指；登记中并列两个 DOI，不擅自合并。
- **关联 ADR**：无（候选条目未入表，不改变规范）
- **状态**：生效

---

### 批次 0013 — 2026-11-12 — 按本地实际文件名修正来源表 local_path

- **涉及文件**：`SOURCE_LEDGER.md`、`CHANGELOG.md`（本批次）
- **变更摘要**：逐份核对 `resources/pm/` 的实际文件名后，修正 `ISO21502-2020`、`PRINCE2-2023`、`ProjectCO-2024`、`ThingFO-2021`、`PMBOK8-2025` 的 `local_path`，并同步修正非官方镜像的排除记录。此前登记的路径是简化写法，与磁盘上的文件不对应。
- **取舍说明**：只改路径字符串，来源条目、落点与结论不变；PMBOK 第 8 版的出版日期经 PMI 官方页面核对为 2025-11，本地文件元数据标注 2026 系该副本的版权/印刷年，不据以修改版本年份。
- **关联 ADR**：无（登记信息的准确性修正）
- **状态**：生效

---

### 批次 0014 — 2026-11-12 — 锚点稳定化：禁用行号、稳定 ID 与指纹基线

- **涉及文件**：
  - 新建：`spec/ANCHOR_SPEC.md`、`scripts/check_anchors.py`、`scripts/anchor_baseline.json`、`adr/0007-anchor-discipline.md`
  - 修复失效引用：`CONSTITUTION.md`（第 3.1、4、7.3 条）、`GRAMMAR.md`（权威关系、字段表）、`validation/CHECKLIST.md`（执行纪律第 1、5 条）、`spec/ASSUMPTION_PROTOCOL.md`（第 5、8 节）、`spec/INTERFACE_CONTRACT_SPEC.md`（第 8 节）、`spec/COMPILATION_METHODS.md`（CM-DET-CHECKER 的 `spec` 字段）、`spec/methods/deterministic-checker.md`（附录来源说明）、`TODO.md`（T-013、T-070、T-114）
  - 同步：`scripts/README.md`、`AGENTS.md`（目录树、维护责任表）、`README.md`（文件地图、治理阅读路径）、`CHANGELOG.md`（本批次）
- **变更摘要**：盘点全仓锚点形态，确认活跃文件无行号锚点（规则/检查项/来源/术语/方法/待办均为稳定 ID，另有 236 处章节号引用）；行号锚仅存在于 ADR-0006 的 7 处历史证据中，且已随来源表重写失效。新增锚点规范与检查器：禁止行号 locator，校验文件、稳定 ID、章节号与标题路径可解析，校验 `grounding_ref` 均指向 active 来源，并对 `GRAMMAR.md` 17 条规则与 `SOURCE_LEDGER.md` 7 个来源做文本块指纹比对。首轮实跑清出 11 处指向已删除 `COMPILATION_SPEC.md` 的活跃引用并全部修复（T-070 完成）。
- **取舍说明**：不引入软工技能的 `@m:`/`@d:` 前缀语法——现有引用在插行场景下本就稳定，全量改写没有定位收益。只复用其“稳定地址、行号禁用、指纹只作漂移、失效显式报错、冻结 as-of”五条原则。指纹采用“空白规范化 + sha256”，不引入 Markdown AST 依赖。
- **负例验证**：在副本中插入一行——块外插入 0 错误 0 警告；在 G-A1 块内插入仅 `rule:G-A1` 一条漂移警告，其余 16 条规则与 7 个来源不受影响。
- **关联 ADR**：ADR-0007（accepted）
- **状态**：生效

---

### 批次 0015 — 2026-11-12 — 按本地 PDF 核对来源；规则组 B 重新锚定

- **涉及文件**：
  - 修改：`GRAMMAR.md`（第 1 条说明、规则组 B 引言与 G-B1/G-B2、G-F1–G-F4 与 G-G1–G-G3 的核验注、规则组状态汇总表 B 行）、`SOURCE_LEDGER.md`（`ISO21502-2020`、`PRINCE2-2023`、`ProjectCO-2024`、`ThingFO-2021`、`PMBOK8-2025`、`SPRINGER-PMBOK-2024` 的核验状态、`claim_mapping`、`allowed_uses`；废止记录；状态汇总）、`ERRATA.md`（新增 E-013–E-016，更新 V-001–V-003）、`TODO.md`（T-113 关闭，T-112 补注，新增 T-118、T-119）、`spec/ANCHOR_SPEC.md`（外部资料页码定位的澄清）
  - 新建：`adr/0008-reanchor-dimension-rules.md`
- **变更摘要**：安装并验证 poppler（`pdftotext`/`pdfinfo`/`pdftoppm`）与 Tesseract（eng/chi_sim/chi_tra），对 `resources/pm/` 六份 PDF 逐份判定载体形态：全部具备文本层，无整本扫描件；ProjectCO 的插图页另做 300 dpi 转图 OCR 复核。核对结论：ISO 21502:2020 不含“五过程组 × 十主题组”矩阵，正文为第 6 章集成实践（八个生命周期位置）与第 7 章管理实践（十七项）；附录 A 对 ISO 21500:2012 的映射为资料性。G-B1、G-B2 据此改写并解除 `pending_reanchor`，`severity` 保持 `advisory`（ADR-0008）。PRINCE2 第 7 版七项原则名称、授权链、产品验收与收尾、问责委派已逐页核对并记入。勘误另记：SPRINGER 请求信实际未发出（SMTP 535）、ProjectCO 本地副本未见 `Actor`/`Commitment`/`Constraint` 三个术语（原文用 `Agent`）。
- **取舍说明**：未改动 `knowledge/` 条目与 G-A1/G-D1/G-E1 的规则文本——术语归属需先取得论文外部附录（T-119），规则改写需另走 ADR。中间产物（全文文本、渲染图、OCR 输出）全部落在 `/tmp/pm-extract/`，未进入仓库；`SOURCE_LEDGER.md` 只登记页码定位与自述结论，不复制原文段落。
- **验证**：`scripts/check_state.py`、`scripts/check_ledger_landings.py`、`scripts/check_anchors.py` 全部通过；锚点指纹基线已按规则文本变更重新冻结。
- **关联 ADR**：ADR-0008（accepted）
- **状态**：生效

---

### 批次 0016 — 2026-11-12 — 原始资料与提取产物禁入库，并接入阻断式检查

- **涉及文件**：
  - 修改：`CONSTITUTION.md`（新增第 13 条；第 5 条保护清单增列第 13 条）、`AGENTS.md`（新增第 7bis 条；第 4 条目录树加入 `.githooks/` 与 `check_no_raw_material.py`）、`.gitignore`（原始资料、扫描件、压缩包与提取产物命名）、`scripts/README.md`（脚本清单、运行方式、判定规则与阈值）、`TODO.md`（新增 T-120）
  - 新建：`scripts/check_no_raw_material.py`、`.githooks/pre-commit`、`adr/0009-no-raw-material-in-git.md`
- **变更摘要**：把“PDF 原文与成段摘录不得进 git”从说明升级为可阻断的纪律。第 13 条明确四类禁止内容（原始资料、提取产物、成段原文、可替代原作的改写）与四类允许形态（页码定位、来源标识、单条不超过一行或一句并附出处的最短引证、自述转述），并规定检查失败即阻断提交。检查器扫描已跟踪文件，按扩展名、体积、引用长度、连续长行、页码序列、目录点线、替换字符与控制字符判定；pre-commit 钩子调用同一脚本。
- **扫描结果**：当前 51 个跟踪文件 0 错误；全历史 `git log --all --diff-filter=A` 未发现任何文档/电子书/图片/压缩包类文件被加入过；最大跟踪文件 35 KB（`GLOSSARY.md`）；未发现贴入 Markdown 的成段原文。
- **负例验证**：在临时仓库放入伪造 PDF、600 KiB 文本、500 字符引用、8 行页码序列，检查器报出 `RM-EXT`、`RM-SIZE`、`RM-QUOTE`、`RM-PAGESEQ` 并以 1 退出；启用钩子后同一提交被拒绝（`git commit` 退出码 1），仓库只保留基线提交。
- **取舍说明**：引用块阈值按现有文档上限（343 字符）留出余量取 800 字符；连续长行阈值按现有最长连续段（6 行）取 15 行。检查器只覆盖“可机械判定”的形态，纯改写型替代无法凭文本特征识别，由第 13.1 条第 4 项与人工评审兜底，不宣称检查器能覆盖全部违规。
- **钩子接入**：`git config core.hooksPath .githooks`（当前克隆已启用；该设置不入库，克隆方需自行执行，等价命令已写入 `scripts/README.md` 与 `AGENTS.md` 第 7bis 条）。
- **关联 ADR**：ADR-0009（accepted）
- **状态**：生效

---

### 批次 0018 — 2026-11-13 — 自建本体可行性评估与受控入库

- **涉及文件**：
  - 新建：`spec/ONTOLOGY_FEASIBILITY.md`、`adr/0010-self-authored-ontology-in-git.md`、`ontology/README.md`
  - 修改：`CONSTITUTION.md`（第 13.2 条新增第 5 项；新增 13.6；第 5 条保护清单措辞）、`AGENTS.md`（第 7bis 条新增第 7 项；第 4 条目录树与维护责任表）、`scripts/check_no_raw_material.py`（本体扩展名与 `RM-ONTO-*`）、`scripts/README.md`、`STATE.md`（新增 `ontology/` 默认状态）、`README.md`（文件地图）、`TODO.md`（新增 T-122–T-123）
- **变更摘要**：对“从本地 PMBOK 8th 自建以约束为主的本体”做可行性评估，并与“手工知识条目 + 反例用例 + 全文档级编译”的基线逐项对比，给出最小原型与全量两档规模。评估结论为：技术可行，采用 SHACL-first；本体保持非规范、非来源。治理侧同步放开一条受控通道：第 13.6 条允许“自写定义 + 标准术语标签”的本体入库，原始资料、提取产物、成段原文与可替代原作的改写仍严禁；检查器新增头注释、超长字面量与超长注释检查。
- **事实更正**：本地 PMBOK 8th 正文显示该版**恢复**了过程式结构——5 个 Focus Areas、7 个绩效域、40 个非规定性过程（Governance 9、Scope 6、Schedule 3、Finance 4、Stakeholders 7、Resources 5、Risk 6），第 4 章为输入/输出、第 5 章为工具与技术。因此“第 8 版缺少过程式类层次”不成立；它缺少的是机器可读本体，不是过程层次。
- **验证**：四个检查器通过（`check_state.py` 0、`check_ledger_landings.py` 0 错误 1 警告、`check_anchors.py` 0 错误 0 警告、`check_no_raw_material.py` 0 错误）。真实负例（临时仓库，不入库）：通过 `.ttl` 通过；含 600 字符转录字面量的 `.ttl` 报 `RM-ONTO-LITERAL`；缺头注释的 `.ttl` 报 `RM-ONTO-HEADER`；600 字符注释行报 `RM-ONTO-COMMENT`；连续 15 行 100+ 字符注释报 `RM-PROSEBLOCK`；伪造 PDF 仍报 `RM-EXT`；全部以非零码退出。
- **取舍说明**：
  1. 批次号取 0018 而非 0017：0017 已在 `TODO.md` 中作为邮件登记标签出现，但未形成 CHANGELOG 条目；为避免同一编号指向两件事，本批顺延，0017 不复用。
  2. 第 13.6 条是对 13.1 第 4 项的边界澄清，不缩小 13.1 的四类禁止，也不降低 13.3 的阻断强度；不满足 13.6 的本体仍按 13.1 禁止。
  3. 未改动 `SOURCE_LEDGER.md`：`PMBOK8-2025` 的 `allowed_uses` 仍限“原则层交叉验证”，本体不得作为 `grounding_ref`；扩展来源用途另立 T-123 与 ADR。
- **关联 ADR**：ADR-0010（accepted）
- **状态**：生效

---

### 批次 0019 — 2026-11-13 — 全量本体与形状校验

- **涉及文件**：
  - 新建：`ontology/pmbok8-vocab.ttl`、`ontology/pmbok8-processes.ttl`、`ontology/pmbok8-artifacts.ttl`、`ontology/pmbok8-tools.ttl`、`ontology/pmbok8-shapes.ttl`、`ontology/fixtures/valid.ttl`、`ontology/fixtures/invalid-*.ttl`（24 个）、`ontology/fixtures/manifest.json`、`scripts/validate_ontology.py`
  - 修改：`ontology/README.md`、`STATE.md`（`ontology/` 改为 `active`）、`AGENTS.md`（第 4 条目录树、第 7bis 条状态）、`README.md`（文件地图）、`TODO.md`（T-122 关闭，新增 T-125、T-126）、`spec/ONTOLOGY_FEASIBILITY.md`（全量档）、`adr/0010-self-authored-ontology-in-git.md`（边界与结果）、`CONSTITUTION.md`（13.6 内容质量口径）
- **变更摘要**：按全量档构建本体：92 个类、35 个对象属性、7 个数据类型属性、7 个绩效域、5 个焦点区、40 个过程及其输入/输出/技术链接、124 个工件、185 个工具与技术、24 条 SHACL 形状，以及每条形状对应的违规 fixture。工件与工具个体保留术语名、类别与页码，定义状态为 `taxonomy-only`；类与属性的定义全部自写。
- **验证**：`python3 scripts/validate_ontology.py` 对本体现有全部 TTL 输出 `conforms: true`；`--matrix` 逐条运行 24 个违规 fixture，24/24 判出预期形状，`valid.ttl` 通过；缺少 `rdflib`/`pyshacl` 时退出码 2 并输出“无法评估”。`check_no_raw_material.py` 对本体文件保持通过（含 `RM-ONTO-HEADER`、`RM-ONTO-LITERAL`、`RM-ONTO-COMMENT`、`RM-PROSEBLOCK`）。
- **取舍说明**：
  1. 不修改 `GRAMMAR.md` 的 `grounding_ref`，不改任何 `check_id` 的绑定，不新增编译方法；形状只约束本体自身的结构。
  2. 本体是派生工件，不是来源；`grounding_ref` 接入建议登记为 T-125。
  3. 工件与工具的自写定义未逐条完成，登记为 T-126；不以原文改写填充。
- **关联 ADR**：ADR-0010（accepted）
- **状态**：生效

---

### 批次 0020 — 2026-11-13 — 引入计划层并给出治理结构改造提案

- **涉及文件**：
  - 新建：`ROADMAP.md`、`spec/GOVERNANCE_RESTRUCTURE.md`
  - 修改：`README.md`、`README.en.md`（文件地图各加一行 `ROADMAP.md`）
- **变更摘要**：按任务台账的实际结构给出判断：`TODO.md` 作为单点台账够用，作为排序与验收依据不足。具体缺陷九条（按批次分组导致同一目标分散、无依赖图与关键路径、无出口条件、无量级、重复与重叠、状态记号不统一、关闭规则自相矛盾、无发布 lane、无外部阻塞状态），另有两条事实缺口（规则组 B 的 `pending_reanchor` 签注已过期；`validation/CHECKLIST.md` 缺 `source_commit`）。据此新增 `ROADMAP.md`：目标 D1–D5、M0–M7 里程碑与可验证出口条件、关键路径与并行关系、全部 64 个未完成条目的唯一归属、按条目数与人工判断量给出的工作量量级、`TODO.md` 保留为台账的处置建议，以及 `v0.4.0` 之后 11 个提交按 minor 定为 `v0.5.0` 的发布安排。
- **治理提案**：`spec/GOVERNANCE_RESTRUCTURE.md` 给出诊断（各文件职责、权威边界、`STATE`/`CHANGELOG`/`TODO`/计划层四者分工与冲突、六条治理结构问题）、目标结构（五层与冲突裁决顺序）、`CONSTITUTION.md`/`AGENTS.md`/`README.md`/`STATE.md`/`TODO.md` 的逐条改法、迁移与防断链措施、代价与风险，以及最小与完整两档方案。推荐最小方案，并把 `manifest.json` 与 tag 的一致性检查并入现有脚本。
- **未提交内容**：`CONSTITUTION.md`、`AGENTS.md`、`STATE.md`、`TODO.md` 的实质改动，以及 ADR-0011，均未落库，待批准后按提案第 4 节的顺序执行。本批次只登记文档层面的新增与导航更新。
- **验证**：`scripts/check_state.py`（89 个跟踪文件，0 错误）、`scripts/check_ledger_landings.py`（0 错误 1 警告，警告为 SPRINGER-PMBOK-2024 待 T-112）、`scripts/check_anchors.py`（46 个 Markdown 文件，0 错误 0 警告）、`scripts/check_no_raw_material.py`（0 错误）。锚点基线未改动，因为规则与来源文本块未变。
- **关联 ADR**：无（治理层改动待 ADR-0011 批准）
- **状态**：生效（仅文档；治理条文改动未生效）
