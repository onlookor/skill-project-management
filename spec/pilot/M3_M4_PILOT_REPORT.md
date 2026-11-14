# M3/M4 试点报告（15 条草稿）

> **性质**：试点记录，`authoritative: false`。不改变任何规格，不构成 M3/M4 出口。**批次**：0047（2026-11-14）。**D4**：未定，全部条目走 `DRAFT-K-<CAT>-<NN>`。

## 1. 产出

| 产出 | 路径 | 说明 |
|---|---|---|
| 15 条草稿 | [spec/pilot/pilot-entries.json](spec/pilot/pilot-entries.json) | 6 工件 + 6 工具 + 1 过程 + 1 焦点区 + 1 绩效域 |
| 草稿 ID 映射 | [spec/pilot/pilot-id-map.json](spec/pilot/pilot-id-map.json) | 草稿 ID → 候选 IRI → 正式 ID 占位；含规则 ↔ 条目双向索引 |
| 试点契约 | [spec/pilot/pilot-contract.yaml](spec/pilot/pilot-contract.yaml) | 复用既有槽位，未向 `GRAMMAR.md` 引入领域词 |
| 产物样例（JSON） | [spec/pilot/pilot-artifact.json](spec/pilot/pilot-artifact.json) | 机器可读源 |
| 产物样例（MD） | [spec/pilot/pilot-artifact.md](spec/pilot/pilot-artifact.md) | 人类可读投影 |
| 冲突样例 | [spec/pilot/pilot-conflicts.jsonl](spec/pilot/pilot-conflicts.jsonl) | 3 组：一致、作用域冲突、单来源 |

## 2. 统计

- 条目总数：15。工件 6、工具 6、过程 1、焦点区 1、绩效域 1。
- 有候选本体 IRI：14。无候选 IRI：1（`DRAFT-K-TOOL-04` Monte Carlo simulation）。
- 有稳定自然键：15。既无 IRI 又无稳定自然键：0。
- `definitionStatus`：`defined` 15，`taxonomy-only` 0，`pending` 0。
- 规则绑定：G-A1、G-A2、G-C1、G-D1、G-E1 各至少 1 条，双向索引覆盖 7 个条目引用。
- **用户指定的止损（≥2 条既无 IRI 又无稳定自然键）：未命中（0 条）。**

候选 IRI 未解析的唯一原因：本体没有 Monte Carlo 个体，最近邻 `pm:tt_Simulation` 语义更宽，不能作为同一概念；该条另有稳定自然键 `monte-carlo-simulation`，因此不触发止损。

## 3. 七条判据逐项判定

| # | 判据 | 判定 | 依据与保留 |
|---|---|---|---|
| 1 | 15 条均有 `definition`、`grounding_ref`、`sourcePage`、`definitionStatus`，无 `taxonomy-only` | **结构通过，实质有条件** | 15/15 字段齐全，0 条 `taxonomy-only`。但 `grounding_ref` 按 D3 指向 `knowledge:<draft-id>`，来源放在 `evidence`；全部依赖 `PMBOK8-2025`，而该来源当前 `allowed_uses` 仅限原则层交叉验证（T-123 未定），草稿不作权威锚定。 |
| 2 | 每条定义可在 1 次检索内回溯来源页码 | **通过** | 每条 `evidence` 含 `source_id` + `page` + `locator`；印刷页与 PDF 页偏移已实测（PDF 230 = 印刷 125），按印刷页写入。 |
| 3 | G-A1/G-A2/G-C1/G-D1/G-E1 各至少 1 条可双向解析，零歧义 | **通过（映射层）** | `pilot-id-map.json` 的 `rule_bindings` 与 `reverse_rule_index` 一一对应，5/5 规则有绑定，反向无一对多歧义。尚未写入 `GRAMMAR.md` 的 `grounding_ref`，接入受 D4/T-125 门控。 |
| 4 | 同一概念在 GLOSSARY / JSONL / TTL / 规则引用四处命名零冲突 | **部分通过，不计为满足** | 草稿层零冲突：草稿 ID 未进入 `GLOSSARY.md`、`knowledge/anchored-entries.jsonl`、TTL 的 `skos:prefLabel`、`GRAMMAR.md` 的 `grounding_ref`。但“零冲突”来自草稿不接入，权威层未被真正检验；D4 未定前无法完成该项。 |
| 5 | 1 份产物可被 3 类消费者读取，无需改格式 | **通过** | 人读 MD 表格、脚本读 JSON 的 `clauses[]` / `aggregate`、M5 按 `clause` 对契约槽位读取判定；三类均未要求改格式。MD 为人工投影，双写漂移风险见 F-06。 |
| 6 | 3 组冲突样例可在现有字段内记录，不丢“谁与谁冲突” | **通过** | `evidence` 数组承载多来源；`provenance_note` 记录定位差异；`relations` 记录作用域。3 组分别是一致（PC-01）、作用域冲突（PC-02）、单来源（PC-03），双方立场均可定位到 `source_id` + `page`。 |
| 7 | 非执行方抽 5 条，按页码核对“自写且不失真”，结论落外部产物 | **blocked-external** | 本会话是执行方，不得自证。未做外部抽样，未生成外部产物；须由非同源复核方执行后才能判定。 |

## 4. 六条止损逐项判定

| # | 止损条件 | 判定 | 说明 |
|---|---|---|---|
| 1 | 15 条中 ≥2 条无法在现有字段内表达 | **未触发** | 0 条需要新增字段或改粒度。D2=b 的 `entry_type`/`status`/`relations`/`evidence` 足够承载 5 类概念。 |
| 2 | 规则 ↔ 条目双向解析 ≥1 条歧义或需引入新规则 | **未触发** | 5/5 规则绑定唯一，反向索引无一对多。 |
| 3 | 3 类消费者中任一类要求改产物格式 | **未触发** | 3/3 直接读取，无格式变更请求。 |
| 4 | 冲突样例任一组无法记录双方立场 | **未触发** | 3/3 可记录；单来源组明确记为 `single-source` 而非伪造第二方。 |
| 5 | 外部抽样 5 条中 ≥2 条被判“改写原文”或“定义不可用” | **无法判定（blocked-external）** | 未做外部抽样，不构成“未触发”的结论；需外部复核。 |
| 6 | 为通过试点需新增检查器、指纹区段或自证机制 | **未触发** | 未新增任何检查器、指纹区段或自证机制；复用现有台账/锚点/状态检查器。 |

## 5. 发现与风险

**F-01（高，阻塞放量）来源授权未定。** 15 条草稿的来源证据全部指向 `PMBOK8-2025`，该来源在 `SOURCE_LEDGER.md` 的 `allowed_uses` 仅限原则层交叉验证，不能作为概念层条目的权威锚定。`T-123` 未关闭前，M3 放量会批量产生“有 grounding_ref 但无使用授权”的条目。建议把 `T-123` 提到 D4 同批拍板。

**F-02（高，阻塞放量）D3 的 `grounding_ref` 语义与现有 JSONL 冲突。** D3 选定 `grounding_ref` 指向 `knowledge:<term>`；现有 10 条 `knowledge/anchored-entries.jsonl` 的 `grounding_ref` 指向来源 ID。试点按 D3 写入并把来源移入 `evidence`，但这意味着两套条目语义不一致。放量前需二选一：调整 D3 表述，或给条目增加独立的 `source_ref` 并迁移现有 10 条。未在本批擅改。

**F-03（中）Monte Carlo 无个体 IRI。** 本体只有 `pm:tt_Simulation`，语义更宽。可接受为 `null` + 稳定自然键，或在 M3 放量时补 `pm:tt_MonteCarloSimulation` 个体；后者改变本体范围，需单独裁定。

**F-04（中）中英双标签成本线性。** 15/15 条目都需要人工给中文标签；D10 未定，若最终选择仅英文，已写中文标签要回退。放量前应定 D10。

**F-05（低）页码粒度需定稿。** 实测印刷页与 PDF 页存在固定偏移，试点统一按印刷页写入。D9 未定前，外部核对若按 PDF 页抽样会得到不一致结果。

**F-06（低）产物双写风险。** 试点 MD 是 JSON 的人工投影。若 R10 要求“生成物与手写物分离”，放量前需补生成器；本批未引入。

**F-07（低，存储形态）JSONL 与原始资料检查冲突。** 15 条草稿若写成每行一条的 JSONL，会形成连续 15 行以上长行，被 `check_no_raw_material` 判为“疑似文本层转储”。试点改用 JSON 数组（字段不变）规避该误报，未给检查器开例外。R10 的存储形态需在放量前定；若最终选 JSONL，应同时确定如何避免长行连续。

## 6. 结论

- 试点结构层面完成：15 条草稿、ID 映射、契约、产物样例、3 组冲突样例均落盘。
- **六条止损中五条明确未触发，一条（外部抽样）因无非执行方而无法判定；用户指定的“双无条目”止损未命中。**
- **不得据此放量。** 放量前至少需要：D4 拍板；`T-123` 来源使用授权裁定；F-02 的 `grounding_ref` 语义统一；外部抽样 5 条（判据 7）。
- 本批未开始 M3 放量，未改动 `GLOSSARY.md`、`knowledge/anchored-entries.jsonl`、TTL 标签、`GRAMMAR.md` 的 `grounding_ref` 与 `SOURCE_LEDGER.claim_mapping`。
