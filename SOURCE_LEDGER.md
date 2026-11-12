## 来源登记表

本表为封闭枚举：任何 `grounding_ref` 必须指向本表中的 `id`。

**登记规则**：见 `CONSTITUTION.md` 第 2 条。本表只登记**服务于编译目标的通用项目管理知识来源**；ADR 格式、规范性措辞等治理自身使用的文献不入本表（见 `adr/README.md` 与 `CONSTITUTION.md` 第 3 条）。

### 字段说明

| 字段 | 含义 |
|---|---|
| `id` | 稳定标识，永不复用 |
| `citation` | 完整引用 |
| `version` | 被引用的具体版本 |
| `local_path` | 本地副本路径（存在时填写，相对于仓库上级目录的 `resources/`） |
| `status` | `active` / `deprecated`（附被谁取代）/ `superseded` |
| `authority_tier` | `international_standard` / `national_standard` / `peer_reviewed` / `preprint` / `official_doc` |
| `verified_date` | 最近一次核验日期 |
| `verification_method` | `local_copy_check`（本地版本核对）/ `authority_page`（权威页面访问）/ `cross_reference`（交叉印证）/ `pending`（待核验） |
| `allowed_uses` | 允许的用途范围 |
| `claim_mapping` | 论断级映射：本条目支持 `GRAMMAR.md` 或 `knowledge/` 中的哪些具体规则/条目 |
| `compilation_landing` | 编译落点：`rule:<规则号>` / `knowledge:<术语>` / `method:<方法号>` / `check:<check_id>`；正文未取得时写 `pending:<TODO 编号>` |

---

### 条目表

#### ISO21502-2020

| 字段 | 内容 |
|---|---|
| `id` | `ISO21502-2020` |
| `citation` | ISO 21502:2020, *Project, programme and portfolio management — Guidance on project management*. International Organization for Standardization. |
| `version` | 2020 版 |
| `local_path` | `resources/pm/[ISO 21502_2020] Project, programme and portfolio management — Guidance on project management{ISO}(2020, ISO){108252832} libgen.li.pdf` |
| `status` | `active` |
| `authority_tier` | `international_standard` |
| `verified_date` | 2026-11-12 |
| `verification_method` | `local_copy_check`（本地 PDF 已获取）；**过程组/主题组矩阵尚未逐页核对** |
| `allowed_uses` | 项目定义、约束管理、过程组/主题组分类（**结构待核对**）、采购主题、时间主题、收尾过程 |
| `claim_mapping` | `GRAMMAR.md`：G-A1、G-A2、G-D1、G-D2、G-F3、G-F4；`knowledge/`：`Project`、`Constraint`、`Outcome` 条目定义 |
| `compilation_landing` | `rule:G-A1`；`rule:G-A2`；`rule:G-D1`；`rule:G-D2`；`rule:G-F3`；`rule:G-F4`；`knowledge:Project`；`knowledge:Constraint`；`knowledge:Outcome` |
| **核验状态** | **本地副本已获取**。标准存在性、版本与正文可访问性已确认；“五过程组 × 十主题组”矩阵在 2020 版中的具体形态**未核对**。该未核对项直接导致 G-B1、G-B2 处于 `pending_reanchor`（核对待办见 T-113）。 |

#### GB-T-37507-2025

| 字段 | 内容 |
|---|---|
| `id` | `GB-T-37507-2025` |
| `citation` | GB/T 37507—2025《项目、项目群和项目组合管理 项目管理指南》。中国国家标准化管理委员会。等同采用 ISO 21502:2020。 |
| `version` | 2025 版 |
| `local_path` | 无（本地未提供） |
| `status` | `active` |
| `authority_tier` | `national_standard` |
| `verified_date` | 2026-11-11 |
| `verification_method` | `cross_reference`（评审方提供的信息；本环境无法直接访问全国标准信息公共服务平台） |
| `allowed_uses` | 作为 `ISO21502-2020` 的**中文锚点**，在中文环境部署时优先引用；内容语义与 ISO 21502:2020 一致，不构成独立来源 |
| `claim_mapping` | 同 `ISO21502-2020`；本条目是语言锚点，不扩展 `claim_mapping` 范围 |
| `compilation_landing` | `rule:G-A1`；`rule:G-A2`；`rule:G-D1`；`rule:G-D2`；`rule:G-F3`；`rule:G-F4`（与 `ISO21502-2020` 同一批落点） |
| **核验状态** | **交叉印证**。评审反馈确认存在且等同采用 ISO 21502:2020；本环境未独立访问。登记时标注为 `cross_reference`。 |

#### PRINCE2-2023

| 字段 | 内容 |
|---|---|
| `id` | `PRINCE2-2023` |
| `citation` | AXELOS. *Managing Successful Projects with PRINCE2*, 7th edition. The Stationery Office, 2023. |
| `version` | 7th edition (2023) |
| `local_path` | `resources/pm/Managing Successful Projects with PRINCE2® -Edition 7（原版带水印） - PeopleCert - 7, 2023 - PEOPLECERT INTERNATIONAL LIMITED - isbn139789925344505.pdf`（官方水印版） |
| `status` | `active` |
| `authority_tier` | `official_doc`（方法论官方手册；非国际标准，但为广泛接受的权威实践框架） |
| `verified_date` | 2026-11-12 |
| `verification_method` | `local_copy_check`（本地官方水印版已获取） |
| `allowed_uses` | 七项原则（持续业务验证、从经验中学习、定义角色与职责、按阶段管理、例外管理、关注产品、根据环境裁剪）；角色模型（最终责任不可委托）；产品描述要求；裁剪原则 |
| `claim_mapping` | `GRAMMAR.md`：G-C1（关注产品）、G-E1（定义角色与职责、问责不可委托）、G-E2（同上）、G-F1（持续业务验证 + 定义角色与职责）、G-F2（关注产品 + 阶段收尾）、G-G1、G-G2、G-G3（根据环境裁剪）；`knowledge/`：`Accountable`、`Responsible`、`Deliverable` 条目定义 |
| `compilation_landing` | `rule:G-C1`；`rule:G-E1`；`rule:G-E2`；`rule:G-F1`；`rule:G-F2`；`rule:G-G1`；`rule:G-G2`；`rule:G-G3`；`knowledge:Accountable`；`knowledge:Responsible`；`knowledge:Deliverable` |
| **核验状态** | **本地副本已获取**。官方水印版可核对具体条款措辞；**逐条核对尚未执行**。G-F1、G-F2、G-G1–G3 的 `assumption` 状态与此直接相关。 |
| **非官方镜像排除** | `resources/pm/Managing Successful Projects with PRINCE2®（无水印） - Andy Murray - 7, 2023 - PeopleCert International Limited - isbn139789925344505.pdf` 为未经授权的水印移除版本，按 `CONSTITUTION.md` 第 2.3 条**不得**作为 `grounding_ref` 的依据；仅官方水印版可用于核对。 |

#### ProjectCO-2024

| 字段 | 内容 |
|---|---|
| `id` | `ProjectCO-2024` |
| `citation` | Olsina, L., Becker, P., & Papa, M. F. (2024). The Project Management Ontology called ProjectCO: Architectural Aspects, Concepts, and Usefulness. *CIbSE 2024*, pp. 61–75. |
| `version` | 2024 会议论文版 |
| `local_path` | `resources/pm/The Project Management Ontology called ProjectCO Architectural Aspects, Concepts, and Usefulness（原稿，位图插图）.pdf` |
| `status` | `active` |
| `authority_tier` | `peer_reviewed` |
| `verified_date` | 2026-11-12 |
| `verification_method` | `local_copy_check`（本地 PDF 已获取） |
| `allowed_uses` | 核心层领域无关概念：`Project`、`Actor`、`Commitment`、`Deliverable`、`Constraint`、`Outcome`、`Assertion`；核心概念的“cross-cutting, domain-independent”定位 |
| `claim_mapping` | `GRAMMAR.md`：G-A1、G-A2、G-D1、G-E1；`knowledge/`：`Project`、`Actor`、`Commitment`、`Deliverable`、`Constraint`、`Outcome` 条目定义 |
| `compilation_landing` | `rule:G-A1`；`rule:G-A2`；`rule:G-D1`；`rule:G-E1`；`knowledge:Project`；`knowledge:Actor`；`knowledge:Commitment`；`knowledge:Deliverable`；`knowledge:Constraint`；`knowledge:Outcome` |
| **核验状态** | **本地副本已获取**。会议与论文存在性确认；正文可核对。本表不引用“45 个核心术语”等未经核对的内部数字。G-A1 的四元组合取形式为技能自身贡献，不宣称是 ProjectCO 原文的表述。 |

#### ThingFO-2021

| 字段 | 内容 |
|---|---|
| `id` | `ThingFO-2021` |
| `citation` | Olsina, L. (2023). ThingFO v1.3's Terms, Properties, Relationships and Axioms — Foundational Ontology for Things. arXiv:2107.09129（v1.3）。 |
| `version` | v1.3（2023-12；本地副本） |
| `local_path` | `resources/pm/Thing Foundational Ontology ThingFO v1.3’s Terms, Properties, Relationships and Axioms - arXiv 2107.09129v2.pdf` |
| `status` | `active` |
| `authority_tier` | `preprint` |
| `verified_date` | 2026-11-12 |
| `verification_method` | `local_copy_check`（本地 v1.3 副本已获取） |
| `allowed_uses` | `Assertion` 作为“人类关于 Particulars 和 Universals 不同方面的陈述”的定义；断言的可区分性 |
| `claim_mapping` | `GRAMMAR.md`：G-C1、G-C2；`knowledge/`：`Assertion` 条目定义 |
| `compilation_landing` | `rule:G-C1`；`rule:G-C2`；`knowledge:Assertion`；`knowledge:Subject` |
| **核验状态** | **本地副本已获取**。`authority_tier` 仍为 `preprint`，在与其他 `peer_reviewed` 来源冲突时优先级较低。 |

#### PMBOK8-2025

| 字段 | 内容 |
|---|---|
| `id` | `PMBOK8-2025` |
| `citation` | Project Management Institute. *A Guide to the Project Management Body of Knowledge (PMBOK Guide)*, 8th Edition. PMI, 2025. |
| `version` | 8th Edition (2025-11) |
| `local_path` | `resources/pm/A Guide to the Project Management Body of Knowledge (PMBOK® - Project Management Institute PMI - 8, 2026 - isbn139781628258301.pdf`；`resources/pm/A Guide to the Project Management Body of Knowledge (PMBOK® - Project Management Institute Pmi - PMBOK® Guide, 8, 2026 - isbn139781628258295.epub` |
| `status` | `active` |
| `authority_tier` | `official_doc` |
| `verified_date` | 2026-11-12 |
| `verification_method` | `local_copy_check`（本地 PDF 与 EPUB 均已获取） |
| `allowed_uses` | **仅限原则层面的交叉验证**。用于检查本技能规则是否与广泛接受的项目管理原则相抵触；**不作为任何规则的直接锚定依据** |
| `claim_mapping` | 无直接规则映射。本条目是“一致性检查来源”，不是“规则锚定来源” |
| `compilation_landing` | `method:M-EST-01`；`method:M-DEC-01`；`method:M-RISK-01`；`method:M-EV-01`（仅作为方法条目的原则层交叉验证依据） |
| **核验状态** | **本地副本已获取**。第 7 版已于本决策（ADR-0005）删除；如需引用具体原则表述，以本版为准。 |

#### SPRINGER-PMBOK-2024

| 字段 | 内容 |
|---|---|
| `id` | `SPRINGER-PMBOK-2024` |
| `citation` | Silega, N., Lapshin, V. S., Rogozov, Y. I., Castro Aguilar, G. F., Martillo Alcívar, I., & Faggioni, K. M. (2024). A Formal Representation of Standards for Project Management: Case PMBOK. In P. Y. Piñero Pérez et al. (Eds.), *Studies in Computational Intelligence*, pp. 327–337. Springer. https://doi.org/10.1007/978-3-031-50495-2_13 |
| `version` | Springer 章节版（© 2024） |
| `local_path` | 无（正文未获取） |
| `status` | `active`（**仅元数据可用**） |
| `authority_tier` | `peer_reviewed` |
| `verified_date` | 2026-11-12 |
| `verification_method` | `authority_page`（Springer 章节页可访问：题名、作者与机构、摘要、参考文献、通讯作者）；**正文未获取（付费墙）**，已于 2026-11-12 向通讯作者请求全文 |
| `allowed_uses` | PMBOK 的 OWL 本体化表示与基于 reasoner 的一致性检查（**在正文取得并核对前，不得作为任何规则的锚定依据**） |
| `claim_mapping` | 无。当前仅登记“该工作存在且主题为 PMBOK 的形式化表示”，不映射任何规则 |
| `compilation_landing` | `pending:T-112`（正文未获取，暂无落点；落点补齐前不得被任何 `grounding_ref` 引用） |
| **核验状态** | **元数据核验，正文未获取**。摘要确认其构建了表示项目管理标准/指南的 OWL 本体；具体类、属性、公理与验证结果均未核对。 |

---

### 废止与重新锚定记录

| 记录 | 内容 |
|---|---|
| **G-B1、G-B2 的锚点撤回** | 原锚点 ISO 21500:2012 于 2021-03-16 撤回，由 ISO 21502:2020（指南）与 ISO 21500:2021（概述）取代。该来源条目已按 ADR-0005 删除，历史见 git。现状：`grounding_ref` 为 `ISO21502-2020`，状态 `pending_reanchor`，在重新锚定完成前降级为 `advisory`。 |
| **重新锚定待办** | 核对本地 `resources/pm/ISO 21502-2020.pdf` 是否保留“五过程组 × 十主题组”矩阵结构及其具体形态。核验完成后，G-B1、G-B2 升级为 `block` 或修订陈述。登记于 `TODO.md` T-113。 |
| **PMBOK 版本迁移** | 第 7 版条目已按 ADR-0005 删除；第 8 版以 `PMBOK8-2025` 入表，用途仍限于原则层交叉验证。 |

---

### 候选来源（未入表）

以下来源在讨论中被提及，但**未通过核验或不符合入表条件**，记录于此以防误用：

| 候选 | 未入表理由 |
|---|---|
| PMBOK 的 OWL 本体（Silega 等 2024 提出；早期讨论误记为“Szwed / 340 类”） | **有可靠来源但尚未获取**：Springer 章节页与摘要可查（见 `SPRINGER-PMBOK-2024`），正文未获取、已向通讯作者请求。“340 类”无出处，不得引用。 |
| “来源接地不能防止幻觉”的 zenodo 论文 | **已核实存在**：Jennifer Evans, *Source-Grounding Does Not Prevent Hallucinations: A Controlled Replication Study of Google NotebookLM*, Zenodo preprint, DOI `10.5281/zenodo.18039274`（2025-12-24）；同日另有标题略异的预印本 `10.5281/zenodo.18043672`。主题为 RAG 与幻觉机制，**不属于通用项目管理知识**，按 `CONSTITUTION.md` 第 2.6 条领域测试不入表。核查记录见 `ERRATA.md` E-012。 |
| 厂商博客、非官方镜像 PDF（含 `resources/pm/Managing Successful Projects with PRINCE2®（无水印） - Andy Murray - 7, 2023 - PeopleCert International Limited - isbn139789925344505.pdf`） | `CONSTITUTION.md` 第 2.3 条排除。 |

---

### 来源状态汇总

| 状态 | 条目 |
|---|---|
| `active`（本地副本已获取） | ISO21502-2020、PRINCE2-2023、ProjectCO-2024、ThingFO-2021、PMBOK8-2025 |
| `active`（仅权威页面/交叉印证） | GB-T-37507-2025、SPRINGER-PMBOK-2024 |
| 待核对项 | ISO 21502:2020 的过程组/主题组矩阵；PRINCE2-2023 的具体条款措辞；Spring 章节正文 |
| 候选（未入表） | OWL 本体（未获取）、zenodo 条目（已核实存在但领域不符）、厂商/非官方镜像（排除） |
