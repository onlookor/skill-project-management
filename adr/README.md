## ADR 说明

本目录存放本技能的治理决策记录。ADR 回答“为什么这样治理”；`CHANGELOG.md` 回答“什么时候、哪些文件被改了”。

### 何时需要 ADR

按 `CONSTITUTION.md` 第 4 条：修改 `CHARTER.md` 的承诺、`GRAMMAR.md` 的规则、`SOURCE_LEDGER.md` 的条目、`CONSTITUTION.md` 的条款，或改变已有规则编译结果的结构性变更，必须附 ADR。

### 可选格式

ADR 不限于一种格式。以下三种均为本目录接受的形态，选择一种并保持一致：

| 格式 | 结构 | 适用场景 |
|---|---|---|
| **Nygard** | 标题 / 状态 / 背景 / 决定 / 结果 | 默认格式。决策明确、后果可枚举时最简洁 |
| **MADR** | 背景与问题 / 考虑过的选项 / 决定 / 后果（含正负） | 选项多、需要并列比较时 |
| **Y-Statement** | 在〈情境〉下，面对〈关注点〉，我们决定〈选项〉，以达到〈目标〉，接受〈后果〉 | 一句话即可说清的轻量决策；也可作为长 ADR 的摘要行 |

本地参考资料：`resources/se/adr/madr/`（MADR 模板与指南）、`resources/se/adr/yadr/`（Y-Statement 模板与示例）。本仓库不复制其原文，只采用其结构。

### 本仓库的强制字段

无论采用哪种格式，`adr/NNNN-*.md` 必须包含以下字段，模板见 `ADR-TEMPLATE.md`：

- `状态`：`proposed` / `accepted` / `deprecated` / `superseded`；
- `日期`；
- `决策者`；
- `serves_charter`：服务于 `CHARTER.md` 的哪条承诺，或声明要修改哪条承诺；
- `grounding_refs`：所依据的 `SOURCE_LEDGER.md` 条目 ID；治理自身的决策写“无”；
- `affected_files`：修改了哪些文件的哪些条款。

### 编号与状态

- 文件名 `NNNN-短横线标题.md`，编号四位、递增、不复用。
- 只有 `accepted` 的 ADR 才能作为修改立法文件的依据。
- 被取代的 ADR 保留原文，状态改为 `superseded`，并在新 ADR 中引用旧编号；ADR 正文不回改历史结论。
