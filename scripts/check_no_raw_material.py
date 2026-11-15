#!/usr/bin/env python3
"""阻断式检查：仓库内不得出现原始资料、OCR/文本层转储或成段原文。

依据：CONSTITUTION.md 第 13 条；执行约定见 AGENTS.md 第 5 条。
只扫描已被 git 跟踪的文件——未跟踪文件由 .gitignore 拦截，已跟踪文件才是
“会进入公开仓库”的内容（覆盖范围缺口见 GAP_LEDGER G-020）。

判定规则（任一命中即非零退出）：
  RM-EXT       文档/电子书/扫描件/压缩包等扩展名
  RM-MAGIC     文件头是 PDF/ZIP/GZIP/PNG/JPEG/TIFF/RAR/7Z/PostScript/OLE/DjVu
  RM-BINARY    文本扩展名下出现 NUL 字节或无法按 UTF-8 解码
  RM-SIZE      单文件超过 512 KiB
  RM-LONGLINE  单行超过 8192 字符（堵住单行整段原文与 base64）
  RM-BASE64    出现 256 字符以上的 base64 形态长串，或 64 字符以上且解码后是已知二进制魔数
  RM-QUOTE     单条引用超过 400 字符，或连续引用块超过 800 字符
  RM-PROSEBLOCK 连续 15 行以上每行不少于 100 字符（PDF 文本转储的行形态），
               空行不重置计数；结构化 JSONL（每行一个合法记录）不适用
  RM-PAGEDUMP  正文页形态：非空行 ≥20 且 ≥60% 是 60–115 字符、无 Markdown 标记的连续正文行，
               其中 ≥50% 不以句末标点结尾（PDF 正文换行特征）
  RM-PAGESEQ   连续 5 行以上为页码/纯数字序列（整页转录特征）
  RM-DOTLEADER 单行出现 30 个以上连续点（PDF 目录提取特征）
  RM-MOJIBAKE  出现 U+FFFD 替换字符（错误解码后粘贴的提取文本）
  RM-CONTROL   出现除制表符/换行以外的 C0 控制字符
  RM-ONTO-HEADER  本体文件缺少 self-authored / source_id 头注释
  RM-ONTO-LITERAL 本体文件的字符串字面量超过 400 字符（疑似原文转录）
  RM-ONTO-COMMENT 本体文件的单行注释超过 400 字符（疑似原文转录）

结构化 JSONL 的豁免不是“每行是对象”即放行，而是按语料 schema 校验：
顶层键白名单、字符串值上限 400 字符、relations/evidence 的子结构与子值上限；
任一未知键、超长值、嵌套可疑结构即不豁免。另有跨记录形态判据：连续 15 条
记录的主文本值都是 60 字符以上、无句末标点的片段时，按 RM-PROSEBLOCK 处理。
见 analyze_jsonl()。

本体文件（CONSTITUTION.md 第 13.6 条）：`.ttl` 等 RDF 序列化允许入库，但仍受
体积、二进制、乱码、控制字符、点线、页码序列与长文本检查；连续 15 行以上的
长注释行按 RM-PROSEBLOCK 处理。

用法：
  python3 scripts/check_no_raw_material.py
  python3 scripts/check_no_raw_material.py --self-test
退出码：0 = 通过；1 = 命中或自测失败；2 = 自测无法完整评估（缺少真实 PDF
文本层样本；非 PDF 用例仍已全部执行，2 不等于通过）。
"""

import argparse
import base64
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

BANNED_EXTS = {
    ".pdf", ".epub", ".mobi", ".azw3", ".djvu", ".chm", ".ps",
    ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx",
    ".tif", ".tiff", ".png", ".jpg", ".jpeg", ".bmp", ".webp",
    ".zip", ".tar", ".gz", ".tgz", ".7z", ".rar",
}

TEXT_EXTS = {
    ".md", ".txt", ".json", ".jsonl", ".py", ".yaml", ".yml",
    ".toml", ".cfg", ".ini", ".sh", ".log", ".csv", ".html", ".htm",
    ".xml", ".tex", ".rst", ".tsv", ".svg", ".dat", "",
}

ONTOLOGY_EXTS = {".ttl", ".nt", ".n3", ".owl", ".rdf", ".jsonld"}
TURTLE_EXTS = {".ttl"}

# 不做“页形态”判据的结构化/代码扩展名，避免把代码块与配置误判为正文页。
PAGE_DUMP_SKIP_EXTS = {".py", ".sh", ".toml", ".yaml", ".yml", ".cfg", ".ini", ".json"}

MAX_FILE_BYTES = 512 * 1024
MAX_LINE_CHARS = 8192
MAX_QUOTE_LINE_CHARS = 400
MAX_QUOTE_BLOCK_CHARS = 800
MAX_LITERAL_CHARS = 400
MAX_JSONL_VALUE_CHARS = 400
MAX_JSONL_SHORT_CHARS = 120
MAX_JSONL_EVIDENCE_CHARS = 200
PROSE_LINE_CHARS = 100
PROSE_BLOCK_RUN = 15
PARA_MIN_LINES = 20
PARA_DUMP_RATIO = 0.6
PARA_CONTINUATION_RATIO = 0.5
BASE64_RUN_CHARS = 256
BASE64_PROBE_CHARS = 64
ONTO_PROSE_LINE_CHARS = 80
ONTO_PROSE_BLOCK_RUN = 12
PAGE_SEQ_RUN = 5

PAGE_LINE_RE = re.compile(
    r"^(?:Page\s+\d{1,4}|\d{1,4}(?:\s*/\s*\d{1,4})?|第\s*\d{1,4}\s*页)$"
)
DOTLEADER_RE = re.compile(r"\.{30,}")
CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")
TRIPLE_QUOTE_RE = re.compile(r'"""(.*?)"""', re.S)
SINGLE_QUOTE_RE = re.compile(r'"(?:\\.|[^"\\\n])*"')
END_PUNCT_RE = re.compile(r'[.!?。！？；;:：)）\]】"”’]$')
LOWER_START_RE = re.compile(r"^[a-z\u4e00-\u9fff]")
MD_MARKER_RE = re.compile(r"^(#{1,6}\s|[-*+]\s|\d+[.)]\s|\||>|```)")
B64_STD_RE = re.compile(r"[A-Za-z0-9+/]{%d,}={0,2}" % BASE64_RUN_CHARS)
B64_URL_RE = re.compile(r"[A-Za-z0-9_-]{%d,}" % BASE64_RUN_CHARS)
B64_PROBE_RE = re.compile(r"[A-Za-z0-9+/]{%d,}={0,2}" % BASE64_PROBE_CHARS)

MAGIC_SIGNATURES = [
    (b"%PDF-", "PDF"),
    (b"PK\x03\x04", "ZIP/DOCX/EPUB"),
    (b"PK\x05\x06", "ZIP（空）"),
    (b"\x1f\x8b", "GZIP"),
    (b"\x89PNG\r\n\x1a\n", "PNG"),
    (b"\xff\xd8\xff", "JPEG"),
    (b"GIF87a", "GIF"),
    (b"GIF89a", "GIF"),
    (b"II*\x00", "TIFF"),
    (b"MM\x00*", "TIFF"),
    (b"Rar!\x1a\x07", "RAR"),
    (b"7z\xbc\xaf\x27\x1c", "7Z"),
    (b"%!PS", "PostScript"),
    (b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1", "OLE"),
    (b"AT&TFORM", "DjVu"),
]

# 语料 schema：顶层键白名单。故意不含 text/content/body/page/chunk/payload/raw 等
# “可整体装下一段原文”的泛化键。
JSONL_TOP_KEYS = {
    "id", "draft_id", "term", "label_zh", "label_en", "entry_type", "status",
    "definition", "definitionStatus", "relations", "provenance_note", "evidence",
    "natural_key", "candidate_iri", "candidate_iri_status", "candidate_iri_reason",
    "sourcePage", "authoritative",
}
JSONL_RELATION_KEYS = {
    "about", "accountable_by", "accountable_for", "asserted_about_by",
    "asserted_by", "asserts", "authorizes", "belongs_to_domain", "by",
    "committed_by", "constrained_by", "constrains", "delegates_autonomy_to",
    "delegates_to", "has_actor", "has_commitment", "has_focus_area",
    "has_outcome", "has_output", "includes_process", "input_to", "instance_of",
    "may_coincide_with", "measures", "nearest_ontology_individual", "output_of",
    "outside_project", "owned_by", "paired_with", "produced_by",
    "records_state", "reports_on", "responsible_by", "responsible_for",
    "specialized_by", "supports", "technique_category", "to", "typed_by",
    "used_in", "verified_by",
}
JSONL_EVIDENCE_KEYS = {
    "source_id", "locator", "page", "precision", "verification", "use_gate"
}


class Finding:
    def __init__(self, code, path, line, message):
        self.code = code
        self.path = path
        self.line = line
        self.message = message

    def render(self):
        loc = self.path if self.line is None else f"{self.path}:{self.line}"
        return f"[错误] {self.code} {loc}：{self.message}"


def detect_magic(prefix):
    for signature, name in MAGIC_SIGNATURES:
        if prefix.startswith(signature):
            return name
    return None


def _string_values(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for value in obj.values():
            yield from _string_values(value)
    elif isinstance(obj, list):
        for value in obj:
            yield from _string_values(value)


def _jsonl_record_ok(record):
    """按语料 schema 校验一条记录；未知键、超长值、异常结构均不豁免。"""
    if not isinstance(record, dict):
        return False
    if not record.keys() <= JSONL_TOP_KEYS:
        return False
    if not isinstance(record.get("term") or record.get("draft_id") or record.get("id"), str):
        return False

    for key, value in record.items():
        if key == "relations":
            if not isinstance(value, dict) or not value.keys() <= JSONL_RELATION_KEYS:
                return False
            for item in value.values():
                if isinstance(item, str):
                    if len(item) > MAX_JSONL_SHORT_CHARS:
                        return False
                elif isinstance(item, bool):
                    continue
                elif isinstance(item, list):
                    if not all(
                        isinstance(sub, str) and len(sub) <= MAX_JSONL_SHORT_CHARS
                        for sub in item
                    ):
                        return False
                else:
                    return False
            continue
        if key == "evidence":
            if not isinstance(value, list):
                return False
            for item in value:
                if not isinstance(item, dict) or not item.keys() <= JSONL_EVIDENCE_KEYS:
                    return False
                for sub in item.values():
                    if isinstance(sub, str):
                        if len(sub) > MAX_JSONL_EVIDENCE_CHARS:
                            return False
                    elif sub is not None and not isinstance(sub, (int, bool)):
                        return False
            continue
        if isinstance(value, str):
            limit = MAX_JSONL_SHORT_CHARS if key in {
                "term", "label_zh", "label_en", "entry_type", "status",
                "definitionStatus", "natural_key", "candidate_iri",
                "candidate_iri_status", "candidate_iri_reason",
            } else MAX_JSONL_VALUE_CHARS
            if len(value) > limit:
                return False
        elif isinstance(value, (int, float, bool)) or value is None:
            continue
        else:
            return False
    return True


def _prose_fragment(record):
    """记录里最长的字符串是否像“被换行截断的正文片段”。"""
    values = [value for value in _string_values(record) if len(value) >= 60]
    if not values:
        return False
    longest = max(values, key=len)
    return not END_PUNCT_RE.search(longest) and bool(LOWER_START_RE.match(longest))


def analyze_jsonl(suffix, text):
    """返回 (是否豁免 RM-PROSEBLOCK, 附加 Finding 或 None)。

    只有“每行一个合法记录 + 值级/键级校验通过 + 不存在连续正文片段”才豁免。
    """
    if suffix != ".jsonl":
        return False, None
    stripped = text.lstrip("\ufeff")
    lines = [line for line in stripped.splitlines() if line.strip()]
    if not lines:
        return False, None

    records = []
    for line in lines:
        try:
            value = json.loads(line)
        except (json.JSONDecodeError, ValueError):
            return False, None
        if not _jsonl_record_ok(value):
            return False, None
        records.append(value)

    run = 0
    run_start = None
    for index, record in enumerate(records, 1):
        if _prose_fragment(record):
            run += 1
            if run == 1:
                run_start = index
            if run == PROSE_BLOCK_RUN:
                return False, Finding(
                    "RM-PROSEBLOCK", "", run_start,
                    f"连续 {PROSE_BLOCK_RUN} 条记录的主文本均为无句末标点的片段，"
                    "疑似正文逐行包裹",
                )
        else:
            run = 0
    return True, None


def tracked_files(root):
    out = subprocess.run(
        ["git", "ls-files", "-z"], cwd=root, capture_output=True, check=True
    ).stdout
    return [p for p in out.decode("utf-8").split("\0") if p]


def check_ontology_text(rel, text, suffix):
    """本体文件的附加检查：头注释、超长字面量、超长注释与注释行形态。

    本体允许入库，但“自写”必须可机械识别，且不能夹带原文转录。
    """
    findings = []

    lines = text.splitlines()
    if suffix in TURTLE_EXTS:
        head = "\n".join(lines[:40]).lower()
        if "self-authored" not in head or "source_id" not in head:
            findings.append(
                Finding(
                    "RM-ONTO-HEADER", rel, 1,
                    "缺少 self-authored / source_id 头注释（CONSTITUTION 13.6）",
                )
            )

    triple_spans = []
    for m in TRIPLE_QUOTE_RE.finditer(text):
        triple_spans.append((m.start(), m.end()))
        body = m.group(1)
        if len(body) > MAX_LITERAL_CHARS:
            lineno = text[: m.start()].count("\n") + 1
            findings.append(
                Finding(
                    "RM-ONTO-LITERAL", rel, lineno,
                    f"三引号字面量 {len(body)} 字符，超过阈值 {MAX_LITERAL_CHARS}",
                )
            )

    for m in SINGLE_QUOTE_RE.finditer(text):
        if any(start <= m.start() < end for start, end in triple_spans):
            continue
        body = m.group(0)[1:-1]
        if len(body) > MAX_LITERAL_CHARS:
            lineno = text[: m.start()].count("\n") + 1
            findings.append(
                Finding(
                    "RM-ONTO-LITERAL", rel, lineno,
                    f"字符串字面量 {len(body)} 字符，超过阈值 {MAX_LITERAL_CHARS}",
                )
            )

    prose_run = 0
    page_run = 0
    for lineno, line in enumerate(lines, 1):
        if CONTROL_RE.search(line):
            findings.append(
                Finding("RM-CONTROL", rel, lineno, "出现 C0 控制字符，疑似二进制/OCR 输出")
            )
        if DOTLEADER_RE.search(line):
            findings.append(
                Finding("RM-DOTLEADER", rel, lineno, "出现 30 个以上连续点，疑似 PDF 目录转储")
            )

        stripped = line.strip()
        if not stripped.startswith("#"):
            prose_run = 0
            page_run = 0
            continue

        body = stripped.lstrip("#").strip()
        if len(body) > MAX_QUOTE_LINE_CHARS:
            findings.append(
                Finding(
                    "RM-ONTO-COMMENT", rel, lineno,
                    f"注释行 {len(body)} 字符，超过阈值 {MAX_QUOTE_LINE_CHARS}",
                )
            )

        if len(body) >= ONTO_PROSE_LINE_CHARS:
            prose_run += 1
            if prose_run == ONTO_PROSE_BLOCK_RUN:
                findings.append(
                    Finding(
                        "RM-PROSEBLOCK", rel, lineno,
                        f"连续 {ONTO_PROSE_BLOCK_RUN} 行注释每行不少于 "
                        f"{ONTO_PROSE_LINE_CHARS} 字符，疑似原文转储",
                    )
                )
        else:
            prose_run = 0

        if PAGE_LINE_RE.match(body):
            page_run += 1
            if page_run == PAGE_SEQ_RUN:
                findings.append(
                    Finding(
                        "RM-PAGESEQ", rel, lineno,
                        f"连续 {PAGE_SEQ_RUN} 行注释为页码/纯数字，疑似整页转录",
                    )
                )
        else:
            page_run = 0

    return findings


def _dump_like(line):
    if not (60 <= len(line) <= 115):
        return False
    if MD_MARKER_RE.match(line) or " " not in line:
        return False
    good = sum(
        1 for ch in line if ch.isalpha() or ch.isspace() or "\u4e00" <= ch <= "\u9fff"
    )
    return good / len(line) >= 0.8


def page_dump_ratio(lines):
    nonblank = [line.strip() for line in lines if line.strip()]
    if len(nonblank) < PARA_MIN_LINES:
        return None
    dump = [line for line in nonblank if _dump_like(line)]
    if not dump:
        return None
    ratio = len(dump) / len(nonblank)
    if ratio < PARA_DUMP_RATIO:
        return None
    continuation = sum(1 for line in dump if not END_PUNCT_RE.search(line))
    if continuation / len(dump) < PARA_CONTINUATION_RATIO:
        return None
    return ratio


def _base64_suspicious(line):
    if B64_STD_RE.search(line) or B64_URL_RE.search(line):
        return True
    for match in B64_PROBE_RE.finditer(line):
        chunk = match.group(0)
        chunk += "=" * (-len(chunk) % 4)
        try:
            decoded = base64.b64decode(chunk, validate=False)
        except (ValueError, TypeError):
            continue
        if detect_magic(decoded[:16]):
            return True
    return False


def check_file(root, rel):
    findings = []
    path = root / rel
    if not path.is_file():
        return findings

    suffix = path.suffix.lower()
    raw = path.read_bytes()

    magic = detect_magic(raw[:16])
    if magic:
        findings.append(
            Finding("RM-MAGIC", rel, None, f"文件头为 {magic}，扩展名 {suffix or '（无）'} 不可信")
        )
        return findings

    if suffix in BANNED_EXTS:
        findings.append(Finding("RM-EXT", rel, None, f"禁止入库的文件类型 {suffix}"))
        return findings

    size = path.stat().st_size
    if size > MAX_FILE_BYTES:
        findings.append(
            Finding(
                "RM-SIZE", rel, None,
                f"{size} 字节，超过阈值 {MAX_FILE_BYTES} 字节",
            )
        )

    if b"\x00" in raw[:8192]:
        findings.append(Finding("RM-BINARY", rel, None, "文本扩展名下出现 NUL 字节"))
        return findings

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        findings.append(Finding("RM-BINARY", rel, None, "无法按 UTF-8 解码"))
        return findings

    text = text.lstrip("\ufeff")

    if "\ufffd" in text:
        line = text[: text.index("\ufffd")].count("\n") + 1
        findings.append(
            Finding("RM-MOJIBAKE", rel, line, "出现 U+FFFD 替换字符，疑似提取文本直接粘贴")
        )

    if suffix in ONTOLOGY_EXTS:
        findings.extend(check_ontology_text(rel, text, suffix))
        return findings

    exempt, extra = analyze_jsonl(suffix, text)
    if extra is not None:
        extra.path = rel
        findings.append(extra)

    lines = text.splitlines()
    quote_block = 0
    quote_block_start = None
    prose_run = 0
    page_run = 0
    for lineno, line in enumerate(lines, 1):
        if len(line) > MAX_LINE_CHARS:
            findings.append(
                Finding(
                    "RM-LONGLINE", rel, lineno,
                    f"单行 {len(line)} 字符，超过阈值 {MAX_LINE_CHARS}",
                )
            )

        if CONTROL_RE.search(line):
            findings.append(
                Finding("RM-CONTROL", rel, lineno, "出现 C0 控制字符，疑似二进制/OCR 输出")
            )

        if DOTLEADER_RE.search(line):
            findings.append(
                Finding("RM-DOTLEADER", rel, lineno, "出现 30 个以上连续点，疑似 PDF 目录转储")
            )

        if _base64_suspicious(line):
            findings.append(
                Finding(
                    "RM-BASE64", rel, lineno,
                    "出现 base64 形态长串或解码后命中二进制魔数",
                )
            )

        stripped = line.strip()
        if stripped.startswith(">"):
            if quote_block == 0:
                quote_block_start = lineno
            quote_block += len(stripped.lstrip(">").strip())
            if quote_block > MAX_QUOTE_BLOCK_CHARS:
                findings.append(
                    Finding(
                        "RM-QUOTE", rel, quote_block_start,
                        f"连续引用块 {quote_block} 字符，超过阈值 {MAX_QUOTE_BLOCK_CHARS}",
                    )
                )
                quote_block = 0
            quoted = stripped.lstrip(">").strip()
            if len(quoted) > MAX_QUOTE_LINE_CHARS:
                findings.append(
                    Finding(
                        "RM-QUOTE", rel, lineno,
                        f"单条引用 {len(quoted)} 字符，超过阈值 {MAX_QUOTE_LINE_CHARS}",
                    )
                )
        else:
            quote_block = 0

        if not stripped:
            continue

        if (
            len(stripped) >= PROSE_LINE_CHARS
            and not stripped.startswith("|")
            and not exempt
        ):
            prose_run += 1
            if prose_run == PROSE_BLOCK_RUN:
                findings.append(
                    Finding(
                        "RM-PROSEBLOCK", rel, lineno,
                        f"连续 {PROSE_BLOCK_RUN} 行每行不少于 {PROSE_LINE_CHARS} 字符，疑似文本层转储",
                    )
                )
        else:
            prose_run = 0

        if PAGE_LINE_RE.match(stripped):
            page_run += 1
            if page_run == PAGE_SEQ_RUN:
                findings.append(
                    Finding(
                        "RM-PAGESEQ", rel, lineno,
                        f"连续 {PAGE_SEQ_RUN} 行以上为页码/纯数字，疑似整页转录",
                    )
                )
        else:
            page_run = 0

    if suffix not in PAGE_DUMP_SKIP_EXTS:
        ratio = page_dump_ratio(lines)
        if ratio is not None:
            findings.append(
                Finding(
                    "RM-PAGEDUMP", rel, None,
                    f"{ratio:.0%} 的非空行呈正文页换行形态（60–115 字符、无标记、"
                    "多数不以句末标点结尾），疑似整页文本层转储",
                )
            )

    return findings


def _find_pdfs(root):
    dirs = []
    env = os.environ.get("PM_RESOURCE_DIR")
    if env:
        dirs.append(Path(env))
    dirs.append(root.parent / "resources")
    candidates = []
    for directory in dirs:
        if not directory.exists():
            continue
        preferred = sorted(directory.rglob("ISOIECIEEE 29148_2018.pdf"))
        candidates.extend(preferred)
        if not preferred:
            candidates.extend(sorted(directory.rglob("*.pdf")))
    return candidates


def _proseblock_count(root, name):
    return sum(1 for f in check_file(root, name) if f.code == "RM-PROSEBLOCK")


def _codes(root, name):
    return {f.code for f in check_file(root, name)}


def _real_body_page(root):
    """从本地 PDF 取一页真实正文（6–20 页），返回 (页码, 文本) 或 None。

    选择条件：该页文本触发 RM-PAGEDUMP 且不含 RM-DOTLEADER，排除目录页干扰。
    """
    for pdf in _find_pdfs(root):
        for page in range(6, 21):
            try:
                completed = subprocess.run(
                    ["pdftotext", "-f", str(page), "-l", str(page), "-layout", str(pdf), "-"],
                    capture_output=True,
                    timeout=120,
                )
            except (OSError, subprocess.SubprocessError):
                return None
            if completed.returncode != 0:
                continue
            text = completed.stdout.decode("utf-8", "ignore")
            with tempfile.TemporaryDirectory() as tmp:
                temp_root = Path(tmp)
                (temp_root / "page.txt").write_text(text, encoding="utf-8")
                codes = _codes(temp_root, "page.txt")
            if "RM-PAGEDUMP" in codes and "RM-DOTLEADER" not in codes:
                return page, text
    return None


def _write_lines(root, name, lines):
    path = root / name
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def run_self_test(root):
    """RM-PROSEBLOCK / RM-PAGEDUMP / RM-MAGIC 双向覆盖。

    非 PDF 用例始终执行；PDF 用例缺资源时标记为未评估并返回 2。
    """
    print("[自测] 原始资料判据双向覆盖")
    failures = 0
    executed = 0

    def report(case, ok, detail):
        nonlocal failures, executed
        executed += 1
        failures += 0 if ok else 1
        print(f"[{'通过' if ok else '失败'}] {case} {detail}")

    with tempfile.TemporaryDirectory() as tmp:
        temp_root = Path(tmp)

        # T-NRM-01：合法结构化 JSONL（含 BOM）应放行
        filler = "自写结构化探针条目用于验证 JSONL 长行不被误判为文本层转储。"
        records = [
            {
                "term": f"Probe-{i}",
                "definition": f"{filler}序号 {i}，定义长度足以让单行超过阈值但仍属合法条目。",
                "relations": {"has_actor": "Actor", "has_outcome": "Outcome"},
                "evidence": [
                    {
                        "source_id": "PMBOK8-2025",
                        "locator": "Glossary",
                        "page": 100 + i,
                        "precision": "term-level",
                        "verification": "local_copy_check",
                    }
                ],
            }
            for i in range(1, PROSE_BLOCK_RUN + 1)
        ]
        body = "\n".join(json.dumps(r, ensure_ascii=False) for r in records) + "\n"
        _write_lines(temp_root, "structured.jsonl", body.splitlines())
        count = _proseblock_count(temp_root, "structured.jsonl")
        report(
            "T-NRM-01",
            count == 0,
            f"合法 JSONL（{PROSE_BLOCK_RUN} 行 × ≥{PROSE_LINE_CHARS} 字符）"
            f"未报 RM-PROSEBLOCK（实际 {count}）",
        )
        (temp_root / "bom.jsonl").write_bytes(b"\xef\xbb\xbf" + body.encode("utf-8"))
        count = _proseblock_count(temp_root, "bom.jsonl")
        report(
            "T-NRM-01b",
            count == 0,
            f"UTF-8 BOM 合法 JSONL 未误报（实际 {count}）",
        )

        # T-NRM-02：每行一个 JSON 字符串（非对象）仍拦
        strings = [
            json.dumps(f"{filler * 2}#{i}" + "x" * 40, ensure_ascii=False)
            for i in range(1, PROSE_BLOCK_RUN + 1)
        ]
        _write_lines(temp_root, "strings.jsonl", strings)
        count = _proseblock_count(temp_root, "strings.jsonl")
        report(
            "T-NRM-02",
            count >= 1,
            f"每行一个 JSON 字符串仍报 RM-PROSEBLOCK（实际 {count}）",
        )

        # T-NRM-05：对象包裹散文（未知键 / 超长值 / base64 分块）
        long_text = (
            "This paragraph is deliberately long enough to exceed one hundred characters "
            "and it continues without a sentence ending so that it looks like a line of text "
            "lifted from a PDF page and wrapped into a JSON field."
        )
        cases = {
            "obj-text.jsonl": [
                json.dumps({"text": long_text}, ensure_ascii=False)
                for _ in range(PROSE_BLOCK_RUN)
            ],
            "obj-content.jsonl": [
                json.dumps({"content": long_text}, ensure_ascii=False)
                for _ in range(PROSE_BLOCK_RUN)
            ],
            "obj-definition.jsonl": [
                json.dumps({"term": f"Probe-{i}", "definition": long_text * 3}, ensure_ascii=False)
                for i in range(1, PROSE_BLOCK_RUN + 1)
            ],
            "obj-chunk.jsonl": [
                json.dumps(
                    {"chunk": base64.b64encode(b"%PDF-1.7\n" + b"A" * 300).decode("ascii")},
                    ensure_ascii=False,
                )
                for _ in range(PROSE_BLOCK_RUN)
            ],
        }
        for name, lines in cases.items():
            _write_lines(temp_root, name, lines)
            codes = _codes(temp_root, name)
            report(
                f"T-NRM-05[{name}]",
                bool(codes),
                f"对象包裹散文被拦（命中 {sorted(codes) or '无'}）",
            )

        # 单行 30 万字符
        (temp_root / "huge-line.txt").write_text(
            "A" * 300000 + "\n", encoding="utf-8"
        )
        codes = _codes(temp_root, "huge-line.txt")
        report(
            "T-NRM-05[huge-line]",
            "RM-LONGLINE" in codes,
            f"单行 300000 字符被拦（命中 {sorted(codes) or '无'}）",
        )

        # T-NRM-06：扩展名旁路与魔数
        for ext in (".log", ".csv", ".html", ".dat"):
            _write_lines(
                temp_root,
                f"dump{ext}",
                [long_text for _ in range(PROSE_BLOCK_RUN)],
            )
            codes = _codes(temp_root, f"dump{ext}")
            report(
                f"T-NRM-06[{ext}]",
                "RM-PROSEBLOCK" in codes or "RM-PAGEDUMP" in codes,
                f"长英文 {ext} 被拦（命中 {sorted(codes) or '无'}）",
            )

        (temp_root / "pdf.dat").write_bytes(b"%PDF-1.7\n" + b"\x00" * 300000)
        codes = _codes(temp_root, "pdf.dat")
        report(
            "T-NRM-06[pdf.dat]",
            "RM-MAGIC" in codes,
            f"300 KB PDF 头改名 .dat 被拦（命中 {sorted(codes) or '无'}）",
        )
        (temp_root / "gz.dat").write_bytes(b"\x1f\x8b\x08\x00" + b"\x00" * 300000)
        codes = _codes(temp_root, "gz.dat")
        report(
            "T-NRM-06[gz.dat]",
            "RM-MAGIC" in codes,
            f"gzip 头改名 .dat 被拦（命中 {sorted(codes) or '无'}）",
        )

        # T-NRM-07：长行之间夹空行；未知扩展名文本仍扫
        spaced = []
        for _ in range(PROSE_BLOCK_RUN):
            spaced.extend([long_text, ""])
        _write_lines(temp_root, "spaced.txt", spaced)
        count = _proseblock_count(temp_root, "spaced.txt")
        report(
            "T-NRM-07[spaced]",
            count >= 1,
            f"长行夹空行仍报 RM-PROSEBLOCK（实际 {count}）",
        )
        _write_lines(
            temp_root, "unknown.weird", [long_text for _ in range(PROSE_BLOCK_RUN)]
        )
        codes = _codes(temp_root, "unknown.weird")
        report(
            "T-NRM-07[unknown-ext]",
            "RM-PROSEBLOCK" in codes or "RM-PAGEDUMP" in codes,
            f"未知扩展名文本仍被扫描（命中 {sorted(codes) or '无'}）",
        )

        # PDF 依赖用例
        body_page = _real_body_page(root)
        if body_page is None:
            print(
                "[跳过] T-NRM-03/04：未找到可用的真实正文页样本"
                "（可用 PM_RESOURCE_DIR 指定资源目录）"
            )
            print(
                f"[无法评估] 非 PDF 用例已执行 {executed} 项；"
                "PDF 正文页与对象包裹正文未评估，返回 2（不等于通过）"
            )
            return 1 if failures else 2

        page_no, page_text = body_page
        (temp_root / "body.txt").write_text(page_text, encoding="utf-8")
        codes = _codes(temp_root, "body.txt")
        report(
            "T-NRM-03",
            "RM-PAGEDUMP" in codes and "RM-DOTLEADER" not in codes,
            f"真实正文第 {page_no} 页 .txt 报 RM-PAGEDUMP 且无 RM-DOTLEADER"
            f"（命中 {sorted(codes) or '无'}）",
        )

        wrapped = [
            json.dumps({"content": line.strip()}, ensure_ascii=False)
            for line in page_text.splitlines()
            if len(line.strip()) >= 60
        ]
        _write_lines(temp_root, "body.jsonl", wrapped)
        codes = _codes(temp_root, "body.jsonl")
        report(
            "T-NRM-04",
            bool(codes),
            f"真实正文第 {page_no} 页对象包裹为 .jsonl 被拦（命中 {sorted(codes) or '无'}）",
        )

    print(f"自测结论：{executed - failures}/{executed} 通过")
    return 0 if failures == 0 else 1


def main():
    parser = argparse.ArgumentParser(description="检查仓库内是否混入原始资料或成段原文")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parent.parent))
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="运行原始资料判据双向覆盖自测（PDF 正文页用例需要本地 PDF 样本）",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if args.self_test:
        return run_self_test(root)

    if not (root / ".git").exists():
        print(f"[错误] 不是 git 仓库：{root}", file=sys.stderr)
        return 2

    findings = []
    files = tracked_files(root)
    for rel in files:
        findings.extend(check_file(root, rel))

    for f in findings:
        print(f.render())

    print(
        f"原始资料入库检查：{len(files)} 个跟踪文件；"
        f"{len(findings)} 个错误，阈值（体积 {MAX_FILE_BYTES}B / 单行 "
        f"{MAX_LINE_CHARS} 字符 / base64 {BASE64_RUN_CHARS} 字符 / 单条引用 "
        f"{MAX_QUOTE_LINE_CHARS} 字符 / 引用块 {MAX_QUOTE_BLOCK_CHARS} 字符 / "
        f"连续长行 {PROSE_BLOCK_RUN} 行 / 正文页 {PARA_DUMP_RATIO:.0%} / "
        f"本体字面量与注释 {MAX_LITERAL_CHARS} 字符 / "
        f"本体连续长注释 {ONTO_PROSE_BLOCK_RUN} 行）"
    )
    if findings:
        print("[阻断] CONSTITUTION 第 13 条：上述内容不得提交。", file=sys.stderr)
        return 1
    print("[通过] 未发现原始资料、提取产物或成段原文。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
