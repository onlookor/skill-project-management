## 后续工作

**登记规则**：见 `AGENTS.md` 第 3.2 条。编号续用，不重排；删除条目保留编号并标记 `[done]` 或 `[dropped]`。

### 规范层补丁

| 编号 | 性质 | 工作项 | 治理路径 | 前置依赖 | 状态 |
|---|---|---|---|---|---|
| T-001 | `pending_reanchor` 解除 | 核验 ISO 21502:2020 是否保留“五过程组 × 十主题组”矩阵结构；核验方式：获取全文（本地优先），核对分类维度 | ADR | 本地资源或权威访问 | `open` |
| T-002 | `assumption` 升级（G-F 组） | 逐条核验 G-F1–G-F4 的锚定来源（ISO 21502:2020 的过程覆盖、PRINCE2 的阶段管理原则）；核验后决定升级为 `block` 或修订陈述 | ADR | T-001 同源核验 | `open` |
| T-003 | `assumption` 升级（G-G 组） | 核验 G-G1–G-G3 的锚定来源（PRINCE2 裁剪原则）；核验后决定升级或修订 | ADR | 无 | `open` |
| T-004 | 来源精度提升 | 为 `M-EST-01`、`M-DEC-01`、`M-RISK-01`、`M-EV-01` 补充更精确的来源锚定（当前仅指向 PMBOK 原则层交叉验证） | ADR + `SOURCE_LEDGER.md` 更新 | 本地资源 | `open` |
| T-005 | 来源精度提升 | 核验 PRINCE2-2023 的具体条款措辞（当前仅版本核验）；核验后更新 `SOURCE_LEDGER.md` 的 `verification_method` 与相关规则的 `provenance_note` | ADR | 本地资源 | `open` |
| T-006 | 来源精度提升 | 核验 ProjectCO-2024 的论文内部细节（当前仅存在性核验）；核验后决定是否扩展 `claim_mapping` | ADR | 本地资源 | `open` |
| T-007 | 一致性检查 | 建立 `GRAMMAR.md` 的 `grounding_ref` 与 `SOURCE_LEDGER.md` 的 `claim_mapping` 的双向一致性检查项 | 执行层补丁（不需 ADR） | 无 | `open` |
| T-008 | 版本漂移 | 评估是否引入 PMBOK 8th edition (2025-11)；引入需 ADR 论证规则依赖 | ADR | T-004 同源 | `open` |

### 执行层补丁

| 编号 | 性质 | 工作项 | 治理路径 | 前置依赖 | 状态 |
|---|---|---|---|---|---|
| T-010 | 解析器实现规格 | 为 `contracts/resolver.md` 补充解析器的参考实现伪代码（供宿主实现时参照） | 结构性变更需 ADR | 无 | `open` |
| T-011 | 检查器实现规格 | 为 `spec/methods/deterministic-checker.md` 附录 A 注册表中的每个 check 补充参考实现的输入/输出样例 | 结构性变更需 ADR | 无 | `open`（**引用路径已从 `COMPILATION_SPEC.md` 更新为 `COMPILATION_META.md` + `spec/methods/deterministic-checker.md`**） |
| T-012 | 多层合并启用评估 | 评估是否启用多层契约合并（`spec/INTERFACE_CONTRACT_SPEC.md` 第 6 节）；启用需 ADR 论证真实需求 | ADR | 三个以上技能接入 | `open` |
| T-013 | PACT 适配验证 | 在宿主安装 PACT 时验证 `COMPILATION_SPEC.md` 第 8 节与 `resolver.md` 第 3 节的可映射/不可映射声明是否与实际 PACT 行为一致 | 执行层补丁 | PACT 可用 | `open` |

### 知识层填充

| 编号 | 性质 | 工作项 | 治理路径 | 前置依赖 | 状态 |
|---|---|---|---|---|---|
| T-020 | 方法条目 | 填充 `estimation` 类别：类比估算、参数估算、自下而上估算 | 来源治理 | T-004 | `open` |
| T-021 | 方法条目 | 填充 `decomposition` 类别：按阶段分解、按地理分解 | 来源治理 | T-004 | `open` |
| T-022 | 方法条目 | 填充 `risk` 类别：蒙特卡洛模拟、决策树 | 来源治理 | T-004 | `open` |
| T-023 | 方法条目 | 填充 `earned_value` 类别：燃尽图、累积流量图 | 来源治理 | T-004 | `open` |
| T-024 | 方法条目 | 填充 `procurement` 类别：合同类型选择 | 来源治理 | T-002 | `open` |
| T-025 | 方法条目 | 填充 `stakeholder` 类别：权力-利益矩阵 | 来源治理 | 来源待定 | `open` |
| T-026 | 方法条目 | 填充 `communication` 类别：沟通计划编制 | 来源治理 | 来源待定 | `open` |
| T-027 | 方法条目 | 填充 `quality` 类别：质量审计、因果图 | 来源治理 | 来源待定 | `open` |
| T-028 | 本体条目 | 补充 `LegalEntity`、`HumanActor`、`AIActor` 的独立条目（当前在 `Actor` 条目中内联） | 来源治理 | 无 | `open` |
| T-029 | 本体条目 | 补充 `Contract`、`ProjectCharter`、`TailoringRecord` 的条目（G-F/G-G 组引用） | 来源治理 | T-002、T-003 | `open` |

### 样例与示例

| 编号 | 性质 | 工作项 | 治理路径 | 前置依赖 | 状态 |
|---|---|---|---|---|---|
| T-030 | 契约样例 | 补充第三个领域样例（如“运维/服务管理”），验证槽位定义的领域无关性 | 随样例更新 | 无 | `open` |
| T-031 | 连接实例样例 | 在 `contracts/examples/` 中补充连接实例声明样例（不进入成文法） | 随样例更新 | 无 | `open` |

### 验证

| 编号 | 性质 | 工作项 | 治理路径 | 前置依赖 | 状态 |
|---|---|---|---|---|---|
| T-040 | 验证套件 | 为首批方法条目设计检索测试集，验证 `CHARTER.md` 承诺 C1 的召回率阈值 | 结果登记 | T-020–T-027 | `open` |
| T-041 | 验证套件 | 为 `GRAMMAR.md` 的 `active` 规则设计检查器测试用例（含 `pass` / `fail` / `cannot_evaluate` 三值覆盖） | 结果登记 | T-011 | `open` |
| T-042 | 验证套件 | 验证 `ASSUMPTION_PROTOCOL.md` 第 5 节的四条 `unknown` 处置纪律在检查器实现中一致 | 结果登记 | T-011 | `open` |

### 治理

| 编号 | 性质 | 工作项 | 治理路径 | 前置依赖 | 状态 |
|---|---|---|---|---|---|
| T-050 | 治理实践 | 为 `CHARTER.md` 承诺 C1 的召回率阈值确定具体数值（当前为“待首批条目入库后确定”） | ADR | T-040 | `open` |
| T-051 | 治理实践 | 评估是否需要在 `CONSTITUTION.md` 第 2 条增加“来源修订”状态（当前只有 active/deprecated/superseded） | ADR | 实际需求出现 | `open` |
| T-052 | 治理实践 | 审查 `SOURCE_LEDGER.md` 候选来源清单，决定是否引入 Silega 等 2024 年 PMBOK 形式化论文（需先核验原文） | ADR | 原文核验 | `open` |

### 新增：编译方法声明文件（候选方法）

| 编号 | 性质 | 工作项 | 治理路径 | 前置依赖 | 状态 |
|---|---|---|---|---|---|
| T-060 | 方法声明 | 编写 `spec/methods/skill-card.md`（CM-SKILL-CARD 的声明文件，按 META 第 4 条格式） | 方法声明变更需 CHANGELOG；启用需 ADR | 无 | `open` |
| T-061 | 方法声明 | 编写 `spec/methods/human-checklist.md`（CM-HUMAN-CHECK 的声明文件） | 同上 | 无 | `open` |
| T-062 | 方法声明 | 编写 `spec/methods/pact-rules.md`（CM-PACT 的声明文件） | 同上 | 无 | `open` |
| T-063 | 方法声明 | 编写 `spec/methods/neuro-symbolic.md`（CM-NEURO-SYMB 的声明文件；v0.1 不评估启用） | 同上 | 无 | `open` |

### 新增：引用修复与一致性

| 编号 | 性质 | 工作项 | 治理路径 | 前置依赖 | 状态 |
|---|---|---|---|---|---|
| T-070 | 引用修复 | 全仓库检索 `spec/COMPILATION_SPEC.md` 的残留引用，更新为 `spec/COMPILATION_META.md` + `spec/methods/deterministic-checker.md` 的对应位置 | 执行层补丁（不需 ADR） | 无 | `open` |
| T-071 | 一致性检查 | 建立 `spec/COMPILATION_METHODS.md` 的方法登记与 `spec/methods/{method-id}.md` 声明文件的一致性检查项（名称、适用范围、状态） | 执行层补丁 | T-060–T-063 | `open` |
| T-072 | 一致性检查 | 建立 `spec/COMPILATION_META.md` 第 2 条（P1–P6）与各方法声明文件第 3–7 节的覆盖检查项（每个方法必须逐条论证 P1–P6） | 执行层补丁 | T-060–T-063 | `open` |

### 新增：验证套件（编译域）

| 编号 | 性质 | 工作项 | 治理路径 | 前置依赖 | 状态 |
|---|---|---|---|---|---|
| T-080 | 验证套件 | 为 `CM-DET-CHECKER` 的 P1c（不扭曲）设计反例检验用例：每条规则至少一个“应通过”与一个“应失败”用例，含量词边界（空集/单元素/多元素）与例外触发用例 | 结果登记 | 无 | `in-progress`（`validation/test-cases/` 已落 3 个用例，其余见 T-101） |
| T-081 | 验证套件 | 验证 `CM-DET-CHECKER` 的退化路径（`runtime: deterministic-checker/human-fallback`）下 P1–P6 仍被满足 | 结果登记 | 无 | `open` |

### 新增：术语表

| 编号 | 性质 | 工作项 | 治理路径 | 前置依赖 | 状态 |
|---|---|---|---|---|---|
| T-090 | 一致性检查 | 建立 `GLOSSARY.md` 的 A 类条目与 `knowledge/anchored-entries.jsonl` 的同步检查项（定义一致、`anchored_entry` 指针有效） | 执行层补丁 | 无 | `in-progress`（`scripts/check_glossary_sync.md` 已给出检查规格，检查执行记录待补） |
| T-091 | 术语补充 | 补充 `GLOSSARY.md` 第 6 节列出的待补充术语（编译域执行失败分类、ADR 状态、`merge: append`、`immutable`、`SLA`、`SLO`、`RPO`、`RTO`、`CI/CD`、`API`、`IDL`） | E/F 类走 CHANGELOG；B/C/D 类走 ADR | 无 | `open` |
| T-092 | 术语补充 | 为 `GLOSSARY.md` A 类的 `HumanActor`、`LegalEntity`、`AIActor`、`Contract`、`ProjectCharter`、`TailoringRecord` 补充 `anchored-entries.jsonl` 的独立条目（与 T-028、T-029 合并执行） | ADR + JSONL 同步 | T-028、T-029 | `open` |
| T-093 | 术语补充 | 为 `GLOSSARY.md` B 类的机制术语补充“首次使用处”的内联定义检查（验证 `GRAMMAR.md`、`spec/` 中各术语首次出现时是否有内联定义或指向 `GLOSSARY.md`） | 执行层补丁 | 无 | `open` |
| T-094 | 术语补充 | 为 `GLOSSARY.md` E 类条目补充更精确的 `grounding_ref`（当前 `WBS`、`PERT`、`EVM` 的 `grounding_ref` 仅为 PMBOK 原则层交叉验证；与 T-004 合并执行） | ADR + `SOURCE_LEDGER.md` 更新 | T-004 | `open` |

### 新增：反例、接地与可运行性缺口

| 编号 | 性质 | 工作项 | 治理路径 | 前置依赖 | 状态 |
|---|---|---|---|---|---|
| T-100 | 检查器判定修正 | 修正 `ROLE_MINIMAL_COMPLETENESS` 的 warn/block 混合判定：区分“问责结构根本性缺失（block）”与“角色合并声明缺失（warn）”两种情形（见 `ERRATA.md` E-004） | 结构性变更需 ADR（改变已有规则的编译结果） | 无 | `open` |
| T-101 | 反例用例补齐 | 补齐未落盘的 10 个反例检验用例正文：`TC-A1-01`、`TC-A1-03`、`TC-C1-01`、`TC-C1-02`、`TC-D1-01`、`TC-D1-02`、`TC-D1-03`、`TC-E1-01`、`TC-E1-02`、`TC-E1-03`；并补齐未覆盖规则（G-A2、G-C2、G-D2、G-E2、G-B1、G-B2、G-F1–F4、G-G1–G3）的用例 | 结果登记 | T-080 | `open` |
| T-102 | ADR 治理补强 | 补充“被拒绝方案”的 ADR 记录（考虑过、论证不可行、拒绝理由），并给出 ADR 合格性评审清单；当前 ADR-0001、ADR-0002 均只记录“决定这样做” | ADR（新增记录）；评审清单本身属执行层补丁 | 无 | `open` |
| T-103 | 检查回放机制 | 定义检查执行记录的回放机制：检查失败后如何以同一输入快照重放、如何比对两次结论、回放记录保存在哪里 | 执行层补丁 | 无 | `open` |
| T-104 | 跨技能端到端走查 | 设计一条“领域技能产物 → 项目管理槽位/baseline”的端到端走查样例（如需求工程产物进入本项目），验证 `spec/INTERFACE_CONTRACT_SPEC.md` 的槽位定义在真实流动中可用 | 随样例更新 | T-031 | `open` |
| T-105 | 方法注册表可用性 | 补充方法的规模/领域筛选机制与方法组合说明（如挣值与风险的配合、WBS 与估算的配合）；当前注册表只有检索键，没有组合与筛选规则 | 来源治理 | T-004、T-020–T-027 | `open` |
| T-106 | 外部依赖失效处置 | 规定“外部来源长期不可得”时的处置规则（T-001–T-003 均依赖获取 ISO 21502:2020 全文；当前未定义永远取不到时如何收口） | ADR | 无 | `open` |
| T-107 | 可执行原型 | 提供一个最小可执行的确定性校验器原型（哪怕只覆盖 3–5 个 `check_id`），以验证 `spec/methods/deterministic-checker.md` 的判定逻辑可被程序实现；`QUICKSTART.md` 的走查为手工推演，不构成可执行证据 | 执行层补丁 | T-011 | `open` |
| T-108 | 版本条文的遗留冲突 | `CONSTITUTION.md` 第 9 条与第 11.7 条仍要求“版本号在文件头声明”，与现行口径（不保留文件版本头，状态登记于 `STATE.md`）冲突；待确认后按规范层程序修订，未确认前不改条文 | ADR | 用户确认 | `open`（ADR-0003 已 accepted，待批次落地后关闭） |

### 新增：版本与状态治理（ADR-0003）

| 编号 | 性质 | 工作项 | 治理路径 | 前置依赖 | 状态 |
|---|---|---|---|---|---|
| T-109 | 产物版本链重构 | `spec/COMPILATION_META.md` 第 10 条与 `spec/methods/deterministic-checker.md` 第 9 节以“文件头版本”为输入定义产物版本与对齐检查；文件层去版本后该链失效，需裁定替代口径（候选：产物记录生成基线的 git 提交，装配时比对源提交） | ADR（改变已有规则的编译结果） | 用户裁定 | `open` |
| T-110 | 发布一致性检查 | 建立 `manifest.json` 的包版本与最新 annotated tag 的一致性检查，避免两处记录漂移 | 执行层补丁 | `manifest.json` 建立 | `open` |
