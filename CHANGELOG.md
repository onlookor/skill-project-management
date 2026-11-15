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

---

### 批次 0021 — 2026-11-13 — 落库最小治理改造：调度层、TODO 重组与发布一致性检查

- **涉及文件**：
  - 新建：`adr/0011-schedule-layer-and-plan.md`
  - 修改：`CONSTITUTION.md`（第 4 条新增调度层一句）、`AGENTS.md`（3.1、3.2、3.3、新增 3.4、第 4 条目录树与维护责任表、第 8 条）、`ROADMAP.md`（移除现状诊断，改为只保留目标、里程碑、依赖与执行内容）、`TODO.md`（按 M0–M7 重组、增加里程碑列、统一状态、补 `blocked-external`）、`STATE.md`（维护规则一句）、`README.md`、`README.en.md`（`TODO.md` 描述与 ADR 范围）、`scripts/check_state.py`（发布一致性核对）、`scripts/README.md`、`spec/GOVERNANCE_RESTRUCTURE.md`（标注为已批准的审查附件）
- **变更摘要**：
  1. 现状诊断（九条 TODO 结构缺陷、两条事实缺口、调度层重叠与治理结构问题）移入 ADR-0011；`ROADMAP.md` 不再记录判断与理由，只保留目标 D1–D5、M0–M7 与出口条件、关键路径、T-xxx 映射、工作量量级、TODO 处置与发布安排。
  2. 按最小方案落库：`CONSTITUTION.md` 第 4 条增加“调度层变更不属实质性修改”一句；第 1 条调度层说明、第 5 条第 2 项扩容、独立检查脚本三项未做。
  3. `AGENTS.md` 修正 3.2 的关闭规则冲突（保留行、标 `done`、附证据），把 TODO 收窄为单点台账；新增 3.4 定义 `ROADMAP.md`；目录树与维护责任表加入 `ROADMAP.md`；第 8 条增加两条禁止项。
  4. `TODO.md` 重组为 M0–M7 八个章节，新增里程碑列，状态统一为 `open` / `in-progress` / `blocked-external` / `done` / `dropped`；外部阻塞项（T-012、T-013、T-052、T-112、T-115、T-119、T-121）标注解锁条件；重复项加交叉引用而不合并编号；共 72 行（65 个未完成、7 个已关闭）。
  5. T-110 落地：`scripts/check_state.py` 增加 `manifest.json` 的 `package_version` / `release_tag` 与最新 annotated tag 的一致性核对，结构无法解析时以 2 退出。T-110 标记 `done`。
  6. 新增 T-127（规则组 B 签注同步）与 T-128（`v0.5.0` 发布），归入 M0。
- **验证**：`scripts/check_state.py`（92 个跟踪文件，0 错误；发布一致性 `0.4.0` ↔ `v0.4.0`）、`scripts/check_ledger_landings.py`（0 错误 1 警告，警告为 SPRINGER-PMBOK-2024 待 T-112）、`scripts/check_anchors.py`（47 个 Markdown 文件，0 错误 0 警告）、`scripts/check_no_raw_material.py`（0 错误）。锚点基线未改动。
- **关联 ADR**：ADR-0011（accepted）
- **状态**：生效

---

### 批次 0022 — 2026-11-13 — M0 收口：已决事项落库、产物基线与 v0.5.0

- **涉及文件**：
  - 修改：`adr/0011-schedule-layer-and-plan.md`（决定 10–12 与跟进事项）、`AGENTS.md`（3.2 状态归属、3.4 计划级动作）、`ROADMAP.md`（第 6 节入口、第 8 节计划级动作）、`spec/methods/deterministic-checker.md`（规则组 B 的状态与 1.2 节）、`spec/COMPILATION_METHODS.md`（`CM-DET-CHECKER` 的 `scope` 行）、`spec/ONTOLOGY_FEASIBILITY.md`（接合表一处过期事实）、`validation/CHECKLIST.md`（B 组状态与 `source_commit`）、`scripts/check_state.py`（tag 指向 `HEAD` 判断）、`scripts/README.md`、`manifest.json`（`0.5.0`）、`TODO.md`（T-111、T-127、T-128 关闭）、`CHANGELOG.md`（本批次）
- **变更摘要**：
  1. 三条已决事项补入 ADR-0011：ROADMAP 允许不分配 T 编号的计划级动作（需跨里程碑追踪者先登记 T 条目）；`blocked-external` 只定义于 `AGENTS.md` 3.2，不进入 `CONSTITUTION.md` 第 9 条；TODO 重复项暂不合并，只加交叉引用，编号语义不动。
  2. T-127：规则组 B 在 `validation/CHECKLIST.md`、`spec/methods/deterministic-checker.md` 与 `spec/COMPILATION_METHODS.md` 中统一为 `active`，`severity` 保持 `advisory`（ADR-0008）；F、G 组的 `assumption` 保留。
  3. T-111：`validation/CHECKLIST.md` 增加 `source_commit`，值为方法声明最后变更所在提交 `b16e3b8`（ADR-0004）。
  4. T-128：按 minor 规则发布 `v0.5.0`（`v0.4.0` 后无规范条文或契约 schema 的向后不兼容变更）；`manifest.json` 改为 `0.5.0` / `v0.5.0`；annotated tag `v0.5.0` 指向本批次提交，仅本地创建、未 push。
  5. `scripts/check_state.py` 的发布一致性检查增加“最新 annotated tag 必须指向 `HEAD`”判断，修复只比对版本字符串与 tag 名的假通过路径。
- **验证**：四个检查器退出码均为 0；`check_state.py` 发布一致性为 `0.5.0` ↔ `v0.5.0`，tag 指向 `HEAD`。
- **关联 ADR**：ADR-0011、ADR-0008、ADR-0004
- **状态**：生效

---

### 批次 0023 — 2026-11-13 — 发布闸门开发态豁免与提交前四检查器接入

- **涉及文件**：
  - 修改：`manifest.json`（新增 `release_state`）、`scripts/check_state.py`（显式发布态与 tag 校验）、`.githooks/pre-commit`（四检查器）、`AGENTS.md`（新增 3.5、修订 7bis）、`scripts/README.md`、`CHANGELOG.md`（本批次）
- **变更摘要**：
  1. `manifest.json` 的 `release_state` 显式声明 `development` 或 `released`；字段缺失按 `released` 严格处理，非法值退出 2；不得根据分支名、提交数或口头说明自动推断。
  2. `development` 仅把“HEAD 领先于 tag”降为警告；`release_tag` / `package_version` 一致性、tag 是否为 annotated、tag 是否为 HEAD 的祖先（分叉即错误）仍严格校验。
  3. `.githooks/pre-commit` 依次运行 `check_no_raw_material.py`、`check_anchors.py`、`check_ledger_landings.py`、`check_state.py`，任一失败即阻断；每个克隆需执行 `git config core.hooksPath .githooks`。
  4. 发布引导提交（切回 `released` 并递增版本）是 `--no-verify` 的唯一例外：tag 只能指向已存在提交；该提交后必须立即打 annotated tag 并复跑四个检查器。
- **验证**：负例提交被 `check_anchors.py` 阻断（退出码 1，未产生提交）；本批次提交由四检查器放行；开发态 `check_state.py` 退出 0 并输出领先警告，移除 `release_state` 后退出 1。
- **关联 ADR**：无（操作约定，规则出处 `AGENTS.md` 3.5；不改变发布点定义与立法文件）
- **状态**：生效

---

### 批次 0024 — 2026-11-13 — 关闭 M0 并发布 v0.5.1

- **涉及文件**：
  - 修改：`TODO.md`（T-116 关闭、M0 状态）、`ROADMAP.md`（M0 关闭与证据、当前基线）、`manifest.json`（`0.5.1` / `v0.5.1` / `released`）、`CHANGELOG.md`（本批次）
- **变更摘要**：
  1. T-116 关闭：`.githooks/pre-commit` 已依次运行四个检查器，任一失败阻断（批次 0023）。
  2. M0 五个出口条件复核通过，M0 正式关闭；工作项 T-070、T-110、T-111、T-114、T-116、T-127、T-128 均为 `done`。
  3. 发布 `v0.5.1`（patch）：`v0.5.0` 已推送，按发布纪律不回改已发布 tag；本次仅新增发布态豁免、提交前接入与调度收口，未新增规范文件、未改变规范条文或契约 schema。
  4. `release_state` 切回 `released`，annotated tag `v0.5.1` 指向本批次提交；本地创建，待批准后推送。
- **验证**：四个检查器 0 错误；`check_state.py` 输出 `manifest 0.5.1 ↔ v0.5.1（released）`，tag 指向 `HEAD`。
- **关联 ADR**：无（操作约定与调度收口；规则出处 `AGENTS.md` 3.5）
- **状态**：生效

---

### 批次 0025 — 2026-11-14 — 绕过通道留痕与撤除条件

- **涉及文件**：
  - 修改：`scripts/check_state.py`、`AGENTS.md`（3.5.1、3.5.2、7bis 第 5 条）、`ROADMAP.md`（M7 工作项与出口 6、发布表、当前基线）、`TODO.md`（T-129）、`manifest.json`（`release_state=development`）、`scripts/README.md`、`CHANGELOG.md`（本批次）
- **变更摘要**：
  1. 实测 git 不记录 `--no-verify`：发布提交对象只有 `tree` / `parent` / `author` / `committer` / `message`，没有旁路标记；因此改用固定 trailer 留痕：`Hook-Bypass: release-bootstrap`、`Hook-Bypass-Reason:`、`Hook-Bypass-Verified:`。
  2. `check_state.py` 对 `v0.5.2` 及以后的发布提交强制三项 trailer，缺失即错误；非发布提交携带即错误；`v0.5.1` 及以前不追溯。
  3. 撤除方向定为两段校验：pre-commit 识别 `Release-Target: <tag>` 显式待发布声明，pre-push 严格校验 tag 存在、annotated、指向 `HEAD`；登记 T-129（M7），硬约束为不晚于 `v0.5.2` 发布、机制生效后最多 1 次豁免。
  4. `manifest.json` 切回 `development`（`v0.5.1` 之后的开发态）。
- **钩子绕过**：本批次不是发布提交，未使用 `--no-verify`。
- **验证**：负例（`v9.9.9` 发布提交无 trailer）退出 1；正例（`v9.9.8` 携带三项 trailer）退出 0；主工作区四个检查器 0 错误，`check_state.py` 输出开发态警告。
- **关联 ADR**：无（操作约定，规则出处 `AGENTS.md` 3.5.1 / 3.5.2）
- **状态**：生效

---

### 批次 0026 — 2026-11-14 — 补 5 个 block 级 check_id 参考样例

- **涉及文件**：
  - 修改：`spec/methods/deterministic-checker.md`（附录 A.1）、`validation/CHECKLIST.md`（`source_commit` 推进）、`TODO.md`（T-011、T-130）
- **变更摘要**：
  1. 为 5 个 `block` 级 `check_id`（`PROJECT_MINIMAL_EXISTENCE`、`CONSTRAINT_ANCHOR_REQUIRED`、`DELIVERABLE_ASSERTION_LINK`、`CHANGE_CONSTRAINT_LINK`、`ROLE_MINIMAL_COMPLETENESS`）各补触发/不触发两组输入/输出样例，共 10 个；输入为 YAML 谓词快照，输出含 `check_id`、`source_rule`、`verdict`、`reason`。
  2. 样例只按附录 A 注册表判定列编写，未新增谓词、未改判定；`ROLE_MINIMAL_COMPLETENESS` 的角色合并子情形按 ERRATA E-004 / T-100 暂不纳入。
  3. 编写中发现 G-A1 的“约束作用于 `Outcome`/`Commitment`”子句未进入判定列，登记 T-130（M1，改判定需 ADR）。
  4. `validation/CHECKLIST.md` 的 `source_commit` 推进到样例提交 `c938c35`（ADR-0004）。
- **钩子绕过**：无。
- **验证**：四个检查器 0 错误（`check_anchors` 0 错误 0 警告；`check_ledger_landings` 1 条既有 `SPRINGER-PMBOK-2024` 警告）。
- **关联 ADR**：无（执行层补丁；T-130 若改判定另走 ADR）
- **状态**：生效

---

### 批次 0027 — 2026-11-14 — 补齐 17 个 check_id 的参考样例

- **涉及文件**：
  - 修改：`spec/methods/deterministic-checker.md`（附录 A.1.6–A.1.17）、`validation/CHECKLIST.md`（`source_commit` 推进）、`TODO.md`（T-011 关闭、T-131）
- **变更摘要**：
  1. 补齐剩余 12 个 `check_id` 的触发/不触发样例：G-B1、G-B2、G-C2、G-D2、G-E2、G-F1–F4、G-G1–G3，每个 2 例，共 24 个。
  2. 连同批次 0026 的 5 个 `block` 级样例，附录 A 现已覆盖 17/17 个 `check_id`，合计 34 个样例；`warn` / `assumption` 级样例显式标注 `severity` 与 `rule_status`。
  3. 样例只按注册表判定列编写，未新增谓词、未改判定；G-A1 约束作用边（T-130）与 G-E2 的 `assumption` 形式/验证条件（T-131）保持原判定，不在样例中固化歧义。
  4. `validation/CHECKLIST.md` 的 `source_commit` 推进到样例提交 `a72caaa`（ADR-0004）；T-011 标 `done`。
- **钩子绕过**：无。
- **验证**：四个检查器 0 错误（`check_anchors` 0 错误 0 警告；`check_ledger_landings` 1 条既有 `SPRINGER-PMBOK-2024` 警告）。
- **关联 ADR**：无（执行层补丁；T-130、T-131 若改判定另走 ADR）
- **状态**：生效

---

### 批次 0028 — 2026-11-14 — 缺口台账、到期裁定与 G 组样例修正

- **涉及文件**：
  - 新增：`GAP_LEDGER.md`、`scripts/check_gap_ledger.py`、`adr/0012-gap-ledger-and-adjudication.md`
  - 修改：`spec/methods/deterministic-checker.md`（A.1.15/A.1.16 修正）、`AGENTS.md`（新增 3.6、目录树、7bis）、`ROADMAP.md`（M1/M3 工作项与出口、D4、发布门槛）、`TODO.md`（T-132；T-100/T-130/T-131 交叉引用）、`scripts/README.md`、`.githooks/pre-commit`、`scripts/check_state.py`、`validation/CHECKLIST.md`（`source_commit` 推进）、`CHANGELOG.md`（本批次）
- **变更摘要**：
  1. **修正 G 组样例名称与内容**：A.1.15 由错误的 `TAILORING_DECISION_JUSTIFICATION` 改为注册表实际的 `TAILORING_RECORD_EXISTENCE`（G-G1）；A.1.16 由 `TAILORING_RATIONALE_ANCHOR` 改为 `TAILORING_NON_TRIMMABLE_SET`（G-G2）。批次 0027 报告的“17/17”在名称层面有误，本批次更正。
  2. **缺口归并**：G-D2、G-A2、G-E1 的未定义判定对象归并为 `G-001`（`undefined-object`，“规则引用了注册表中未定义的判定对象”）；T-130、T-131、T-100 保留独立编号，分别对应 `G-002`、`G-003`、`G-004`，台账注明四者同属“规则正文严于判定列”大类。
  3. **临时治理机制**：`AGENTS.md` 3.6 规定入口三条件与机械判据、L1–L3 分级与停留上限、按里程碑的例行裁定点、四处置出口、到期阻断与撤除条件；ADR-0012 记录决策与不写入 `CONSTITUTION.md` 的理由；T-132（M3）承担撤除评估。
  4. **机械核查**：`check_gap_ledger.py` 输出总数、`open`/`closed`、按级与到期计数、核查矩阵 `consistent` 比例；到期未裁定退出 1；`--staged` 要求规则/判定文件与台账同批更新。它成为第五个提交前检查器，并由 `check_state.py` 调用，使到期未裁定阻断发布。
  5. `validation/CHECKLIST.md` 的 `source_commit` 推进到 `033528f`（ADR-0004）。
- **钩子绕过**：无。
- **验证**：
  - 正面：`check_gap_ledger.py` 输出“4 条（open 4 / closed 0）；L1 1 / L2 2 / L3 1；到期 0；核查矩阵 12/17 consistent”，退出 0；五个检查器均退出 0。
  - 负例 1（到期）：副本台账改为 `M2` 后，输出 `G-004 已到期未裁定（登记 M1，L1 上限 1，到期 M2，当前 M2）`，退出 1。
  - 负例 2（暂存门）：只暂存方法判定列、不暂存台账时，输出“规则/判定变更必须先过缺口复核”，退出 1。
  - 负例 3（发布阻断）：主工作区临时改为 `M2` 后运行 `check_state.py`，输出“缺口台账核查未通过（退出码 1）……G-004 已到期未裁定”，退出 1。
- **关联 ADR**：ADR-0012
- **状态**：生效

---

### 批次 0029 — 2026-11-14 — T-107 最小原型与输入 schema

- **涉及文件**：
  - 新增：`validation/checker-prototype/checker.py`、`spec/CHECKER_INPUT_SCHEMA.md`
  - 修改：`spec/methods/deterministic-checker.md`（A.1 增加 schema 指针）、`AGENTS.md`（目录树）、`TODO.md`（T-107 标 `done`）、`GAP_LEDGER.md`（核查记录）、`validation/CHECKLIST.md`（`source_commit` 推进）、`CHANGELOG.md`（本批次）
- **变更摘要**：
  1. **可运行原型**：纯标准库实现，直接解析附录 A.1 的 34 个 YAML 样例，按 A 表判定列输出 `check_id` / `source_rule` / `severity` / `rule_status` / `verdict` / `reason`，并与样例期望逐项比对。
  2. **输入 schema 固定**：`spec/CHECKER_INPUT_SCHEMA.md` 定义通用约定、共享字段、17 个 `check_id` 的量化域、枚举与后续样例的遵循规则；附录 A 增加指针，后续样例不得自行引入字段。
  3. **覆盖缺口显式化**：原型在输出中逐条声明 5 处“未覆盖规则正文”（G-001 / G-002 / G-003 / G-004 对应条件），不关闭台账条目，也不宣称全保真。
  4. **依赖**：仅 Python 标准库；无第三方依赖，因此没有“缺依赖静默通过”的退化路径。
- **钩子绕过**：无。
- **验证**：
  - `python3 validation/checker-prototype/checker.py`：34/34 样例通过（100.0%），17/17 个 `check_id` 全通过，退出 0；输出含全部未覆盖项。
  - 五个检查器均退出 0；`check_gap_ledger.py` 仍为 4 条 `open`、到期 0、矩阵 12/17 `consistent`。
- **关联 ADR**：无（执行层补丁；T-100 / T-130 / T-131 的裁定仍走 ADR）
- **状态**：生效

---

### 批次 0030 — 2026-11-14 — 独立复核 TODO 与只读验收包

- **涉及文件**：新增 `validation/independent-review-package.md`；修改 `TODO.md`（T-133）、`ROADMAP.md`（M2 工作项与出口 4、映射表）、`AGENTS.md`（目录树）、`CHANGELOG.md`（本批次）
- **变更摘要**：
  1. **登记 T-133（M2）**：明确 T-107 的 34/34 是样例与实现同源的自证，不构成独立证据；关闭条件是“由非同源实现或人工逐条比对规则正文得出独立结论并记录差异”，不得用原型自身运行结果关闭。
  2. **只读验收包**：`validation/independent-review-package.md` 选定 `PROJECT_MINIMAL_EXISTENCE`（G-A1）、`DELIVERABLE_ASSERTION_LINK`（G-C1）、`CHANGE_CONSTRAINT_LINK`（G-D1），给出规则条款位置与陈述、6 个样例的原文位置与输入快照、原型实际判定与 `reason`、已知未覆盖项；**不包含原型源码**。
  3. **里程碑绑定**：ROADMAP M2 出口新增第 4 条，独立复核未完成不得关闭 M2。
- **钩子绕过**：无。
- **验证**：`python3 validation/checker-prototype/checker.py` 仍为 34/34（100.0%）；五个检查器均退出 0。验收包中的 6 个样例与附录 A.1.1 / A.1.3 / A.1.4 逐字一致。
- **关联 ADR**：无
- **状态**：生效

---

### 批次 0031 — 2026-11-14 — 独立复核缺口补登、T-133 部分完成与 `d3e2363` 更正

- **涉及文件**：`GAP_LEDGER.md`（新增 G-005–G-007、核查矩阵、共同成因、核查记录）、`TODO.md`（T-133 状态、新增 T-134–T-136）、`ROADMAP.md`（M2 工作项、出口 4 改写与新增出口 5、映射表）、`ERRATA.md`（E-017）、`CHANGELOG.md`（本批次）
- **变更摘要**：
  1. **补登缺口 G-005**（`rule-stricter`，L1，影响 G-C1，关联 T-134）：G-C1 正文要求断言内容是关于交付物“是什么、处于什么状态、满足什么条件”的明确陈述，判定列只检查 `asserted_by` 边存在；样例 A.1.3-2 的空断言仍期望 `pass`。
  2. **补登缺口 G-006**（`rule-stricter`，L1，影响 G-D1，关联 T-135）：G-D1 正文把变更提议限定为对 `Commitment` 或 `Deliverable` 的提议，判定列对任何变更提议生效，缺少 `target` 对象类型谓词。
  3. **补登缺口 G-007**（`undefined-object`，L1，影响 G-A1/G-A2/G-C1/G-D1，关联 T-136）：复核方所报 5 处“判定列语义未定明”**合并为一条**登记——端点量词、空对象语义、悬空引用的原因码、多违规时 `reason` 优先级、`about` 反向引用是否构成 G-C1 的出边。合并理由：五者同属“判定列语义未定明”，既非单一规则条款与判定列的落差，也没有各自独立的处置路径；逐条登记只会让同源问题重复占用裁定带宽，合并后用说明列逐项列举，裁定与核查仍可逐点覆盖。
  4. **到期口径**：G-005–G-007 均按 L1（停留 1 个里程碑）、登记 M1，到期 M2；`check_gap_ledger.py` 在 M1 下判定到期 0，可在 M2 内裁定，不构成必然到期。
  5. **T-133 改为部分完成**：复核已覆盖 3/17 个 `check_id`（G-A1、G-C1、G-D1 的 6 个样例，6/6 一致），剩余 14 项未复核；状态保持 `in-progress`，不因 6/6 关闭。ROADMAP M2 出口 4 由“3 个 `check_id`”改写为“全部 17 个 `check_id`”，并新增出口 5 要求 G-005–G-007 在 M2 关闭前裁定或显式降级。
  6. **`d3e2363` 矛盾更正**：见 `ERRATA.md` E-017。“文本输出补齐字段”准确；“未改动原型源码”若指该提交则不准确（实测只改 `checker.py`，+2 行），未改原型源码的是 `3defa84`。
- **钩子绕过**：无。
- **验证**：
  - `python3 scripts/check_gap_ledger.py`：7 条（open 7 / closed 0）；L1 4 / L2 2 / L3 1；到期 0；核查矩阵 10/17 `consistent`；退出 0。
  - `python3 validation/checker-prototype/checker.py`：34/34 样例通过（100.0%），17/17 个 `check_id` 全通过。
  - 五个检查器（`check_no_raw_material.py`、`check_anchors.py`、`check_ledger_landings.py`、`check_gap_ledger.py --staged`、`check_state.py`）均退出 0。
- **关联 ADR**：无（缺口登记与状态更新；G-005–G-007 的裁定若改变已有 `check_id` 判定，届时另立 ADR）
- **状态**：生效

---

### 批次 0032 — 2026-11-14 — ADR-0013 草案：单次裁定收口“判定列语义与表达能力补全”

- **涉及文件**：新增 `adr/0013-unified-adjudication-of-check-semantics.md`；修改 `ROADMAP.md`（M2 出口 5）、`GAP_LEDGER.md`（核查记录）、`STATE.md`（例外表）、`AGENTS.md`（目录树）、`CHANGELOG.md`（本批次）
- **变更摘要**：
  1. **起草 ADR-0013（`draft`）**：把 G-001、G-002、G-003、G-005、G-006、G-007 并为**一次裁定**的范围，逐点列出 D0–D9 待决项（子句级覆盖、端点量词、空对象语义、悬空引用原因码、多违规 `reason` 优先级、`about` 反向引用、G-C1 断言内容、G-D1 `target` 类型、G-001 未定义判定对象、G-002/G-003 是否纳入判定列），每点给候选与影响面，不预设结论。
  2. **裁定门**：T-133 全部 17 个 `check_id` 复核完成方可定稿；复核新增条目按“成因相同 + 处置路径相同 + 指向语义/表达补全”三项判据决定是否并入。G-004 明确不并入（`severity-mismatch`，按 T-100 单独裁定）。
  3. **设计层风险单列**：给出四项判断——两表结构天然漂移（缺子句级覆盖声明，现有台账只做事后探测）；输入 schema 表达力不足（量词/空值/关系路径缺失，G-007 是表达缺陷而非文档不清）；检查项粒度过粗与过细并存（切分单位应是“可判定的规则子句”）；整体可收敛，但收敛判据应改为“同源缺口零新增”。
  4. **复核期间冻结清单**：`GRAMMAR.md`、方法声明与附录 A 判定列/样例、`CHECKER_INPUT_SCHEMA.md`、原型 `checker.py`、只读验收包、`validation/test-cases/` 既有用例；本轮只改台账、调度文档、ADR 与 `STATE.md`。
  5. **状态登记**：`STATE.md` 增例外行，把该 ADR 记为 `skeleton`（文件内状态 `draft`），避免 `adr/` 目录默认值 `accepted` 误标为已接受。
- **钩子绕过**：无。
- **验证**：五个检查器均退出 0；`check_gap_ledger.py` 仍为 7 条 `open`、L1 4 / L2 2 / L3 1、到期 0、矩阵 10/17 `consistent`；原型仍 34/34（本轮未触碰冻结文件）。
- **关联 ADR**：ADR-0013（本批次创建，状态 `draft`）
- **状态**：生效（ADR 草案登记；裁定未生效，判定列与样例未改）

---

### 批次 0033 — 2026-11-14 — ADR-0013 最终裁定：判定层表示规范收口、三表机械对照与术语治理

- **涉及文件**：`adr/0013-unified-adjudication-of-check-semantics.md`（`draft` → `accepted`）、`spec/CHECKER_INPUT_SCHEMA.md`（整篇重写）、`spec/methods/deterministic-checker.md`（A 表子句列、A.2 子句表、§4.2/§4.4、样例）、`validation/checker-prototype/checker.py`、新增 `scripts/check_three_table.py`、新增 `scripts/check_glossary_usage.py`、新增 `knowledge/glossary-usage.json`、`GLOSSARY.md`（新增第 4 节生成块）、`GAP_LEDGER.md`、`TODO.md`、`ROADMAP.md`、`AGENTS.md`、`STATE.md`、`.githooks/pre-commit`、`scripts/README.md`、`scripts/check_state.py`、`scripts/check_gap_ledger.py`、`CHANGELOG.md`（本批次）
- **变更摘要**：
  1. **ADR-0013 一次性裁定**：范围从“补判定列语义”扩为“判定层表示规范”，D0–D9 与独立复核报出的八条上层设计问题（P1–P8）在同一次裁定中出结论，不分批改冻结文件、不重复跑复核。
  2. **八条问题的处置**：P1 子句被压缩 → A 表新增“子句”列 + A.2 子句表（39 条）；P2 未封闭枚举与自然语言值 → schema 第 4 节具名枚举；P3 跨对象全称/相关性 → schema §1.6–1.7 与 §3bis 关系路径；P4 引用完整性全局统一 → schema §1.5（悬空 `fail` / 类型未定义 `cannot_evaluate`）；P5 assumption 时效与批准资格 → schema §1.9 `assumption` 对象；P6 链/路径/可达性 → schema §1.10；P7 适用性状态机与 `not_applicable` → 方法 §4.4 + schema 第 4 节；P8 三表无机械对照 → `scripts/check_three_table.py`。
  3. **三表机械对照作为交付物**：检查器覆盖“正文 ↔ 判定列”“判定列 ↔ schema”“正文 ↔ schema”三对关系，并核对子句闭合与枚举封闭；pre-commit 与 `check_state.py` 双重调用，退出 1 即阻断提交与发布。不接受“后续人工对照”。
  4. **判定列与 schema 同步**：A.2 子句表给出子句级 severity（`G-E1#3` 为 `warn`，关闭 G-004）；样例 A.1.1 / A.1.3–A.1.5 / A.1.10 按新表示补齐 `about`、`statement_kind`、`target`、`kind`、`verification_condition`；原型实现相应子句并在 `COVERAGE_GAPS` 为空时输出“无（ADR-0013 已消解全部 5 项）”。
  5. **缺口关闭**：G-001–G-007 全部以 `check-change` 关闭；八条设计问题合并登记为 G-008（`undefined-object`，L2，M1）并关闭。核查矩阵 17/17 `consistent`，到期 0。`check_gap_ledger.py` 的锚定规则修正为“只有 `open` 缺口必须被矩阵引用”——`closed` 缺口已记录处置出口，继续强制锚定会让矩阵永远无法达到撤除条件。
  6. **M2 重定位为“表示层收口”**：17 项复核结论作为输入；出口改为三表对照通过、子句覆盖 100%、表示规范有载体、原型重跑通过、同源缺口零新增；“补齐 17 项”与“独立复核完成”从出口移除，T-133 的非同源重跑保留为验证输入而非关闭门。
  7. **术语纳入治理**：`AGENTS.md` 新增 5bis.1，要求每次提交前扫描本次改动并判断术语新增/修改/废弃（新概念必须登记、改义必须同步、废弃标注而不删）。`check_glossary_usage.py` 以“生成 + 冻结基线 + 变更时校验”实现：扫描 `git ls-files` 的 Markdown / JSONL，匹配行内代码、`GLOSSARY.md#term_id` 与裸 `term_id`（裸术语正文不匹配），生成 `knowledge/glossary-usage.json` 与 `GLOSSARY.md` 第 4 节位置表；陈旧位置、行号越界、生成块手改、术语集合漂移均退出 1。与缺口台账分工明确：台账管“正文 ↔ 判定列”的语义裁定，本检查器管“术语条目 ↔ 仓库引用”的引用完整性。
  8. **发布阻断接入**：pre-commit 由五个检查器扩为七个，`check_state.py` 调用三表对照与术语使用位置核查。
- **钩子绕过**：无。
- **验证**：
  - `python3 validation/checker-prototype/checker.py`：34/34 样例通过（100.0%），17/17 个 `check_id` 全通过，`COVERAGE_GAPS` 为空。
  - `python3 scripts/check_three_table.py`：正文 17 条规则、判定列 17 个 `check_id` / 39 个子句、schema 17 个输入域；退出 0。
  - `python3 scripts/check_gap_ledger.py`：8 条（open 0 / closed 8）；L1 4 / L2 3 / L3 1；到期 0；矩阵 17/17 `consistent`；退出 0。
  - `python3 scripts/check_glossary_usage.py`：82 条术语、800 余个使用位置、39 个零使用警告；退出 0。负例（基线行号改为越界值、手改生成块、删除位置）均退出 1，恢复后退出 0。
  - 七个检查器均退出 0（`check_state.py` 在开发态只对“HEAD 领先 tag”告警）。
  - **复核状态**：本批次只做同源重验（原型 + 三表检查器）；独立复核会话对改动后判定列/schema 的单次非同源重跑仍待执行，结论另记，不冒充已完成。
- **关联 ADR**：ADR-0013（`accepted`）
- **状态**：生效

---

### 批次 0034 — 2026-11-14 — 复核推翻后的账务修正、原型/schema/判定列修订与样例追溯性降级

- **涉及文件**：`GAP_LEDGER.md`、`AGENTS.md`、`adr/0013-unified-adjudication-of-check-semantics.md`、`STATE.md`、`spec/CHECKER_INPUT_SCHEMA.md`、`spec/methods/deterministic-checker.md`、`validation/checker-prototype/checker.py`、`scripts/check_gap_ledger.py`、`scripts/check_three_table.py`、`scripts/README.md`、`ROADMAP.md`、`TODO.md`、`knowledge/glossary-usage.json`、`GLOSSARY.md`（生成块）、`CHANGELOG.md`（本批次）
- **变更摘要**：
  1. **账务回滚**：G-001–G-008 全部由 `closed` 回到 `open`，核查矩阵由 17/17 `consistent` 降为 0/17，逐行改指缺口编号；新增 G-009–G-017 九条（null 崩溃、引用完整性未全局、`assumption.pending` 缺批准者、路径缺 `target_id` 与扁平双轨、`subject_group` 17 项未物化、聚合优先级矛盾、A 表叙述性短语、A.2 缺原因码列、三表检查器只查结构）。当前 open 17 / closed 0，L1 9 / L2 7 / L3 1，到期 0。
  2. **关闭判据**：`GAP_LEDGER.md` 新增“关闭判据（硬要求）”，`AGENTS.md` 新增 3.6.6。缺口不得以同源结果（自家原型通过、自家脚本退出 0、同批改样例后自证）关闭；`closed` 必须写“关闭依据”列，且只能取 `非同源复核：<复核者>，<日期>` 或 `人工签收：<签收人>，<日期>`。`check_gap_ledger.py` 校验依据缺失、前缀非法、说明/依据含同源自证措辞；`open` 填依据同样报错。
  3. **原型**：17 个 check 函数的必需键守卫统一为 `require_fields()`，键缺失或值为 `null` 均返回 `cannot_evaluate/missing_input`；新增 `validate_references()`，在 check 返回 `pass` 时统一校验全局引用（含 `commitments.by/to`、`constraints.constrains`、`changes.target`、`charters.*`、`contracts.constrained_by/accountable_signature`、`tailoring_records.approver`、`assertions.about/deliverable/subject/accountable_confirmation`）；该调用在 pass 分支之后，只能把本应 pass 的结果改为 fail/cannot_evaluate，不推翻既有 fail。`assumption.pending` 分支补 `approved_by` 检查。`delegated_from` 改为路径对象，扁平字符串返回 `invalid_path`。
  4. **schema**：§1.10 路径补 `steps[].target_id` 并删除扁平字符串写法；`subject_group` 17 项（ISO 21502:2020 7.2–7.18）完整物化；§1.14 与 A.2 统一为 `fail > cannot_evaluate > pass`；§3 补 `assumption_unclosed` / `invalid_path` 等原因码。
  5. **判定列格式**：A 表改为 `check_id | 规则 | 判定（子句 id） | 输入 | 原因码 | 规则状态`，判定列只留子句 id，叙述下沉 A.2；A.2 增加原因码列（40 条子句），新增 `G-D2#3`（pending 须 `approved_by`）；A 表原因码集合与子句原因码集合机械一致；G-B1 不再写枚举条件。
  6. **样例追溯性修正**：A.1.11-2、A.1.12-2、A.1.13-2、A.1.15-2 四个样例自 T-107 起一直带悬空引用（章程指向未提供的 Outcome/Constraint/Actor/Assertion；验收确认与契约签署指向未提供的 Actor；契约约束指向未提供的 Constraint；裁剪批准者指向未提供的 Actor）。**只改输入块，4 个样例的期望输出均未变**；依据 schema §1.5（所有引用必须解析到同一快照）。此前的多次“34/34 通过”包含这 4 条未被发现的无效验证，是对既有绿色数字的追溯性降级，不是新缺陷；已记入台账核查记录。`validate_references()` 只在 pass 分支调用、不能推翻既有 fail 是刻意取舍：已有 fail 的样例保留其特定原因码，避免全局校验淹没规则语义。
  7. **三表检查器深度**：新增判定列叙述性短语检测、G-B1/G-B2 条件归属、原因码定义与 A 表/子句映射一致性检查。文档明确其边界：只保证结构与已列举的语义短语规则，不保证规则正文与子句表的全文语义等价；绿字不等于语义闭合。
  8. **ADR 与计划**：ADR-0013 由 `accepted` 回到 `proposed`（修订中），新增第 8 节记录首轮裁定失效原因与修订范围；`STATE.md` 加回 `skeleton` 例外。M2 出口改为“结构/枚举/子句/原因码机械一致 + 原型重跑 + 非同源复核关闭缺口”，同源结果明确不构成出口。T-100、T-130、T-131、T-134–T-136 由 `done` 回到 `in-progress`，T-133 描述更新。
- **钩子绕过**：无。
- **验证**：
  - `python3 validation/checker-prototype/checker.py`：34/34 样例通过，17/17 `check_id` 通过。
  - `python3 validation/checker-prototype/checker.py --null-sweep`：31/31 键级用例返回 `cannot_evaluate`，崩溃 0（覆盖 17 个 check 函数）。
  - 全局引用负例：G-F1 章程 `outcomes` 指向 `O-999` → `fail/dangling_reference`；改回 `O-1` → `pass`。路径负例：合法路径对象 → `pass`；扁平字符串 → `cannot_evaluate/invalid_path`；`target_id` 悬空 → `fail/dangling_reference`。`assumption.pending` 无批准者 → `cannot_evaluate/assumption_unclosed`，补 `approved_by` → `pass`。
  - `python3 scripts/check_three_table.py`：正文 17 条规则、判定列 17 个 `check_id` / 40 个子句、schema 17 个输入域；退出 0。负例：G-B1 子句写“值在枚举内”、A 表判定列写叙述性短语、原因码改为未定义值，三种均退出 1。
  - `python3 scripts/check_gap_ledger.py`：17 条（open 17 / closed 0），到期 0，矩阵 0/17；退出 0。负例：G-009 以“非同源复核：复核会话R，2026-11-14”关闭 → 退出 0；以“自家原型通过，退出 0”关闭 → 退出 1；`closed` 但关闭依据为空 → 退出 1。
  - 七个检查器均退出 0（`check_state.py` 在开发态只对“HEAD 领先 tag”告警）。
  - **复核状态**：本批次未执行非同源复核；G-001–G-017 全部保持 `open`，不以本轮同源结果关闭。待复核会话对修订后版本单次重跑，结论记入 `GAP_LEDGER.md` 后再行关闭。
- **关联 ADR**：ADR-0013（`proposed`，修订中）
- **状态**：生效（修订中；缺口未关闭）

---

### 批次 0035 — 2026-11-14 — 四层修订（第一、二层）：入口 null 归一化与引用字段由 schema 生成

- **涉及文件**：`validation/checker-prototype/checker.py`、`spec/CHECKER_INPUT_SCHEMA.md`、`spec/methods/deterministic-checker.md`（A.1.9/A.1.11–A.1.17 输入块）、`scripts/check_three_table.py`、`adr/0013-unified-adjudication-of-check-semantics.md`（§8.4）、`GAP_LEDGER.md`（核查记录）、`knowledge/glossary-usage.json`、`GLOSSARY.md`（生成块）、`CHANGELOG.md`（本批次）
- **变更摘要**：
  1. **第一层：入口统一 null 归一化**。新增 `find_null()`，在 `evaluate()`（`run_case` 的唯一入口）中一次覆盖**顶层键、嵌套对象键、数组元素**三种 `null`；命中即返回 `cannot_evaluate` / `missing_input`，17 个 `check` 函数不再各自兜底。D1 的 `commitments: null` 不再落入 `fail/invalid_change_target`。样例中 4 处语义性 `null`（A.1.9-1 `assumption/verification_condition`、A.1.13-1 `contract`、A.1.15-1 `record`、A.1.17-1 `reassessment_condition`）改为“缺键”或 `{}`，期望输出未变。
  2. **第一层负例**：`--null-sweep` 重写为路径级扫描。顶层必需键 43/43、数组元素 89/89（覆盖 54 条 `(check_id, 路径)` / 27 条唯一路径）、嵌套对象键 6/6，合计 138/138 返回 `cannot_evaluate`，崩溃 0。单点负例：D1 `commitments: null`、D1 `deliverables: [null]`、C1 `assertions: [{...}, null]`、D1 `target: null` 均返回 `cannot_evaluate/missing_input`。
  3. **第二层：引用字段清单由 schema 生成**。schema 新增 §2bis：2bis.1 用 34 行标注引用字段（源路径 / 字段 / 目标集合 / 形态，含 `type` 判别与 `any`），2bis.2 显式登记 40 个非引用字段。原型启动时解析 §2bis.1 生成 `REFERENCE_RULES`，删除手写 `checks` 列表；解析 §3 生成 `REQUIRED_KEYS`。补齐 `contracts[].accountable_signature` 与 `changes[].assumption.approved_by`（并新增 `assertions[].assumption.approved_by`）。
  4. **第二层负例**：F3 的 `accountable_signature: "A-404"` → `fail/dangling_reference`，改回 `A-1` → `pass`；D2 的 `assumption.approved_by: "A-404"` → `fail/dangling_reference`。临时在 §2 `contracts[]` 行加入 `counterparty_id` 且不在 §2bis 标注时，`check_three_table.py` 输出“字段 `counterparty_id` 在第 2 节声明，但 §2bis 既未标注为引用也未登记为非引用”并退出 1；移除后退出 0。
  5. **§3 输入域同步**：`ASSERTION_MUTUAL_EXCLUSION` +`deliverables`，`ALL_IMPROVEMENT_ASSUMPTION` +`actors`，`PROJECT_CHARTER_EXISTENCE` +`outcomes/constraints/actors/assertions`，`CLOSURE_ACCEPTANCE_LINK` +`actors`，`PROCUREMENT_CONTRACT_ANCHOR` +`constraints/actors`，`TAILORING_RECORD_EXISTENCE` +`actors`。新增 `--input-domain`：样例中实际出现的引用目标集合必须已在 §3 声明，实测 0 处缺口；样例顶层键无 §3 之外的额外集合。
  6. **检查器**：`check_three_table.py` 新增第 6 项（§2 字段必须被 §2bis.1 或 §2bis.2 覆盖）与第 7 项（输入域闭包）。
- **钩子绕过**：无。
- **验证**：
  - `python3 validation/checker-prototype/checker.py`：34/34 样例通过，17/17 `check_id` 通过。
  - `python3 validation/checker-prototype/checker.py --null-sweep`：138/138，崩溃 0（顶层 43、数组元素 89、嵌套对象 6）。
  - `python3 validation/checker-prototype/checker.py --input-domain`：0 处缺口。
  - `python3 scripts/check_three_table.py`：正文 17 条规则、判定列 17 个 `check_id` / 40 个子句、schema 17 个输入域、引用字段 27 个 / 非引用字段 40 个；退出 0。负例（`counterparty_id` 未标注）退出 1。
  - 七个检查器均退出 0（`check_state.py` 在开发态只对“HEAD 领先 tag”告警）。
  - **复核状态**：G-001–G-017 仍为 `open`（17/17），本轮同源结果不构成关闭依据；第三、四层待执行，全部完成后只重跑一次非同源复核。
- **关联 ADR**：ADR-0013（`proposed`，§8.4）
- **状态**：生效（修订中；缺口未关闭）

---

### 批次 0036 — 2026-11-14 — 四层修订（第三层）：A 表由 A.2 派生与固定变异集

- **涉及文件**：`spec/methods/deterministic-checker.md`（A 表 7 列、A.2 第 8 列、A.1 样例基线）、`scripts/check_three_table.py`（派生与逐格比较、`--write`、`--method`）、`scripts/test_check_table_mutations.py`（新增）、`adr/0013-unified-adjudication-of-check-semantics.md`（§8.4）、`GAP_LEDGER.md`（核查记录）、`CHANGELOG.md`（本批次）
- **变更摘要**：
  1. **A 表唯一生成路径**：A 表不再手工维护，`scripts/check_three_table.py --write` 由 A.2 重建；A 表列固定为 `check_id | 规则 | 判定（子句 id） | 子句指纹 | 输入 | 原因码 | 规则状态`。默认模式逐格比较“文件 A 表”与“A.2 生成结果”，不再做两表字段互比。
  2. **子句指纹**：`sha256(clause id | 规则 | 子句文本 | 原因码 | 承接 check_id | severity | 规则状态)[:12]`，再按 `check_id` 聚合。任一项语义改动都会改变指纹并使检查失败；`canonical()` 只忽略空白差异。
  3. **A.2 第 8 列**：40 条子句补 `规则状态`（F/G 组为 `assumption`，其余 `active`），与方法 §4.5、A 表规则状态列同源。
  4. **样例基线**：A.1 区新增“样例基线（跨轮横比锚点）”，锚定提交 `1a42b8b`（批次 0034）、34 个样例，并逐条登记 A.1.9-1、A.1.9-2、A.1.11-1、A.1.12-1、A.1.13-1、A.1.15-1、A.1.17-1 的输入块改动与原因；**期望输出零改动**。此后“34/34”一律相对该基线比较。
  5. **固定变异集**：新增 `scripts/test_check_table_mutations.py`，变异副本写入临时目录，不改工作区；基线必须退出 0，逐条变异必须退出 1 且命中预期证据，否则脚本退出 1。变异集固定为 11 条，可重复执行。
- **变异测试全表**：

| 编号 | 类别 | 变异内容 | 抓到 | 退出码 | 证据 |
|---|---|---|---|---|---|
| M01 | 子句语义 | G-C1#1 改成“必须有 Actor 负责人” | 是 | 1 | `DELIVERABLE_ASSERTION_LINK` 子句指纹不一致（`32a91e4431f9` → `6f4b58fcac7a`） |
| M02 | 量词 | G-A1#1 的“至少一个”改为“恰好一个” | 是 | 1 | `PROJECT_MINIMAL_EXISTENCE` 子句指纹不一致（`6a4f8c0ad633` → `ad8e6f971ba0`） |
| M03 | 原因码删除 | G-E1#1 删除 `multiple_accountable` | 是 | 1 | `ROLE_MINIMAL_COMPLETENESS` 子句指纹不一致（`a707061b238f` → `9a2223634395`） |
| M04 | 枚举归属 | 把枚举条件写进 G-B1#2 | 是 | 1 | 子句 `G-B1#2` 写了枚举条件；枚举归属 G-B2 |
| M05 | 枚举归属 | 从 G-B2#1 删除枚举条件 | 是 | 1 | `G-B2#1` 未写枚举条件；值闭合必须由 B2 承接 |
| M06 | 承接规则 | G-C1#1 的承接 `check_id` 改指向 `CHANGE_CONSTRAINT_LINK` | 是 | 1 | `CHANGE_CONSTRAINT_LINK` 规则列不一致（文件 `G-D1`，生成 `G-C1、G-D1`） |
| M07 | 子句 id | G-C1#1 改为 G-D1#4（指向别的规则） | 是 | 1 | `DELIVERABLE_ASSERTION_LINK` 子句 id 列不一致（`G-C1#1` → `G-D1#4`） |
| M08 | severity | G-E1#3 的 severity 由 `warn` 改为 `block` | 是 | 1 | `ROLE_MINIMAL_COMPLETENESS` 子句指纹不一致（`a707061b238f` → `652398553027`） |
| M09 | 规则状态 | G-B1#2 的规则状态由 `active` 改为 `assumption` | 是 | 1 | `DUAL_DIMENSION_ANNOTATION` 子句指纹不一致（`2cde52fd3961` → `6650cf0c3301`） |
| M10 | 子句删除 | 删除 G-E1#3 整行 | 是 | 1 | `ROLE_MINIMAL_COMPLETENESS` 子句 id 列不一致（文件含 `G-E1#3`，生成不含） |
| M11 | 原因码篡改 | G-D1#3 改为未定义的 `invalid_relation` | 是 | 1 | `CHANGE_CONSTRAINT_LINK` 子句指纹不一致（`3e473f8ea1e8` → `9dfa4c069d15`） |

- **边界说明**：变异集只改 A.2、不改 A 表，检测机制是“A.2 派生结果 ≠ 提交的 A 表”。若改动 A.2 后执行 `--write` 重建 A 表，检查器无法区分“合法规格修订”与“绕过”，这只能由提交差异与评审承担；该结构性边界已在脚本与本节写明，不属于检查器可检测范围。
- **钩子绕过**：无。
- **验证**：
  - `python3 scripts/check_three_table.py`：17 条规则 / 17 个 `check_id` / 40 个子句 / 17 个输入域；退出 0。
  - `python3 scripts/test_check_table_mutations.py`：11 条变异，抓到 11 条，未抓到 0 条；退出 0。
  - `python3 validation/checker-prototype/checker.py`：34/34，17/17 `check_id`；退出 0。
  - `--null-sweep`：138/138，崩溃 0；`--input-domain`：0 缺口。
  - **复核状态**：G-001–G-017 仍为 `open`（17/17），本轮同源结果不构成关闭依据；第四层完成后只重跑一次非同源复核。
- **关联 ADR**：ADR-0013（`proposed`，§8.4）
- **状态**：生效（修订中；缺口未关闭）

---

### 批次 0037 — 2026-11-14 — 四层修订（第四层）：扩展关系、悬空原因、violations 撤除、G-A2#2 可达

- **涉及文件**：`spec/CHECKER_INPUT_SCHEMA.md`（§1.5、§1.14、§2、§2bis.2、§3、§4）、`spec/methods/deterministic-checker.md`（A.2 的 `G-B2#2`、`G-C1#1`、`G-E2#3`、原因码映射、悬空引用原因归属表、G-A2#2 可达性）、`validation/checker-prototype/checker.py`（`EXTENSION_RELATIONS`、`check_dimension_value`）、`adr/0013-unified-adjudication-of-check-semantics.md`（§8.4）、`GAP_LEDGER.md`（核查记录）、`CHANGELOG.md`（本批次）
- **变更摘要**：
  1. **`subject_group_extension` 扩展关系**：schema §2 定义 `value` / `relation` / `base` 三字段，§4 新增 `subject_group_extension_relation = {specializes, cross_cuts}`；`base` 必须是 17 项基础 `subject_group` 之一，`value` 不得与基础枚举重名。A.2 新增 `G-B2#2`（`invalid_subject_group_extension`），`G-B2#1` 只承接“标签值在基础枚举或**合法**扩展内”。原型按行序判定：先值闭合、后扩展声明。只写 `{value}` 不再通过。
  2. **悬空引用原因统一为“规则子句原因优先”**：A.2 的“悬空引用原因归属”表固定每个 `check_id` 在悬空时返回的原因码；只有子句原因码列显式列出 `dangling_reference` 才返回该码（`G-C1#1`、`G-E2#1`、`G-E2#3`）。其余子句返回自己的原因码；无子句承接的引用由 `validate_references()` 在全部子句 `pass` 后兜底。schema §1.5 同步该定性。
  3. **`violations[]` 选择撤除**：schema §1.14 明确“原型不输出 `violations[]`；`reason` 为按 A.2 行序首条命中原因码”；实现不新增该字段，`run_case` 输出键实测为 `check_id / source_rule / severity / rule_status / verdict / reason`。
  4. **`G-A2#2` 在声明输入域内可达**：schema §2 的 `commitments[]` / `deliverables[]` 增加可选 `node_type`，§3 的 `CONSTRAINT_ANCHOR_REQUIRED` 判定所需字段注明“提供时须 ∈ `management_node_type`”。未提供视为未断言类型，不触发本子句；提供非法值 → `cannot_evaluate` / `undefined_object_type`。
- **负例实测**：
  - `subject_group_extension: [{value: "custom"}]` 且标签引用 `custom` → `fail` / `dimension_value_out_of_enum`；只写 `{value: "custom"}` 但未被引用 → `fail` / `invalid_subject_group_extension`；`value` 与基础枚举重名 → `fail` / `invalid_subject_group_extension`；合法 `{value: "custom", relation: "specializes", base: "planning"}` → `pass`。
  - 悬空引用：`A2` → `unanchored_management_item`；`C1` → `dangling_reference`；`D1` → `invalid_change_target`；`E1` → `unknown_accountable`；`E2#1` / `E2#3` → `dangling_reference`。与 A.2 归属表逐行一致。
  - `run_case` 输出不含 `violations[]`。
  - `G-A2#2`：`node_type: "Unknown"` → `cannot_evaluate` / `undefined_object_type`；`node_type: "ManagementActivity"` + 完整 A.1.2-2 输入 → `pass`。
- **验证**：
  - `python3 validation/checker-prototype/checker.py`：34/34，17/17 `check_id`；退出 0。
  - `--null-sweep`：138/138，崩溃 0；`--input-domain`：0 缺口。
  - `python3 scripts/check_three_table.py`：17 条规则 / 17 个 `check_id` / 41 个子句 / 17 个输入域；退出 0。
  - `python3 scripts/test_check_table_mutations.py`：11/11 抓到；退出 0。
  - 七个检查器全部退出 0（`check_no_raw_material` 曾因 A.1 基线引用块 803 字符超 800 阈值失败，已把基线移出引用块后复跑通过；`check_glossary_usage --write` 已重建基线）。
  - **复核状态**：G-001–G-017 仍为 `open`（17/17）。四层修订完成，只重跑一次非同源复核；在同源结果下不关闭任何缺口。
- **关联 ADR**：ADR-0013（`proposed`，§8.4）
- **状态**：生效（修订中；缺口未关闭）

---

### 批次 0038 — 2026-11-14 — 补漏：A.2 改动的非同源签收纪律

- **性质**：这是对批次 0036“A 表由 A.2 派生”的**补漏**，不是新决定。派生检查只能保证“A 表与 A.2 一致”；改 A.2 再跑 `--write` 会使两者自洽，无法区分合法规格修订与绕过。签收纪律补上这一缺口。
- **涉及文件**：`AGENTS.md`（新增 3.6.7）、`adr/0013-unified-adjudication-of-check-semantics.md`（决策表新增 `A2-SIGNOFF`，P1 子句数 40→41，P8 检查深度补签收同步）、`spec/methods/deterministic-checker.md`（A.2 区头新增复核签收行）、`scripts/check_three_table.py`（规则 8）、`scripts/test_check_table_mutations.py`（S01/S02）、`CHANGELOG.md`（本批次）
- **签收格式**：`复核签收：<复核者/会话> / <YYYY-MM-DD> / A.2 指纹 `<12位>``。指纹 = 全部子句指纹按 clause id 排序后的 sha256 前 12 位。
- **机械阻断**：`scripts/check_three_table.py` 规则 8 比对签收行指纹与当前 A.2 指纹；不一致即退出 1。`--write` 只重建 A 表，**不更新签收行**，因此“改 A.2 + --write”仍会被拦。
- **正负例（`scripts/test_check_table_mutations.py`）**：

| 编号 | 场景 | 预期 | 实际 | 退出码 | 证据 |
|---|---|---|---|---|---|
| S01 | 只改 A.2 + `--write`，不更新签收 | 阻断 | 阻断 | 1 | `A.2 已改动但复核签收未同步：签收行 … a7e02bdfd23f，当前 A.2 指纹 08979d4851b5` |
| S02 | 改 A.2 并更新签收与指纹 | 通过 | 通过 | 0 | `[通过] 正文、判定列、schema 三表一致…A.2 签收与指纹同步…` |

- **基线例外**：本次提交的签收行标注“纪律基线（同源修订；非同源复核待提交后执行）”，仅此一次；此后 A.2 改动必须由非同源复核更新签收行。
- **边界**：检查器只验证签收记录与 A.2 同步，不能验证签收人是否真的非同源；后者由提交评审与 AGENTS 3.6.6 共同约束。
- **验证**：变异集 11/11 抓到；签收正负例 2/2 符合预期；34/34、null-sweep 138/138、input-domain 0 缺口；七个检查器退出 0。
- **复核状态**：G-001–G-017 仍为 `open`（17/17），等非同源复核结论。
- **关联 ADR**：ADR-0013（`proposed`，§2.2、§8.4）
- **状态**：生效（纪律补漏；缺口未关闭）

---

### 批次 0039 — 2026-11-14 — 第一段：缺键归一化与顺序无关聚合

- **性质**：纯缺陷修复，不涉及设计变更。对应 G-009（缺键/`null` 路径）与 G-014（聚合顺序）。17 条缺口仍为 `open`，本批次不关闭任何缺口。
- **涉及文件**：`validation/checker-prototype/checker.py`（入口归一化、17 个 check 改为子句级结果列表、`aggregate()`、`--missing-key-sweep`、`--aggregation-order`）、`GAP_LEDGER.md`（G-009/G-014 描述更新，状态仍 `open`）、`CHANGELOG.md`（本批次）
- **变更摘要**：
  1. **缺键路径**：`evaluate()` 在进入 check 前先比对 schema §3 生成的 `REQUIRED_KEYS`，键不存在与值为 `null` 走同一出口 `cannot_evaluate` / `missing_input`。check 函数内不再承担缺键守卫；`{}` 直入 check 仍 17/17 抛 `KeyError`，证明拦截在入口。
  2. **聚合顺序**：17 个 check 统一返回子句级结果列表，由 `aggregate()` 聚合：verdict 取 `fail > cannot_evaluate > pass` 最高级；reason 只在胜出 verdict 内按 A.2 行序取首条；severity 取胜出子句最高级（缺省用 check 默认）。函数内不得提前 `return` 首个失败；`check_ai_autonomy` 的路径子句与断言子句分别收集，`invalid_path` 不再掩盖断言 `fail`。
- **负例实测**：
  - `--missing-key-sweep`：43 个必需键逐一单删，43/43 返回 `cannot_evaluate/missing_input`，偏离 0。
  - 对照：`{}` 直入 17 个 check 函数仍 17/17 抛 `KeyError`，说明修复位于入口归一化而非函数内守卫。
  - `--aggregation-order`：A2（3 项：fail/`cannot_evaluate`/fail）6 种排列 → 1 种结论 `fail/unanchored_management_item`；E2（3 个 grant：`invalid_path`/断言不完整/链未达 `Accountable`）6 种排列 → 1 种结论 `fail/delegation_chain_not_accountable`。
  - `--null-sweep`：138/138，崩溃 0；`--input-domain`：0 缺口。
- **验证**：
  - `python3 validation/checker-prototype/checker.py`：34/34，17/17 `check_id`；退出 0。
  - `python3 scripts/check_three_table.py`：退出 0；`python3 scripts/test_check_table_mutations.py`：11/11 抓到，签收正负例 2/2，退出 0。
  - 七个检查器全部退出 0。
  - **复核状态**：G-001–G-017 仍为 `open`（17/17）。G-009 与 G-014 待非同源复核关闭，其余 15 条不动。
- **关联 ADR**：ADR-0013（`proposed`，§2.1 P7、§2.3 D4）
- **状态**：生效（缺陷修复；缺口未关闭）

---

### 批次 0040 — 2026-11-14 — 第二段：覆盖闸门

- **性质**：新增机械闸门，不关闭缺口；17 条缺口仍为 `open`。
- **涉及文件**：`spec/methods/deterministic-checker.md`（A.1 新增 23 个负例，34 → 57；样例基线注记）、`validation/checker-prototype/coverage.json`（新增覆盖矩阵）、`scripts/check_coverage_gate.py`（新增）、`scripts/test_coverage_gate.py`（新增）、`validation/checker-prototype/checker.py`（样例解析支持多例；severity 按 A.2 子句取值）、`.githooks/pre-commit`（第七 → 第八个检查器）、`GLOSSARY.md`、`knowledge/glossary-usage.json`（位置重建）、`CHANGELOG.md`（本批次）
- **覆盖矩阵**：A.2 的 41 个子句逐条登记 `check_id + positive[] + negative[]`；正例必须存在、`check_id` 一致且期望 `verdict=pass`；负例必须存在、`check_id` 一致、期望 `verdict≠pass` 且 `reason` 属于该子句原因码；未被任何子句引用的样例同样阻断。
- **样例补齐**：新增 23 个负例，覆盖此前无专属负例的子句（G-A1#1/#2/#3/#5/#6、G-A2#2、G-C1#2/#3、G-D1#1/#2、G-E1#2/#3、G-B1#1、G-B2#2、G-D2#2/#3、G-E2#2/#3、G-F1#2、G-F2#2、G-F3#2、G-G1#2、G-G3#2）。既有 34 例输入与期望输出零改动。
- **负例实测**：
  - `check_coverage_gate.py`：子句 41、矩阵 41、正例 41、负例 41、样例 57、问题 0。
  - N01 删除 `G-F4#1` 唯一负例登记 → 退出 1，`[错误] G-F4#1：缺少负例`。
  - N02 把 `A.1.14-1` 期望 `verdict` 改成 `pass` → 退出 1，`负例被改成正例`。
  - N03 删除 `A.1.14-1` 样例块 → 退出 1，位置重编号后原正例落入负例位置，同样被识别为“负例被改成正例”。
- **回归**：原型 57/57、17/17；null-sweep 138/138；missing-key-sweep 43/43；aggregation-order 6×2 各 1 种结论；三表检查器 17/17/41/17；变异 11/11；A.2 签收正负例 2/2；八个检查器全部退出 0。
- **样例基线**：批次 0034 的 `1a42b8b`（34 例）→ 本批次 57 例；新提交号在批次 0041 补记。
- **状态**：生效（闸门上线；缺口未关闭）

---

### 批次 0041 — 2026-11-14 — 第三段：验证权绑定（检查器 / 规格 / 快照）

- **性质**：新增四道绑定与一份 ADR，把“静默改检查器或规格”变成“显式改且留痕”。不改变判定语义，不关闭缺口；17 条缺口仍为 `open`。
- **涉及文件**：`scripts/check_checker_pins.py`、`scripts/checker-pins.json`、`scripts/test_checker_pins.py`、`scripts/check_spec_pins.py`、`scripts/spec-pins.json`、`scripts/test_spec_pins.py`、`validation/pinned/checker.py`（新增）；`adr/0014-validation-chain-self-attestation.md`（新增）；`.githooks/pre-commit`、`AGENTS.md`（3.6.8、十个检查器、目录树）、`ROADMAP.md`（M2 出口 4/6/7）、`scripts/README.md`、`GLOSSARY.md`、`knowledge/glossary-usage.json`、`GAP_LEDGER.md`（核查记录）、`CHANGELOG.md`（本批次）
- **变更摘要**：
  1. **检查器绑定**：`scripts/checker-pins.json` 登记 `scripts/` 下 14 个检查器脚本的 sha256 与 `basis`；`check_checker_pins.py` 在 pre-commit 比对工作区哈希，不一致退出 1。改动检查器必须 `--write --basis "<裁定依据>"`；无 `basis` 的 `--write` 退出 2。
  2. **规格区段绑定**：`scripts/spec-pins.json` 分别登记 `GRAMMAR.md` 全文、方法 A.2、`spec/CHECKER_INPUT_SCHEMA.md` §2bis/§3/§4 共 5 个区段指纹。区段相对 `HEAD` 变化时，同一提交必须附含 `非同源复核：`、`区段：<key>`、`复核产物：<文件名>` 与结论词（实质收敛/认可/通过）的复核记录，否则退出 1。`--write` 只重建指纹，不生成复核记录。
  3. **验收检查器与工作区副本**：`validation/pinned/checker.py` 为只读快照，`check_checker_pins.py` 校验它与 `validation/checker-prototype/checker.py` 字节一致。**这条做不到真正的版本分离**：两份文件同处一个工作区、同一写权限，同一方可以同时修改并重跑 `--write`，漂移检测会保持“一致”。真正的分离需要提交者写不到的位置（CI 受保护分支检出、签名发布物、只读挂载）与复核者独立读取；本机无 CI、无受保护分支，因此本条**只做漂移检测与变更留痕，不冒充权限分离**。残余风险见 ADR-0014 第 5 节（签收人身份不可验证、检查器与登记/快照可被同一方同改、复核记录可伪造、`--no-verify` 可绕过、覆盖 ≠ 充分、指纹绑定文本不绑定意图）。
  4. **ADR-0014**：独立记录“验证链自证”问题的信任边界、四层机械化能力与残余风险；M2 出口改为“两个实现缺陷关闭 + 覆盖闸门绿 + 四道绑定生效 + 非同源复核判‘实质收敛’”。
- **正负例（`scripts/test_checker_pins.py`）**：

| 编号 | 场景 | 预期 | 实际 | 退出码 | 证据 |
|---|---|---|---|---|---|
| CP01 | 改检查器不更新登记 | 阻断 | 阻断 | 1 | `check_sample.py：哈希不一致（登记 660bc902a1cf，工作区 606690d5617c）` |
| CP02 | 更新登记但不给裁定依据 | 拒绝 | 拒绝 | 2 | `检查器有改动但未提供 --basis 裁定依据` |
| CP03 | 更新登记并给出裁定依据 | 通过 | 通过 | 0 | `登记与工作区一致` |
| CP04 | 验收检查器与快照不一致 | 阻断 | 阻断 | 1 | `验收检查器与 validation/pinned/checker.py 快照不一致`（附“漂移检测不等于权限分离”） |

- **正负例（`scripts/test_spec_pins.py`）**：

| 编号 | 场景 | 预期 | 实际 | 退出码 | 证据 |
|---|---|---|---|---|---|
| SP01 | 改 A.2 不更新指纹 | 阻断 | 阻断 | 1 | `#A.2：指纹未更新（当前 41075a8d699f，登记 a3924c3de39b）` |
| SP02 | 更新指纹但不附复核记录 | 阻断 | 阻断 | 1 | `区段已改动但同一提交缺少合格的非同源复核记录` |
| SP03 | 更新指纹并附合格复核记录 | 通过 | 通过 | 0 | 无问题 |
| SP04 | 复核记录结论词不合格 | 阻断 | 阻断 | 1 | 同 SP02 的错误信息 |

- **回归实测**：
  - `python3 validation/checker-prototype/checker.py`：57/57 样例，17/17 `check_id`，退出 0。
  - `--null-sweep`：214/214 返回 `cannot_evaluate`，崩溃 0（顶层必需键 43、数组元素 159 / 56 条唯一路径、嵌套对象键 12）。
  - `--missing-key-sweep`：43/43 返回 `cannot_evaluate/missing_input`，偏离 0；对照 `{}` 直入 check 函数仍 17/17 抛 `KeyError`。
  - `--aggregation-order`：A2 与 E2 各 6 种排列，各收敛为 1 个结论，偏离 0；`--input-domain`：0 处缺口。
  - `check_coverage_gate.py`：子句 41、矩阵 41、正例 41、负例 41、样例 57、问题 0；`test_coverage_gate.py` N01–N03 阻断 3/3。
  - `test_check_table_mutations.py`：变异 11/11 抓到，A.2 签收正负例 2/2，退出 0。
  - 十个检查器全部退出 0（`check_checker_pins.py` 登记 14、工作区 14、快照一致；`check_spec_pins.py` 区段 5、已登记 5、问题 0）。
- **样例基线补记**：批次 0040 的 57 例基线提交为 `87ccf13`；既有 34 例输入与期望输出未改动，新增 23 例为负例。
- **更正（不改写批次 0040）**：批次 0040 记录的 `--null-sweep 138/138` 是 34 例时的计数；样例增至 57 后同一扫描为 214/214。两数均为实测，差异只来自样例数增加，不涉及判定行为变化。
- **复核状态**：G-001–G-017 仍为 `open`（17/17），核查矩阵 `0/17 consistent`（全部缺口未关闭，故无 `consistent` 行）。G-009 与 G-014 待非同源复核判“实质收敛”后关闭，其余 15 条不动。
- **关联 ADR**：ADR-0014（`proposed`）
- **状态**：生效（绑定上线；缺口未关闭）

---

### 批次 0042 — 2026-11-14 — 按非同源复核清单机械化 + 缺口记账

- **性质**：按非同源复核（基线 `d8bf413`，产物 `validation/reviews/2026-11-14-d8bf413-review.md`）列出的八项“本可机械化但没做”执行一轮；先按复核结论记账（closed 12 / partly 5 / open 0），再将 5 条 `partly` 按台账允许的状态记为 `open` 并写明残留。**不是**对实现质量的最终认可。
- **涉及文件**：`.githooks/pre-commit`、`AGENTS.md`（3.6.8、7bis.4、目录树）、`ROADMAP.md`（M2 出口）、`adr/0014-validation-chain-self-attestation.md`、`GAP_LEDGER.md`（17 条状态与核查记录）、`GLOSSARY.md`、`knowledge/glossary-usage.json`、`scripts/README.md`、`scripts/check_checker_pins.py`、`scripts/check_spec_pins.py`、`scripts/check_coverage_gate.py`、`scripts/test_checker_pins.py`、`scripts/test_spec_pins.py`、`scripts/test_coverage_gate.py`、`scripts/checker-pins.json`、`scripts/spec-pins.json`、`spec/methods/deterministic-checker.md`（A.1/A.2/样例基线）、`spec/CHECKER_INPUT_SCHEMA.md`（§2bis/§2ter/§3/§4）、`validation/checker-prototype/checker.py`、`validation/checker-prototype/coverage.json`、`validation/pinned/checker.py`、`validation/reviews/2026-11-14-d8bf413-review.md`（新增）、`CHANGELOG.md`（本批次）
- **变更摘要**：
  1. **根检查器与 pre-commit 纳入保护**：`checker-pins.json` 登记 17 个受保护对象（15 个 `scripts/` 检查器 + `.githooks/pre-commit` + 验收原型），**`check_checker_pins.py` 自身不再自排除**；`--write` 的 `basis` 必须是含 `非同源复核：`、`复核产物：<存在的路径>`、`复核基线：<提交号>` 的复核记录，自由文本被拒（退出 2）。
  2. **样例与覆盖矩阵纳入绑定**：`spec-pins.json` 由 5 个区段增至 7 个，新增方法 A.1 样例区段与 `validation/checker-prototype/coverage.json` 全文。
  3. **覆盖闸门改子句级**：`coverage.json` 每条负例必须声明 `expected_failed_clauses`；闸门调用原型实际求值，核对“声明的子句真的被触发”，不再依赖共享 `reason` 码。守卫子句（G-C2#2）用空声明 + `pass` + 无触发子句表达。
  4. **pre-commit 跑样例与关键扫描**：新增 A.1 全部 60 条样例、`--aggregation-order`、`--missing-key-sweep`、`--null-sweep --quick`、`--nested-missing-sweep`、`--enum-sweep`；改 `aggregate()` 或入口归一化后无法只靠十个检查器全绿。**单次耗时 29.78–31.46 s**（本机两次实测，含十个检查器）。
  5. **嵌套对象缺键归一化**：入口 `nested_missing()` 覆盖 `ENTITY_COLLECTIONS` 的 14 个实体集合，逐元素要求 `id`；schema 新增 §2ter 全表，逐项列出 **53 项**嵌套缺键路径（`--nested-missing-sweep` 53/53）。检测前删 `commitments[0].id` 等 10 项曾静默 `pass`，现已统一 `cannot_evaluate/missing_input`。
  6. **封闭枚举全局强制**：`applicability.state`、`assumption.status`、`node_type`、`subject_group.relation` 的非法值统一 `cannot_evaluate/undefined_enum_value`（`--enum-sweep` 4/4）；`orthogonal_to` 选“实现”而非删语义——`EXTENSION_RELATIONS` 纳入并允许无 `base`，A.1 新增正例 A.1.7-4，schema §4 与 A.2 `G-B2#2` 同步。理由：`orthogonal_to` 在 GRAMMAR 中表达“与基础主体组正交”的独立语义，删掉会失去对正交分组的约束能力，而实现成本仅一个关系枚举与 `base` 可空判定。
  7. **E2 链终点限人类/法人**：`accountable: true` 且类型不是 `HumanActor`/`LegalEntity` → `fail/accountable_not_human`（A.1.10-5 从 `pass` 改为 `fail`），不再因链可达而通过。
  8. **A.2 条数更正**：A.2 实际为 **41 条子句，不是 40**。台账 G-016、ADR-0013 与现存表述已更正；**批次 0034/0035/0036 的历史文本不改写**，以本更正为准。
- **记账**：12 条关闭（G-002/004/005/006/009/010/011/012/013/014/015/016），`关闭依据` 逐条为 `非同源复核：基线 \`d8bf413\`……复核产物 \`validation/reviews/2026-11-14-d8bf413-review.md\``；5 条维持 `open`（G-001/003/007/008/017），残留分别写明“枚举未全量强制”“扁平字符串双轨”“嵌套/枚举仍在收敛”“覆盖 ≠ 充分”“语义等价未保证”。
- **M2 出口改写**：改为“清单清零 + 非同源复核判实质收敛”；明写两项残余风险（复核记录可伪造、同一方拥有写权限）由外部控制（真 CI + 受保护分支 + 复核方独立持有工具链）承接，**不再以“打不穿”作为关闭条件**。
- **正负例（`scripts/test_checker_pins.py`）**：

| 编号 | 场景 | 预期 | 实际 | 退出码 | 证据 |
|---|---|---|---|---|---|
| CP01 | 改检查器不更新登记 | 阻断 | 阻断 | 1 | `scripts/check_sample.py：哈希不一致（登记 660bc902a1cf，工作区 606690d5617c）` |
| CP02 | 更新登记但不给 basis | 拒绝 | 拒绝 | 2 | `检查器有改动，但 --basis 不合格：缺少 \`非同源复核：\` 前缀` |
| CP03 | `--basis "测试"` | 拒绝 | 拒绝 | 2 | 同上 |
| CP04 | 合格复核记录更新登记 | 通过 | 通过 | 0 | `登记与工作区一致` |
| CP05 | 根检查器换成空壳 | 阻断 | 阻断 | 1 | `validation/checker-prototype/checker.py：哈希不一致` |
| CP06 | 删除 pre-commit 检查行 | 阻断 | 阻断 | 1 | `.githooks/pre-commit：哈希不一致` |
| CP07 | 验收检查器与快照不一致 | 阻断 | 阻断 | 1 | `验收检查器与 validation/pinned/checker.py 快照不一致` |

- **正负例（`scripts/test_spec_pins.py`）**：

| 编号 | 场景 | 预期 | 实际 | 证据 |
|---|---|---|---|---|
| SP01 | 改 A.2 不更新指纹 | 阻断 | 阻断 | `#A.2：指纹未更新` |
| SP02 | 更新指纹但不附复核记录 | 阻断 | 阻断 | `区段已改动但同一提交缺少合格的非同源复核记录` |
| SP03 | 更新指纹并附合格复核记录 | 通过 | 通过 | 无问题 |
| SP04 | 复核记录结论词不合格 | 阻断 | 阻断 | 同 SP02 |
| SP05 | 只改 `coverage.json` 引用关系、不改样例 | 阻断 | 阻断 | `coverage.json：指纹未更新（当前 22fb49ba7ceb，登记 517f0d88af13）` |

- **正负例（`scripts/test_coverage_gate.py`）**：

| 编号 | 负例动作 | 预期 | 实际 | 证据 |
|---|---|---|---|---|
| N01 | 删除子句唯一负例登记 | 阻断 | 阻断 | `G-F4#1：缺少负例` |
| N02 | 负例期望改成 pass | 阻断 | 阻断 | `G-F4#1：负例 A.1.14-1 期望 verdict=pass，负例被改成正例` |
| N03 | 删除负例样例块 | 阻断 | 阻断 | `A.1.14 的 YAML 块应为 4 的倍数，实际 2 个` |
| N04 | B1#2 负例换成 B1#1 用例 | 阻断 | 阻断 | `G-B1#2：负例 A.1.6-1 实际触发 ['G-B1#1']，未触发声明的 G-B1#2` |

- **回归实测**：
  - `checker.py`：60/60 样例，17/17 `check_id`，新增 A.1.7-4（`pass`）、A.1.8-3（守卫 `pass`）、A.1.10-5（`fail/accountable_not_human`）。
  - `--null-sweep`：225/225 返回 `cannot_evaluate`，崩溃 0（顶层 43、数组元素 159、嵌套 13）；`--null-sweep --quick`：80/80。
  - `--missing-key-sweep`：43/43；对照 `{}` 直入 check 函数仍 17/17 抛 `KeyError`。
  - `--nested-missing-sweep`：53/53；`--enum-sweep`：4/4；`--aggregation-order`：A2/E2 各 6 种排列各收敛 1 个结论；`--input-domain`：0 缺口。
  - `check_coverage_gate.py`：子句 41、矩阵 41、正例 42、负例 41、守卫 1、样例 60、问题 0。
  - `test_check_table_mutations.py`：变异 11/11，A.2 签收正负例 2/2。
  - 十个检查器与 pre-commit 全部退出 0；`check_checker_pins.py` 登记 17 / 工作区 17 / 快照一致；`check_spec_pins.py` 区段 7 / 已登记 7 / 复核记录 1 / 问题 0。
- **更正（不改写旧批次）**：批次 0034、0035、0036 中的“40 条子句”“非引用字段 40 个”按当时文本保留；A.2 实际为 41 条子句，schema 非引用字段实际为 41 个。批次 0034 已写明“新增 `G-D2#3`”却仍记 40 条，属计数错误；本批次以 41 为准。
- **复核状态**：`open` 5 / `closed` 12；核查矩阵 `0/17 consistent`。关闭依据均来自非同源复核转录件，**转录件本身不是身份验证**。
- **关联 ADR**：ADR-0014（`proposed`，本次补入自证/钩子/A.1/coverage 绑定与残余风险外置）
- **状态**：生效（机械化项上线；5 条缺口仍 `open`）

---

### 批次 0043 — 2026-11-14 — 六项实现修正、关闭依据外置、信任根止损、规划归档

- **性质**：处理基线 `48128a8` 复核结论中“已批准但未执行”的六项实现修正；把缺口关闭依据从仓库内转录件改为外部产物路径 + sha256；新增 ADR-0015 记录“停止加门”；归档 `spec/M3_M4_PLAN.md`（单独提交 `ce5c19d`）。**不新增检查器**。
- **涉及文件**：`GAP_LEDGER.md`、`AGENTS.md`（3.6.6、目录树）、`ROADMAP.md`（M2 出口 1/5/7、残余风险、状态）、`adr/0015-trust-root-external-infrastructure.md`（新增）、`spec/methods/deterministic-checker.md`（A.1.8-4、A.2 `G-C2#2` 原因码、A.2 签收行）、`spec/CHECKER_INPUT_SCHEMA.md`（§2bis.11）、`validation/checker-prototype/checker.py`、`validation/checker-prototype/coverage.json`、`validation/pinned/checker.py`、`validation/reviews/2026-11-14-d8bf413-review.md`（头注）、`validation/reviews/2026-11-14-48128a8-external.md`（新增，区段 basis）、`scripts/check_coverage_gate.py`、`scripts/check_gap_ledger.py`、`scripts/README.md`、`scripts/checker-pins.json`、`scripts/spec-pins.json`、`GLOSSARY.md`、`knowledge/glossary-usage.json`、`CHANGELOG.md`（本批次）

- **六项修正与实测**：
  1. **G-014 选“枚举非法值参与 `aggregate()`”**，不做入口短路。理由：A.2 的 `fail > cannot_evaluate > pass` 与顺序无关性是已签收语义；入口短路会让同一输入因“哪个检查先看到枚举”而结论不同。实测：A2 的 `undefined` + `unanchored` 两种顺序均 `fail/unanchored_management_item`；`node_type`/`assumption.status`/`relation` 非法值在无 `fail` 时仍 `cannot_evaluate/undefined_enum_value`。G-014 重开为 `open`。
  2. **`management_items[].node_type = Bogus`**：B1/B2 从 `pass` 改为 `cannot_evaluate/undefined_enum_value`（实测两处均为该结论）。
  3. **`assumption.status`**：`{}` → `cannot_evaluate/missing_input`；`{status: Bogus}` → `cannot_evaluate/undefined_enum_value`；`{status: pending}` 或 `{status: satisfied}`（只给 `{status}`）→ `cannot_evaluate/missing_input`；完整合法假设 → `pass`。D1/D2 两个 `check_id` 实测一致。
  4. **E2 `assertion.assumption = {}`**：从 `pass` 改为 `cannot_evaluate/missing_input`（`G-E2#3`）。
  5. **堵掉守卫豁免**：`check_coverage_gate.py` 对 `expected_failed_clauses: []` 直接报错；实测把 `G-F4#1` 负例改成空声明 → 退出 1，报“空声明不算负例”。`G-C2#2` 改为可触发子句（`state` 缺失 → `cannot_evaluate/missing_input`，新增 A.1.8-4），不再用空声明豁免。
  6. **G-016 更正**：共用原因码组为 **6 组**（B1、C2、E2 两处、F2、G3），不是 7 组；已写入台账说明。

- **关闭依据外置**：
  - `GAP_LEDGER.md` 的 `关闭依据` 只接受 `外部复核：<路径>；sha256：<64hex>；基线：<提交号>`，可选 `；caveat：`。
  - `scripts/check_gap_ledger.py` 机械核对路径存在、是文件、哈希一致；`--self-test` 的 E01–E05 实测 5/5（E02 路径不存在、E03 哈希不符、E04 指向目录、E05 缺 sha256）。
  - `validation/reviews/` 转录件加头注“非权威、不构成关闭依据”；`AGENTS.md` 3.6.6 写明“复核结论不得由执行方转录为依据”。
  - 11 条 `closed` 按新格式重述依据（`/tmp/verify-4812/REPORT_48128a8.md`，sha256 `d0f8275f…`，基线 `48128a8`）；G-010 保留 caveat `F1.charter.project→missing_charter；E2.assertions→assertion_incomplete`。

- **ADR-0015（新）**：信任根（`checker-pins.json`、复核转录件、根检查器）无法在仓库内部自保，新增门只会成为新信任根；M2 关闭受阻于基础设施（真 CI、受保护分支、复核方独立工具链）；因此停止加门。`ROADMAP.md` 的 M2 出口 5 与状态改为“受阻于外部基础设施，暂不关闭”，出口 7 去掉旧签收措辞。

- **规划归档**：`spec/M3_M4_PLAN.md` 头注“已暂停，未批准，不构成承诺”，状态 `archived`，单独提交 `ce5c19d`；未按该规划开工，未动 14 条待批决策。

- **回归实测**：
  - `checker.py`：61/61 样例，17/17 `check_id`；`--null-sweep` 227/227；`--missing-key-sweep` 43/43；`--nested-missing-sweep` 53/53；`--enum-sweep` 4/4；`--aggregation-order` 0 偏离。
  - `check_three_table.py`：A.2 指纹 `55c96288c69f`，A 表已由 A.2 重建，签收同步。
  - `check_coverage_gate.py`：子句 41、矩阵 41、正例 43、负例 42、样例 61、问题 0；空声明负例阻断 1 条。
  - `test_check_table_mutations.py` 11/11 + S01/S02 2/2；`test_coverage_gate.py` N01–N04 4/4；`test_checker_pins.py` CP01–CP07 7/7；`test_spec_pins.py` SP01–SP05 5/5。
  - 十个检查器退出 0；`check_checker_pins.py` 登记 17 / 工作区 17 / 快照一致；`check_spec_pins.py` 区段 7 / 已登记 7 / 问题 0。

- **缺口状态**：**17 条（`open` 6 / `closed` 11）**。`open`：G-001、G-003、G-007、G-008、G-014、G-017；`closed`：G-002、G-004、G-005、G-006、G-009、G-010、G-011、G-012、G-013、G-015、G-016。核查矩阵 `0/17 consistent`；到期 0。
- **关联 ADR**：ADR-0015（`proposed`，信任根与止损）；ADR-0014 的残余风险处置由本批次收敛为“外部基础设施未具备前不关闭 M2”。
- **状态**：生效（六项修正上线；G-014 仍 `open`，待修后外部复核）

---

### 批次 0044 — 2026-11-14 — 复核产物迁出 `/tmp`，11 条关闭依据改为持久路径

- **性质**：`/tmp` 会被清理，批次 0043 登记的 11 条关闭依据若继续指向 `/tmp/verify-4812/REPORT_48128a8.md` 将集体失效。把两份复核报告与探针/攻击脚本、原始结果复制到仓库外持久目录，重述依据路径并复算哈希。**未新增检查器**。
- **持久目录**：`/home/wgz/projects/skills/2026-11-14/pm-governance-review/`（在 `project-management` 仓库之外，不受 git 管理）
  - `verify-4812/`：`REPORT_48128a8.md`、`attacks.py`、`attacks2.py`、`attacks.json`、`attacks2.json`、`probes/`、`probes2/`
  - `verify-d8/`：`REPORT_d8bf413.md`、`attacks.py`、`attacks2.py`、`attacks3.py`、`attacks*.json`、`probes/`
- **哈希**：
  - `verify-4812/REPORT_48128a8.md` → `d0f8275f9931f36da93c640ad8a070c8af7200929d0a4a685e5309268356c4e7`（与迁出前一致，字节级复制）
  - `verify-d8/REPORT_d8bf413.md` → `658a7f4e725a879583d85a78ba146a89002786960fb98f2ebf9d8ded3fa6cf5e`
- **涉及文件**：`GAP_LEDGER.md`（11 条 `closed` 的路径改为持久路径，哈希不变；G-010 caveat 保留）、`AGENTS.md`（3.6.6 新增“外部复核产物必须位于仓库外持久位置，`/tmp` 不得作为关闭依据”）、`CHANGELOG.md`（本批次）
- **复核**：`python3 scripts/check_gap_ledger.py` 退出 0、`--staged` 退出 0；17 条（`open` 6 / `closed` 11）、到期 0。复用现有台账校验，未加 `/tmp` 前缀的新判定。
- **状态**：生效

---

### 批次 0045 — 2026-11-14 — M3/M4 解冻进入决策阶段，产出待批决策单

- **性质**：M3/M4 从归档转为决策阶段；把规划中的 14 条待批决策整理为可逐条拍板的决策单。**不写内容条目、不改任何规格、不新增检查器。**
- **涉及文件**：`spec/M3_M4_DECISIONS.md`（新增）、`spec/M3_M4_PLAN.md`（头注改为“进入决策阶段”，状态 `archived` → `deciding`，记录批次 0045）、`CHANGELOG.md`（本批次）
- **决策单结构**：按“不定就无法开工”的紧迫度分三组——A 组 5 条（D1、D2、D3、D4、D8）、B 组 5 条（D7、D6、D9、D10、D13）、C 组 4 条（D5、D11、D14、D12）。每条含问题、2–3 个选项、建议与理由、不定的卡点、影响面，控制在 150 字内。
- **稳定性判断**：几乎不会改 5 条（D5、D8、D10、D12、D14）；大概率试点后推翻 8 条（D1、D2、D3、D4、D6、D7、D9、D13）；待观察 1 条（D11）。最危险组合 D1+D2+D4：均标“现在必须定”且大概率被推翻，返工面覆盖 309 条、103 个术语 ID 与全部锚点。
- **状态**：生效（等待用户逐条拍板）

---

### 批次 0046 — 2026-11-14 — G-014/G-001/G-003/G-007/G-008 关闭、G-006 措辞更正、G-018 新登记、A 组决策落账

- **性质**：按非同源复核（基线 `9519b82`，产物 `/home/wgz/projects/skills/2026-11-14/pm-governance-review/verify-g014/REPORT_9519b82.md`）关闭 5 条缺口；更正 G-006 证据措辞；登记新缺口 G-018；记录 A 组决策与 D4 降级。**未开始试点内容写作。**
- **缺口关闭**：G-014、G-001、G-003、G-007、G-008 → `closed`，`关闭依据` 均带 `报告章节：§一/§三（G-0xx）`；关闭依据分指：
  - G-014：§一（枚举结果参与 `aggregate()`，四组场景全排列顺序无关、唯一收敛 `fail`；5 个无关子句正常）。
  - G-001：§三（`node_type=Bogus` → cannot，`orthogonal_to` pass，`subject_group` 17/17）。
  - G-003：§三（`assumption={}` → cannot；端点 AIActor → fail；flat grant → cannot/invalid_path）。
  - G-007：§三（`status` 缺失、仅 `{status}`、`{}` 均 → cannot/missing_input）。
  - G-008：§三（空 `expected_failed_clauses` 被覆盖闸门直接判错）。
- **G-006 措辞更正**：原报告“缺 constraint 均 fail”不成立；`constraint=null` 实测 `cannot_evaluate/missing_input`，用 `48128a8` 旧基线复跑同样如此，属原报告写错。按“非 pass”口径 G-006 仍关闭，依据改指新报告 §二；不改写批次 0043 历史记录，来由记于台账说明与本批次。
- **G-018 新登记**：`actors[].type=Bogus` 仍 `pass`；`CHECKER_INPUT_SCHEMA.md` §2 已声明枚举，但 §1.11 归一化未列 `actor_type`，原型未校验。等级 L1、成因 `representation-defect`、登记 M1、到期 M2、出口 `check-change`、关联 T-137。
- **缺口状态**：18 条（`open` 2：G-017、G-018 / `closed` 16）。G-017 维持 `open`（无全文语义等价机器证明）。
- **决策落账**：A 组 D1=c、D2=b、D3=a+映射表、D8=b；D4 从 A 组移至 B 组末尾，七条降级前提写入 `spec/M3_M4_DECISIONS.md`（草稿 ID `DRAFT-K-<CAT>-<NN>` + `authoritative: false`、禁止进入五个权威面、`pilot-id-map.json` 唯一映射面、ID 作不透明字符串、候选 IRI 覆盖统计、≥2 条无 IRI 回 A 组、进权威文件前必须定）。`spec/M3_M4_PLAN.md` 状态头同步为“A 组已定、试点未开工”。
- **涉及文件**：`GAP_LEDGER.md`、`AGENTS.md`（3.6.6 增加 `报告章节` 字段）、`ROADMAP.md`（M2 出口 5 改为 18 条）、`TODO.md`（T-130/131/133/134/135/136 → `done`，新增 T-137）、`spec/M3_M4_DECISIONS.md`、`spec/M3_M4_PLAN.md`、`CHANGELOG.md`。
- **未改动**：`STATE.md`（无新增/删除受管文件，目录默认状态未变）、`manifest.json`（版本与发布字段不受影响）。
- **状态**：生效

---

### 批次 0047 — 2026-11-14 — M3/M4 试点执行（15 条草稿）

- **性质**：按 `spec/M3_M4_PLAN.md` 第 3 节执行试点，产出 15 条草稿、ID 映射、契约、产物样例与冲突样例；逐项判定 7 条判据与 6 条止损。**D4 未定，未放量，未写任何权威条目。**
- **执行口径**：D1=c（按概念类型混合，`entry_type` 区分）；D2=b（五字段扩 `entry_type`/`status`/`relations`/`evidence`，不另立 schema）；D3=a + `pilot-id-map.json` 反向索引；D8=b（`definitionStatus` 含 `disputed`/`blocked-external`）；D4 全程 `DRAFT-K-<CAT>-<NN>` 且 `authoritative: false`。
- **产出**：`spec/pilot/pilot-entries.json`（6 工件 + 6 工具 + 1 过程 + 1 焦点区 + 1 绩效域）、`spec/pilot/pilot-id-map.json`、`spec/pilot/pilot-contract.yaml`、`spec/pilot/pilot-artifact.json`、`spec/pilot/pilot-artifact.md`、`spec/pilot/pilot-conflicts.jsonl`、`spec/pilot/M3_M4_PILOT_REPORT.md`。
- **统计**：15 条全部 `defined`；候选 IRI 有 14、无 1（Monte Carlo；本体最近邻 `pm:tt_Simulation` 语义更宽，置 `null` 并写原因）；稳定自然键 15；既无 IRI 又无稳定自然键 0，用户指定止损未命中。
- **判据**：1 结构通过但受 T-123 来源授权限制；2 通过；3 通过（映射层，未接入 `GRAMMAR.md`）；4 部分通过（草稿层零冲突，权威层未检验）；5 通过；6 通过；7 `blocked-external`（无非执行方抽样）。
- **止损**：五条明确未触发；外部抽样一条无法判定；未新增检查器、指纹区段或自证机制。
- **放量门**：D4 拍板、T-123 来源使用授权、T-139 `grounding_ref` 语义统一、外部抽样 5 条。本批未开始放量。
- **涉及文件**：`spec/pilot/` 下 7 个新文件、`spec/M3_M4_PLAN.md`（状态头）、`spec/M3_M4_DECISIONS.md`（状态头）、`TODO.md`（T-138 `done`、T-139 `open`、T-123 补试点证据）、`STATE.md`（`spec/pilot/` 默认 `example`）、`AGENTS.md`（目录结构）、`CHANGELOG.md`。
- **未改动**：`GLOSSARY.md`、`knowledge/anchored-entries.jsonl`、TTL 的 `skos:prefLabel`、`GRAMMAR.md` 的 `grounding_ref`、`SOURCE_LEDGER.md` 的 `claim_mapping`、`manifest.json`。
- **状态**：生效（试点完成，放量未开始）

---

### 批次 0048 — 2026-11-14 — PMBOK8-2025 放宽至概念层、T-139 字段语义拆开、F-07 定性登记 G-019

- **性质**：落实用户两项裁定与 F-07 定性。放宽 `PMBOK8-2025` 至概念层用途（附 ADR-0016）；把 `grounding_ref` 与来源归属拆成两种意图，迁移现有 10 条权威条目；判定 F-07 为检查器缺陷并登记 G-019。**D4 仍未定，未放量，未动判据 7 的外部抽样。**
- **一、来源用途放宽**：`SOURCE_LEDGER.md` 的 `PMBOK8-2025`：
  - `allowed_uses` 从“仅限原则层面”改为“概念层与原则层均可用（2026-11-14 用户授权，批次 0048）”，概念层用于知识条目的术语名、定义结构与页码范围证据，写入条目 `evidence[]`；
  - 仍不包含：成段摘录入库（`CONSTITUTION.md` 第 13 条）、以原文替代自写定义、未核页的批量引用、规则正文的直接锚定（规则仍须经 `claim_mapping` 显式包含）；
  - `verification_method` 记为“概念层页码已按 15 条试点逐条核对印刷页，未全文逐页核对”；`claim_mapping` 明确概念层来源归属不进本字段；
  - 新增 `adr/0016-pmbok8-concept-layer-use.md`（`accepted`）作为实质变更依据。
- **二、T-139 两种意图拆开**：
  - `knowledge/anchored-entries.jsonl` 10 条权威条目删除 `grounding_ref`，来源改为 `evidence[]`（每项含 `source_id` / `locator` / `page` / `precision` / `verification`）；映射：Project/Actor/Commitment/Deliverable/Constraint/Outcome → `ProjectCO-2024`（Deliverable 另加 `ThingFO-2021`），Assertion/Subject → `ThingFO-2021`，Accountable/Responsible → `PRINCE2-2023`；
  - `grounding_ref` 仅保留两种用途：规则/方法条目指向 `SOURCE_LEDGER.md` 条目 ID；本体或规则到知识条目的绑定取 `knowledge:<term>`；
  - 语义写入 `spec/CHECKER_INPUT_SCHEMA.md` §1.16、`spec/ANCHOR_SPEC.md`、`GRAMMAR.md`、`GLOSSARY.md`（T-B-003）、`spec/methods/deterministic-checker.md`、`scripts/check_glossary_sync.md`、`scripts/README.md`；
  - `scripts/check_anchors.py` 改为校验 `evidence[].source_id` 可解析到 active 来源，未新增检查器；
  - 试点 15 条删除自指的 `grounding_ref`（原为把草稿 ID 当 `knowledge:` 值的自环），`evidence` 保留；`pilot-id-map.json` 增加 `grounding_ref_semantics` 说明，`knowledge_ref` 保留；
  - 新增 `adr/0017-grounding-ref-vs-evidence.md`（`accepted`）作为字段语义拆分的结构性变更依据；用户裁定转录见 `validation/reviews/2026-11-14-t139-user-adjudication.md`，供检查器绑定核对。
- **三、F-07 定性**：判为 `implementation-defect`。`RM-PROSEBLOCK` 已豁免 Markdown 表格行但未识别结构化 JSONL：连续 ≥15 行、每行 ≥100 字符即报“文本层转储”。当前 `anchored-entries.jsonl` 为 10 条尚不触发，扩到 15 条长行即阻断 M3 按条目铺开。登记 `G-019`（L1、`implementation-defect`、登记 M1、到期 M2、出口 `check-change`、关联 T-140），新增 TODO T-140。
- **缺口状态**：19 条（`open` 3：G-017、G-018、G-019 / `closed` 16）。
- **涉及文件**：`SOURCE_LEDGER.md`、`adr/0016-pmbok8-concept-layer-use.md`（新增）、`adr/0017-grounding-ref-vs-evidence.md`（新增）、`validation/reviews/2026-11-14-t139-user-adjudication.md`（新增）、`knowledge/anchored-entries.jsonl`、`scripts/check_anchors.py`、`scripts/checker-pins.json`、`scripts/spec-pins.json`、`scripts/README.md`、`scripts/check_glossary_sync.md`、`spec/CHECKER_INPUT_SCHEMA.md`、`spec/ANCHOR_SPEC.md`、`spec/methods/deterministic-checker.md`、`spec/pilot/pilot-entries.json`、`spec/pilot/pilot-id-map.json`、`spec/pilot/M3_M4_PILOT_REPORT.md`、`GLOSSARY.md`、`GRAMMAR.md`、`scripts/anchor_baseline.json`、`knowledge/glossary-usage.json`、`GAP_LEDGER.md`、`TODO.md`、`CHANGELOG.md`。
- **未改动**：`manifest.json`、`ROADMAP.md`，以及判据 7 的外部抽样（维持 `blocked-external`）。
- **状态**：生效（放量仍未开始）

---

### 批次 0049 — 2026-11-14 — 修复 G-019：`RM-PROSEBLOCK` 识别结构化 JSONL

- **性质**：修正检查器实现缺陷（`implementation-defect`），不新增判据。G-019 保持 `open`，按 `AGENTS.md` 3.6.6 等非同源复核或人工签收后关闭。
- **修复**：`scripts/check_no_raw_material.py` 新增 `is_structured_jsonl()`，仅当文件为 `.jsonl` 且每行（非空）都解析为 JSON 对象时，豁免 `RM-PROSEBLOCK`。仅凭扩展名、JSON 字符串行、文本层转储改名 `.jsonl` 均不放行；PDF/OCR 转储检测保持原样。
- **双向覆盖**：新增 `--self-test`，T-NRM-01 结构化 JSONL（15 行 × ≥100 字符）不报；T-NRM-02 每行一个 JSON 字符串仍报；T-NRM-03 真实 PDF 文本层（ISO 29148 第 4 页，15 行 × ≥100 字符）仍报；T-NRM-04 转储改名 `.jsonl` 仍报。4/4 通过；缺少本地 PDF 样本时返回 `2`（无法评估），可用 `PM_RESOURCE_DIR` 指定资源目录。
- **实测**：15 条试点条目 JSONL（最长行 998 字符）与 20 条扩展 JSONL（最长 1004 字符）`RM-PROSEBLOCK` 均为 0 报。
- **台账**：G-019 说明追加修复与负例记录，状态维持 `open`、关闭依据留空；T-140 → `done`（G-019 关闭待复核）。
- **涉及文件**：`scripts/check_no_raw_material.py`、`scripts/checker-pins.json`、`scripts/README.md`、`validation/reviews/2026-11-14-g019-user-authorization.md`（新增）、`GAP_LEDGER.md`、`TODO.md`、`CHANGELOG.md`。
- **未改动**：D4 决定、放量、判据 7 外部抽样、`manifest.json`、`ROADMAP.md`。
- **状态**：生效（G-019 待复核关闭）

---

### 批次 0050 — 2026-11-15 — G-019 二次加固、G-020 登记（覆盖范围与准入形态）

- **性质**：按外部复核（基线 `dcd2240`，`/home/wgz/projects/skills/2026-11-14/pm-governance-review/verify-g019/REPORT.md`）修复 `--self-test` 与 `RM-PROSEBLOCK` 的绕过面；同时新立覆盖范围缺口。G-019 保持 `open`，不自行关闭；D4 未动、未放量、未碰判据 7 外部抽样。
- **一、G-019 六条补强**（`scripts/check_no_raw_material.py`）：
  - **值级判据**：JSONL 豁免不再只看“每行是对象”。顶层字符串值上限 400 字符（`term`/`label_*`/`status`/`candidate_iri*` 等身份键 120），`relations` 子值 ≤120，`evidence` 字符串 ≤200；超限即不豁免。
  - **键白名单**：`JSONL_TOP_KEYS` 固定为语料实际键集合，**不含** `text`/`content`/`body`/`page`/`chunk`/`payload`/`raw`；`relations` 与 `evidence` 各有子键白名单，未知键不豁免。
  - **单行与 base64**：新增 `RM-LONGLINE`（单行 >8192 字符）与 `RM-BASE64`（≥256 字符 base64 形态串，或 ≥64 字符且解码后命中已知魔数）。
  - **形态识别**：新增 `RM-MAGIC`，在扩展名判断前识别 PDF/ZIP/GZIP/PNG/JPEG/GIF/TIFF/RAR/7Z/PostScript/OLE/DjVu；未知扩展名不再跳过，一律按文本扫描（NUL/非 UTF-8 → `RM-BINARY`）；`TEXT_EXTS` 纳入 `.log/.csv/.html/.htm/.xml/.tex/.rst/.tsv/.svg/.dat`。
  - **段落级判据**：新增 `RM-PAGEDUMP`（非空行 ≥20、60–115 字符且无 Markdown 标记的行占比 ≥0.6、其中 ≥50% 不以句末标点结尾），补上原判据只对目录页有效的问题。
  - **BOM**：JSONL 解析前 `lstrip("\ufeff")`，合法 BOM JSONL 不再误报。
- **二、负例与自测**：`--self-test` 扩为 18 项断言——T-NRM-01 合法 JSONL、01b BOM、02 JSON 字符串行、03 真实正文第 6 页 `.txt`（断言 `RM-PAGEDUMP` 命中且无 `RM-DOTLEADER`，排除干扰）、04 对象包裹正文、05 对象包裹/超长值/base64/单行 30 万字符、06 `.log/.csv/.html/.dat` 与 PDF/gzip 魔数、07 长行夹空行/未知扩展名。18/18 通过。PDF 资源缺失时返回 `2`，并明确“非 PDF 用例已执行 N 项，2 ≠ 通过”；不依赖 PDF 的负例始终执行。
- **三、全仓实测**：放宽扫描面后，130 个跟踪文件 0 错误、**0 新命中**（无合法 csv/html/日志形态误报，未加白名单豁免）。15 条试点条 JSONL（最长 998 字符）、20 条扩展 JSONL（最长 1003 字符）、20 条权威条目 JSONL（最长 683 字符）`RM-PROSEBLOCK` 均为 0 报。
- **四、G-020 登记**：`representation-defect`、L1、登记 M1、到期 M2、是否阻断=否、待裁定方=架构负责人、关联 T-142。成因是第 13 条“原始资料不许入库”实际执行为“某些扩展名下某些形态的文本不许入库”：只扫 `git ls-files` 已跟踪文件、内容扫描按扩展名名单分流、不扫子模块、未知形态依赖 fail-closed。与 G-019 的边界：G-019 是既有判据缺失（`implementation-defect`），G-020 是防线覆盖面与准入口径（设计层判断），建议出口 `rule-change` 或 `check-change`。矩阵首行与矩阵说明同步。
- **五、台账与调度**：G-019 说明追加本批加固与负例记录，状态维持 `open`、关闭依据留空；新增 G-020；核查记录追加批次 0050。台账 20 条（`open` 4：G-017、G-018、G-019、G-020 / `closed` 16）。`TODO.md` 新增 T-141（`done`）、T-142（`open`），T-140 保持 `done`。
- **涉及文件**：`scripts/check_no_raw_material.py`、`scripts/README.md`、`scripts/checker-pins.json`（重冻）、`validation/reviews/2026-11-15-g019-hardening-user-authorization.md`（新增，检查器绑定 `basis`）、`GAP_LEDGER.md`、`TODO.md`、`CHANGELOG.md`。
- **未改动**：D4 决定、放量、判据 7 外部抽样、`manifest.json`、`ROADMAP.md`、`GRAMMAR.md`/A.2/A.1/schema（`spec-pins` 不受影响）。
- **状态**：生效（G-019 待非同源复核关闭）

---

### 批次 0051 — 2026-11-15 — 原始资料防线换轴方案（只出方案）

- **性质**：按 r2 复核（基线 `58641d0`，`/home/wgz/projects/skills/2026-11-14/pm-governance-review/verify-g019-r2/REPORT.md`）出改造方案。本批**不改实现、不改 `CONSTITUTION.md`**；D4 未动、未放量、未碰判据 7 外部抽样。
- **失效证据**：形态启发式双向失准且不收敛——整页正文单条记录 0 命中、390 字符补句号切块 0 命中、base64 60 字符切块 0 命中、`RM-PAGEDUMP` 真实召回 4/15、合法 450–1500 字符定义被 `RM-PROSEBLOCK`/`RM-ONTO-LITERAL` 误杀、中文正文页与 80 列硬换行文档分别漏判与误报。
- **方案**：新增 `spec/RAW_MATERIAL_ADMISSION.md`——以分区准入替代形态推断；D 数据区（结构化 + schema + 字段配额）、O 本体区（13.6 + 谓词分档）、P 散文区（P0/P1/P2，仅硬约束）、C 代码/配置区；未归类路径 fail-closed；现有 131 个跟踪文件逐条判定（D 16 / O 30 / C 19 / P 66）；数据区 schema 来源、散文残留按字段位置判定、规则清单逐条留改删（`RM-PROSEBLOCK`/`RM-PAGEDUMP`/`RM-PAGESEQ` 退役，新增 `RM-ZONE`/`RM-SCHEMA`/`RM-FIELD`）；第 13 条条文级修订草案；迁移四步与不设豁免期的理由；残余风险与 ADR-0015 的关系；G-019/G-020 改写建议；成本量级与 10 条待批 D 清单。
- **ADR**：新增 `adr/0018-raw-material-admission-control.md`（`proposed`），记录五个被否方案及理由，尤其“继续加启发式”因双向失准被否。
- **台账**：G-019、G-020 均追加本批说明，状态维持 `open`、关闭依据留空，不自行关闭；核查记录追加批次 0051，总数仍 20（`open` 4 / `closed` 16）。`TODO.md` 新增 T-143（`done`）、T-144（`open`）。`STATE.md` 新增 `adr/0018` 与 `spec/RAW_MATERIAL_ADMISSION.md` 的 `skeleton` 例外。
- **涉及文件**：`spec/RAW_MATERIAL_ADMISSION.md`（新增）、`adr/0018-raw-material-admission-control.md`（新增）、`GAP_LEDGER.md`、`TODO.md`、`STATE.md`、`CHANGELOG.md`。
- **未改动**：`scripts/check_no_raw_material.py`、`CONSTITUTION.md`、`scripts/README.md`、`checker-pins.json`、`spec-pins.json`、D4、放量、判据 7 外部抽样。
- **状态**：方案待批（ADR-0018 `proposed`，T-144 `open`）

---

### 批次 0052 — 2026-11-15 — 准入制落地（阶段一：条文与 ADR）

- **性质**：用户 2026-11-15 批准 `spec/RAW_MATERIAL_ADMISSION.md` 第 13.2 节全部 10 条 D 项，按建议执行。本批是四阶段迁移的第一阶段：修条文与 ADR，不改检查器实现。D4 未动、未放量、未碰判据 7 外部抽样；G-019/G-020/G-021 均不自行关闭。
- **宪法修订**（`CONSTITUTION.md`）：
  - 13.3 由“后果与执行”改为“合规判定与执行”：按目录角色分区判定（数据区 schema + 配额、散文区仅硬约束、本体区按 13.6、未归类 fail-closed），并明确“未命中不等于合规”。
  - 13.5 保留原句，增补 2026-11-15 裁定：本次换轴不构成对 13.1 禁止范围的缩小，也不构成对 13.3 阻断强度的实质性降低；依据是 `RM-PROSEBLOCK`/`RM-PAGEDUMP` 实测漏杀与误杀并存、`RM-PAGEDUMP` 真实召回 4/15、整页单条与切块均 0 命中；残余风险由外部指纹与人工评审承接。
  - 13.1、13.2、13.4、13.6 未改。
- **ADR**：`adr/0018-raw-material-admission-control.md` 由 `proposed` 转 `accepted`，决策者记为用户（2026-11-15），并同步 13.5 裁定与受影响文件状态。
- **授权记录**：新增 `validation/reviews/2026-11-15-admission-axis-authorization.md`，逐条转录 D-1–D-10、注明用户裁定日期、复核基线 `2d0c0ea` 与“不构成缺口关闭依据”的边界。
- **台账**：`STATE.md` 移除 ADR-0018 的 `skeleton` 例外（随 `adr/` 默认值 `accepted`），`spec/RAW_MATERIAL_ADMISSION.md` 改为 `active` 并注明非现行规范；`TODO.md` 的 T-144 转 `in-progress` 并记录本批进度。
- **涉及文件**：`CONSTITUTION.md`、`adr/0018-raw-material-admission-control.md`、`validation/reviews/2026-11-15-admission-axis-authorization.md`（新增）、`STATE.md`、`TODO.md`、`CHANGELOG.md`。
- **未改动**：`scripts/check_no_raw_material.py`、`scripts/README.md`、`checker-pins.json`、`spec-pins.json`、`manifest.json`（未发布，版本与 tag 保持 `0.5.1` / `v0.5.1`）、D4、放量、判据 7 外部抽样。
- **状态**：生效（阶段二实现与阶段三过检待后续批次；G-019/G-020 仍 `open`）

---

### 批次 0053 — 2026-11-15 — 准入制落地（阶段二：检查器与 schema）

- **性质**：按批次 0052 的授权落地 D-1、D-4、D-5、D-9 与 §7 规则变更。D4 未动、未放量、未碰判据 7 外部抽样；G-019/G-020/G-021 均不自行关闭。
- **归区表**：新增 `spec/ACCESS_ZONES.md`。路径前缀表覆盖 D/O/P/C 四区与 P0–P2 分级；数据区准入登记表覆盖 16 个结构化文件；未归类路径 fail-closed（`RM-ZONE`），数据区未登记文件报 `RM-SCHEMA`，不降级为文本扫描（D-1）。`ontology/` 归 O，`ontology/fixtures/manifest.json` 归 D（D-9）。
- **schema**：新增 `contracts/schema/knowledge-entry.schema.json`（anchored 与 pilot 共用，含 D2/D3/D7/M3-E1 字段与 `x-prose-fields`）与 `contracts/schema/pilot-conflict.schema.json`；两者纳入 `scripts/spec-pins.json`（D-5）。配额按方案 §4.3：`definition` 2000 / `provenance_note` 800 / 单条散文字段 2500 / 单文件 20 KiB / 身份键 120 / `relations` 120 / `evidence` 200 / `candidate_iri_reason` 400（D-4）。
- **检查器重写**（`scripts/check_no_raw_material.py`）：按区执行硬约束、schema 与字段配额；删除 `RM-PROSEBLOCK`、`RM-PAGEDUMP`、`RM-PAGESEQ`；新增 `RM-ZONE`、`RM-SCHEMA`、`RM-FIELD`；`RM-ONTO-LITERAL` 对 `skos:definition`/`rdfs:comment`/`dcterms:description` 放宽到 2000，其他字面量维持 400；`RM-ONTO-COMMENT` 400 → 800。退出码重定为 0/1/2，其中 2 仅表示归区表或准入登记不可解析；`--self-test` 只返回 0/1，全部为合成用例，不依赖本地 PDF 资源。
- **自测**：按新轴重建为 30 项（T-NRM-01–T-NRM-09），覆盖合法 15 条 JSONL 与 BOM、退役启发式不再误杀长散文/硬换行/中文页/长定义、对象包裹 `text`/`content`/`chunk`、未知键/缺必填/超长字段/单文件配额、30 万字符单行、base64 PDF 头、长引用、PDF/gzip 魔数改名、禁止扩展名、未归类与未登记 fail-closed、本体字面量分档与注释上限、归区最长前缀与全仓覆盖；不保留已退役启发式的样例。
- **同步**：`.githooks/pre-commit` 增加 `--self-test`；`scripts/README.md` 更新规则表、退出码、分区与自测说明；`GLOSSARY.md` 新增 T-D-014–T-D-020（数据区、散文区、本体区、代码与配置区、分区准入、归区表、豁免）并生成使用位置；重冻 `scripts/checker-pins.json`（17 个受保护对象）与 `scripts/spec-pins.json`（9 个区段）。
- **实测**：全仓 134 个跟踪文件 0 违规（D 16 / O 30 / P 69 / C 19 / 未归类 0）；自测 30/30；全套检查器、pre-commit 与原型快检全绿。
- **涉及文件**：`spec/ACCESS_ZONES.md`（新增）、`contracts/schema/knowledge-entry.schema.json`（新增）、`contracts/schema/pilot-conflict.schema.json`（新增）、`scripts/check_no_raw_material.py`、`scripts/check_spec_pins.py`、`scripts/checker-pins.json`、`scripts/spec-pins.json`、`validation/pinned/checker.py`、`.githooks/pre-commit`、`scripts/README.md`、`GLOSSARY.md`、`knowledge/glossary-usage.json`、`validation/reviews/2026-11-15-admission-axis-implementation.md`（新增）、`TODO.md`、`CHANGELOG.md`。
- **未改动**：`manifest.json`（未发布，版本与 tag 保持 `0.5.1` / `v0.5.1`）、D4、放量、判据 7 外部抽样。
- **状态**：生效（阶段三一次性过检与豁免判定待批次 0054；G-019/G-020 仍 `open`）

---

### 批次 0054 — 2026-11-15 — 准入制落地（阶段三：一次性过检与豁免判定）

- **性质**：对全仓跟踪文件执行阶段二的新检查器，逐文件确认归区与准入；按 D-6 判定是否设豁免期。D4 未动、未放量、未碰判据 7 外部抽样；G-019/G-020/G-021 均不自行关闭。
- **过检对象**：`git ls-files` 的 138 个跟踪文件。
- **归区分布**：D 18 / O 30 / P 71（P0 16、P1 42、P2 13）/ C 19；未归类 0。
- **违规**：0。数据区 18 个文件全部在 `spec/ACCESS_ZONES.md` 第 2 节登记并通过 schema；本体区 30 个文件全部通过第 13.6 条与字面量分档；散文区与代码区全部通过硬约束。逐文件核对方式为对每个跟踪文件解析区与准入登记后调用 `check_file()`，复跑命令 `python3 scripts/check_no_raw_material.py`。
- **豁免判定（D-6）**：0 违规，收敛为**不设豁免期**。依据：准入制要求“存量先合规、再切闸门”，存量已全部合规；此时开豁免窗口只会把已合规存量重新放入无复核的例外通道。未创建 `validation/exemptions/`。将来若出现暂时无法修正的合法文件，按方案第 10.3 节登记，且不得用于原始资料或提取产物。
- **记录位置**：`spec/ACCESS_ZONES.md` 第 6 节。
- **涉及文件**：`spec/ACCESS_ZONES.md`、`TODO.md`、`CHANGELOG.md`。
- **未改动**：`manifest.json`（未发布，版本与 tag 保持 `0.5.1` / `v0.5.1`）、`STATE.md`（新文件均由目录默认值覆盖，无新增例外）、D4、放量、判据 7 外部抽样。
- **状态**：生效（阶段四台账改写与 G-021 登记待批次 0055；G-019/G-020 仍 `open`）

---

### 批次 0055 — 2026-11-15 — 准入制落地（阶段四：台账）

- **性质**：按已批准的 D-7、D-8、D-10 与阶段四要求改写缺口台账，并完成 T-144。D4 未动、未放量、未碰判据 7 外部抽样；三条缺口均不自行关闭，等非同源复核。
- **G-019 改写**：标题改为“形态判据退役与准入制落地”。说明保留 0049/0050/0051 的历史与 r2 实测数字，补记 0052–0054 的条文修订、归区与 schema、检查器重写、30 项自测、138 文件 0 违规与 D-6 收敛。状态维持 `open`，关闭依据留空。
- **G-020 改写**：标题改为“子模块、外部生成物与未登记路径的扫描范围”。文件枚举一半不再保留（未知扩展名/魔数改名已由批次 0050 覆盖），形态分类一半并入 G-019；剩余范围只含 `git ls-files` 之外的未跟踪文件、外部生成物与子模块。
  - **D-8**：子模块按“显式声明不纳入”处理；实测当前 0 个 gitlink、无 `.gitmodules`，属口径预留而非现存盲区。
  - **D-7**：外部指纹只记方向（仓库外常驻来源指纹比对，与 ADR-0015 同批外置），不定时点。
  - 状态维持 `open`。
- **G-021 登记**：`representation-defect`/L3，影响面为散文区与数据区 `prose_fields` 的内容层原创性；出口倾向 `accepted`（接受仓库内不做来源层判定，由外部指纹与人工评审承接）。状态 `open`，不自行关闭。
- **核查矩阵**：`PROJECT_MINIMAL_EXISTENCE` 行补 `G-021`；矩阵说明同步 G-019/G-020 的新边界与 G-021 的仓库级定位。
- **TODO**：T-144 转 `done`（实现批次 0052–0055 已完成）；新增 T-145 承接外部指纹与 G-021 的方向登记（不定时点）。
- **ADR-0018**：跟进事项同步为已完成/待复核状态。
- **AGENTS.md 同步**：第 4 条目录结构补 `spec/ACCESS_ZONES.md` 与两份数据区 schema；第 7bis 条第 7 项把已退役的 `RM-PROSEBLOCK` 改为分区准入规则码（`RM-ZONE`/`RM-SCHEMA`/`RM-FIELD`）。
- **涉及文件**：`GAP_LEDGER.md`、`TODO.md`、`adr/0018-raw-material-admission-control.md`、`AGENTS.md`、`CHANGELOG.md`。
- **未改动**：`manifest.json`（未发布，版本与 tag 保持 `0.5.1` / `v0.5.1`，`check_state.py` 一致性核对通过）、`STATE.md`（无新增文件例外）、D4、放量、判据 7 外部抽样。
- **状态**：生效（G-019/G-020/G-021 均 `open`，关闭依据留空，待非同源复核）

---

### 批次 0056 — 2026-11-15 — 复核修复（第一批：程序闭合与裁定句改写）

- **性质**：按非同源复核（`/home/wgz/projects/skills/2026-11-14/pm-governance-review/verify-admission/REPORT.md`，sha256 `905cf234539cccb916f9096e3e137f12876e24b2fb9c1960a034157ac33aff06`，基线 `deaac46`）第一、二件修复。D4 未动、未放量、未碰判据 7 外部抽样。
- **第 5 条程序闭合**：`adr/0018-raw-material-admission-control.md` 的 `grounding_refs` 由“无”改为 7 个 `active` 来源条目，并新增“受影响对象”行——引用对象是 13.1 所保护原文的原作，不是决策的内容依据；同时说明 `GRAMMAR.md` 无规则受影响（本次只改判定与执行面）。条件 2 由此补齐。
- **13.5 裁定句改写**：删除“不构成实质性降低”的回避性表述，改为“承认降低、显式接受、列明补偿控制”；列 6 项补偿控制（数据区 schema 与集合字段、本体区三项机械承接、散文区硬约束、外部指纹、人工评审、未命中不等于合规），并写明缺失即失效。13.5 增“唯一例外”句，限定本次裁定不构成先例。13.6 结尾“行形态检查继续执行”改为实际执行的五项检查。
- **T-145**：改为有承接方、有时点的交付项——外部指纹由维护方在 M4 来源收口前交付；人工评审由人类责任方在来源/知识/规则变更同批执行；干净克隆缺 `resources/` 时降级为“不执行”并显式声明，结论按 `assumption` 处理。
- **涉及文件**：`CONSTITUTION.md`、`adr/0018-raw-material-admission-control.md`、`TODO.md`、`CHANGELOG.md`。
- **状态**：生效（八项实现修复待批次 0057；台账处置待批次 0058）

---

### 批次 0057 — 2026-11-15 — 复核修复（第二批：八项实现修复）

- **性质**：按非同源复核 `verify-admission`（sha256 `905cf234539cccb916f9096e3e137f12876e24b2fb9c1960a034157ac33aff06`，基线 `deaac46`）第三件修复。D4 未动、未放量、未碰判据 7 外部抽样。
- **人工维护文件补 schema**：新增 `package-manifest`、`ontology-fixtures-manifest`、`pilot-artifact`、`pilot-id-map` 四份内容 schema；`pilot-contract.yaml` 改用 `pm-slot-contract.schema.json`（新增可选 `authoritative`、`evidence_forms` 与条目级 `grounding_ref`）。数据区由 18 个文件升至 22 个：10 个受内容 schema 约束、7 个 schema 自身、5 个生成器。
- **`knowledge-entry` 收紧**：`relations` 改为 41 键白名单并加 `maxProperties: 12`；`evidence` 加 `maxItems: 12` 与 `page` 下界 1；`claim_mapping` 加 `maxItems: 20`；`definitionStatus` 按 D8 落枚举（`defined`/`taxonomy-only`/`pending`/`disputed`/`blocked-external`）；`sourcePage` 加下界 1。顺带为检查器补 `$ref`、`propertyNames`、`maxProperties` 支持，并把 `maxProperties` 归入字段配额。
- **契约 schema 值级上限**：`pm-slot-contract` 全部字段补 `maxLength`、数组补 `maxItems`，新增 `x-prose-fields`（`assumption_refs[].statement` 与 `verification.alignment_criterion`），检查器相应支持 `a[].b` 形式的散文字段路径。
- **配额矛盾修正**：单条散文字段上限由 2500 改为 2800，与 `definition` 2000 + `provenance_note` 800 的 schema 上限一致；自测新增“合法 2800 不被误杀”正向例。
- **13.6 三项检查落地**：本体区新增 `RM-ONTO-PAGESEQ`（连续 12 个以上页码数字）与 `RM-ONTO-PROVENANCE`（页码无来源承接、来源无页码），头注释检查由 `.ttl` 扩到全部本体扩展名；13.6 结尾“行形态检查继续执行”已在批次 0056 改为实际检查项。
- **指纹重冻**：`spec/ACCESS_ZONES.md` 与 `contracts/schema/pm-slot-contract.schema.json` 纳入 `spec-pins`（现 11 区段）；`checker-pins` 17 个受保护对象重冻，basis 指向批次 0056–0057 的复核转录记录。归区表从此“插行换区”必须同批复核记录，否则 `check_spec_pins.py` 退出 1。
- **自测**：30 → 43 项，新增 13 项负例/正向例：300 KB 散文塞 `manifest.json`、5 万字符契约字段、5 万字符 `statement`、200 键 `relations`、100 条 `evidence`、100 条 `claim_mapping`、非法 `definitionStatus`、合法 2800 字符定义、归区表与契约 schema 的指纹存在性、页码序列、有来源无页码、非 `.ttl` 扩展名头注释。自测 43/43 通过。
- **全仓复跑**：143 个跟踪文件（D 22 / O 30 / P 72 / C 19 / 未归类 0），0 命中。
- **涉及文件**：`scripts/check_no_raw_material.py`、`scripts/check_spec_pins.py`、`scripts/checker-pins.json`、`scripts/spec-pins.json`、`scripts/README.md`、`spec/ACCESS_ZONES.md`、`contracts/schema/`（4 新增 + 2 修改）、`validation/reviews/2026-11-15-admission-r2-review.md`、`AGENTS.md`、`GLOSSARY.md`、`knowledge/glossary-usage.json`、`CHANGELOG.md`。
- **状态**：生效（台账处置待批次 0058）

---

### 批次 0058 — 2026-11-15 — 复核修复（第三批：台账处置与 basis 更正）

- **性质**：按非同源复核 `verify-admission`（sha256 `905cf234539cccb916f9096e3e137f12876e24b2fb9c1960a034157ac33aff06`，基线 `deaac46`）第四件修复，并更正批次 0057 的 `checker-pins` basis。D4 未动、未放量、未碰判据 7 外部抽样。
- **G-020 关闭**：状态 `closed`、出口 `accepted`，关闭依据为上述复核报告（路径 + sha256 + 基线 + §6），并登记三条备注：① 子模块不纳入是声明式排除，不是“已扫描无违规”；② 引入子模块须与 `spec/ACCESS_ZONES.md` 同批重新裁定；③ 现状 0 gitlink、无 `.gitmodules`。说明中注明该报告不构成 G-019/G-021 的关闭依据。
- **G-019 维持 `open`**：说明补记 r2 复核结论——“13/18 个数据区文件不受内容 schema 或字段配额约束”，以及批次 0056–0057 的修正（5 个文件补 schema、集合字段收紧、2800 配额、13.6 三项检查、归区表入指纹）；现数据区 22 个文件，10 受 schema、7 schema 自身、5 生成器。
- **G-021 改写**：把“可修的实现缺陷”（`relations` 键空间、`evidence`/`claim_mapping` 长度、2500/2800 矛盾）从已接受残余中剥离，注明批次 0057 已修；残余收窄为“改写、翻译、合理切块是否实质替代原作”，量级改为实测口径（每文件 10 × 2000 字符、单条跨字段可达 2800），不再用 15 × 390；D-7 承接方与时点指向 T-145。仍 `open`。
- **`checker-pins` basis 更正**：`--write --basis` 改为指向仓库外复核产物 + sha256 + 基线，不再指向仓库内转录件；`check_checker_pins.py` 同步收紧——`basis` 的复核产物必须位于仓库外、必须带 64 位 sha256 且与实际摘要一致，转录件只作索引。`validation/reviews/2026-11-15-admission-r2-review.md` 保留但明确标注“非权威、不构成依据”。
- **子模块排除机械化**：`check_no_raw_material.py` 对 gitlink、符号链接与缺失路径显式判 `RM-ZONE`，使 G-020 的“声明式排除”不再静默。
- **schema 补说明**：`knowledge-entry` 的 `entry_type`/`status` 明确为自由文本（不设枚举）。
- **全仓复跑**：143 个跟踪文件 0 命中，自测 43/43；`checker-pins` 17/17、`spec-pins` 11 区段、`check_gap_ledger --staged` 均通过。
- **涉及文件**：`GAP_LEDGER.md`、`TODO.md`、`adr/0018-raw-material-admission-control.md`、`scripts/check_no_raw_material.py`、`scripts/check_checker_pins.py`、`scripts/checker-pins.json`、`contracts/schema/knowledge-entry.schema.json`、`validation/reviews/2026-11-15-admission-r2-review.md`、`CHANGELOG.md`。
- **状态**：生效（G-019/G-021 待非同源复核）

---

### 批次 0059 — 2026-11-15 — 结构性修法（第一批：指纹自动发现与依据标准对齐）

- **性质**：按非同源复核 `verify-g019-r3`（sha256 `877047e8f825ad905f560fc27bd6b94dd19277edd80a6d44a0912cd6c707f0b0`，基线 `3664b64`）第五节 P0-3 与 P1-8 修复。D4 未动、未放量、未碰判据 7 外部抽样。
- **schema 自动发现**：`check_spec_pins.py` 不再依赖人工清单——运行时枚举 `contracts/schema/` 下全部文件，出现未登记文件即报错（文件路径 + “未登记为规格区段”），退出 1。`package-manifest`、`ontology-fixtures-manifest`、`pilot-artifact`、`pilot-id-map` 四份漏钉 schema 同批登记，区段由 11 增至 15。
- **依据标准对齐**：`check_spec_pins.py` 的 `basis` 与复核记录改按 `check_checker_pins.py` 同一标准校验——`复核产物：` 必须指向**仓库外**文件、`sha256：` 必须为 64 位且与产物实际摘要一致、必须含 `复核基线：`；仓库内转录件只作索引。`--write` 在区段新增或变更时强制 `--basis`，逐区段保存 basis（未变更项保留原值或标“初始登记”）。原“复核产物文件名出现在记录里”这一较弱条件删除。
- **负例**：`scripts/test_spec_pins.py` 由 5 例扩到 8 例——新增 SP06/SP06b（仓库内转录件当依据 → 阻断）、SP07（`contracts/schema/` 下未登记文件 → 阻断）。外部复核产物在系统临时目录生成，不写入仓库。8/8 通过。
- **指纹重冻**：`spec-pins` 15 区段；`checker-pins` 17 个受保护对象。两处 basis 均指向上述仓库外复核报告 + sha256 + 基线 `3664b64`。
- **全仓复跑**：143 个跟踪文件 0 命中；`checker-pins` 17/17；`spec-pins` 15/15；`test_spec_pins` 8/8。
- **涉及文件**：`scripts/check_spec_pins.py`、`scripts/test_spec_pins.py`、`scripts/spec-pins.json`、`scripts/checker-pins.json`、`scripts/README.md`、`CHANGELOG.md`。
- **状态**：生效（G-019/G-021 仍 `open`，待非同源复核）

---

### 批次 0060 — 2026-11-15 — 结构性修法（第二批：schema 完整性 lint 与按路径配额）

- **性质**：按非同源复核 `verify-g019-r3`（sha256 `877047e8f825ad905f560fc27bd6b94dd19277edd80a6d44a0912cd6c707f0b0`，基线 `3664b64`）第三节 P0-1、P0-2、P1 修复。D4 未动、未放量、未碰判据 7 外部抽样。
- **schema 完整性 lint**：新增 `RM-SCHEMA-LINT`，对 `contracts/schema/` 下全部 7 份 schema 强制——数组须有 `maxItems` 与 `items`、字符串须有 `maxLength`、对象须 `additionalProperties: false`（或受 `maxProperties` + `propertyNames` 约束的映射）；`enum`/`const` 视为有限值集，不重复要求长度。报错带文件与 JSON 指针。lint 同时校验 `x-prose-fields` 条目形状与 `x-prose-budget`。
- **关键字白名单与显式失败**：新增 `SUPPORTED_KEYWORDS` / `UNSUPPORTED_KEYWORDS`；白名单外的拼写（`mxLength`）与未实现的标准关键字（`patternProperties`、`prefixItems`、`dependentSchemas` 等）一律报错。`oneOf` 改为**恰好命中 1 个分支**，不再退化为 `anyOf`；`$ref` 带同级断言关键字被 lint 拒绝，运行时不静默丢弃。
- **配额按字段路径**：`x-prose-fields` 由字符串列表改为 `{"path", "maxChars"}`，逐路径计量；新增 `x-prose-budget` 作为单条所有散文字段总和的兜底。两道都保留，单文件 20 KiB 不变。路径语法新增 `map.*.field`。具体值：`knowledge-entry` 2000/800（预算 2800）、试点契约 3200/2400（预算 5600）、`pilot-id-map` 800/600/4800 + `rule_bindings.*.note` 3200（预算 9400）、`pilot-conflict` 800/2400（预算 3200）。
- **r3 硬缺陷**：`pilot-conflict` 的 `positions` 加 `maxItems: 40`、`recorded_fields` 加 `maxItems: 40`；四份漏钉 schema 已在批次 0059 由自动发现兜住；`pilot-id-map` 四处映射补 `propertyNames`；pattern-only 字符串补 `maxLength`（`package-manifest`、`pilot-artifact`、`pm-slot-contract`、`pilot-id-map`）。
- **正向例（上一轮误杀）**：自测固定 3 条假设 × 1400（合计 4200）与 12 条 `notes` 的 id-map（合计 6200）必须放行，且不再受整条求和影响。
- **负例**：`positions` 300×400、`recorded_fields` 200×120、`package-manifest` 削弱为 `additionalProperties: true`（lint 与数据文件 fail-closed 各一条）、三类缺上限、拼错关键字、未实现关键字、`$ref` 同级关键字、`oneOf` 排他。自测 43 → 55 项，55/55 通过。
- **文档同步**：`CONSTITUTION.md` 13.3 补偿控制第 1 项、`spec/ACCESS_ZONES.md` 第 3 节、`spec/RAW_MATERIAL_ADMISSION.md` §4.3、`scripts/README.md`、`GLOSSARY.md` T-D-014 同步为新语义；`spec/RAW_MATERIAL_ADMISSION.md` 中残留的“2500”修正为按 schema 声明。
- **指纹重冻**：`spec-pins` 15 区段（本次变更 8 个），`checker-pins` 17 个；basis 均指向上述仓库外复核报告 + sha256 + 基线 `3664b64`；新增 `validation/reviews/2026-11-15-admission-r3-structural.md` 作为**非权威索引**，不构成依据。
- **全仓复跑**：144 个跟踪文件 0 命中；自测 55/55；`checker-pins` 17/17；`spec-pins` 15/15；`test_spec_pins` 8/8；pre-commit 全绿。
- **涉及文件**：`scripts/check_no_raw_material.py`、`scripts/check_spec_pins.py`、7 份 `contracts/schema/*.schema.json`、`CONSTITUTION.md`、`spec/ACCESS_ZONES.md`、`spec/RAW_MATERIAL_ADMISSION.md`、`scripts/README.md`、`GLOSSARY.md`、`validation/reviews/2026-11-15-admission-r3-structural.md`、两份 pins JSON、`CHANGELOG.md`。
- **状态**：生效（G-019/G-021 仍 `open`，待非同源复核）

---

### 批次 0061 — 2026-11-15 — 结构性修法（第三批：本体页码与来源规则重写）

- **性质**：按非同源复核 `verify-g019-r3`（sha256 `877047e8f825ad905f560fc27bd6b94dd19277edd80a6d44a0912cd6c707f0b0`，基线 `3664b64`）第三节 P1 修复。D4 未动、未放量、未碰判据 7 外部抽样。
- **`RM-ONTO-PAGESEQ` 重写**：旧规则只认裸数字串，对真实的 299 行 `ex:pN pm:page N .` 三元组转储 0 命中。新规则三形态任一命中即阻断：连续 12 行以上页码三元组（`pm:page` / `pm:sourcePage` / `dcterms:sourcePage` / `foaf:page`）、12 个以上逗号分隔页码、12 个以上裸页码数字（保留兜底）。
- **`RM-ONTO-PROVENANCE` 重写**：旧规则只在“有页码无来源且文件头无 `source_id`”时触发，对来源与页码两项都缺的术语 0 命中。新规则按空行切块，对含定义谓词、页码定位或 `dcterms:source` 的块逐块核对：来源与页码必须由术语级字段或文件头 `source_id` / `source_pages` 之一交代；头注释写 `source_pages: n/a` 但正文含页码值 → 声明矛盾，阻断。
- **头注释补项**：`RM-ONTO-HEADER` 由两项（`self-authored`、`source_id`）增至三项（加 `source_pages:`），与 `CONSTITUTION.md` 13.6 第 5 项一致。5 份真实 TTL 补页码范围（artifacts `1-113`、processes `17-101`、tools `1-145`、shapes/vocab `n/a`）；25 份 `ontology/fixtures/*.ttl` 按各自实际页码补范围。
- **召回实测**（写入 `spec/ACCESS_ZONES.md` 第 6 节）：真实 TTL 5 文件、349 个页码值、501 个义务块，两条规则均 0 命中；299 行三元组转储、逗号页码表、裸数字串、“两项都缺”术语、`n/a` 声明矛盾均命中。旧版对同样输入 0 命中。
- **负例/正例**：自测 55 → 58 项——新增 `pageseq-triples`（299 行）、`provenance-both`（两项都缺）、`real-ttl-clean`（真实文件 0 命中）三条；58/58 通过。
- **指纹重冻**：`spec-pins` 15 区段（`spec/ACCESS_ZONES.md` 变更），`checker-pins` 17 个；basis 指向上述仓库外报告 + sha256 + 基线 `3664b64`；新增 `validation/reviews/2026-11-15-ontology-rules-r3.md` 作为**非权威索引**。
- **全仓复跑**：145 个跟踪文件 0 命中；自测 58/58；`checker-pins` 17/17；`spec-pins` 15/15；pre-commit 全绿。
- **涉及文件**：`scripts/check_no_raw_material.py`、5 份 `ontology/*.ttl`、25 份 `ontology/fixtures/*.ttl`、`spec/ACCESS_ZONES.md`、`scripts/README.md`、`validation/reviews/2026-11-15-ontology-rules-r3.md`、两份 pins JSON、`CHANGELOG.md`。
- **状态**：生效（G-019/G-021 仍 `open`，待非同源复核）

---

### 批次 0062 — 2026-11-15 — 结构性修法（第四批：台账按 r3 复核改写）

- **性质**：按非同源复核 `verify-g019-r3`（sha256 `877047e8f825ad905f560fc27bd6b94dd19277edd80a6d44a0912cd6c707f0b0`，基线 `3664b64`）改写 G-019/G-021 并同步台账。D4 未动、未放量、未碰判据 7 外部抽样。
- **G-021 按真实量级改写**：旧的“每份 10 × 2000 字符”改为按字段路径口径——`relations` 12 键 × 20 值 × 120 字符 = 28,800，`evidence` 12 条 × 6 字段 ≈ 9,000，`pilot-conflicts` 的 `positions` 修复前 300 × 400 = 120,000 / `recorded_fields` 200 × 120 = 24,000（批次 0060 加 `maxItems: 40` 后为 16,000 与 4,800），`pilot-id-map` 的 12 条 `notes` 与 `rule_bindings.*.note` 合计上限 9,400。三类字符量均计入**总量口径**，明确“通过检查只证明结构合规”。
- **G-019 补记落地**：说明补入批次 0059–0061 的结构性修法（schema 目录自动发现、`basis` 抬到检查器绑定同一标准、`RM-SCHEMA-LINT` 与关键字白名单、`oneOf` 排他、`$ref` 同级拒绝、按路径配额、`positions`/`recorded_fields` 加 `maxItems`、两条本体规则按真实 TTL 形态重写及召回统计），并写明自测 58 项覆盖 r3 全部攻击输入。维持 `open`。
- **G-020 不动**：三条关闭备注与关闭依据原文未改；仅确认本批改动未触及该条的声明式排除口径。
- **台账同步**：G-021 影响面由 `prose_fields` 改为 `x-prose-fields` / `x-prose-budget`；G-019 影响面补 `scripts/check_spec_pins.py` 与 `contracts/schema/` 全部 schema；核查记录表补批次 0052–0062 共九行。台账 21 条：`open` 4（G-017、G-018、G-019、G-021）/ `closed` 17。
- **涉及文件**：`GAP_LEDGER.md`、`TODO.md`、`CHANGELOG.md`。
- **状态**：生效（G-019/G-021 仍 `open`，待非同源复核）

---

### 批次 0063 — 2026-11-15 — 收紧 `source_pages: n/a` 的声明

- **性质**：按用户裁定，`source_pages: n/a` 不再是一个词即成立的豁免；声明 `n/a` 必须同时给出可机械核验的依据。基线 `11c5d92`。仅改本项，未动校验层（`validate()`、lint 与 schema 基线不变）。
- **判据**：新增头注释 `source_pages_basis:`。依据须非空、非占位符（`n/a`、`TBD`、`待补` 等）、含仓库内**真实存在**的 `adr/NNNN-*.md` 引用，并在 ADR 引用之外另有至少 8 个字符的自写理由。
- **规则分工**：缺 `source_pages_basis:` → `RM-ONTO-HEADER`；写了但为空串、占位符或 ADR 引用不存在 → `RM-ONTO-PROVENANCE`，且该 `n/a` 不再解除逐块页码义务。`n/a` 与正文页码值矛盾的旧判据保留，依据不能抵消矛盾。
- **存量补齐**：`ontology/pmbok8-vocab.ttl`、`ontology/pmbok8-shapes.ttl` 两份标 `n/a` 的 TTL 各补一行依据，引用 ADR-0010。
- **自测**：58 → 65 项。新增 7 项覆盖“只写 n/a 无依据”（`RM-ONTO-HEADER` + `RM-ONTO-PROVENANCE` 同时命中）、“依据为空串”、“占位符 `n/a` / `TBD`”、“指向不存在的 ADR”均阻断，附自写理由与仓库内 ADR 引用放行，`n/a` 与正文页码矛盾仍阻断。
- **涉及文件**：`scripts/check_no_raw_material.py`、`ontology/pmbok8-vocab.ttl`、`ontology/pmbok8-shapes.ttl`、`spec/ACCESS_ZONES.md`、`scripts/README.md`、`GAP_LEDGER.md`、`TODO.md`、`CHANGELOG.md`、`scripts/spec-pins.json`、`scripts/checker-pins.json`、`validation/reviews/2026-11-15-source-pages-na-basis.md`。
- **状态**：生效（G-019/G-021 仍 `open`）

---

### 批次 0064 — 2026-11-15 — 改用成熟 JSON Schema 实现（第一段：依赖与 ADR）

- **性质**：按用户裁定以成熟实现替换自写 `validate()` 子集。基线 `f049f28`。
- **ADR**：新增 `adr/0019-mature-json-schema-validator.md`（accepted）——记录放弃自写子集的理由、两个被否方案（继续扩充自写、改为代码校验函数）、例外范围（只覆盖校验语义，不覆盖数据与证据）与三档撤销条件（换成熟实现 / 限关键字自写 / 判无法评估）。
- **依赖与指纹**：固定 `jsonschema==4.26.0`；新增 `scripts/dependency-pins.json`，登记分发产物 wheel 的 sha256（`d489f15263b8d200f8387e64b4c3a75f06629559fb73deb8fdfb525f2dab50ce`）与安装树 `RECORD` 摘要（45 个文件）；新增 `scripts/check_dependency_pins.py` 核对版本、安装树与产物三重指纹，产物缺席只警告，依赖缺失退出 2（不降级为跳过）。负例 `scripts/test_dependency_pins.py` 9/9。
- **接线**：`spec/ACCESS_ZONES.md` §2 登记指纹文件；根 `README.md` 与 `scripts/README.md` 写安装与核对步骤；`.githooks/pre-commit` 增加依赖指纹与负例。
- **涉及文件**：`adr/0019-mature-json-schema-validator.md`、`scripts/dependency-pins.json`、`scripts/check_dependency_pins.py`、`scripts/test_dependency_pins.py`、`spec/ACCESS_ZONES.md`、`README.md`、`scripts/README.md`、`.githooks/pre-commit`、`TODO.md`、`CHANGELOG.md`、`scripts/spec-pins.json`、`scripts/checker-pins.json`。
- **状态**：第一段完成；第二段（接入与契约不变）与第三段（r4 验收）待做。G-019/G-021 仍 `open`。

---

### 批次 0065 — 2026-11-15 — 改用成熟 JSON Schema 实现（第二段：接入与契约不变）

- **性质**：按用户裁定把 `validate()` 交给 `jsonschema==4.26.0`，对外契约不变。
- **校验入口**：`validate()` 改为 `validator_for` + `check_schema` + `iter_errors`；返回仍是 `(keyword, pointer, message)`，`RM-FIELD`/`RM-SCHEMA` 分派、`required` 缺失键指针、`oneOf` 排他语义、`check_data` 行为与退出码保持。缺少依赖时抛 `SchemaDependencyError`，`main()` 预检打印“无法评估”并退出 2，不降级为跳过。
- **元 schema**：仓库级 lint、`schema-doc` 与数据校验三处均先过官方 Draft 2020-12 元 schema；schema 自身不合规即失败。
- **扩展关键字**：`x-prose-fields` 路径改由 `_resolve_prose_path` 按 schema 结构解析（`field`、`a.b`、`list[].field`、`map.*.field`），解析不到或终点非字符串/字符串数组即报 `RM-SCHEMA-LINT`；`x-prose-budget` 保留。
- **递归发现**：`lint_schema_files` 与 `check_spec_pins.discover_schema_files` 改为 `rglob`，子目录 schema 同样 lint、同样要求登记为规格区段；新增 SP08。
- **配额口径**：路径上限按出现值计量；`x-prose-budget` 上调至 schema 合法上限（`pm-slot-contract` 28,000、`pilot-conflict` 16,800、`pilot-id-map` 22,200）；单文件上限 20 KiB → 32 KiB；真实 schema 的枚举字符串补 `maxLength`（6 处）。
- **自测**：65 → 76 项。新增覆盖 r4 四类攻击面、官方元 schema、依赖缺失 fail-closed、子目录 lint、20 条假设（28,000）与 8 条 `positions`（3,200）不被误杀。
- **涉及文件**：`scripts/check_no_raw_material.py`、`scripts/check_spec_pins.py`、`scripts/test_spec_pins.py`、`contracts/schema/*.schema.json`（6 份）、`spec/ACCESS_ZONES.md`、`spec/RAW_MATERIAL_ADMISSION.md`、`CONSTITUTION.md`（13.5 配额数值）、`scripts/README.md`、`TODO.md`、`CHANGELOG.md`、`scripts/spec-pins.json`、`scripts/checker-pins.json`。
- **状态**：第二段完成；第三段（r4 验收与 G-021 口径）同批收尾。G-019/G-021 仍 `open`。

---

### 批次 0066 — 2026-11-15 — 改用成熟 JSON Schema 实现（第三段：r4 攻击面验收）

- **性质**：用 r4 复核报告（`/home/wgz/projects/skills/2026-11-14/pm-governance-review/verify-g019-r4/REPORT.md`，sha256 `47b0be71a05d726a690278f2075efb13ed54ee79582176a373e8fb6dd7f74fbb`）逐类验收，并改写 G-021 口径。
- **四类缺陷复现与消除**：`items: true` / 元组 `items` → lint 拒绝非对象 `items`；`enum`/`const` 跳过 `maxLength` → 去掉豁免，同级断言必须同时成立；`x-prose-fields` 路径拼错 → 结构解析失败即报错；`contracts/schema/sub/` → 递归发现后同样 lint（`T-NRM-12[recursive-subdir]`）与钉扎（SP08）。
- **自测**：76 项全部通过（新增 `T-NRM-12` 11 项），原有 65 项保留。
- **G-021**：删除“`relations`/`evidence`/`positions` 均计入总量口径”的错误表述；按 r4 实测改写容量差额（knowledge-entry 45,136 − 2,800 = 42,336；pm-slot-contract 69,060 − 28,000 = 41,060；pilot-conflict 27,240 − 16,800 = 10,440；pilot-id-map 329,910 − 22,200 = 307,710；pilot-artifact 82,165；fixtures manifest 40,800；package-manifest 791），逐条列明 8 条未登记通道，并给出反向误杀（20 条假设合计 28,000、8 条 `positions` 合计 3,200）的处置。维持 `open`，待复核确认后再谈 `accepted`。
- **G-019**：补记 0064–0066 落地（成熟实现、元 schema、递归、严格路径、依赖指纹），维持 `open`。G-020 未改动。
- **涉及文件**：`GAP_LEDGER.md`、`scripts/check_no_raw_material.py`、`validation/reviews/2026-11-15-jsonschema-dependency.md`、`adr/0019-mature-json-schema-validator.md`、`TODO.md`、`CHANGELOG.md`、`scripts/spec-pins.json`、`scripts/checker-pins.json`。
- **状态**：三段完成；G-019/G-021 仍 `open`。

---

### 批次 0067 — 2026-11-15 — 让分发产物核对真正执行（DP-ARTIFACT 语义收口）

- **性质**：修正“自报三重核对、实际只跑两重”的缺陷。此前 pip 缓存找不到 wheel，产物核对降级为 `DP-ARTIFACT` 警告，登记的 sha256 从未被验证——与“声明了但不生效”同类。
- **产物落地**：`jsonschema==4.26.0` 的 wheel 取自 PyPI，放在仓库外持久路径 `~/.local/share/pm-governance/wheels/`（不提交进 git），实测 sha256 与登记值 `d489f15263b8d200f8387e64b4c3a75f06629559fb73deb8fdfb525f2dab50ce` 一致。
- **语义收口**：`DP-ARTIFACT` 从“警告”改为“无法评估”——产物缺失即退出 2，并在消息中给出下载命令与默认目录；版本、安装树、产物三重全部强制。`JSONSCHEMA_WHEEL` / `--artifact` 保留为覆盖。输出与文档统一为“缺失 = 未评估，不是通过”。
- **文档**：根 `README.md`、`scripts/README.md`、`adr/0019-mature-json-schema-validator.md` 写明 wheel 路径、获取命令与第三重不生效时的退档口径（不得保留只报警的检查）。
- **负例**：`test_dependency_pins.py` 9 → 10 项；DP-T03 改为“产物缺席按无法评估阻断”，新增 DP-T10 验证默认读取持久目录。
- **复跑**：`check_dependency_pins.py` 输出“分发产物 sha256 核对 1 个”，全套检查器与 pre-commit 全绿。
- **涉及文件**：`scripts/check_dependency_pins.py`、`scripts/test_dependency_pins.py`、`README.md`、`scripts/README.md`、`adr/0019-mature-json-schema-validator.md`、`spec/ACCESS_ZONES.md`、`CHANGELOG.md`、`scripts/checker-pins.json`、`scripts/spec-pins.json`。

---

### 批次 0068 — 2026-11-15 — r5 复判：逐文件核对、契约指针恢复、可诊断失败与威胁模型收口

- **依据**：r5 复判报告 `/home/wgz/projects/skills/2026-11-14/pm-governance-review/verify-g019-r5/REPORT.md`（sha256 `5373a537d05870dcf4f52756bf7e0012bc0128879e22df92cb85d86007258108`，基线 `3d7211c`）。用户已定“收紧威胁模型 + 修可机械修的部分”。
- **依赖核对（G-019 关闭条件 1）**：安装树不再只对 `RECORD` 文本排序取摘要，改为按 wheel 内 `RECORD` **逐文件重算 urlsafe-base64 内容哈希**并核对大小，且断言 `jsonschema.__file__` 落在分发目录内（`DP-IMPORT`）。影子包 / `PYTHONPATH`、`sitecustomize`、改 `validators.py` 保留原 `RECORD`、同名假 wheel 四类情形全部阻断。`test_dependency_pins.py` 10 → 13 项。
- **输出契约（条件 2）**：`additionalProperties` 指针恢复 `$.x` / `$.a.x`，`propertyNames` 恢复 `$.m.<键>`；口径统一为“指针由本仓库恢复、消息文本取自库的英文诊断（`oneOf` 另加中文前缀）”，ADR-0019 与 `README.md`、`scripts/README.md` 同步，不再声称逐字中文消息。
- **诊断化（条件 3）**：缺失本地 `$ref` 不再抛未捕获 `_WrappedReferencingError`，转 `RM-SCHEMA`“引用无法解析”；`validate()` 兜底捕获 `referencing` 模块异常。
- **语义风险（二）**：`RM-SCHEMA-LINT` 拒绝 `pattern` 嵌套量词与超过 512 字符（灾难性回溯）、schema 嵌套超过 64 层；`lint_schema_doc`、`_validator_for`、`validate()` 捕获 `RecursionError`，输出带 reason code 与文件/指针的诊断失败，不崩溃。结构性 heuristic 之外仍可能漏检的指数型 alternation 不在静默之列——已写入 ADR 负面项。
- **威胁模型（三）**：ADR-0019 删去“替换可被发现”的安全暗示，改为“能发现误装与非恶意不一致，不构成对有权写本机 Python 环境者的防护”；`PYTHONPATH` 注入、`sitecustomize`、直接改 `site-packages` 明确移出威胁模型，与 ADR-0015 同一信任模型。新立 G-022 承接，未并入 G-019。
- **台账（四、五）**：G-021 修正“`positions[].stance` 只有 2,400 预算”为“单值路径上限 2,400，16,800 才是单条总和预算”，按 3.6.4 补理由、批准依据、承接方与时点，以 r5 报告为关闭依据，改 `closed` / `accepted`；G-022 同批 `closed` / `accepted`（成因、影响、承接方与 ADR-0015 外置方向）；G-019 补本轮修复与残留、维持 `open`；G-020 未改。台账 22 条：`open` 3 / `closed` 19。
- **自测（六）**：`check_no_raw_material.py --self-test` 76 → 82 项（缺失 `$ref`、灾难性 `pattern`、深嵌套、`sitecustomize`、`additionalProperties` 指针、`propertyNames` 指针）；依赖负例 13 项。
- **涉及文件**：`scripts/check_dependency_pins.py`、`scripts/test_dependency_pins.py`、`scripts/check_no_raw_material.py`、`adr/0019-mature-json-schema-validator.md`、`README.md`、`scripts/README.md`、`GAP_LEDGER.md`、`CHANGELOG.md`、`validation/reviews/2026-11-15-jsonschema-dependency.md`、`scripts/checker-pins.json`。

---

### 批次 0069 — 2026-11-15 — r6 复判：撤掉 `pattern` 启发式、退出码与替换范围口径对齐

- **依据**：r6 复判报告 `/home/wgz/projects/skills/2026-11-14/pm-governance-review/verify-g019-r6/REPORT.md`（sha256 `1db2586e…6bd1db`，基线 `bafcb04`）。
- **撤掉 `pattern` 嵌套量词启发式**：schema 是仓库自写的可信资产、不是外部输入，正则回溯不在威胁模型内；`RM-SCHEMA-LINT` 只保留 512 字符上限。ADR-0019 威胁模型一节写明该风险不属于威胁模型成员及理由，不再保留“已用启发式覆盖”的说法。实测原启发式误拒 4 个合法常见写法（官方 semver 正则 179 字符、dotted-id、dotted-version、list-of-pairs，均由 `(?:\.\w+)*` 类“分隔符 + 段 + 重复”触发），又漏拒 `^(a|aa)+$`；撤除后 5 个写法全部放行。
- **自测改写**：删除依赖启发式的负例，新增“常见写法全部放行”与“只按 512 字符上限拒绝超长 `pattern`”，82 → 83 项，不留空壳。
- **退出码表述对齐**：`scripts/README.md` 原称运行时探测失败“退出 2”，实测为逐文件 24 条 `RM-SCHEMA`/`RM-SCHEMA-LINT` 后退出 1，只有 `jsonschema` 导入失败才退 2；ADR-0019“不改变失败方向”同步改写为分档表述。
- **替换范围表述对齐**：`sitecustomize` 只替换 `validator_for`、保留 `Draft202012Validator` 时不阻断，属 G-022 声明的信任边界（有权写本机 Python 环境者的针对性替换）。更正批次 0068“`sitecustomize` 全部阻断”的表述：被阻断的是空实现/整体替换与同名假 wheel。
- **台账**：G-019 说明改“非针对性替换均阻断”，补记 r6 实测与“剩余项只有三处口径对齐、本轮已全部完成”，维持 `open`；G-021、G-022 未动；G-020 未改。台账 22 条：`open` 3 / `closed` 19。
- **涉及文件**：`scripts/check_no_raw_material.py`、`adr/0019-mature-json-schema-validator.md`、`scripts/README.md`、`GAP_LEDGER.md`、`CHANGELOG.md`、`validation/reviews/2026-11-15-jsonschema-dependency.md`、`scripts/checker-pins.json`。

---

### 批次 0070 — 2026-11-15 — r7 复判：退出码文档补同一情形，G-019 关闭

- **依据**：r7 复判报告 `/home/wgz/projects/skills/2026-11-14/pm-governance-review/verify-g019-r7/REPORT.md`（sha256 `65e319da5b5e3a511b5d8dbf6b3f45f1ddbc9f86e8a4a86c17b4121cea20dacb`，基线 `7300283`）。结论：`pattern` 撤除干净、无回归，G-019 只差一处文档口径。
- **文档补同一情形（不改实现）**：`scripts/README.md`、ADR-0019 两处（wheel 段与“不改变失败方向”）与 `scripts/check_dependency_pins.py` docstring 均写明“分发产物存在但不可读取 / 逐文件数据不可核对”按“无法评估”退出 2，且与指纹不符同时命中时按 2 处理。实测：同名 `not a wheel` 文件命中 `DP-ARTIFACT` sha256 不符且 `DP-TREE` 无逐文件数据，退出 2；可读但 sha 不符退 1。
- **台账**：G-019 说明改为“r6 三处已完成；r7 另有一处退出码文档缺口，已同批勘误”，并补记 r7 的 `pattern` 与退出码矩阵结论；按 3.6.6 以 r7 报告 §1 / §2 / §4 为依据，改 `closed` / `check-change`。G-021、G-022 未动；G-020 未改。台账 22 条：`open` 2（G-017、G-018）/ `closed` 20。
- **涉及文件**：`scripts/check_dependency_pins.py`、`adr/0019-mature-json-schema-validator.md`、`scripts/README.md`、`GAP_LEDGER.md`、`CHANGELOG.md`、`scripts/checker-pins.json`。

---

### 批次 0071 — 2026-11-15 — G-018：`actors[].type` 纳入封闭枚举归一化

- **依据**：`GAP_LEDGER.md` G-018（`open`，`representation-defect`，L1，关联 T-137）与用户 2026-11-15 指令；实施按台账建议出口 `check-change`，缺口状态不自行关闭。
- **规格**：`spec/CHECKER_INPUT_SCHEMA.md` §1.11 增列 `actors[].type`，写明必填性与三个出口——键缺失 → 子句级 `missing_input`；值为 `null` → 入口 `missing_input`（第 1.2 条）；非法值、大小写变体、空字符串 → 子句级 `undefined_enum_value`；归属 `G-A1#1` / `G-E1#1` / `G-E2#1`，其余 `check_id` 只做全局校验。§2 `actors[]` 行同步必填性，§3 三行补 `undefined_enum_value`，§4 新增 `actor_type` 具名枚举行。
- **原型**：`enum_results()` 对每个 `actors[]` 元素校验 `type`，结果以子句级形式与各 `check` 函数结果一并交给 `aggregate()`，不做入口短路（G-014 的教训）。`ROLE_MINIMAL_COMPLETENESS` 与 `AI_AUTONOMY_DELEGATION_AUDITABLE` 改为“仅对已知类型判 `accountable_not_human`”，避免未定义类型产生的 `fail` 盖掉 `cannot_evaluate`。`--enum-sweep` 4 → 5 项。
- **样例与覆盖**：新增 A.1.1-8（非法值）、A.1.1-9（大小写变体 `humanactor`）、A.1.1-10（空字符串）、A.1.5-5（缺失 `type` 键）、A.1.10-6（`type: null`），期望分别为 `cannot_evaluate/undefined_enum_value` 与 `cannot_evaluate/missing_input`；`coverage.json` 对应 5 条 `expected_failed_clauses` 指向 `G-A1#1` / `G-E1#1` / `G-E2#1`。A.1 样例 61 → 66，`validation/pinned/checker.py` 同步。
- **reason code**：无新增。复用 `missing_input`（缺失/`null`）与 `undefined_enum_value`（非法值），与 G-001/G-003/G-007 的既有口径一致。
- **台账**：G-018 维持 `open`，说明补本轮实现与负例，关闭依据留空，等非同源复核；核查记录追加批次 0071。台账 22 条：`open` 2（G-017、G-018）/ `closed` 20。
- **涉及文件**：`spec/CHECKER_INPUT_SCHEMA.md`、`spec/methods/deterministic-checker.md`、`validation/checker-prototype/checker.py`、`validation/checker-prototype/coverage.json`、`validation/pinned/checker.py`、`AGENTS.md`、`.githooks/pre-commit`、`GAP_LEDGER.md`、`CHANGELOG.md`、`validation/reviews/2026-11-15-g018-actor-type-enum.md`、`scripts/spec-pins.json`、`scripts/checker-pins.json`、`spec/GLOSSARY.md`（位置刷新）。

---

### 批次 0072 — 2026-11-15 — G-018 复核整改：非字符串 `type`、A.2 同步与次要项

- **依据**：G-018 复核报告（基线 `0b88547`，sha256 `4a72e5a1…59fb21`）判不可关闭，逐项整改；缺口状态仍为 `open`。
- **阻断项 1（崩溃）**：`enum_results()` 以 `isinstance(value, str)` 守卫，对象、数组、数字、布尔等非字符串 `type` 一律给子句级 `cannot_evaluate/undefined_enum_value`，不再抛 `TypeError`；`ROLE_MINIMAL_COMPLETENESS` 与 `AI_AUTONOMY_DELEGATION_AUDITABLE` 的 `accountable_not_human` 同样只在字符串类型下判定。新增对象型 A.1.1-11 与数组型 A.1.11-4。
- **阻断项 2（A.2 未同步）**：A.2 的 `G-A1#1`、`G-E1#1`、`G-E2#1` 原因码列补 `undefined_enum_value`；F 类 `actors[]` 归属 `G-F1#2` 并补同一原因码。A 表由 `check_three_table.py --write` 重建，`clause_of()` 对四个归属均返回正确子句 id。
- **次要项**：`failed_clauses()` 在必需顶层键缺失或为 `null` 时返回空集，不再抛 `KeyError`；覆盖矩阵 note 改为实际检查项（不核对 reason 归属），并写明 A.1.10-6 走生产 `evaluate()` 的入口归一化、其子句归属只用于取证。
- **计数**：A.1 样例 66 → 68，覆盖矩阵负例 47 → 49（新增 2 条负例：对象型 A.1.1-11、数组型 A.1.11-4）。
- **pins**：本批按裁定重冻，basis 指向 G-018 复核报告并显式标注“覆盖范围缺失：报告审查的是批次 0071，未审查本批修复，仅作指纹登记”。`check_dependency_pins.py` 的 r7 basis 未改。
- **涉及文件**：`spec/CHECKER_INPUT_SCHEMA.md`、`spec/methods/deterministic-checker.md`、`validation/checker-prototype/checker.py`、`validation/checker-prototype/coverage.json`、`validation/pinned/checker.py`、`AGENTS.md`、`.githooks/pre-commit`、`GAP_LEDGER.md`、`CHANGELOG.md`、`validation/reviews/2026-11-15-g018-actor-type-enum.md`、`scripts/spec-pins.json`、`scripts/checker-pins.json`、`spec/GLOSSARY.md`（位置刷新）。

---

### 批次 0073 — 2026-11-15 — G-018 r2 复判整改：`missing_input` 登记、撤回 `G-F1#2`、覆盖闸门语义变更

- **依据**：G-018 第二轮非同源复核报告（基线 `ea9b674`，`/home/wgz/projects/skills/2026-11-14/pm-governance-review/verify-g018-r2/REPORT.md`，sha256 `17f631140bc700bf5826a7468f6919e7fc7f65da56302aef9d152b7fd1c1232d`）判不可关闭；运行时行为已认可，本批只修表示层与归属。缺口状态仍为 `open`。
- **`missing_input` 登记**：A.2 的 `G-A1#1`、`G-E1#1`、`G-E2#1` 原因码列补 `missing_input`，子句条件写明 `actors[].type` 必填、键缺失按 §1.11 判 `missing_input`；schema §3 三行原因码列同步；A 表由 `check_three_table.py --write` 重建。`clause_of()` 对三个 `check_id` 的 `missing_input` 均返回对应子句，`PROJECT_CHARTER_EXISTENCE` 返回 `None`（无子句归属）。
- **撤回 `G-F1#2` 归属**：`PROJECT_CHARTER_EXISTENCE` 的子句语义是章程关联完整性，承接不了“任意 actor 类型合法”；实现对全部 `actors[]` 生效（含章程无关 actor、无执行阶段项目），与 A.2“关联的”不符。删除 `ACTOR_TYPE_CLAUSES` 中的 F1 项，A.2 该行、schema §3、§1.11 归属同步复原；F 类数组型样例 A.1.11-4 移入覆盖矩阵新增的 `global_normalization` 分区。不补 ADR：撤回即恢复原判定逻辑，不构成结构性变更。
- **覆盖闸门规则 6 语义变更**：从“每条样例必须被至少一个子句引用”改为“被子句或 `global_normalization` 分区之一引用”。新增生产路径 `evaluate_trace()` 取证（`evaluate()` 改为其薄包装），删除绕过入口归一化的 `failed_clauses()`；子句负例须 verdict/reason 与子句归属均命中声明，全局归一化样例声明 `expected_clause: null`；新增 `(reason, clause)` 登记检查，样例 reason 必须出现在 A.2 该子句原因码列。该变更只改验证工具、不改任何 `check_id` 判定逻辑，按方法 §9 不需要 ADR；已在 `scripts/README.md`、`TODO.md` T-137、覆盖矩阵说明中写明。
- **更正批次 0072 的记述**：F 类 `G-F1#2` 归属是本批自行扩展，既不属 r1 复核“阻断项 1”（对象/数组 `type` 崩溃），也不属“阻断项 2（A.2 未同步）”；该归属已按 r2 报告 §3.2 撤回。A.2 签收不再引用这两个说法。
- **计数**：A.1 样例 68 不变；覆盖矩阵子句 41、正例 43、负例 49 → 47、`global_normalization` 2、样例 68。`--enum-sweep` 仍 5 项。
- **pins**：`spec/CHECKER_INPUT_SCHEMA.md#4` 用 r2 报告重冻（basis 含 `非同源复核：`、`复核产物：`、`sha256：`、`复核基线：ea9b674`、`区段：spec/CHECKER_INPUT_SCHEMA.md#4`、`结论：认可（§4 actor_type 与实现一致）`）；其余本批改动区段保持“未审查本批”占位，待 r3 报告统一重冻，不预写结论词。`check_dependency_pins.py` 的 r7 basis 未改。
- **涉及文件**：`spec/CHECKER_INPUT_SCHEMA.md`、`spec/methods/deterministic-checker.md`、`validation/checker-prototype/checker.py`、`validation/checker-prototype/coverage.json`、`validation/pinned/checker.py`、`scripts/check_coverage_gate.py`、`scripts/test_coverage_gate.py`、`scripts/README.md`、`TODO.md`、`GAP_LEDGER.md`、`CHANGELOG.md`、`validation/reviews/2026-11-15-g018-actor-type-enum.md`、`scripts/spec-pins.json`、`scripts/checker-pins.json`、`AGENTS.md`、`.githooks/pre-commit`（如计数或说明需同步）。
- **状态**：G-018 维持 `open`，关闭依据留空，待 r3 非同源复核在修复提交上确认。

---

### 批次 0074 — 2026-11-15 — 修复过期钉扎测试并接入 pre-commit

- **背景**：`scripts/test_checker_pins.py` 在 `ea9b674` 上即失败——`valid_basis` 收紧为“复核产物必须在仓库外、`sha256` 与之一致、含 `复核基线：`”后，测试仍用仓库内 `validation/reviews/review.md` 且无 sha256。该测试从未接入 pre-commit，所以 pre-commit 一直全绿，属“声明了但不生效”。
- **修断言（不放宽实现）**：测试改为在临时仓库 `repo/` 之外创建复核产物 `review.md`，按其内容现算 sha256，并让 `VALID_BASIS` 同时包含 `非同源复核：`、`复核产物：<仓库外绝对路径>`、`sha256：<64hex>`、`复核基线：d8bf413`、`区段：`、`结论：认可`；CP01–CP07 七条恢复全部符合预期。
- **接入 pre-commit**：新增 `scripts/test_checker_pins.py` 与 `scripts/test_spec_pins.py` 两行，分别紧随 `check_checker_pins.py`、`check_spec_pins.py`；`scripts/test_dependency_pins.py` 原已接入，未动。此前 `test_checker_pins.py` 与 `test_spec_pins.py` 从未被钩子或 CI 执行（仓库无 CI 配置）。
- **文档**：`scripts/README.md` 新增“测试脚本与执行入口”一节，写明自批次 0074 起接入；并列出仍未接入的 `test_coverage_gate.py`、`test_check_table_mutations.py`，以及 `AGENTS.md` 要求提交前运行但未接入的 `validate_ontology.py --matrix`（均未在本批修改）。
- **pins**：`scripts/test_checker_pins.py`、`.githooks/pre-commit` 哈希按 `--write` 重冻，basis 标为“未审查本批（批次 0074）”，待后续非同源复核统一重冻。
- **验证**：`test_checker_pins.py` 7/7、`test_spec_pins.py` 9/9、`test_dependency_pins.py` 13/13；pre-commit 全套 rc=0。

---

### 批次 0075 — 2026-11-15 — G-018 关闭（r3）、pins 重冻与三项治理收紧

- **背景**：r3 非同源复核（产物 `/home/wgz/projects/skills/2026-11-14/pm-governance-review/verify-g018-r3/REPORT.md`，sha256 `2ce810…9602c6`，基线 `a9ff5bb`）判 G-018 可关闭，附两条 caveat：`global_normalization` 不限制无子句原因码集合；`G-A1#1`/`G-E2#1` 的 `missing_input` 无专用样例（分支由 A.1.5-5 间接守卫）。
- **关闭 G-018**：`GAP_LEDGER.md` 的 G-018 改 `status=closed`、处置出口 `check-change`，关闭依据按 3.6.6 写入 r3 报告路径/sha256/基线/章节与两条 caveat；说明列同步记录 caveat；核查矩阵三行移除 G-018，矩阵说明删去其锚定句；`TODO.md` T-137 改 `done`。
- **pins 重冻（10 条）**：`spec-pins.json` 的 `#A.1`、`#A.2`、`#3`、`coverage.json`，`checker-pins.json` 的 `pre-commit`、`checker.py`、`check_coverage_gate.py`、`test_coverage_gate.py`、`test_check_table_mutations.py`、`test_checker_pins.py`，basis 统一为 r3 模板（仓库外产物 + sha256 + 基线 + `区段：` + `结论：认可`）；`spec/CHECKER_INPUT_SCHEMA.md#4` 保持 r2 重冻不动。
- **A.2 签收**：`spec/methods/deterministic-checker.md` A.2 签收行改指 r3；子句表指纹保持 `b14854847668`（签收行不参与 `a2_block_fingerprint`）。
- **doc-only**：`adr/0014-validation-chain-self-attestation.md` §4 的 `expected_failed_clauses` 更正为 `expected_clause`；CHANGELOG/GAP_LEDGER 中的历史批次叙述不改写。
- **basis 默认校验**：`check_spec_pins.py` 与 `check_checker_pins.py` 在默认读取模式即校验 basis——`复核产物：` 必须是仓库外真实文件、`sha256：` 与实算一致、含 `复核基线：`、`区段：` 与所绑对象一致、结论词在允许集合内；`初始登记` 前缀表示无复核声明的历史登记项。新增负例 CP08–CP11 / SP09–SP12（只把 basis 改成“结论：认可”、sha256 改一字符、产物改仓库内文件、区段写错）。
- **pre-commit 接入**：`test_coverage_gate.py` 紧随 `check_coverage_gate.py`、`test_check_table_mutations.py` 紧随 `check_three_table.py`、`validate_ontology.py --matrix` 紧随 `test_dependency_pins.py`。自批次 0075 起三者由钩子执行。
- **本体依赖钉扎**：`dependency-pins.json` 扩展为 `jsonschema`、`rdflib==7.6.0`、`pyshacl==0.40.2`，沿用同一登记表与同一判定轴（版本、wheel sha256、按 RECORD 逐文件安装树）；`check_dependency_pins.py` 支持 `--artifact <包名>=<wheel>` 可重复；`validate_ontology.py --matrix` 缺依赖仍以退出码 2 报“无法评估”。新增负例 DP-T14–T16（缺依赖、版本不符、安装树被改）。
- **验证**：检查器全套、`test_coverage_gate.py`、`test_check_table_mutations.py`、`test_checker_pins.py` 11/11、`test_spec_pins.py` 13/13、`test_dependency_pins.py` 16/16；`--matrix` 单次耗时约 0.46s；pre-commit 全套 rc=0。

---

### 批次 0076 — 2026-11-15 — 按 0075 复核整改钉扎（待复核）

- **背景**：批次 0075 复核（基线 `20a5450`，报告 `/home/wgz/projects/skills/2026-11-14/pm-governance-review/verify-pins-0075/REPORT.md`，sha256 `77149b…1582`）判不可接受，指出 `初始登记：` 前缀短路、结论词子串命中、区段可重复/带后缀、基线只验形状、历史 basis 名实不符、`§1.11` 未钉扎。
- **收口短路**：`check_spec_pins.py`/`check_checker_pins.py` 删除 `startswith("初始登记：")` 放行，改为代码内冻结的 `UNREVIEWED_KEYS` 白名单（spec 3 项、checker 13 项），且**不做任何前缀判定**：历史基文必须逐字相等，本批改动必须是结构化 `待复核：批次 NNNN …；无复核声明，不构成认可`。`--write` 不接受冻结的历史基文（旧状态不是新授权），只接受合格复核记录或结构化待复核；`valid_review()` 使用 `allow_unreviewed=False` 的严格版，复核记录永不接受该状态。
- **结论词与区段**：结论词改为精确匹配 `结论：(实质收敛|认可|通过)` 并要求后接边界，`不予/未/无法` 前缀直接拒绝；`区段：` 必须精确等于所绑 key 且只出现一次（重复或 `.bak` 后缀均阻断）。
- **基线存在性**：`复核基线：` 除形状外增加 `git cat-file -e <sha>^{commit}` 校验，`deadbeef` 这类不存在的基线阻断。
- **历史 basis 改写**：六条历史项（`check_anchors`、`check_gap_ledger`、`check_glossary_usage`、`check_ledger_landings`、`check_state`、`check_three_table`）改为显式 `无复核声明：历史指针——…；非权威，不构成认可`，删除 `结论：认可` 字样，并把仓内路径标为“历史指针（仓内转录件）”而非 `复核产物：`。
- **新增钉扎**：`spec/CHECKER_INPUT_SCHEMA.md#1.11`（封闭枚举全局归一化）纳入 `spec-pins.json`，规格区段 15 → 16。
- **负例**：`test_checker_pins.py` 11 → 17 条（CP12–CP17：假结论词、重复/带后缀区段、不存在的基线、非白名单 `初始登记：`、白名单对象用同一前缀 `--write`、用冻结旧状态覆盖新改动）；`test_spec_pins.py` 13 → 18 条（SP13–SP17 同构）。
- **待复核**：本批改动的 7 个脚本（含两个 pins 检查器与两个测试）在 `checker-pins.json` 中登记为 `待复核：批次 0076 …；无复核声明，不构成认可`；`TODO.md` 新增 T-138（`open`）。需另起一轮非同源复核作为放量前的钉扎基础；规则未变，不新增 ADR。
- **验证**：`test_checker_pins.py` 17/17、`test_spec_pins.py` 18/18；攻击 1（`check_state.py` 加一行 + `--write --basis "初始登记：任意未复核改动"`）rc=2，攻击 1b（手改同一 basis 后默认运行）rc=1，攻击 2（改 A.1 + 更新指纹 + 仓内假复核记录）rc=1；pre-commit 全套 rc=0。

---

### 批次 0077 — 2026-11-15 — 目标层新增 D6「技能自足运行」

- **涉及文件**：`ROADMAP.md`、`TODO.md`、`CHANGELOG.md`
- **变更摘要**：按用户裁定，把“agent 挂上本技能即可完成各类项目管理任务，而不依赖背后超大规模参数模型”正式写入目标体系，编号 **D6**。目标陈述按原话记录（技能本身承担流程、口径、分解与校验），未弱化为“降低依赖”。
- **出口**：留显式占位“出口待定：需人类责任方裁定基准模型与达标判据”；不编造数字，不以检查器通过率代替；D1–D5 只验证产物内部一致性，不构成 D6 的证据。
- **受影响的既有里程碑**（待用户裁定出口时一并处置）：M3（309 条自写定义，T-126）、M4（来源落点与 `grounding_ref` 粒度）、M3/M4 内容工作（T-138 试点、T-139 字段语义统一）、技能运行期形态（`CM-DET-CHECKER` 的 `human-fallback`）。
- **`CONSTITUTION.md`**：不新增条款。D6 属目标层而非约束层，`CONSTITUTION.md` 登记的是对产物的禁令与准入；出口未定前写成条款会产生无法机械判定的强制项。理由同时写入 `ROADMAP.md` 的 D6 说明。
- **跟踪**：`TODO.md` 新增 T-147（M7，`open`，出口待定）。
- **关联 ADR**：无（目标层记录，不改任何规则语义）

---

### 批次 0078 — 2026-11-15 — D6 需求与设计重审提案（待裁定）

- **涉及文件**：新建 `spec/D6_REBASELINE_PROPOSAL.md`；修改 `TODO.md`（新增 T-148）；修改 `CHANGELOG.md`。
- **变更摘要**：承接批次 0077 的 D6，对全项目做需求与整体设计重审，产出可单独评审的提案：需求层（G0-a/b/c/d 拆分、5 类使用者场景、验收三要件 V1–V3、明确不做、9 条"目标实为方法"、8 条目标冲突）、42 项原子能力五档分解（11 M / 18 M+J / 4 M+J+H / 6 M+H / 3 J+H）、五层架构（新增 L1 运行契约层，含任务契约/工件契约/签字契约与 6 算子闭集）、既有资产逐项定位、R0–R6 可判真假出口、18 项资产处置与代价、9 条待裁决策。
- **核心结论**：现行设计的可执行产物是"项目管理产物的合规检查器"，缺少任务目录、工序、工件 schema、模板整层；D6 原话应改写为"技能把可机械部分做到极致、判断部分显式外置"；`pmbok8:` 本体在运行期被引用 0 次，309 条定义/92 类/24 条 SHACL 建议标 `dormant`；D6 因缺基准模型、任务集、判据而处于**未验收**。
- **不改动的文件**：`CONSTITUTION.md`、`ROADMAP.md`、`CHARTER.md`、`GRAMMAR.md` 及任何既有规范正文。提案第 10 节只列修订建议，不执行。
- **性质**：提案，不产生约束；裁定后若改规范正文另走 ADR。
- **关联 ADR**：无（提案层，无规则语义变化）。

---

### 批次 0079 — 2026-11-15 — 钉扎体系"甲方案"整改：取消自我声明通道

- **涉及文件**：`scripts/check_checker_pins.py`、`scripts/check_spec_pins.py`、`scripts/check_state.py`、`scripts/test_checker_pins.py`、`scripts/test_spec_pins.py`、`scripts/no-review-declarations.json`（新建）、`scripts/checker-pins.json`、`scripts/spec-pins.json`、`scripts/README.md`、`AGENTS.md`、`TODO.md`、`CHANGELOG.md`。
- **变更摘要**：按用户裁定（甲方案），取消钉扎体系的自我声明通道，把例外改走 `AGENTS.md` 3.5 既有的 `--no-verify` 留痕机制。
  1. **取消"待复核"通道**：`--write --basis` 只接受两类输入——五要素齐全的非同源复核记录，或固定字面量 `无复核声明（不构成认可，不放行）`。后者可如实登记但**永不放行**（默认模式 rc=1），只能 `--no-verify`。删除 `UNREVIEWED_KEYS` 白名单与全部"待复核：批次 NNNN"形态；任何自由文本一律 rc=2。
  2. **例外改走 3.5**：新增 `AGENTS.md` 3.5.3（钉扎面未复核例外）与 3.5.2 的钉扎面撤除条件（到期未补复核即冻结通道）；`Hook-Bypass` 新增 `pin-review-debt` 取值与 `Hook-Bypass-Items`，`check_state.py` 机械核对 `Items` 中每个 `T-xxx` 在 `TODO.md` 存在且未关闭。复用既有 trailer 机制，未另造登记体系。
  3. **白名单表进入受保护范围**：异常清单移出到 `scripts/no-review-declarations.json`，并纳入 `checker-pins.json`；改表与改检查器同等受约束，两个 pins 检查器交叉校验登记项（须为受保护对象、字段齐全、已有复核却仍登记即报错）。
  4. **补无痕面**：`spec/CHECKER_INPUT_SCHEMA.md` 由 §1.11/§2bis/§3/§4 四段合并为**整文件**钉扎（spec 区段 16 → 13）；检查器覆盖面由 `scripts/{check_,test_,validate_}*.py` 扩为**全仓 `.py`**（含未跟踪未忽略者，`PY_EXCLUDE` 为空），新 helper 默认受保护；结论词后只允许行尾或 `；`/`。`，`结论：认可（但实质上不予认可）` 被拒；`复核基线` 增加 `git merge-base --is-ancestor` 祖先校验，`git commit-tree` 造出的无关提交被拒。
- **收口结果**：21 个检查器对象中 15 个显式无复核、6 个保留真实 r3/r6 复核；spec 13 区段中 2 个无复核（`GRAMMAR.md`、schema 整文件）。此前接受自我声明的 13 个对象全部收口为"不构成认可、不放行"。
- **验证**：`test_checker_pins.py` 20/20、`test_spec_pins.py` 23/23；默认模式 `check_spec_pins.py` rc=1、`check_checker_pins.py` rc=1（预期内，本批未经复核）。
- **钩子绕过**：本批以 `git commit --no-verify` 提交；`Hook-Bypass: pin-review-debt`、`Hook-Bypass-Reason` 见提交信息，`Hook-Bypass-Items: T-149`。原因：本批改的正是钉扎检查器自身与受钉扎的 spec 区段，未经非同源复核，两个 pins 检查器必然 rc≠0。到期项登记于 `TODO.md` T-149 与 `scripts/no-review-declarations.json`（逐对象一条，未批量豁免）。
- **关联 ADR**：无（收紧既有机制，未变规则语义；`AGENTS.md` 属执行约定）

---

### 批次 0080 — 2026-11-15 — D6 九条裁定落文本；`AGENTS.md` §3.5 纳入钉扎

- **涉及文件**：`ROADMAP.md`、`TODO.md`、`AGENTS.md`、`scripts/check_spec_pins.py`、`scripts/spec-pins.json`、`scripts/no-review-declarations.json`、`scripts/README.md`、`CHANGELOG.md`；另含 `spec/D6_REBASELINE_PROPOSAL.md`（另一会话续写第 8 节的改动，本提交一并纳入，本会话未编辑）。
- **变更摘要**：用户对 D6 重审提案第 7 节九条作出裁定，本批只落文本与口径，不实现解释器、不写 7 项能力的规则。
  1. **7.1 分档口径**：D6 目标陈述改写为「26% 完全脱离模型 / 43% 受约束填槽 / 31% 显式外置并留痕」；`TODO.md` T-147 的完成判据同步；**出口仍标待定**，直到 R4 基准跑出结果。
  2. **7.2 基准模型**：验收要件必须写成「模型族 + 量化位宽 + 上下文长度」三要素，弱档与对照档各一组，每次大版本重测一次。
  3. **7.3 任务集**：公开案例改造；真实 ≥20 题、合成 ≤10 题。
  4. **7.4 阈值**：机械项 ≥90%、人评项 ≥70%、控制臂差值 ≥20 个百分点；**必须同时报错题清单**，不得只报通过率。
  5. **7.5 最小执行器**：纳入 6 个算子解释器（`fill_schema`/`compute`/`lookup`/`check`/`human_approve`/`render`）；两条边界——任务卡/工序卡/工件契约用 **JSON 不用 YAML**；最小形态只验收**过程正确性**，不含模型自动填槽闭环。工作量与前置按提案第 5 节 R1–R3 记入 T-151。
  6. **7.6 本体休眠**：309 条定义 / 92 类 / 24 条 SHACL 标 `dormant`，不删，保留重新接上的开关；休眠期间不计入运行期收益。M3 出口移出 `v0.9.0` 门槛。
  7. **7.7 维保降级**：缺口台账与全量钉扎降为维护期；**明文例外：影响运行期判定结果的缺口不得降级**，写入 `AGENTS.md` 3.6.2 / 3.6.5 与 ROADMAP D6 说明。
  8. **7.8 范围边界**：只做通用项目管理工件；领域判断、法律效力、多人协作执行明确不做（写入 `ROADMAP.md` 第 9 节）。
  9. **7.9 发布口径**：下一发布点改为 `v0.9.0`（M7 出口，口径明示 D6「未验收」）；`v1.0.0` 门槛保留并必须满足 D6 验收；**1.0 的含义是「证明过了」，发布说明文字不能替代测量结果**。
  10. **钉扎补面**：`AGENTS.md` §3.5（含 3.5.1–3.5.3 绕过通道与撤除条件）纳入 `spec-pins.json`，堵「改宽通道无需复核」。新增区段登记为无复核声明，并入 T-149，未以其他方式绕过。spec 区段 13 → 14。
- **新增 TODO**：T-150（D6 验收件）、T-151（最小执行器）、T-152（本体休眠）、T-153（维保降级与运行期例外）、T-154（发布口径 0.9.0）；T-147、T-149 同步更新。
- **验证**：`test_checker_pins.py` 20/20、`test_spec_pins.py` 23/23；`check_checker_pins.py` rc=1（15 个无复核对象）、`check_spec_pins.py` rc=1（3 个无复核区段，含新增的 `AGENTS.md#3.5`），均为预期。
- **钩子绕过**：`Hook-Bypass: pin-review-debt`、`Hook-Bypass-Items: T-149`（新增 `AGENTS.md#3.5` 无复核项与检查器哈希刷新，仍 rc≠0）。
- **关联 ADR**：无（本批为口径落地；7.6/7.7 的机制变更按其自身条目走 ADR，见 T-152/T-153）
---

### 批次 0081 — 2026-11-15 — 可配置元规则；EVM 五条来源入表；案例素材处置 ADR

- **涉及文件**：`AGENTS.md`、`ROADMAP.md`、`TODO.md`、`SOURCE_LEDGER.md`、`adr/0020-case-material-handling.md`（新建）、`CHANGELOG.md`。
- **变更摘要**：
  1. **可配置优先（新元规则）**：`AGENTS.md` 新增 §1bis，顺序固定为“先判可配置性 → 再定归属（运行契约层，挂载时与项目用户约定）→ 只有确实不可配置才请人裁定”。偏差按科目分档、状态采样按里程碑计划进度周期的分数（1/2、1/3、1/5）或自然日/周/月/小时等一律为配置项；**不得写成技能常量、不设默认值**；未配置即 `cannot_evaluate`，不得回落为通过；跨配置不得比较，结果须带配置快照指纹。`ROADMAP.md` D6 验收要件新增第 5 条并把阈值改为“配置项”，`TODO.md` T-150 改为“配置随任务集记录、双臂锁同一配置快照”，不再写死阈值数字。
  2. **EVM 来源登记**：`SOURCE_LEDGER.md` 新增 `GAO-20-195G`、`NASA-NTRS-20200000301`、`NASA-NTRS-20180001499`、`DOE-G-413.3-10A`、`AACE-RP-82R-13` 五条，均标“仅章节级可用”、`verification_method: authority_page`、`claim_mapping` 暂空、`compilation_landing: pending:T-151`。并写明三条使用条件（以章节为对象；一项能力只固定一个主源、EAC 三法不得跨源混用；`provenance_note` 记录 EIA-748 准则映射并声明原文未核验）与新旧指标名差异（BCWP/BCWS/ACWP ↔ EV/PV/AC）。
  3. **案例素材处置**：新增 ADR-0020——素材**不入**登记表，放 `validation/cases/` 并附 MANIFEST（来源、许可、日期、改造说明）；只有由案例抽象出的评分判据入表；解释第 2.3 条“本地副本应入表”不适用于数据素材，并说明“另立类别”与“逐份挂 pending”两条替代路径为何否决。**宪法正文未改**。
- **新增 TODO**：T-155（EVM 规则与落点）、T-156（案例素材库与 MANIFEST）；T-147、T-150 判据同步。
- **验证**：全套检查器复跑见提交信息；`check_checker_pins.py` / `check_spec_pins.py` 仍因既有 15 + 3 个无复核对象 rc=1（T-149），本批未新增钉扎对象。
- **钩子绕过**：`Hook-Bypass: pin-review-debt`、`Hook-Bypass-Items: T-149`（沿用既有到期项，本批未新增无复核登记）。
- **关联 ADR**：ADR-0020
---

### 批次 0082 — 2026-11-15 — 缺口台账 RG 节：8 条缺口按第 9 节改判为配置

- **涉及文件**：`GAP_LEDGER.md`、`TODO.md`（T-157）、`CHANGELOG.md`。
- **变更摘要**：以 `spec/D6_REBASELINE_PROPOSAL.md` 第 9 节（配置层设计）与 9.6 反向审查为基准，`GAP_LEDGER.md` 新增“需求缺口（RG）与配置改判”一节，逐条写明**被配置吸收的部分 / 仍是缺口的部分 / 剩余关闭出口 / 关联**：
  - **RG-10 偏差阈值**：全量改判 → CFG-01/02/03；剩余缺口是“数值该取多少无权威来源”，出口 `doc-only` 或非同源复核，**明确禁止以“已改为配置”关闭**。
  - **RG-09 状态采集**：部分 → CFG-04/05/06/07/08；数据字典本身与“缺数不得默认通过”仍为判据。
  - **RG-08 风险刻度、RG-07 成本科目表**：部分 → 配置项，但 9.2 未给出 CFG 编号，**不擅自扩号**，登记 T-157 待责任方指定编号。
  - **RG-05 关口证据**：`approver_role` 映射 → CFG-12；`must_see` 清单仍是判据。
  - **RG-04 口径判定规则**：阈值类 → CFG-01/02/03/13；定义、枚举、区间、优先级仍缺。
  - **RG-02 工件字段集**：命名与版本 → CFG-11；字段集与必填性仍是判据。
  - **RG-11 挣值口径**：计量规则 → CFG-13；公式、EAC 三法与术语别名仍是判据（T-155）。
  - **未改判的 8 条**（RG-01/03/06/12/13/14/15/16）：不满足 C2，保持原判。
- **关闭数**：**0**。16 条中 8 条改判（1 全量 + 7 部分），全部保持 `open`；“改判不等于解决”写入本节规则。
- **新增 TODO**：T-157（RG-08 / RG-07 的 CFG 编号补录与 schema 扩展）。
- **验证**：`check_no_raw_material` / `check_anchors` / `check_ledger_landings` / `check_three_table` / `check_coverage_gate` / `check_gap_ledger` / `check_dependency_pins` / `check_glossary_usage` / `check_state` 均 rc=0；`check_checker_pins` rc=1（15 个既有无复核对象）、`check_spec_pins` rc=1（3 个既有无复核区段），均为本批之前已登记的 T-149 债务，本批未新增钉扎对象。
- **钩子绕过**：`Hook-Bypass: pin-review-debt`、`Hook-Bypass-Items: T-149`（沿用既有到期项，本提交未新增钉扎对象）。
- **关联 ADR**：无（改判依据为已批准的提案第 9 节，非新治理决定）

---

### 批次 0083 — 2026-11-15 — 配置层 schema 落盘（CFG-01～CFG-13）与四类退出码

- **涉及文件**：
  - 新建：`contracts/schema/runtime-config.schema.json`、`contracts/schema/runtime-config-lock.schema.json`、`scripts/config_codes.py`
  - 修改：`spec/CHECKER_INPUT_SCHEMA.md`（新增第 7 节）、`AGENTS.md`（目录树与区段计数 14→16）、`scripts/README.md`（脚本清单与运行方式）、`TODO.md`（T-158）、`scripts/no-review-declarations.json`、`scripts/spec-pins.json`、`scripts/checker-pins.json`、`CHANGELOG.md`
- **变更摘要**：按第 9 节落配置层结构，**不实现求值**。
  1. **配置实例 schema**：13 项 CFG 全覆盖，键只能取 `CFG-01`～`CFG-13`（`propertyNames` + `additionalProperties: false`），故技能判据、验收参数、能力开关的键在本文件中结构上不可出现；每项以 `$comment` 登记 `cfg=/class=/defaultable=/absent=`，`--self-check` 机械核验。
  2. **默认值规则**：仅 CFG-10（舍入口径）、CFG-11（命名与版本）标 `defaultable=true`；CFG-01～09、CFG-13 无默认，缺失即 `cannot_evaluate`；CFG-12 无默认且 `absent=conservative_no_relaxation`（缺失只是不额外加关口，任务卡 mandatory gate 仍全量启用）。
  3. **四条安全边界**：B1 缺配置不得默认通过（无默认 + 退出码 3）；B2 人审关口不可删除（CFG-12 无删除表达）；B3 检查项不可关闭（schema 内无 enable/disable/skip/ignore/waive 类字段，`config_codes.py` 递归扫描并阻断）；B4 配置不改写工件必填字段集合（schema 只约束取值）。
  4. **配置摘要**：`config_digest`（`sha256:<64hex>`，规范化 JSON）、`item_digests`、`defaulted`、`schema_version` 落在 `runtime-config-lock.schema.json`，供“跨配置不可比”判定。
  5. **四类退出码**：`cannot_evaluate=3`、`config_invalid=2`、`config_incomplete=2`、`config_drift=1`，优先顺序 `config_invalid → config_incomplete → config_drift → cannot_evaluate`；写入 `spec/CHECKER_INPUT_SCHEMA.md` 第 7 节与 `config_codes.py`，检查器可按退出码分流。
- **边界遵守**：未改 `CONSTITUTION.md`、未改 `spec/D6_REBASELINE_PROPOSAL.md`、未动任何判定逻辑。
- **新增 TODO**：T-158（配置解释器与 9.5 的 A1–A6 工件契约接入，下一批）。
- **钉扎面变化**：新增 2 个规格区段（两份配置 schema，`contracts/schema/` 自动发现）与 1 个受保护检查器对象（`config_codes.py`）。规格区段 14→16、检查器对象 21→22；无复核项规格 3→5、检查器 15→16，逐对象登记入 `scripts/no-review-declarations.json`，全部指向 T-149。
- **验证**：`config_codes.py --self-check` rc=0；四类场景实测 `ok=0`、`config_incomplete=2`、`cannot_evaluate=3`、`config_invalid=2`、`config_drift=1`；其余检查器结果见提交信息。
- **钩子绕过**：`Hook-Bypass: pin-review-debt`、`Hook-Bypass-Items: T-149`（新增 3 个无复核对象，均已登记）。
- **关联 ADR**：无（结构依据为已批准的提案第 9 节）
- **收尾补正（同一批第三个提交）**：pre-commit 复核发现两份新 schema 未在 `spec/ACCESS_ZONES.md` 第 2 节（数据区准入登记）登记，按 D-1 不应降级为文本扫描。补登记两行 `schema-doc` 后，`check_no_raw_material.py` 由 2 个错误回到 0。**代价如实记录**：该区段此前按 G-019 r4 有合格复核记录，本次改动超出原复核范围，`spec-pins.json` 的 basis 只能降为无复核声明（原复核记录仍在 git 历史 `441218d` 中），并已登记入 `scripts/no-review-declarations.json` 与 T-149；这是本次改动的真实治理成本，不以旧复核顶新内容。
