## GLOSSARY / JSONL 同步检查规格

**用途**：检查 `GLOSSARY.md` 的 A 类条目与 `knowledge/anchored-entries.jsonl` 的对应条目是否一致。执行结果用于 `spec/GROUNDING_CRITERIA.md` G4 的验证。

### 1. 检查项

**S1（条目存在性）**：`GLOSSARY.md` 的每个 A 类条目，其 `anchored_entry` 字段指向的条目必须在 `anchored-entries.jsonl` 中存在。反向不要求（JSONL 可以有条目未在 GLOSSARY 中登记，但需在 GLOSSARY 第 6 节“待补充”中登记）。

**S2（术语名一致）**：`GLOSSARY.md` 的 A 类条目的 `term` 字段必须与 `anchored-entries.jsonl` 对应条目的 `term` 字段一致。

**S3（定义一致）**：`GLOSSARY.md` 的 A 类条目的 `definition` 字段必须与 `anchored-entries.jsonl` 对应条目的 `definition` 字段**语义一致**。

- **“语义一致”的判定**：由人工评审判定，不由脚本自动判定。脚本只输出“两条定义的文本差异”，供人工评审参考。
- **完全一致**（文本逐字相同）：`pass`。
- **语义一致**（文本不同但含义相同）：`pass`，但记录差异供后续统一。
- **语义不一致**（含义不同）：`fail`，按 `CONSTITUTION.md` 第 11.5 条处置。

**S4（来源一致）**：`GLOSSARY.md` 的 A 类条目的 `grounding_ref` 所指向的来源 ID，必须出现在 `anchored-entries.jsonl` 对应条目 `evidence[].source_id` 中（若有）。知识条目的 `grounding_ref` 不承载来源，按 T-139 的拆分语义检查。

**S5（provenance_note 存在性）**：`GLOSSARY.md` 的 A 类条目与 JSONL 对应条目都必须有 `provenance_note` 字段；缺失则 `fail`（`CONSTITUTION.md` 第 3.2 条要求形式化边界说明）。

### 2. 输出格式

```json
{
  "check_id": "GLOSSARY_SYNC",
  "executed_at": "<时间戳>",
  "checks": [
    { "id": "S1", "verdict": "pass|fail", "details": [...] },
    { "id": "S2", "verdict": "pass|fail", "details": [...] },
    { "id": "S3", "verdict": "pass|fail|needs_review", "details": [
        { "term": "Assertion", "glossary_def": "...", "jsonl_def": "...", "diff": "..." }
    ]},
    { "id": "S4", "verdict": "pass|fail", "details": [...] },
    { "id": "S5", "verdict": "pass|fail", "details": [...] }
  ],
  "overall": "pass|fail|needs_review"
}
```

**overall 的判定**：
- 全部 `pass` → `pass`；
- 任一 `fail` → `fail`；
- 无 `fail` 但有 `needs_review` → `needs_review`（人工评审后决定）。

### 3. 实现形态（参考）

脚本可用任何语言实现（Python / Node / Shell）。输入为两个文件的路径；输出为上述 JSON。**实现细节不在本规格范围内**——本规格只规定检查项与输出格式；实现由 `TODO.md` T-102 跟进。

### 4. 与接地判据的关系

`spec/GROUNDING_CRITERIA.md` G4 要求“同步检查通过”。**通过的标准**：`overall` 为 `pass` 或 `needs_review` 且人工评审结论为“已接受差异”。`fail` 不通过 G4。
