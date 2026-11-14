# ADR-0016: 放宽 `PMBOK8-2025` 至概念层用途

- **状态**：`accepted`（2026-11-14）
- **日期**：2026-11-14
- **决策者**：用户（人类责任方）批准；架构负责人执行
- **serves_charter**：C3（来源封闭、可追溯）、C6（可机械检查、可审计）
- **grounding_refs**：PMBOK8-2025
- **affected_files**：`SOURCE_LEDGER.md`（`PMBOK8-2025` 的 `allowed_uses` / `verification_method` / `claim_mapping`）、`TODO.md`（T-123）、`knowledge/anchored-entries.jsonl`（来源迁移至 `evidence`）、`spec/ANCHOR_SPEC.md`、`spec/CHECKER_INPUT_SCHEMA.md`、`GRAMMAR.md`、`GLOSSARY.md`、`spec/pilot/`、`CHANGELOG.md`

## 1. 背景

M3/M4 试点（批次 0047）的 15 条草稿全部以 `PMBOK8-2025` 为证据来源。该来源此前的 `allowed_uses` 为“仅限原则层面的交叉验证”，不得作为概念层条目的依据；试点因此只能把来源写成候选，无法正当落为知识条目的 `evidence`。M3 放量会把这一限制放大到数百条条目。

## 2. 决定

把 `PMBOK8-2025` 的允许用途从“仅原则层”放宽为“原则层与概念层均可用”：

- **保留**：原则层交叉验证。
- **新增**：作为工件、工具与技术、过程、焦点区、绩效域等知识条目的术语名、定义结构与页码范围证据来源，写入条目的 `evidence[]`。
- **仍不包含**：成段摘录入库（`CONSTITUTION.md` 第 13 条）；以原文替代自写定义；未核页的批量引用；规则正文的直接锚定（规则仍须经本表 `claim_mapping` 显式包含）。

`claim_mapping` 不新增规则映射；概念层条目的来源归属写在各自 `evidence[]`，不进入该字段。

## 3. 后果

- 15 条试点草稿与后续 M3 条目可以正当地把该来源写入 `evidence[].source_id`。
- 不改变 `CONSTITUTION.md` 第 13 条：仍禁止原始资料与成段提取产物入库；自建定义必须自写。
- `scripts/check_ledger_landings.py` 的 active 来源落点要求不变；本次放宽不新增落点，只扩大允许用途。
- 若后续把该来源用于规则正文的直接锚定，须另立 ADR 并更新 `claim_mapping`。
