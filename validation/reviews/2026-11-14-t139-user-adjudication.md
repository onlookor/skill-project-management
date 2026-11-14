# T-139 字段语义拆分的非同源裁定记录

- 非同源复核：用户裁定（parent session `6af45947fead009e7bdd1e76`，批次 0048），2026-11-14
- 区段：GRAMMAR.md（`knowledge/` 条目来源字段说明）、`grounding_ref` 语义
- 复核产物：GRAMMAR.md；`spec/ANCHOR_SPEC.md`；`spec/CHECKER_INPUT_SCHEMA.md` §1.16；`knowledge/anchored-entries.jsonl`
- 复核基线：`563c26c`
- 结论：认可

## 裁定内容

用户同意把 `grounding_ref` 的两种意图拆开：

1. `grounding_ref` 只指向知识条目（`knowledge:<term>` 形态），或按 `GRAMMAR.md` 字段表指向 `SOURCE_LEDGER.md` 条目 ID（规则/方法条目）；
2. 知识条目的来源归属交给 `evidence[]`，每项至少含 `source_id`；
3. 现有 10 条指向来源 ID 的 `grounding_ref` 迁入 `evidence`；
4. 语义写入 `CHECKER_INPUT_SCHEMA.md` 与判定层文档中涉及 `grounding_ref` 的段落；
5. 试点 15 条草稿的引用同步对齐，`pilot-id-map.json` 随之更新。

## 边界

本记录是用户裁定的转录，用于检查器与规格区段的绑定核对；它不构成缺口关闭依据（`AGENTS.md` 3.6.6），也不证明复核者独立于实现方之外的代码审查。
