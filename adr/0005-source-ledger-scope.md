# ADR-0005: 来源登记表收缩、本地资料入表与治理文献出表

- **状态**：accepted
- **日期**：2026-11-12
- **决策者**：用户（人类责任方）批准，执行方落地
- **serves_charter**：服务于 C3（来源封闭、可追溯，且每条来源必须真正支撑编译目标）
- **grounding_refs**：无（治理决策；涉及的具体来源见 `SOURCE_LEDGER.md`）
- **affected_files**：`SOURCE_LEDGER.md`（删除 4 个条目、新增 2 个条目、改写候选清单）、`CONSTITUTION.md` 第 2.3、2.4、3、4、6、8 条与第 10.3/10.7 条、`adr/README.md`（新建）、`adr/ADR-TEMPLATE.md`、`GLOSSARY.md`、`CHARTER.md`、`README.md`、`AGENTS.md`、`ERRATA.md`、`GRAMMAR.md`、`spec/ASSUMPTION_PROTOCOL.md`、`spec/COMPILATION_META.md`、`spec/CONTEXT_ASSEMBLY.md`、`spec/methods/deterministic-checker.md`、`contracts/examples/construction.pm-contract.yaml`、`knowledge/anchored-entries.jsonl`、`knowledge/methods/registry-skeleton.md`

## 背景

本地 `resources/pm/` 与 `resources/se/` 已具备一批实际资料，而 `SOURCE_LEDGER.md` 仍停留在“无全文、仅凭评审转述”的状态，并混入了三类不属于本表职责的内容：

1. **过期或已被取代的来源**：ISO 21500:2012（2021-03-16 撤回）、PMBOK 第 7 版（第 8 版已于 2025-11 出版且本地有副本）。
2. **不服务于编译目标的文献**：Nygard 的 ADR 文章、RFC 2119。二者分别属于软件架构文档实践与互联网标准措辞，不是通用项目管理知识；把它们放在封闭来源表里，会让“任何 `grounding_ref` 都可指向本表”的封闭枚举混入与规则无关的条目。
3. **未核验且无法核验的候选**：Jarke 三世界被误当作本技能的“三空间”锚点；“Szwed / 340 类 OWL 本体”被评审指出张冠李戴。

同时，`CONSTITUTION.md` 第 2.3 条把“非官方镜像 PDF”一律排除、第 2.4 条禁止删除任何被引用过的条目，与“用户已在本地提供权威副本”“过期条目应彻底删除”这两个事实冲突。

## 决定

1. **删除过期来源条目**：`ISO21500-2012`、`PMBOK7-2021`。删除后不保留 `deprecated` 条目；可追溯性由 git 历史承担（ADR-0003）。
2. **治理文献出表**：`Nygard-ADR-2011`、`RFC2119-1997` 移出 `SOURCE_LEDGER.md`。ADR 的格式说明移入新建的 `adr/README.md`（Nygard、MADR、Y-Statement 三种格式并存）；规范性措辞的语义依据改为 BCP 14（RFC 2119 + RFC 8174），引用写在 `CONSTITUTION.md` 第 3 条，不再占用来源表条目。
3. **本地资料入表**：`resources/pm/` 下的实际文件按 `local_copy_check` 登记——ISO 21502:2020、PRINCE2 7th（官方水印版）、ProjectCO 2024、ThingFO v1.3、PMBOK 第 8 版。文件路径写入条目的 `local_path` 字段。
4. **新增 Springer 章节**：`SPRINGER-PMBOK-2024`（DOI 10.1007/978-3-031-50495-2_13，PMBOK 的形式化/OWL 本体表示）。正文未获取，已向通讯作者请求；在正文取得前不作为任何规则的锚定依据。
5. **OWL 本体候选保留**：以“有可靠来源但尚未获取”标注保留，不得被引用。
6. **三空间清理**：删除 Jarke 候选条目；除软件工程语境（`spec/INTERFACE_CONTRACT_SPEC.md` 第 7 节与 `contracts/examples/software-engineering.pm-contract.yaml`）外，其余文档中的“三空间/三世界”叙述一律删除或改写为“外部本体插件”。
7. **修订第 2.3、2.4 条**：2.3 放宽为“用户认可的来源、或本地 `resources` 目录中确实存在的来源，应被认可”；2.4 改为“过期或撤回的来源可以删除，可追溯性由 git 历史承担”。

## 考虑过的替代方案

1. **保留 `deprecated` 条目不删，只标状态**。拒绝：用户明确要求彻底删除；且同一条目保留会继续被误引用为“可用的历史锚点”，而本技能的规则并不需要历史引用。
2. **把 ADR 与 RFC 保留在表内，标注“治理专用”**。拒绝：来源表的职责是“服务于编译目标的通用项目管理知识来源”，加入治理专用文献会破坏封闭枚举的语义，使 `grounding_ref` 的合法取值失去一致含义。
3. **把三空间相关叙述全部删除，包括 SE 语境**。拒绝：`INTERFACE_CONTRACT_SPEC.md` 第 7 节与 SE 契约样例已把三空间作为**软件工程技能的专有概念**以 `assumption` 形式引用，删除会破坏已有的验证条件与样例；保留但限定语境更准确。
4. **Springer 章节暂不登记，等内容获取后再说**。拒绝：用户要求登记并如实标注获取状态；登记元数据（而不是论断）能让后续核验有明确对象。

## 结果

### 正面

- 来源表只剩“通用项目管理知识”，与 `SOURCE_LEDGER.md` 的封闭枚举语义一致。
- 本地资料从“评审转述”升级为 `local_copy_check`，可核验性提高；非官方镜像被明确排除。
- ADR 格式不再依赖单一博客文献，`adr/README.md` 提供三种可选格式，模板随之扩展。
- 三空间不再是本技能的隐含概念；仅在 SE 语境以假设形式存在。

### 负面

- 删除条目后，旧文档中若存在对 `ISO21500-2012`、`PMBOK7-2021` 的引用会失效，需要一次性清理；本次已逐处处理。
- `PRINCE2-2023` 的“官方水印版”与“无水印版”并存，前者作为依据、后者被排除，若日后只保留无水印版，条目需重新核验。
- Springer 章节在正文取得前只能支持“存在性与主题”，不能支持任何规则论断。

### 需要跟进的事项

- **T-112**（新增）：取得 Springer 章节全文后，核对其 OWL 本体与“reasoner 一致性检查”的论断，决定是否将其作为知识层条目的来源。
- **T-113**（新增）：核对本地 ISO 21502:2020 的过程组/主题组矩阵（原 T-003 的本地核验路径），决定 G-B1、G-B2 是否解除 `pending_reanchor`。
