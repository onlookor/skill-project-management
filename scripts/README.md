## 辅助脚本

**性质**：本目录存放技能的辅助检查脚本规格。**当前为规格形态，尚未实现为可执行脚本**（实现登记于 `TODO.md` T-102）。

### 已登记的脚本规格

| 脚本 | 用途 | 规格文件 | 实现状态 |
|---|---|---|---|
| `check_glossary_sync` | 检查 `GLOSSARY.md` 的 A 类条目与 `knowledge/anchored-entries.jsonl` 的定义一致性 | `check_glossary_sync.md` | 未实现（T-102） |

### 脚本的定位

- 脚本是**辅助工具**，不是技能的核心规范。它们的缺失不构成技能不完备（`CHARTER.md` 承诺 C4 的延伸）。
- 脚本的执行结果是**证据工件**，可用于 `spec/GROUNDING_CRITERIA.md` G4 的验证。
- 脚本的规格（如 `check_glossary_sync.md`）是**规范性的**——脚本实现必须与规格一致；规格与实现冲突时以规格为准。
