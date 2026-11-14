# 试点检查产物摘录

**性质**：M3/M4 试点格式样例，`authoritative: false`。**不是检查执行结果**，用于验证同一份产物能否被三类消费者读取。
**机器可读源**：[spec/pilot/pilot-artifact.json](spec/pilot/pilot-artifact.json)

## 三类消费者

| 消费者 | 读取方式 | 是否需要改格式 |
|---|---|---|
| 人 | 读下方表格 | 否 |
| 脚本 | 解析 JSON 的 `clauses[]` 与 `aggregate` | 否 |
| M5 走查 | 按 `clause` 对应契约槽位，读取 `verdict` / `reason` | 否 |

## 子句结果

| check_id | 规则 | severity | 规则状态 | 子句 | 判定 | 原因 |
|---|---|---|---|---|---|---|
| `PROJECT_MINIMAL_EXISTENCE` | G-A1 | `block` | `active` | `G-A1#1` | `pass` | `all_required_nodes_present` |
| `CONSTRAINT_ANCHOR_REQUIRED` | G-A2 | `block` | `active` | `G-A2#1` | `cannot_evaluate` | `missing_input` |
| `DELIVERABLE_ASSERTION_LINK` | G-C1 | `block` | `active` | `G-C1#1` | `fail` | `assertion_missing` |
| `CHANGE_CONSTRAINT_LINK` | G-D1 | `advisory` | `active` | `G-D1#1` | `not_applicable` | `no_change_proposal` |
| `ROLE_MINIMAL_COMPLETENESS` | G-E1 | `block` | `active` | `G-E1#1` | `pass` | `accountable_present` |
| `PROJECT_CHARTER_EXISTENCE` | G-F1 | `advisory` | `assumption` | `G-F1#1` | `cannot_evaluate` | `source_not_available` |

## 聚合

`fail`。聚合顺序无关，优先级为 `fail` > `cannot_evaluate` > `pass` > `not_applicable`；表中出现 `fail` 即收敛到 `fail`，与列出顺序无关。

## 基线

- 产物 `source_commit`：`cc0cd2a882df66f87d381ca855f4590b11570763`
- 清单 `source_commit`：`0669a4b031f02dc6045c6b2696c5c9f3eb427a4b`
