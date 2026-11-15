# 准入区表（ACCESS_ZONES）

**性质**：执行第 13.3 条的路径归区与数据区准入登记。本文件是 `scripts/check_no_raw_material.py` 的唯一归区来源；改本表必须与检查器同批提交，并按 3.6.8 重冻 `scripts/checker-pins.json`。

**依据**：`CONSTITUTION.md` 第 13 条；方案 `spec/RAW_MATERIAL_ADMISSION.md`；ADR-0018。

## 1. 路径归区表

匹配规则：按最长前缀匹配；以 `/` 结尾的条目是目录前缀，其余条目是精确文件路径；`./` 表示根目录下不含目录前缀的文件。`分区准入`以本 `归区表` 为唯一来源；未命中任何条目的路径**默认阻断**（`RM-ZONE`），必须先在本表登记。

| 路径 | 区 | 级别 | 说明 |
|---|---|---|---|
| `./` | P | P0 | 根级治理与说明文档 |
| `.gitignore` | C | — | 仓库配置 |
| `.githooks/` | C | — | 提交钩子 |
| `manifest.json` | D | — | 发布元数据（结构化） |
| `adr/` | P | P1 | 架构决策记录 |
| `contracts/` | P | P1 | 契约说明（数据与 schema 由下列前缀覆盖） |
| `contracts/examples/` | D | — | 契约样例 |
| `contracts/schema/` | D | — | JSON Schema 文件 |
| `knowledge/methods/` | P | P1 | 方法说明 |
| `knowledge/` | D | — | 知识条目与生成索引 |
| `ontology/README.md` | P | P1 | 本体说明 |
| `ontology/fixtures/manifest.json` | D | — | 本体夹具清单（数据） |
| `ontology/` | O | — | 本体序列化文件 |
| `scripts/anchor_baseline.json` | D | — | 锚点基线（生成） |
| `scripts/checker-pins.json` | D | — | 检查器指纹登记（生成） |
| `scripts/spec-pins.json` | D | — | 规格指纹登记（生成） |
| `scripts/README.md` | P | P1 | 脚本说明 |
| `scripts/check_glossary_sync.md` | P | P1 | 术语同步说明 |
| `scripts/` | C | — | 检查器与工具 |
| `spec/pilot/pilot-artifact.json` | D | — | 试点工件（生成） |
| `spec/pilot/pilot-conflicts.jsonl` | D | — | 试点冲突记录 |
| `spec/pilot/pilot-contract.yaml` | D | — | 试点契约样例 |
| `spec/pilot/pilot-entries.json` | D | — | 试点知识条目 |
| `spec/pilot/pilot-id-map.json` | D | — | 试点 ID 映射（生成） |
| `spec/pilot/` | P | P2 | 试点说明与报告（非权威） |
| `spec/` | P | P1 | 规范正文 |
| `validation/checker-prototype/coverage.json` | D | — | 覆盖矩阵（生成） |
| `validation/checker-prototype/` | C | — | 原型检查器 |
| `validation/pinned/` | C | — | 冻结的检查器快照 |
| `validation/reviews/` | P | P2 | 复核与授权转录（非权威） |
| `validation/test-cases/` | P | P2 | 测试用例说明 |
| `validation/` | P | P1 | 验证与复核材料 |

## 2. 数据区准入登记

数据区文件必须在本表登记；未登记即 `RM-SCHEMA`，不降级为按文本扫描（D-1）。`形态` 决定解析方式，`schema 或生成器` 决定校验方式：

- 第三列是 `contracts/schema/*.schema.json`：按该 schema 校验（支持本仓库用到的 JSON Schema 子集）。
- 第三列以 `生成器 ` 开头：该文件由所列脚本生成并自校验；准入检查器只要求解析成功与声明的顶层形态。
- `schema-doc`：JSON Schema 文件自身，要求可解析且含 `$schema` 与 `type`。

| 路径 | 形态 | schema 或生成器 |
|---|---|---|
| `knowledge/anchored-entries.jsonl` | jsonl | `contracts/schema/knowledge-entry.schema.json` |
| `knowledge/glossary-usage.json` | json-object | 生成器 `scripts/check_glossary_usage.py` |
| `manifest.json` | json-object | `contracts/schema/package-manifest.schema.json` |
| `spec/pilot/pilot-entries.json` | json-array | `contracts/schema/knowledge-entry.schema.json` |
| `spec/pilot/pilot-conflicts.jsonl` | jsonl | `contracts/schema/pilot-conflict.schema.json` |
| `spec/pilot/pilot-artifact.json` | json-object | `contracts/schema/pilot-artifact.schema.json` |
| `spec/pilot/pilot-id-map.json` | json-object | `contracts/schema/pilot-id-map.schema.json` |
| `spec/pilot/pilot-contract.yaml` | yaml-object | `contracts/schema/pm-slot-contract.schema.json` |
| `contracts/examples/` | yaml-object | `contracts/schema/pm-slot-contract.schema.json` |
| `contracts/schema/pm-slot-contract.schema.json` | schema-doc | — |
| `contracts/schema/knowledge-entry.schema.json` | schema-doc | — |
| `contracts/schema/pilot-conflict.schema.json` | schema-doc | — |
| `contracts/schema/package-manifest.schema.json` | schema-doc | — |
| `contracts/schema/ontology-fixtures-manifest.schema.json` | schema-doc | — |
| `contracts/schema/pilot-artifact.schema.json` | schema-doc | — |
| `contracts/schema/pilot-id-map.schema.json` | schema-doc | — |
| `ontology/fixtures/manifest.json` | json-object | `contracts/schema/ontology-fixtures-manifest.schema.json` |
| `scripts/anchor_baseline.json` | json-object | 生成器 `scripts/check_anchors.py --write` |
| `scripts/checker-pins.json` | json-object | 生成器 `scripts/check_checker_pins.py --write` |
| `scripts/dependency-pins.json` | json-object | 生成器 `scripts/check_dependency_pins.py --write` |
| `scripts/spec-pins.json` | json-object | 生成器 `scripts/check_spec_pins.py --write` |
| `validation/checker-prototype/coverage.json` | json-object | 生成器 `scripts/check_coverage_gate.py --write` |

## 3. 区的含义与检查强度

| 区 | 允许形态 | 检查 |
|---|---|---|
| `数据区` | 本表登记的结构化文件 | 解析 + schema（成熟校验器，ADR-0019）+ 字段配额与集合上限（`RM-SCHEMA` / `RM-FIELD`）；schema 完整性 lint 与官方元 schema 校验（`RM-SCHEMA-LINT`）；散文按 `x-prose-fields` 逐路径计量 + `x-prose-budget` 单条总和兜底 + 单文件 32 KiB |
| `本体区` | `.ttl`、`.nt`、`.n3`、`.owl`、`.rdf`、`.jsonld` | 头注释（全部本体扩展名）、谓词分档字面量、注释上限、目录点线、页码序列、`dcterms:source`/`pm:sourcePage` 存在性、`source_pages: n/a` 的可机械核验依据 |
| `散文区` | 散文与说明文档 | 原始文件扩展名与文件头、体积、二进制、乱码、控制字符、目录点线、引证长度、单行上限 |
| `代码与配置区` | 代码与配置 | 与散文区相同的硬约束（不含引证与目录点线两项散文判据） |

散文区分三级，差别在复核义务与转录件标识，不在内容形状：P0 根级治理与说明文档；P1 `adr/`、`spec/` 正文等规范性文档；P2 报告、复核转录、试点报告与用例，必须带“非权威、不构成关闭依据”一类的头注。

## 4. 新文件如何归区

1. 先按第 1 节前缀表判定；命中即用。
2. 前缀表未命中时，在提交前把该路径（精确文件或目录前缀）登记进第 1 节；不得先提交后登记。
3. 数据区新文件还必须同时登记进第 2 节；只登记区、不登记 schema 或生成器，仍报 `RM-SCHEMA`。
4. 未登记的路径一律 `RM-ZONE` 阻断。新增顶层目录不会获得默认放行。

本表原则上不设 `豁免`。确有暂时无法修正的合法文件时，按方案第 10.3 节登记 `validation/exemptions/<批次>.md`，写明路径、原因、责任人、到期里程碑与复核人；`豁免` 不得用于原始资料或提取产物，到期未移除即阻断。当前未启用任何豁免。

## 5. 修改程序

本表与 `scripts/check_no_raw_material.py` 是同一执行面对；修改归区或准入登记必须：

1. 与检查器改动同批提交；
2. 运行 `python3 scripts/check_no_raw_material.py --self-test` 与全仓检查；
3. 按 `AGENTS.md` 3.6.8 重冻 `scripts/checker-pins.json`；
4. 在 `CHANGELOG.md` 记录归区变化与影响文件数。

## 6. 一次性过检记录

- **日期**：2026-11-15（批次 0054）
- **基线**：`4c060fe`（阶段二完成、新检查器与 schema 生效）
- **对象**：`git ls-files` 的全部 138 个跟踪文件
- **归区分布**：D 18 / O 30 / P 71（P0 16、P1 42、P2 13）/ C 19；未归类 0
- **违规**：0 次检查器命中。**更正（批次 0057）**：原文写“数据区 18 个文件全部通过 schema”不成立——当时只有 1 个 JSONL、2 个试点数据文件与 2 个示例受内容 schema 约束，5 个人工维护文件仅做“结构化登记”、5 个生成器文件靠生成器自证、3 个 schema 文件只校验自身形态，合计 13/18 不受内容 schema 或字段配额约束。批次 0057 已为 5 个人工维护文件补内容 schema（D 区升至 22 个文件：10 个受 schema 约束、7 个 schema 自身、5 个生成器）。
- **逐文件核对方式**：对每个跟踪文件调用本表解析出的区与准入登记，再执行 `check_file()`；结果按区计数并列出全部违规。复跑命令：

```
python3 scripts/check_no_raw_material.py
```

- **复核后补检（批次 0057，基线 `deaac46`）**：复核报告（`/home/wgz/projects/skills/2026-11-14/pm-governance-review/verify-admission/REPORT.md`，sha256 `905cf234539cccb916f9096e3e137f12876e24b2fb9c1960a034157ac33aff06`）指出五类缺口——人工维护数据文件无内容 schema、`relations` 键无白名单、`prose_fields` 单条 2500 与 schema 允许的 2800 矛盾、归区表未进指纹、13.6 三项检查无人承接。本批已全部修正并重跑：全仓 0 命中，自测 43 项通过。

- **本体规则召回实测（批次 0061，基线 `3664b64`）**：`RM-ONTO-PAGESEQ` 与 `RM-ONTO-PROVENANCE` 按真实 TTL 形态重写后的实测结果——

| 规则 | 真实 TTL 基数 | 真实 TTL 命中 | 攻击输入命中 |
|---|---|---|---|
| `RM-ONTO-PAGESEQ` | 5 个文件；349 个页码值；连续页码三元组最长 1 行 | 0 | 299 行 `ex:pN pm:page N .` 转储 → 命中（起始行）；12 个以上逗号页码 → 命中；裸数字串 → 命中 |
| `RM-ONTO-PROVENANCE` | 501 个带定义或页码定位的块，全部可由术语级或文件头声明交代 | 0 | 来源与页码两项都缺的定义术语 → 命中；`source_pages: n/a` 但正文含页码值（声明矛盾）→ 命中 |

  旧版两条规则对同样输入均 0 命中：旧 `PAGESEQ` 只认裸数字串，旧 `PROVENANCE` 只在“有页码无来源”且文件头无 `source_id` 时触发。新版的判据改为“连续页码三元组 / 逗号页码表 / 裸数字串”与“逐块核对来源与页码，允许文件头 `source_id` + `source_pages` 统一声明”。文件头 `source_pages:` 现为 `RM-ONTO-HEADER` 的必填项（取值为页码范围或 `n/a`；`n/a` 与正文页码值矛盾即报错）。

- **`n/a` 依据收紧（批次 0063，基线 `11c5d92`）**：`source_pages: n/a` 不再是写一个词就成立的豁免。声明 `n/a` 时头注释还必须给出 `source_pages_basis:`，且依据须可机械核验——非空、非占位符（`n/a`、`TBD`、`待补` 等）、含仓库内**真实存在**的 `adr/NNNN-*.md` 引用，并在 ADR 引用之外另有自写理由。缺 `source_pages_basis:` 由 `RM-ONTO-HEADER` 阻断；写了但为空串、占位符或 ADR 引用不存在，由 `RM-ONTO-PROVENANCE` 阻断，并视为页码未交代（不再解除逐块页码义务）。`n/a` 与正文页码值矛盾的旧判据保留，依据不能抵消矛盾。当前两份标 `n/a` 的 TTL（`pmbok8-vocab.ttl`、`pmbok8-shapes.ttl`）已按此补齐依据；自测新增 7 项正负例。

- **校验语义换用成熟实现（批次 0064–0066，实现基线 `f049f28`）**：数据区与 schema 自身的校验改由 `jsonschema==4.26.0` 执行（ADR-0019），依赖以版本 + 安装树摘要 + 分发产物 sha256 三重指纹登记（`scripts/dependency-pins.json`）；缺少依赖即“无法评估”并退出 2，不降级为跳过。schema 自身先过官方 Draft 2020-12 元 schema；`x-prose-fields` 路径必须能在 schema 结构中解析，拼错即报错；`contracts/schema/` 的发现改为递归，子目录 schema 同样 lint、同样钉扎。r4 四类攻击面（`items: true`/元组、`enum`/`const` 跳过 `maxLength`、散文路径拼错静默失效、子目录逃检）逐项复现并由结构消除。复跑结果：全仓 0 命中；`--self-test` 76/76；`test_spec_pins.py` 9/9；`test_dependency_pins.py` 9/9。

- **豁免判定（D-6）**：0 违规，收敛为**不设豁免期**。依据：准入制要求“存量先合规、再切闸门”；存量已全部合规，若仍开豁免窗口，只会把已合规的存量重新暴露在无复核的例外通道下。未创建 `validation/exemptions/`；将来若出现暂时无法修正的合法文件，按第 4 节与方案第 10.3 节登记，且不得用于原始资料或提取产物。
- **边界**：本次过检证明“已登记的区与结构条件成立”，不证明内容不是原文。**未命中不等于合规**；来源层比对仍由仓库外指纹方案与人工评审承接。
