#!/usr/bin/env python3
"""规格区段绑定：GRAMMAR.md 全文、A.2、A.1、CHECKER_INPUT_SCHEMA.md **整文件**、
全部数据 schema、coverage.json 与 ACCESS_ZONES.md。

规则：
  1. 任一区段当前指纹与 scripts/spec-pins.json 不一致 → 阻断（先 --write）；
  2. `contracts/schema/` 下任何文件未登记为区段 → 阻断（自动发现，取代人工清单）；
  3. 区段相对 HEAD 有改动时，同一提交必须附合格的非同源复核记录，否则阻断；
  4. basis 只有两种合法形态：(a) 合格的非同源复核记录——指向**仓库外**存在的产物、
     `sha256：` 与之一致、`复核基线：` 是 HEAD 的祖先提交、唯一且等值的 `区段：`、
     **行尾**结论词（后面不得跟括号补充），并且**该基线处的同一区段内容必须与当前
     内容一致**——区段在基线之后被改过即 basis 失效，必须重新取证；(b) 固定字面量
     `无复核声明（不构成认可，不放行）`——它记录事实但**永不放行**，登记项会持续
     报错，只能 `git commit --no-verify` 并在 `scripts/no-review-declarations.json`
     与 `TODO.md` 到期项中留痕（AGENTS.md 3.5.3）。不存在“待复核/初始登记”通行证。

  5. A.2 的内容比较沿用 `check_three_table.a2_block_fingerprint` 的既有口径：
     复核签收行是“复核记录”本身，不是被签收的内容，不参与比较（除此行外，
     A.2 的其余文本仍逐字比较）。若签收行参与比较，写入复核记录这一动作就会让
     被签收对象失效，合格在结构上不可达。
     **排除范围仅限“那一条固定模板的签收行”**：须整行匹配
     `> 复核签收：外部复核基线 `<7–40 位十六进制>`；<YYYY-MM-DD>；A.2 指纹 `<12 位十六进制>``，
     行内不得含任何自由文本（批次 0088 甲方案：原括号叙述已移入
     `validation/reviews/2026-11-15-a2-signoff-record.md`）。A.2 内至多一行，且必须是
     区段最后一条非空行。任何不符合模板的行一律不排除、参与比较，从而该死判 basis 失效。
     理由与范围见 `validation/reviews/2026-11-15-a2-comparison-scope.md`。
     `--write` 只登记区段指纹，不生成也不改写签收行；签收行只能按上述固定模板人工写入，
     因而不存在“由工具重写签收行”的路径。
     另核验签收行事实（批次 0090；0092 收紧）：所载基线必须与登记 basis 的 `复核基线：`
     解析为同一提交且在仓库存在；日期须为合法日历日期，并与登记项同级字段
     `review_date`（`{"value": "YYYY-MM-DD", "origin": "executor"}`）一致。日期证据
     **只能**来自 `复核产物：` 所指文件自身：该文件须含**恰好一个**独占一行的专用记号
     `<!-- 复核日期：YYYY-MM-DD -->`，且该记号不得位于围栏代码块内；缺记号即报
     “日期未核验”。批次 0091 的独立 `日期记录：` 文件与任意位置的同日子串一律不再算
     佐证——执行方可以自建这类文件，等于自证。日期证据只在 `evaluate()` 中检查，
     不进入 `--write` 的结构门，否则“日期未核验”会让指纹刷新结构性不可达。
  6. 已判失效的对象可在登记项上带 `invalidated`（字符串原因）作为**显示层**标记：
     它不改变 basis 原文，也不改变判定（`valid_basis()` 仍是唯一依据）；检查器报错时
     附出该标记，且 basis 又变得可验证通过时会要求人工核实并移除标记。`--write` 原样
     保留该字段，不自动清除。
  7. `--write` 新增或变更的区段必须附 `--basis`（合格复核记录，或无复核字面量）。

记录文件放在 validation/reviews/ 下并在同一提交暂存；也可用 --review 指定。
这不是“签收人身份验证”：机器只能核对记录的存在与字段，不能验证复核者是谁。

用法：
  python3 scripts/check_spec_pins.py
  python3 scripts/check_spec_pins.py --write --basis "非同源复核：... 复核产物：/abs/report.md sha256：<64hex> 复核基线：3664b64"
  python3 scripts/check_spec_pins.py --review validation/reviews/20261114-xxx.md
退出码：0 = 一致；1 = 指纹未更新或缺少复核记录；2 = 解析/登记缺失或 basis 不合格。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

PINS = Path("scripts/spec-pins.json")
REGISTRY = Path("scripts/no-review-declarations.json")
METHOD = "spec/methods/deterministic-checker.md"
SCHEMA = "spec/CHECKER_INPUT_SCHEMA.md"
AGENTS = "AGENTS.md"
SCHEMA_DIR = "contracts/schema"
CONCLUSIONS = ("实质收敛", "认可", "通过")
# 唯一允许的“无复核”字面量：它记录事实，但不构成认可、也不放行。
DECLARATION = "无复核声明（不构成认可，不放行）"
REGISTRY_FIELDS = ("reason", "missing_review", "due", "owner", "todo")


def load_registry(root: Path) -> dict:
    path = root / REGISTRY
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("spec", {}) if isinstance(data, dict) else {}


SECTIONS = (
    {"key": "GRAMMAR.md", "path": "GRAMMAR.md", "start": None, "end": None},
    {"key": f"{METHOD}#A.2", "path": METHOD, "start": "### A.2 ", "end": "### A.1 "},
    {"key": f"{METHOD}#A.1", "path": METHOD, "start": "### A.1 ", "end": None},
    {"key": SCHEMA, "path": SCHEMA, "start": None, "end": None},
    {"key": f"{AGENTS}#3.5", "path": AGENTS, "start": "#### 3.5 ", "end": "#### 3.6 "},
    {
        "key": "validation/checker-prototype/coverage.json",
        "path": "validation/checker-prototype/coverage.json",
        "start": None,
        "end": None,
    },
    {
        "key": "contracts/schema/knowledge-entry.schema.json",
        "path": "contracts/schema/knowledge-entry.schema.json",
        "start": None,
        "end": None,
    },
    {
        "key": "contracts/schema/pilot-conflict.schema.json",
        "path": "contracts/schema/pilot-conflict.schema.json",
        "start": None,
        "end": None,
    },
    {
        "key": "contracts/schema/pm-slot-contract.schema.json",
        "path": "contracts/schema/pm-slot-contract.schema.json",
        "start": None,
        "end": None,
    },
    {
        "key": "contracts/schema/package-manifest.schema.json",
        "path": "contracts/schema/package-manifest.schema.json",
        "start": None,
        "end": None,
    },
    {
        "key": "contracts/schema/ontology-fixtures-manifest.schema.json",
        "path": "contracts/schema/ontology-fixtures-manifest.schema.json",
        "start": None,
        "end": None,
    },
    {
        "key": "contracts/schema/pilot-artifact.schema.json",
        "path": "contracts/schema/pilot-artifact.schema.json",
        "start": None,
        "end": None,
    },
    {
        "key": "contracts/schema/pilot-id-map.schema.json",
        "path": "contracts/schema/pilot-id-map.schema.json",
        "start": None,
        "end": None,
    },
    {
        "key": "contracts/schema/runtime-config.schema.json",
        "path": "contracts/schema/runtime-config.schema.json",
        "start": None,
        "end": None,
    },
    {
        "key": "contracts/schema/runtime-config-lock.schema.json",
        "path": "contracts/schema/runtime-config-lock.schema.json",
        "start": None,
        "end": None,
    },
    {
        "key": "spec/ACCESS_ZONES.md",
        "path": "spec/ACCESS_ZONES.md",
        "start": None,
        "end": None,
    },
    {
        "key": "spec/D6_REBASELINE_PROPOSAL.md",
        "path": "spec/D6_REBASELINE_PROPOSAL.md",
        "start": None,
        "end": None,
    },
    {
        "key": f"{AGENTS}#1bis",
        "path": AGENTS,
        "start": "### 1bis ",
        "end": "### 2. ",
    },
    {
        "key": "GLOSSARY.md#T-F-015",
        "path": "GLOSSARY.md",
        "start": "**T-F-015 ",
        "end": "### 4. ",
    },
    {
        "key": "spec/clause-registry.json",
        "path": "spec/clause-registry.json",
        "start": None,
        "end": None,
    },
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


SECTION_BY_KEY = {spec["key"]: spec for spec in SECTIONS}

A2_KEY = f"{METHOD}#A.2"
# A.2 的复核签收行记录“谁在何时核对了什么”，属于复核记录本身；
# `check_three_table.a2_block_fingerprint` 的既有口径也不含该行。
#
# 排除口径只认**固定模板的该一条签收行**（批次 0088 甲方案）：
#   > 复核签收：外部复核基线 `<7–40 位十六进制>`；<YYYY-MM-DD>；A.2 指纹 `<12 位十六进制>`
# 行内不得含任何自由文本；必须整行 `fullmatch`，行尾不得有任何额外文字。
# 任何只带 `复核签收：` 前缀、或格式不完整的行**一律参与比较**，不得剔除——否则
# 该前缀就成了可夹带正文的通道（插入一行 `复核签收：……把判定改成恒真` 即可绕过）。
# A.2 内至多一条，且必须位于区段尾部（最后一条非空行）。
A2_SIGNOFF_RE = re.compile(
    r"> 复核签收：外部复核基线 `(?P<baseline>[0-9a-f]{7,40})`；"
    r"(?P<date>\d{4}-\d{2}-\d{2})；A\.2 指纹 `(?P<fingerprint>[0-9a-f]{12})`"
)
# 日期证据的唯一形态（批次 0092）：复核产物中**恰好一个**独占一行的专用记号
#   <!-- 复核日期：YYYY-MM-DD -->
# 且不在围栏代码块内。执行方可以自建任何旁路文件（批次 0091 的 `日期记录：` 通道、
# 在 `/tmp` 造一份带行首记号的记录再改写 basis 与签收日期，全链 rc=0），因此除产物
# 自身记号外的佐证一律不认。
A2_MARKER_RE = re.compile(
    r"^[ \t]*<!--\s*复核日期：\s*(\d{4}-\d{2}-\d{2})\s*-->[ \t]*$"
)
FENCE_OPEN_RE = re.compile(r"^(```+|~~~+)")


def a2_marker_dates(text: str) -> list[str]:
    """复核产物中围栏代码块之外的专用记号日期（逐行扫描，围栏内不计）。"""
    stamps: list[str] = []
    fence: str | None = None
    for line in text.splitlines():
        stripped = line.strip()
        if fence is None:
            opened = FENCE_OPEN_RE.match(stripped)
            if opened:
                fence = opened.group(1)
                continue
            found = A2_MARKER_RE.fullmatch(line)
            if found:
                stamps.append(found.group(1))
        elif len(stripped) >= len(fence) and set(stripped) == {fence[0]}:
            fence = None
    return stamps


def resolve_commit(root: Path, ref: str) -> str | None:
    """把提交号（含缩写）解析为完整对象 id；不可解析返回 None。"""
    result = subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}"],
        cwd=root,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() or None if result.returncode == 0 else None


def a2_date_evidence_errors(
    root: Path, key: str, basis: str | None, stamp: str
) -> list[str]:
    """登记日期须由 `复核产物：` 文件自身**恰好一个**专用记号佐证；否则“日期未核验”。"""
    artifact = re.search(r"复核产物：`?([^`\s；，、]+)`?", basis or "")
    if artifact is None:
        return [f"{key}：日期未核验：basis 无 `复核产物：`，无法核对日期 `{stamp}`"]
    path = Path(artifact.group(1))
    if not path.is_file():
        return [f"{key}：日期未核验：复核产物不存在，无法核对日期：{path}"]
    stamps = a2_marker_dates(path.read_text(encoding="utf-8", errors="replace"))
    if not stamps:
        return [
            f"{key}：日期未核验：复核产物 {path.name} 中缺少专用记号"
            f" `<!-- 复核日期：{stamp} -->`（须独占一行且不在围栏代码块内）"
        ]
    if len(stamps) > 1:
        return [
            f"{key}：日期未核验：复核产物 {path.name} 中出现 {len(stamps)} 个专用记号"
            "（只认恰好一个）"
        ]
    if stamps[0] != stamp:
        return [
            f"{key}：日期未核验：复核产物 {path.name} 的记号为 `{stamps[0]}`，"
            f"与登记日期 `{stamp}` 不一致"
        ]
    return []


def a2_signoff_fact_errors(
    root: Path, key: str, match: re.Match, basis: str | None
) -> list[str]:
    """签收行的结构核验：基线与 basis 一致且存在；日期为合法日历日期。

    日期是否有凭据属于证据核验，放在 `a2_signoff_date_errors()`，只在 `evaluate()`
    调用：若并入门内，“日期未核验”会让 A.2 的指纹刷新结构性不可达。
    """
    errors: list[str] = []
    text = basis or ""
    signed_baseline = match.group("baseline")
    signed_at = match.group("date")
    recorded = re.search(r"复核基线：`?([0-9a-f]{7,40})`?", text)
    if recorded is None:
        errors.append(
            f"{key}：basis 无可比对的 `复核基线：`，签收行基线 `{signed_baseline}`"
            f"与日期 `{signed_at}` 无法核验"
        )
        return errors
    if signed_baseline != recorded.group(1):
        signed_id = resolve_commit(root, signed_baseline)
        recorded_id = resolve_commit(root, recorded.group(1))
        if signed_id != recorded_id:
            errors.append(
                f"{key}：签收行基线 `{signed_baseline}` 与 basis "
                f"`复核基线：{recorded.group(1)}` 不一致"
            )
    if resolve_commit(root, signed_baseline) is None:
        errors.append(f"{key}：签收行基线不存在于仓库：{signed_baseline}")
    try:
        date.fromisoformat(signed_at)
    except ValueError:
        errors.append(f"{key}：签收行日期不是合法日历日期：{signed_at}")
    return errors


def a2_signoff_date_errors(
    root: Path, spec: dict, text: str, entry: dict | None
) -> list[str]:
    """日期核验（仅 evaluate）：登记日期、签收日期、产物记号三者一致。"""
    if spec["key"] != A2_KEY or not isinstance(entry, dict):
        return []
    body = section_text(text, spec["start"], spec["end"])
    match = next(
        (found for line in body.splitlines() if (found := A2_SIGNOFF_RE.fullmatch(line))),
        None,
    )
    if match is None:
        return []
    key = spec["key"]
    signed_at = match.group("date")
    registered = entry.get("review_date")
    value = registered.get("value") if isinstance(registered, dict) else None
    origin = registered.get("origin") if isinstance(registered, dict) else None
    if not value or not origin:
        return [
            f"{key}：日期未核验：登记项缺少 `review_date`"
            "（`{\"value\": \"YYYY-MM-DD\", \"origin\": \"executor\"}`）"
        ]
    errors: list[str] = []
    try:
        date.fromisoformat(value)
    except (TypeError, ValueError):
        errors.append(f"{key}：日期未核验：登记的 `review_date.value` 不是合法日历日期：{value}")
    if value != signed_at:
        errors.append(
            f"{key}：日期未核验：签收行日期 `{signed_at}` 与登记日期 `{value}` 不一致"
        )
    errors.extend(
        a2_date_evidence_errors(root, key, entry.get("basis"), value)
    )
    return errors


def a2_signoff_errors(
    root: Path, spec: dict, text: str, basis: str | None = None
) -> list[str]:
    """A.2 只允许一条固定模板签收行，必须在区段尾部，且事实可核验。"""
    if spec["key"] != A2_KEY:
        return []
    body = section_text(text, spec["start"], spec["end"])
    content = [line for line in body.splitlines() if line.strip()]
    matches = [
        (index, A2_SIGNOFF_RE.fullmatch(line))
        for index, line in enumerate(content)
        if A2_SIGNOFF_RE.fullmatch(line)
    ]
    if len(matches) > 1:
        return [
            f"{spec['key']}：复核签收行至多一行（实得 {len(matches)} 行模板签收行）；"
            "多行签收不得被当作复核记录剔除，须保留唯一一条"
        ]
    if not matches:
        return []
    index, match = matches[0]
    errors: list[str] = []
    if index != len(content) - 1:
        errors.append(
            f"{spec['key']}：复核签收行必须是区段最后一条非空行"
            f"（当前位于倒数第 {len(content) - index} 行）"
        )
    errors.extend(a2_signoff_fact_errors(root, spec["key"], match, basis))
    return errors


def comparable_text(spec: dict, text: str) -> str:
    """按区段定位取文本；A.2 只去掉那一条固定模板签收行，其余逐字比较。"""
    body = section_text(text, spec["start"], spec["end"])
    if spec["key"] != A2_KEY:
        return body
    return "\n".join(
        line for line in body.splitlines() if not A2_SIGNOFF_RE.fullmatch(line)
    ).rstrip("\n")


def baseline_section(root: Path, sha: str, spec: dict) -> str | None:
    """按区段定位规则，从 `git show <sha>:<path>` 中取出同一区段文本。"""
    shown = subprocess.run(
        ["git", "show", f"{sha}:{spec['path']}"], cwd=root, capture_output=True
    )
    if shown.returncode != 0:
        return None
    try:
        return comparable_text(spec, shown.stdout.decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        return None


def discover_schema_files(root: Path) -> list[str]:
    """`contracts/schema/` 下全部文件（含子目录）；未登记为区段即视为漏钉。"""
    directory = root / SCHEMA_DIR
    if not directory.is_dir():
        return []
    return sorted(
        path.relative_to(root).as_posix()
        for path in directory.rglob("*")
        if path.is_file()
    )


def valid_basis(root: Path, text: str, key: str) -> tuple[bool, str]:
    """basis 只接受合格的非同源复核记录；“无复核声明”记录事实但永不通过。"""
    text = text.strip()
    if text == DECLARATION:
        return False, (
            "无复核声明：不构成认可，也不放行（例外只能 --no-verify 提交，并须在 "
            "scripts/no-review-declarations.json 与 TODO.md 到期项中留痕）"
        )
    if "非同源复核：" not in text:
        return False, "缺少 `非同源复核：` 前缀"
    artifact = re.search(r"复核产物：`?([^`\s；，、]+)`?", text)
    if artifact is None:
        return False, "缺少 `复核产物：<路径>`"
    artifact_path = Path(artifact.group(1))
    if not artifact_path.exists():
        return False, f"复核产物不存在：{artifact_path}"
    try:
        artifact_path.resolve().relative_to(root.resolve())
    except ValueError:
        pass
    else:
        return False, "复核产物位于本仓库内；转录件只作索引，不能作为 basis"
    baseline = re.search(r"复核基线：`?([0-9a-f]{7,40})`?", text)
    if baseline is None:
        return False, "缺少 `复核基线：<提交号>`"
    sha = baseline.group(1)
    exists = subprocess.run(
        ["git", "cat-file", "-e", f"{sha}^{{commit}}"], cwd=root, capture_output=True
    )
    if exists.returncode != 0:
        return False, f"复核基线不存在：{sha}"
    ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", sha, "HEAD"],
        cwd=root,
        capture_output=True,
    )
    if ancestor.returncode != 0:
        return False, f"复核基线不是 HEAD 的祖先提交（无关提交）：{sha}"
    recorded = re.search(r"sha256：`?([0-9a-f]{64})`?", text)
    if recorded is None:
        return False, "缺少 `sha256：<64 位十六进制>`"
    if digest(artifact_path) != recorded.group(1):
        return False, "`sha256` 与复核产物不一致"
    segments = re.findall(r"区段：\s*`?([^`\s；，、]+)`?", text)
    if segments != [key]:
        return False, f"`区段：` 必须精确等于 {key} 且只出现一次"
    if re.search(r"结论：\s*(?:不|未|无法)", text) is not None:
        return False, "结论词被否定（`不予`/`未`/`无法` 前缀）"
    if re.search(
        rf"结论：\s*(?:{'|'.join(CONCLUSIONS)})(?=[ \t]*(?:$|[；;。]))", text, re.M
    ) is None:
        return False, (
            f"缺少结论词或其后紧跟补充说明（{'/'.join(CONCLUSIONS)}）；"
            "结论词后只允许行尾或 `；`/`。` 分隔，不得跟括号"
        )
    spec = SECTION_BY_KEY.get(key)
    if spec is None:
        return False, f"未登记的区段：{key}"
    base_text = baseline_section(root, sha, spec)
    if base_text is None:
        return False, f"复核基线 {sha} 中不存在区段 {key} 的源文件或起点"
    try:
        current_text = comparable_text(
            spec, (root / spec["path"]).read_text(encoding="utf-8")
        )
    except (OSError, ValueError) as exc:
        return False, f"无法定位当前区段 {key}：{exc}"
    if base_text != current_text:
        return False, (
            f"basis 失效：复核基线 {sha} 处的区段 {key} 内容与当前内容不一致，"
            "需重新取证（复核只对基线处的内容负责）"
        )
    return True, ""


def writable(root: Path, text: str, key: str) -> tuple[bool, str]:
    """`--write` 放行口径：合格复核记录，或无复核字面量（后者写入后仍会报错）。"""
    if text.strip() == DECLARATION:
        return True, ""
    return valid_basis(root, text, key)



def section_text(text: str, start: str | None, end: str | None) -> str:
    lines = text.splitlines()
    if start is None:
        return "\n".join(line.rstrip() for line in lines).strip("\n")
    begin = next((i for i, line in enumerate(lines) if line.startswith(start)), None)
    if begin is None:
        raise ValueError(f"找不到区段起点 {start!r}")
    finish = len(lines)
    for index in range(begin + 1, len(lines)):
        if end is not None and lines[index].startswith(end):
            finish = index
            break
    chunk = [line.rstrip() for line in lines[begin:finish]]
    while chunk and not chunk[-1]:
        chunk.pop()
    return "\n".join(chunk)


def fingerprint(text: str, start: str | None, end: str | None) -> str:
    return hashlib.sha256(section_text(text, start, end).encode("utf-8")).hexdigest()


def load_pins(path: Path) -> dict:
    if not path.exists():
        return {"version": 1, "sections": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def valid_review(root: Path, reviews: list[str], key: str) -> bool:
    pattern = re.compile(rf"区段：`?{re.escape(key)}`?")
    for text in reviews:
        if pattern.search(text) is None:
            continue
        if not any(word in text for word in CONCLUSIONS):
            continue
        ok, _ = valid_basis(root, text, key)
        if ok:
            return True
    return False


def evaluate(
    root: Path,
    current: dict[str, str],
    head: dict[str, str | None],
    pins: dict[str, dict],
    reviews: list[str],
    registry: dict | None = None,
) -> list[str]:
    errors: list[str] = []
    for spec in SECTIONS:
        key = spec["key"]
        if key not in current:
            errors.append(f"{key}：当前文件缺失")
            continue
        actual = fingerprint(current[key], spec["start"], spec["end"])
        entry = pins.get(key)
        if isinstance(entry, str):
            entry = {"sha256": entry}
        registered = entry.get("sha256") if isinstance(entry, dict) else None
        if registered is None:
            errors.append(f"{key}：指纹未登记（运行 --write）")
        elif registered != actual:
            errors.append(
                f"{key}：指纹未更新（当前 {actual[:12]}，登记 {registered[:12]}）"
            )
        errors.extend(
            a2_signoff_errors(
                root,
                spec,
                current[key],
                entry.get("basis") if isinstance(entry, dict) else None,
            )
        )
        # 日期证据只在 evaluate 中核验，不进 --write 的结构门（批次 0092）。
        errors.extend(
            a2_signoff_date_errors(root, spec, current[key], entry)
        )
        if isinstance(entry, dict):
            basis = entry.get("basis")
            if not basis:
                errors.append(f"{key}：登记项缺少 basis 裁定依据")
            else:
                ok, why = valid_basis(root, basis, key)
                if not ok:
                    marked = entry.get("invalidated")
                    suffix = f"；存储层已显式标记失效：{marked}" if marked else ""
                    errors.append(f"{key}：basis 不合格：{why}{suffix}")
                elif entry.get("invalidated"):
                    errors.append(
                        f"{key}：存储层标记 basis 失效（{entry['invalidated']}），"
                        "但当前 basis 可验证通过；须人工核实后移除该标记"
                        "（--write 不自动清除）"
                    )
        head_text = head.get(key)
        changed = head_text is None or fingerprint(head_text, spec["start"], spec["end"]) != actual
        if changed and not valid_review(root, reviews, key):
            errors.append(
                f"{key}：区段已改动但同一提交缺少合格的非同源复核记录"
                f"（需含且仅含一条 `区段：{key}`、结论词 {'/'.join(CONCLUSIONS)}，"
                "且 `复核产物：` 指向仓库外文件、`sha256：` 与之一致、"
                "`复核基线：` 指向仓库内存在的提交，复核基线处的区段内容与当前一致；"
                "区段改动后须重新取证）"
            )
    if registry is None:
        try:
            registry = load_registry(root)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{REGISTRY}：无法解析（{exc}）")
            registry = {}
    for key, entry in sorted(pins.items()):
        if isinstance(entry, dict) and entry.get("basis") == DECLARATION:
            if key not in registry:
                errors.append(
                    f"{key}：无复核声明未在 {REGISTRY} 登记"
                    "（须含缺哪份复核、到期里程碑、责任人）"
                )
    for key, info in sorted(registry.items()):
        entry = pins.get(key)
        if not isinstance(entry, dict):
            errors.append(f"{REGISTRY}：登记项 {key} 不是已登记区段")
            continue
        if entry.get("basis") != DECLARATION:
            errors.append(f"{REGISTRY}：{key} 已有复核记录，应删除该例外登记")
        if not isinstance(info, dict):
            errors.append(f"{REGISTRY}：{key} 的登记项必须是对象")
            continue
        missing = [field for field in REGISTRY_FIELDS if not info.get(field)]
        if missing:
            errors.append(f"{REGISTRY}：{key} 缺少字段 {', '.join(missing)}")
    declared = {spec["path"] for spec in SECTIONS}
    for path in discover_schema_files(root):
        if path not in declared:
            errors.append(
                f"{path}：`{SCHEMA_DIR}/` 下的文件未登记为规格区段（自动发现；"
                "新增 schema 必须同批登记）"
            )
    for key in sorted(set(pins) - {spec["key"] for spec in SECTIONS}):
        errors.append(f"{key}：登记项指向未定义的区段")
    return errors


def read_head(root: Path, path: str) -> str | None:
    result = subprocess.run(
        ["git", "show", f"HEAD:{path}"], cwd=root, capture_output=True, text=True
    )
    return result.stdout if result.returncode == 0 else None


def staged_reviews(root: Path) -> list[str]:
    listed = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=AM"],
        cwd=root,
        capture_output=True,
        text=True,
    )
    texts = []
    for name in listed.stdout.split():
        if name.startswith("validation/reviews/") and name.endswith(".md"):
            path = root / name
            if path.exists():
                texts.append(path.read_text(encoding="utf-8"))
    return texts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", help="仓库根目录；默认由脚本位置推断")
    parser.add_argument("--pins", help="登记文件；默认 scripts/spec-pins.json")
    parser.add_argument("--review", action="append", default=[], help="复核记录文件，可重复")
    parser.add_argument("--write", action="store_true", help="按当前内容重写区段指纹")
    parser.add_argument(
        "--basis",
        action="append",
        default=[],
        help="非同源复核记录（新增或变更区段时必填；可重复，按 `区段：` 匹配对应区段）",
    )
    args = parser.parse_args()
    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[1]
    pins_path = Path(args.pins) if args.pins else root / PINS

    try:
        current = {
            spec["key"]: (root / spec["path"]).read_text(encoding="utf-8")
            for spec in SECTIONS
        }
        pins = load_pins(pins_path)
        previous = pins.get("sections", {})
        if args.write:
            structural = []
            for spec in SECTIONS:
                old = previous.get(spec["key"])
                if isinstance(old, str):
                    old = {"sha256": old}
                structural.extend(
                    a2_signoff_errors(
                        root,
                        spec,
                        current[spec["key"]],
                        old.get("basis") if isinstance(old, dict) else None,
                    )
                )
            if structural:
                for problem in structural:
                    print(f"[错误] {problem}")
                return 2
            sections = {}
            changed: list[str] = []
            chosen: dict[str, str] = {}
            for spec in SECTIONS:
                key = spec["key"]
                actual = fingerprint(current[key], spec["start"], spec["end"])
                old = previous.get(key)
                if isinstance(old, str):
                    old = {"sha256": old}
                old_sha = old.get("sha256") if isinstance(old, dict) else None
                if old_sha != actual:
                    changed.append(key)
                    match = next(
                        (text for text in args.basis if writable(root, text, key)[0]),
                        None,
                    )
                    if match is None:
                        why = (
                            writable(root, args.basis[0], key)[1]
                            if args.basis
                            else "缺少 --basis"
                        )
                        print(f"[错误] 区段 {key} 有新增或变更，但 --basis 不合格：{why}")
                        return 2
                    chosen[key] = match.strip()
                sections[key] = {
                    "sha256": actual,
                    "path": spec["path"],
                    "basis": (
                        chosen[key]
                        if old_sha != actual
                        else (old or {}).get("basis") or DECLARATION
                    ),
                }
                # 显式失效标记只能人工增删；--write 原样保留，不自动抹掉。
                if isinstance(old, dict) and old.get("invalidated"):
                    sections[key]["invalidated"] = old["invalidated"]
                # 日期属于登记方的同级字段（origin: executor），basis 只放复核方原文；
                # --write 不生成也不删除该字段。
                if isinstance(old, dict) and old.get("review_date"):
                    sections[key]["review_date"] = old["review_date"]
            pins = {
                "version": 1,
                "note": (
                    "规格区段指纹。区段新增或改动必须 --write --basis；basis 只接受合格的非同源"
                    "复核记录，或无复核字面量（后者不放行，须 --no-verify 并在 "
                    "scripts/no-review-declarations.json 与 TODO.md 到期项留痕）。"
                    "指纹只证明内容一致，不证明签收人身份。"
                ),
                "sections": sections,
            }
            pins_path.write_text(
                json.dumps(pins, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
            print(
                f"[完成] 已登记 {len(sections)} 个规格区段指纹"
                f"（本次新增或变更 {len(changed)} 个）。"
            )
            return 0
        head = {spec["key"]: read_head(root, spec["path"]) for spec in SECTIONS}
        reviews = [
            Path(path).read_text(encoding="utf-8") for path in args.review
        ] or staged_reviews(root)
        errors = evaluate(root, current, head, previous, reviews)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"[错误] 解析失败：{exc}")
        return 2

    for error in errors:
        print(f"[错误] {error}")
    registered = len(pins.get("sections", {}))
    print(
        f"规格区段绑定：区段 {len(SECTIONS)}，已登记 {registered}，"
        f"复核记录 {len(reviews)}，问题 {len(errors)}"
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
