## 辅助脚本

**性质**：本目录存放技能的辅助检查脚本及其规格。`check_state.py`、`check_ledger_landings.py` 与 `check_anchors.py` 已实现且可直接运行；`check_glossary_sync` 仍为规格，实现登记于 `TODO.md` T-090。

### 脚本清单

| 脚本 | 用途 | 规格文件 | 实现状态 |
|---|---|---|---|
| `check_state.py` | 以 `git ls-files` 核对 `STATE.md`：漏登、登了不存在的文件、状态值非法 | 无独立规格（规则见 `STATE.md` 与本文件“脚本的定位”） | 已实现 |
| `check_ledger_landings.py` | 核对 `SOURCE_LEDGER.md` 每个 active 来源条目是否声明编译落点，且落点在 `GRAMMAR.md`、`knowledge/`、方法条目或检查项中真实存在 | 无独立规格（规则见 `CONSTITUTION.md` 第 2.6 条） | 已实现 |
| `check_anchors.py` | 解析并校验全仓锚点：禁止行号 locator、文件/稳定 ID/章节号/标题路径可解析、`grounding_ref` 指向 active 来源、规则与来源文本块指纹未漂移 | `spec/ANCHOR_SPEC.md` | 已实现 |
| `anchor_baseline.json` | `check_anchors.py` 的指纹基线（`rule:*` 与 `source:*`），内容变更后重冻 | `spec/ANCHOR_SPEC.md` 第 5 节 | 数据文件 |
| `check_glossary_sync` | 检查 `GLOSSARY.md` 的 A 类条目与 `knowledge/anchored-entries.jsonl` 的定义一致性 | `check_glossary_sync.md` | 未实现（T-090） |

### 运行方式

```
python3 scripts/check_state.py
python3 scripts/check_ledger_landings.py
python3 scripts/check_anchors.py
```

`check_state.py` 退出码：`0` 通过；`1` 存在错误（逐条列出）；`2` `STATE.md` 结构无法解析或不在 git 仓库中。

`check_ledger_landings.py` 退出码：`0` 通过（可有待落点警告）；`1` 存在错误；`2` 登记表结构无法解析。

`check_anchors.py` 退出码：`0` 通过（可有警告/提示）；`1` 存在错误；`2` 结构或基线无法解析。规则/来源被有意修改后，用 `--write-baseline` 重冻基线，并把基线变更与内容变更同批提交。`--root` 可指向副本，用于插行负例演练。

### 脚本的定位

- 脚本是**辅助工具**，不是技能的核心规范。它们的缺失不构成技能不完备（`CHARTER.md` 承诺 C4 的延伸）。
- 脚本的执行结果是**证据工件**，可用于 `spec/GROUNDING_CRITERIA.md` G4 的验证。
- 脚本的规格（如 `check_glossary_sync.md`）是**规范性的**——脚本实现必须与规格一致；规格与实现冲突时以规格为准。
