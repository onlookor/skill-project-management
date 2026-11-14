# ADR-0017: `grounding_ref` 与来源归属拆成两种意图（T-139）

- **状态**：`accepted`（2026-11-14）
- **日期**：2026-11-14
- **决策者**：用户（批次 0048 裁定，由架构负责人执行）
- **serves_charter**：C3（来源封闭、可追溯）、C6（可机械检查、可审计）
- **grounding_refs**：无（决策针对字段语义本身，不依赖来源条目）
- **affected_files**：`knowledge/anchored-entries.jsonl`（10 条 `grounding_ref` → `evidence[]`）、`scripts/check_anchors.py`（校验 `evidence[].source_id`）、`spec/CHECKER_INPUT_SCHEMA.md` §1.16、`spec/ANCHOR_SPEC.md`、`GRAMMAR.md`、`GLOSSARY.md`（T-B-003）、`spec/methods/deterministic-checker.md`、`scripts/check_glossary_sync.md`、`scripts/README.md`、`spec/pilot/pilot-entries.json`、`spec/pilot/pilot-id-map.json`

## 1. 问题

D3 决定 `grounding_ref` 指向知识条目（`knowledge:<term>`），但 `knowledge/anchored-entries.jsonl` 现有 10 条把来源 ID 写在 `grounding_ref`。同一字段承载两种意图：

| 意图 | 期望取值 |
|---|---|
| 规则正文对来源的锚定 | `SOURCE_LEDGER.md` 条目 ID |
| 规则或本体对知识条目的绑定 | `knowledge:<term>` |
| 知识条目自身的来源归属 | 来源条目 ID（与第一类同形，但语义不同） |

试点 15 条又出现把草稿 ID 当 `knowledge:` 值的自指写法，进一步说明字段语义未封闭。若不拆开，`check_anchors.py` 无法区分“规则锚定”与“条目来源”，扩量时会把来源归属误当规则锚定校验。

## 2. 决定

**按两种意图拆字段，不复用同一字段。**

1. **规则/方法条目**的 `grounding_ref` 继续按 `GRAMMAR.md` 字段表指向 `SOURCE_LEDGER.md` 条目 ID；`null` 表示 `assumption`。
2. **本体或规则到知识条目的绑定**取 `knowledge:<term>`。
3. **知识条目自身的来源归属**写入 `evidence[]`，每项至少含 `source_id`，可附 `locator` / `page` / `precision` / `verification`。知识条目不再使用 `grounding_ref` 承载来源。
4. `spec/CHECKER_INPUT_SCHEMA.md` 的检查输入不携带 `grounding_ref`；`scripts/check_anchors.py` 分别校验规则 `grounding_ref` 与知识条目 `evidence[].source_id` 均可解析到 active 来源。
5. 试点草稿删除自指的 `grounding_ref`，保留 `evidence`；映射关系继续由 `spec/pilot/pilot-id-map.json` 承载。

## 3. 考虑过的选项

| 选项 | 为什么不选 |
|---|---|
| 修订 D3，让 `grounding_ref` 只指向来源 | 会破坏 D3 已批准的“规则到知识条目绑定”用法，且规则锚定仍需来源 |
| 新增独立 `source_ref` 字段 | 与 D2 已定的五字段扩展冲突，增加一个仅知识条目使用的平行字段 |
| 维持现状、靠文档约定区分 | 检查器无法机械区分两种意图，扩量后必然误报或漏报 |

## 4. 后果

**正向**：字段意图封闭，检查器可按对象类型分别校验；知识条目来源可携带页码与精度，不必挤进单个字符串。

**负向**：迁移了 10 条权威条目，旧引用若仍读 `grounding_ref` 需同步改造；`grounding_ref` 的文档说明分散在 `GRAMMAR.md`、`ANCHOR_SPEC.md`、`GLOSSARY.md` 与 schema，需保持一致。

## 5. 关联

- `TODO.md` T-139（本 ADR 的登记项）。
- `spec/CHECKER_INPUT_SCHEMA.md` §1.16。
- `spec/ANCHOR_SPEC.md`“`grounding_ref` 的两种意图”。
- ADR-0013（判定层表示规范）。
