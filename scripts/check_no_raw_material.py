#!/usr/bin/env python3
"""阻断式检查：仓库内不得出现原始资料、OCR/文本层转储或成段原文。

依据：CONSTITUTION.md 第 13 条；执行约定见 AGENTS.md 第 5 条。
只扫描已被 git 跟踪的文件——未跟踪文件由 .gitignore 拦截，已跟踪文件才是
“会进入公开仓库”的内容。

判定规则（任一命中即非零退出）：
  RM-EXT       文档/电子书/扫描件/压缩包等扩展名
  RM-BINARY    文本扩展名下出现 NUL 字节
  RM-SIZE      单文件超过 512 KiB
  RM-QUOTE     单条引用超过 400 字符，或连续引用块超过 800 字符
  RM-PROSEBLOCK 连续 15 行以上每行不少于 100 字符（PDF 文本转储的行形态）
  RM-PAGESEQ   连续 5 行以上为页码/纯数字序列（整页转录特征）
  RM-DOTLEADER 单行出现 30 个以上连续点（PDF 目录提取特征）
  RM-MOJIBAKE  出现 U+FFFD 替换字符（错误解码后粘贴的提取文本）
  RM-CONTROL   出现除制表符/换行以外的 C0 控制字符
  RM-ONTO-HEADER  本体文件缺少 self-authored / source_id 头注释
  RM-ONTO-LITERAL 本体文件的字符串字面量超过 400 字符（疑似原文转录）
  RM-ONTO-COMMENT 本体文件的单行注释超过 400 字符（疑似原文转录）

本体文件（CONSTITUTION.md 第 13.6 条）：`.ttl` 等 RDF 序列化允许入库，但仍受
体积、二进制、乱码、控制字符、点线、页码序列与长文本检查；连续 15 行以上的
长注释行按 RM-PROSEBLOCK 处理。
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

BANNED_EXTS = {
    ".pdf", ".epub", ".mobi", ".azw3", ".djvu", ".chm", ".ps",
    ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx",
    ".tif", ".tiff", ".png", ".jpg", ".jpeg", ".bmp", ".webp",
    ".zip", ".tar", ".gz", ".tgz", ".7z", ".rar",
}

TEXT_EXTS = {
    ".md", ".txt", ".json", ".jsonl", ".py", ".yaml", ".yml",
    ".toml", ".cfg", ".ini", ".sh", "",
}

ONTOLOGY_EXTS = {".ttl", ".nt", ".n3", ".owl", ".rdf", ".jsonld"}
TURTLE_EXTS = {".ttl"}

MAX_FILE_BYTES = 512 * 1024
MAX_QUOTE_LINE_CHARS = 400
MAX_QUOTE_BLOCK_CHARS = 800
MAX_LITERAL_CHARS = 400
PROSE_LINE_CHARS = 100
PROSE_BLOCK_RUN = 15
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


class Finding:
    def __init__(self, code, path, line, message):
        self.code = code
        self.path = path
        self.line = line
        self.message = message

    def render(self):
        loc = self.path if self.line is None else f"{self.path}:{self.line}"
        return f"[错误] {self.code} {loc}：{self.message}"


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


def check_file(root, rel):
    findings = []
    path = root / rel
    if not path.is_file():
        return findings

    suffix = path.suffix.lower()
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

    if suffix not in TEXT_EXTS and suffix not in ONTOLOGY_EXTS:
        return findings

    raw = path.read_bytes()
    if b"\x00" in raw[:8192]:
        findings.append(Finding("RM-BINARY", rel, None, "文本扩展名下出现 NUL 字节"))
        return findings

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        findings.append(Finding("RM-BINARY", rel, None, "无法按 UTF-8 解码"))
        return findings

    if "\ufffd" in text:
        line = text[: text.index("\ufffd")].count("\n") + 1
        findings.append(
            Finding("RM-MOJIBAKE", rel, line, "出现 U+FFFD 替换字符，疑似提取文本直接粘贴")
        )

    if suffix in ONTOLOGY_EXTS:
        findings.extend(check_ontology_text(rel, text, suffix))
        return findings

    quote_block = 0
    quote_block_start = None
    prose_run = 0
    page_run = 0
    for lineno, line in enumerate(text.splitlines(), 1):
        if CONTROL_RE.search(line):
            findings.append(
                Finding("RM-CONTROL", rel, lineno, "出现 C0 控制字符，疑似二进制/OCR 输出")
            )

        if DOTLEADER_RE.search(line):
            findings.append(
                Finding("RM-DOTLEADER", rel, lineno, "出现 30 个以上连续点，疑似 PDF 目录转储")
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

        if (
            len(stripped) >= PROSE_LINE_CHARS
            and not stripped.startswith("|")
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

    return findings


def main():
    parser = argparse.ArgumentParser(description="检查仓库内是否混入原始资料或成段原文")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parent.parent))
    args = parser.parse_args()

    root = Path(args.root).resolve()
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
        f"{len(findings)} 个错误，阈值（体积 {MAX_FILE_BYTES}B / 单条引用 "
        f"{MAX_QUOTE_LINE_CHARS} 字符 / 引用块 {MAX_QUOTE_BLOCK_CHARS} 字符 / "
        f"连续长行 {PROSE_BLOCK_RUN} 行 / 本体字面量与注释 {MAX_LITERAL_CHARS} 字符 / "
        f"本体连续长注释 {ONTO_PROSE_BLOCK_RUN} 行）"
    )
    if findings:
        print("[阻断] CONSTITUTION 第 13 条：上述内容不得提交。", file=sys.stderr)
        return 1
    print("[通过] 未发现原始资料、提取产物或成段原文。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
