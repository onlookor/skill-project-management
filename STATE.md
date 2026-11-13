## 状态台账

**用途**：登记本目录中每个文件的当前状态。变更历史见 `CHANGELOG.md`；待办与任务状态见 `TODO.md`。本台账不记录历史批次，也不记录任务级待办。

**维护规则**：状态按目录给默认值，只有例外才逐文件标注。文件新增、删除或移动时更新默认值或例外表；一次性的内容变更写入 `CHANGELOG.md`，未完成工作写入 `TODO.md`。

**对账**：`python3 scripts/check_state.py` 以 `git ls-files` 为准核对本台账——文件漏登、登了未跟踪的文件、状态值非法均报错并以非零码退出。

**状态取值**：

- `active`：当前有效，可被引用或执行。
- `skeleton`：结构已建立，内容待填充。
- `template`：模板，不承载现行内容。
- `example`：示例，非规范。
- `accepted`：已接受的决策记录。

## 目录默认值

按最长前缀匹配；`./` 表示根目录下不含目录前缀的文件。

| 范围 | 默认状态 |
|---|---|
| `./` | `active` |
| `.githooks/` | `active` |
| `spec/` | `active` |
| `contracts/` | `active` |
| `contracts/examples/` | `example` |
| `knowledge/` | `active` |
| `ontology/` | `skeleton` |
| `adr/` | `accepted` |
| `scripts/` | `active` |
| `validation/` | `active` |

## 例外

| 文件 | 状态 | 说明 |
|---|---|---|
| `adr/ADR-TEMPLATE.md` | `template` | 模板，不承载已接受的决策 |
| `knowledge/methods/registry-skeleton.md` | `skeleton` | 方法注册表骨架，条目待填充 |
