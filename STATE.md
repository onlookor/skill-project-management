## 状态台账

**用途**：登记本目录中每个文件的当前状态。变更历史见 `CHANGELOG.md`；待办与任务状态见 `TODO.md`。本台账不记录历史批次，也不记录任务级待办。

**维护规则**：文件新增、删除或状态变化时更新本表；一次性的内容变更写入 `CHANGELOG.md`，未完成工作写入 `TODO.md`。

**状态取值**：

- `active`：当前有效，可被引用或执行。
- `skeleton`：结构已建立，内容待填充。
- `template`：模板，不承载现行内容。
- `example`：示例，非规范。
- `accepted`：已接受的决策记录。

| 文件 | 层 | 当前状态 | 说明 |
|---|---|---|---|
| `README.md` | 入口 | `active` | 定位、文件地图与阅读路径 |
| `AGENTS.md` | 执行 | `active` | 执行约定与目录结构权威 |
| `CHANGELOG.md` | 调度 | `active` | 批次变更历史 |
| `TODO.md` | 调度 | `active` | 待办与任务状态 |
| `STATE.md` | 调度 | `active` | 本文件：逐文件当前状态 |
| `CHARTER.md` | 意图 | `active` | 技能初衷与可检验承诺 |
| `CONSTITUTION.md` | 治理 | `active` | 元规则与治理程序 |
| `GRAMMAR.md` | 立法 | `active` | 成文法规则组 A–G |
| `SOURCE_LEDGER.md` | 立法 | `active` | 封闭来源登记表 |
| `GLOSSARY.md` | 立法（支撑） | `active` | 术语定义与术语治理 |
| `spec/COMPILATION_META.md` | 编译元框架 | `active` | 方法无关的编译元框架 |
| `spec/COMPILATION_METHODS.md` | 编译方法 | `active` | 编译方法注册表 |
| `spec/methods/deterministic-checker.md` | 编译方法 | `active` | 确定性校验器方法声明 |
| `spec/ASSUMPTION_PROTOCOL.md` | 执行 | `active` | `assumption` 区块协议 |
| `spec/INTERFACE_CONTRACT_SPEC.md` | 执行 | `active` | 接口契约与槽位定义 |
| `contracts/schema/pm-slot-contract.schema.json` | 契约 | `active` | 契约 JSON Schema |
| `contracts/resolver.md` | 契约 | `active` | 契约解析规则 |
| `contracts/examples/construction.pm-contract.yaml` | 契约 | `example` | 建筑施工领域样例 |
| `contracts/examples/software-engineering.pm-contract.yaml` | 契约 | `example` | 软件工程领域样例 |
| `knowledge/anchored-entries.jsonl` | 知识 | `active` | 本体条目 |
| `knowledge/methods/registry-skeleton.md` | 知识 | `skeleton` | 方法注册表骨架 |
| `adr/ADR-TEMPLATE.md` | 治理 | `template` | ADR 模板 |
| `adr/0001-separate-grammar-from-governance.md` | 治理 | `accepted` | 规范层与执行层分离决策 |
| `adr/0002-compilation-meta-vs-methods.md` | 治理 | `accepted` | 编译元框架与方法分离决策 |
| `validation/CHECKLIST.md` | 验证 | `active` | 检查项规格投影 |
| `.gitignore` | 仓库 | `active` | Git 忽略规则 |
