## 来源登记表

本表为封闭枚举：任何 `grounding_ref` 必须指向本表中的 `id`。

**登记规则**：见 `CONSTITUTION.md` 第 2 条。本表只登记**已核验**的来源；未核验的候选来源见文末“候选来源（未入表）”。

### 字段说明

| 字段 | 含义 |
|---|---|
| `id` | 稳定标识，永不复用 |
| `citation` | 完整引用 |
| `version` | 被引用的具体版本 |
| `status` | `active` / `deprecated`（附被谁取代）/ `superseded` |
| `authority_tier` | `international_standard` / `national_standard` / `peer_reviewed` / `preprint` / `official_doc` |
| `verified_date` | 最近一次核验日期 |
| `verification_method` | `local_copy_check`（本地版本核对）/ `authority_page`（权威页面访问）/ `cross_reference`（交叉印证）/ `pending`（待核验） |
| `allowed_uses` | 允许的用途范围 |
| `claim_mapping` | 论断级映射：本条目支持 `GRAMMAR.md` 或 `knowledge/` 中的哪些具体规则/条目 |

---

### 条目表

#### ISO21502-2020

| 字段 | 内容 |
|---|---|
| `id` | `ISO21502-2020` |
| `citation` | ISO 21502:2020, *Project, programme and portfolio management — Guidance on project management*. International Organization for Standardization. |
| `version` | 2020 版 |
| `status` | `active` |
| `authority_tier` | `international_standard` |
| `verified_date` | 2026-11-11 |
| `verification_method` | `authority_page`（ISO 官方目录确认标准存在与版本）；**内容细节待核验**（本环境无法访问标准全文） |
| `allowed_uses` | 项目定义、约束管理、过程组/主题组分类（**结构待核验**）、采购主题、时间主题、收尾过程 |
| `claim_mapping` | `GRAMMAR.md`：G-A1、G-A2、G-D1、G-D2、G-F3、G-F4；`knowledge/`：`Project`、`Constraint`、`Outcome` 条目定义 |
| **核验状态** | **部分核验**。标准存在性与版本已确认；“五过程组 × 十主题组”矩阵是否在 2020 版中保留、以何种形态保留，**未核验**。该未核验项直接导致 G-B1、G-B2 处于 `pending_reanchor`。 |

#### GB-T-37507-2025

| 字段 | 内容 |
|---|---|
| `id` | `GB-T-37507-2025` |
| `citation` | GB/T 37507—2025《项目、项目群和项目组合管理 项目管理指南》。中国国家标准化管理委员会。等同采用 ISO 21502:2020。 |
| `version` | 2025 版 |
| `status` | `active` |
| `authority_tier` | `national_standard` |
| `verified_date` | 2026-11-11 |
| `verification_method` | `cross_reference`（评审方提供的信息；本环境无法直接访问全国标准信息公共服务平台） |
| `allowed_uses` | 作为 `ISO21502-2020` 的**中文锚点**，在中文环境部署时优先引用；内容语义与 ISO 21502:2020 一致，不构成独立来源 |
| `claim_mapping` | 同 `ISO21502-2020`；本条目是语言锚点，不扩展 `claim_mapping` 范围 |
| **核验状态** | **交叉印证**。评审反馈确认存在且等同采用 ISO 21502:2020；本环境未独立访问。登记时标注为 `cross_reference`。 |

#### ISO21500-2012

| 字段 | 内容 |
|---|---|
| `id` | `ISO21500-2012` |
| `citation` | ISO 21500:2012, *Guidance on project management*. International Organization for Standardization. |
| `version` | 2012 版 |
| `status` | **`deprecated`**。2021-03-16 撤回，由 ISO 21502:2020（指南）与 ISO 21500:2021（概述）取代。 |
| `authority_tier` | `international_standard` |
| `verified_date` | 2026-11-11 |
| `verification_method` | `cross_reference`（评审反馈确认废止；ISO 官方目录可查废止记录） |
| `allowed_uses` | **仅限历史引用**。不得作为新规则的锚定依据。已锚定在其上的规则（G-B1、G-B2）标记 `pending_reanchor`。 |
| `claim_mapping` | 无新映射。G-B1、G-B2 的 `grounding_ref` 已改为 `ISO21502-2020` 并标 `pending_reanchor`；本条目保留为废止记录。 |
| **备注** | 保留此条目的理由：`CONSTITUTION.md` 第 2.4 条（不可删除性）。它是“来源存在性检查 ≠ 接地”的实例记录。 |

#### PRINCE2-2023

| 字段 | 内容 |
|---|---|
| `id` | `PRINCE2-2023` |
| `citation` | AXELOS. *Managing Successful Projects with PRINCE2*, 7th edition. The Stationery Office, 2023. |
| `version` | 7th edition (2023) |
| `status` | `active` |
| `authority_tier` | `official_doc`（方法论官方手册；非国际标准，但为广泛接受的权威实践框架） |
| `verified_date` | 2026-11-11 |
| `verification_method` | `cross_reference`（版本信息经评审与公开书目确认；**本环境无法访问全文**） |
| `allowed_uses` | 七项原则（持续业务验证、从经验中学习、定义角色与职责、按阶段管理、例外管理、关注产品、根据环境裁剪）；角色模型（最终责任不可委托）；产品描述要求；裁剪原则 |
| `claim_mapping` | `GRAMMAR.md`：G-C1（关注产品）、G-E1（定义角色与职责、问责不可委托）、G-E2（同上）、G-F1（持续业务验证 + 定义角色与职责）、G-F2（关注产品 + 阶段收尾）、G-G1、G-G2、G-G3（根据环境裁剪）；`knowledge/`：`Accountable`、`Responsible`、`Deliverable` 条目定义 |
| **核验状态** | **版本核验**。7th edition 2023 的存在性与版本经公开书目确认；**具体条款的原文措辞未核验**。G-F1、G-F2、G-G1–G3 的 `assumption` 状态与此直接相关。 |
| **非官方镜像排除** | 评审指出此前讨论中出现的“非官方中文镜像 PDF”不得入表。本条目仅登记官方版本；若部署环境只有非官方镜像，该镜像不得作为 `grounding_ref` 的依据。 |

#### ProjectCO-2024

| 字段 | 内容 |
|---|---|
| `id` | `ProjectCO-2024` |
| `citation` | Olsina, L., Becker, P., & Papa, M. F. (2024). The Project Management Ontology called ProjectCO: Architectural Aspects, Concepts, and Usefulness. *CIbSE 2024*, pp. 61–75. |
| `version` | 2024 会议论文版 |
| `status` | `active` |
| `authority_tier` | `peer_reviewed` |
| `verified_date` | 2026-11-11 |
| `verification_method` | `cross_reference`（评审确认会议官方目录可查；**论文内部细节未核验**——原文页面访问失败） |
| `allowed_uses` | 核心层领域无关概念：`Project`、`Actor`、`Commitment`、`Deliverable`、`Constraint`、`Outcome`、`Assertion`；核心概念的“cross-cutting, domain-independent”定位 |
| `claim_mapping` | `GRAMMAR.md`：G-A1、G-A2、G-D1、G-E1；`knowledge/`：`Project`、`Actor`、`Commitment`、`Deliverable`、`Constraint`、`Outcome` 条目定义 |
| **核验状态** | **存在性核验**。会议与论文存在性确认；**“45 个核心术语”等论文内部数字未核验**，本表不引用该数字。G-A1 的四元组合取形式为技能自身贡献，不宣称是 ProjectCO 原文的表述。 |

#### ThingFO-2021

| 字段 | 内容 |
|---|---|
| `id` | `ThingFO-2021` |
| `citation` | Olsina, L. (2021). ThingFO v1.2's Terms, Properties, Relationships and Axioms — Foundational Ontology for Things. *arXiv:2107.09129*. |
| `version` | v1.2（arXiv 2021） |
| `status` | `active` |
| `authority_tier` | `preprint` |
| `verified_date` | 2026-11-11 |
| `verification_method` | `cross_reference`（评审确认真实存在，且与 Olsina/Becker 团队系列工作可交叉印证） |
| `allowed_uses` | `Assertion` 作为“人类关于 Particulars 和 Universals 不同方面的陈述”的定义；断言的可区分性 |
| `claim_mapping` | `GRAMMAR.md`：G-C1、G-C2；`knowledge/`：`Assertion` 条目定义 |
| **核验状态** | **存在性核验**。arXiv 预印本存在性确认；`authority_tier` 标为 `preprint`，在与其他 `peer_reviewed` 来源冲突时优先级较低。 |

#### PMBOK7-2021

| 字段 | 内容 |
|---|---|
| `id` | `PMBOK7-2021` |
| `citation` | Project Management Institute. *A Guide to the Project Management Body of Knowledge (PMBOK Guide)*, 7th Edition. PMI, 2021. |
| `version` | 7th Edition (2021) |
| `status` | `active` |
| `authority_tier` | `official_doc` |
| `verified_date` | 2026-11-11 |
| `verification_method` | `cross_reference` |
| `allowed_uses` | **仅限原则层面的交叉验证**。用于检查本技能规则是否与广泛接受的项目管理原则相抵触；**不作为任何规则的直接锚定依据**。 |
| `claim_mapping` | 无直接映射。本条目是“一致性检查来源”，不是“规则锚定来源”。 |
| **备注** | PMBOK 已出至第 8 版（2025-11）。本表暂不引入第 8 版，理由：本技能规则尚未依赖第 8 版的结构；引入需 ADR。若未来规则需要第 8 版的原则表述，再行登记。版本漂移记录于此。 |

#### Nygard-ADR-2011

| 字段 | 内容 |
|---|---|
| `id` | `Nygard-ADR-2011` |
| `citation` | Nygard, M. (2011). Documenting Architecture Decisions. *Cognitect Blog*. |
| `version` | 2011-11-15 |
| `status` | `active` |
| `authority_tier` | `official_doc`（业界广泛接受的实践文献；非学术同行评议，但在架构决策记录领域具有事实权威） |
| `verified_date` | 2026-11-11 |
| `verification_method` | `cross_reference` |
| `allowed_uses` | ADR 五要素格式（标题 / 状态 / 背景 / 决定 / 结果）；治理决策的记录形态 |
| `claim_mapping` | `CONSTITUTION.md` 第 4 条（ADR 格式）；`adr/ADR-TEMPLATE.md` 的结构依据 |

#### RFC2119-1997

| 字段 | 内容 |
|---|---|
| `id` | `RFC2119-1997` |
| `citation` | Bradner, S. (1997). Key words for use in RFCs to Indicate Requirement Levels. *IETF RFC 2119*, BCP 14. |
| `version` | 1997 版（BCP 14） |
| `status` | `active` |
| `authority_tier` | `international_standard`（IETF 标准轨道文档） |
| `verified_date` | 2026-11-11 |
| `verification_method` | `cross_reference` |
| `allowed_uses` | 情态动词四档（MUST / MUST NOT / SHOULD / MAY）的语义定义；`GRAMMAR.md` 与 `CONSTITUTION.md` 中规范性措辞的语义依据 |
| `claim_mapping` | `CONSTITUTION.md` 第 3 条（规则陈述的形式要求）；`GRAMMAR.md` 使用说明（规则陈述的措辞纪律） |
| **备注** | RFC 8174（2017）对其大小写歧义作了澄清；本技能不依赖大小写区分，故不单独登记 RFC 8174。 |

---

### 废止与重新锚定记录

| 记录 | 内容 |
|---|---|
| **ISO21500-2012 废止** | 2021-03-16 撤回。取代关系：ISO 21502:2020（指南）+ ISO 21500:2021（概述）。受影响的规则：G-B1、G-B2。处置：`grounding_ref` 改为 `ISO21502-2020`，状态标 `pending_reanchor`，在重新锚定完成前降级为 `advisory`。 |
| **重新锚定待办** | 核验 ISO 21502:2020 是否保留“五过程组 × 十主题组”矩阵结构，以及该结构的具体形态。核验方式：获取 ISO 21502:2020 全文或 GB/T 37507-2025 全文（本地优先，见 `AGENTS.md` 第 1 条），核对过程组与主题组的分类维度。核验完成后，G-B1、G-B2 升级为 `block` 或修订陈述。登记于 `TODO.md`。 |

---

### 候选来源（未入表）

以下来源在讨论中被提及，但**未通过核验或不符合入表条件**，记录于此以防误用：

| 候选 | 未入表理由 |
|---|---|
| “Szwed 的 PMBOK OWL 本体（340 类）” | 评审指出“reasoner 自动验证一致性”的表述系张冠李戴（实际出自 Silega 等 2024 年论文）；“340 类”无可核验出处。**不得入表**，直至找到可核验的原始文献。 |
| Silega 等（Springer, CIIP 2023）PMBOK 形式化论文 | 评审确认存在，但本环境未核验其具体内容。若未来需要用其“reasoner 验证一致性”的论断，须先核验原文并走 ADR。当前**不登记**。 |
| “来源接地不能防止幻觉”的 zenodo 论文 | 评审未核验。当前**不登记**。 |
| Jarke 三世界（subject world / system world / usage world） | 评审指出“Jarke 三世界 = 本技能三空间”是未经确认的等同。本技能不登记该来源；三空间与本技能的映射关系在 `spec/INTERFACE_CONTRACT_SPEC.md` 中以 `assumption` 形式存在，**不以 Jarke 为锚**。 |
| 厂商博客、非官方镜像 PDF | `CONSTITUTION.md` 第 2.3 条排除。 |
| PMBOK 8th edition (2025-11) | 存在性经评审确认，但本技能规则尚未依赖其结构。引入需 ADR。当前**不登记**，版本漂移记录于 `PMBOK7-2021` 条目备注。 |

---

### 来源状态汇总

| 状态 | 条目 |
|---|---|
| `active` | ISO21502-2020（部分核验）、GB-T-37507-2025（交叉印证）、PRINCE2-2023（版本核验）、ProjectCO-2024（存在性核验）、ThingFO-2021（存在性核验）、PMBOK7-2021（交叉验证用途）、Nygard-ADR-2011、RFC2119-1997 |
| `deprecated` | ISO21500-2012 |
| 待核验项 | ISO21502-2020 的过程组/主题组结构；PRINCE2-2023 的具体条款措辞；ProjectCO-2024 的论文内部细节 |
