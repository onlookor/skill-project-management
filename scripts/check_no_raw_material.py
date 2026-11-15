#!/usr/bin/env python3
"""阻断式检查：按目录分区执行 CONSTITUTION.md 第 13.3 条的准入条件。

依据：`CONSTITUTION.md` 第 13 条、`spec/ACCESS_ZONES.md`、ADR-0018。
只扫描已被 git 跟踪的文件——未跟踪文件由 .gitignore 拦截，已跟踪文件才是
“会进入公开仓库”的内容（覆盖范围缺口见 GAP_LEDGER G-020）。

判定轴（任一命中即非零退出）：
  分区
    RM-ZONE     路径未在 `spec/ACCESS_ZONES.md` 登记，或区的扩展名与文件不符；
                未归类默认 fail-closed
  全区分硬约束
    RM-MAGIC    文件头是 PDF/ZIP/GZIP/PNG/JPEG/TIFF/RAR/7Z/PostScript/OLE/DjVu
    RM-EXT      文档/电子书/扫描件/压缩包等扩展名
    RM-BINARY   出现 NUL 字节或无法按 UTF-8 解码
    RM-SIZE     单文件超过 512 KiB
    RM-CONTROL  出现除制表符/换行以外的 C0 控制字符
    RM-MOJIBAKE 出现 U+FFFD 替换字符
    RM-BASE64   256 字符以上的 base64 长串，或 64 字符以上且解码后是二进制魔数
  数据区（D）
    RM-SCHEMA-LINT schema 自身不完整：数组缺 maxItems/items、字符串缺 maxLength、
                对象缺 additionalProperties:false（或受 maxProperties+propertyNames
                约束的映射）、关键字不在支持白名单、使用了未实现的关键字、
                `$ref` 与同级断言关键字并用
    RM-SCHEMA   未在准入登记表、解析失败、未知键、必填/类型/枚举不通过
    RM-FIELD    字段超长或模式不符、按路径的散文字段合计超上限、单条总和超预算、
                单文件散文字段合计超配额
  本体区（O）
    RM-ONTO-HEADER     缺少 self-authored / source_id 头注释（覆盖全部本体扩展名）
    RM-ONTO-LITERAL    定义类谓词字面量超过 2000 字符，其他字面量超过 400 字符
    RM-ONTO-COMMENT    单行注释超过 800 字符
    RM-ONTO-PAGESEQ    出现 12 个以上连续页码数字（页码序列转储）
    RM-ONTO-PROVENANCE 带 skos:definition 的文件缺少 dcterms:source / pm:sourcePage
  散文区（P）与代码区（C）
    RM-LONGLINE  单行超过 8192 字符
    RM-QUOTE     P 区单条引用超过 400 字符，或连续引用块超过 800 字符
    RM-DOTLEADER P/O 区单行出现 30 个以上连续点

已退役：RM-PROSEBLOCK、RM-PAGEDUMP、RM-PAGESEQ。它们用行长、行数、句末标点与
空格比例推断“是否原文”，实测漏杀与误杀并存（见 `spec/RAW_MATERIAL_ADMISSION.md`
第 1 节）；替代保护是数据区 schema + 配额、散文区硬约束、外部指纹与人工评审。
**未命中不等于合规。** 本检查器只证明已登记的结构条件成立。

用法：
  python3 scripts/check_no_raw_material.py
  python3 scripts/check_no_raw_material.py --self-test
退出码：0 = 通过；1 = 命中或自测失败；2 = 无法评估（归区表/准入登记缺失或
本身不可解析，此时不得视为通过）。
"""

import argparse
import base64
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ZONES_FILE = "spec/ACCESS_ZONES.md"

BANNED_EXTS = {
    ".pdf", ".epub", ".mobi", ".azw3", ".djvu", ".chm", ".ps",
    ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx",
    ".tif", ".tiff", ".png", ".jpg", ".jpeg", ".bmp", ".webp",
    ".zip", ".tar", ".gz", ".tgz", ".7z", ".rar",
}

ONTOLOGY_EXTS = {".ttl", ".nt", ".n3", ".owl", ".rdf", ".jsonld"}
TURTLE_EXTS = {".ttl"}
PROSE_EXTS = {".md", ".txt", ".rst", ".html", ".htm", ".tex", ".svg", ""}
CODE_EXTS = {".py", ".sh", ".json", ".toml", ".cfg", ".ini", ".yaml", ".yml", ""}

MAX_FILE_BYTES = 512 * 1024
MAX_LINE_CHARS = 8192
MAX_QUOTE_LINE_CHARS = 400
MAX_QUOTE_BLOCK_CHARS = 800
MAX_LITERAL_CHARS = 400
MAX_DEFINITION_LITERAL_CHARS = 2000
MAX_ONTO_COMMENT_CHARS = 800
MAX_RECORD_PROSE_CHARS = 2800
MAX_FILE_PROSE_CHARS = 20 * 1024
BASE64_RUN_CHARS = 256
BASE64_PROBE_CHARS = 64

DEFINITION_PREDICATES = {
    "skos:definition", "rdfs:comment", "dcterms:description",
}

PAGESEQ_RE = re.compile(r"(?:\b\d{1,4}\b[\s,;]{0,2}){12,}")
PAGE_LIST_RE = re.compile(r"(?:\b\d{1,4}\b\s*,\s*){12,}")
PAGE_PREDICATES = ("pm:page", "pm:sourcePage", "dcterms:sourcePage", "foaf:page")
PAGE_TRIPLE_RE = re.compile(
    r"^\s*(?:<[^>\n]+>|[A-Za-z][\w.-]*:[\w.-]+)\s+(?:"
    + "|".join(re.escape(pred) for pred in PAGE_PREDICATES)
    + r")\s+\d{1,4}\s*[.;]\s*$"
)
PAGE_RUN_MIN = 12
PAGE_VALUE_RE = re.compile(
    r"(?:" + "|".join(re.escape(pred) for pred in PAGE_PREDICATES) + r")\s+\d{1,4}\b"
)
SOURCE_PAGES_HEADER_RE = re.compile(r"^#\s*source_pages:\s*(\S.*)$", re.M)

DOTLEADER_RE = re.compile(r"\.{30,}")
CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")
B64_STD_RE = re.compile(r"[A-Za-z0-9+/]{%d,}={0,2}" % BASE64_RUN_CHARS)
B64_URL_RE = re.compile(r"[A-Za-z0-9_-]{%d,}" % BASE64_RUN_CHARS)
B64_PROBE_RE = re.compile(r"[A-Za-z0-9+/]{%d,}={0,2}" % BASE64_PROBE_CHARS)
LITERAL_RE = re.compile(
    r'("""(?:.|\n)*?"""|\'\'\'(?:.|\n)*?\'\'\'|"(?:\\.|[^"\\\n])*"|\'(?:\\.|[^\'\\\n])*\')'
)
PREDICATE_RE = re.compile(r"([A-Za-z][\w.-]*:[A-Za-z][\w.-]*)\s*$", re.S)

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

SCHEMA_KEYWORDS = {
    "type", "required", "additionalProperties", "enum", "const",
    "anyOf", "oneOf", "allOf", "not",
}
FIELD_KEYWORDS = {
    "maxLength", "minLength", "pattern", "minItems", "maxItems",
    "maximum", "minimum", "maxProperties",
}

# 支持的关键字白名单：不在这里的关键字一律报错，不在运行时静默忽略。
ANNOTATIONS = {
    "$schema", "$id", "$comment", "title", "description",
    "default", "examples", "deprecated", "readOnly", "writeOnly",
    "x-prose-fields", "x-prose-budget",
}
SUPPORTED_KEYWORDS = ANNOTATIONS | {
    "$defs", "$ref", "type", "required", "properties", "additionalProperties",
    "propertyNames", "items", "enum", "const", "not",
    "anyOf", "oneOf", "allOf", "if", "then", "else",
    "minLength", "maxLength", "pattern", "minItems", "maxItems",
    "minimum", "maximum", "maxProperties",
}
# 明确“本校验器不实现”的标准关键字：出现在 schema 里即报错，不许假装支持。
UNSUPPORTED_KEYWORDS = {
    "$anchor", "$dynamicRef", "$dynamicAnchor", "$vocabulary",
    "$recursiveRef", "contains", "minContains", "maxContains",
    "prefixItems", "unevaluatedItems", "unevaluatedProperties",
    "patternProperties", "dependentRequired", "dependentSchemas",
    "dependencies", "exclusiveMinimum", "exclusiveMaximum", "multipleOf",
    "minProperties", "uniqueItems", "format", "contentEncoding",
    "contentMediaType", "contentSchema", "elseIf",
}
COMBINATORS = ("anyOf", "oneOf", "allOf")
CONDITIONALS = ("if", "then", "else", "not")
JSON_TYPES = {"object", "array", "string", "integer", "number", "boolean", "null"}


TYPE_MAP = {
    "object": dict,
    "array": list,
    "string": str,
    "boolean": bool,
    "null": type(None),
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


def tracked_files(root):
    out = subprocess.run(
        ["git", "ls-files", "-z"], cwd=root, capture_output=True, check=True
    ).stdout
    return [p for p in out.decode("utf-8").split("\0") if p]


def _strip_cell(cell):
    return cell.strip().strip("`").strip()


def _parse_table(lines, heading_prefix):
    """解析指定小节下的 Markdown 表格，返回单元格列表（不含表头与分隔行）。"""
    rows = []
    active = False
    for line in lines:
        if line.startswith("## "):
            active = line.startswith(heading_prefix)
            continue
        if not active or not line.lstrip().startswith("|"):
            continue
        cells = [_strip_cell(c) for c in line.strip().strip("|").split("|")]
        if not cells or set(cells[0]) <= set("-: "):
            continue
        if cells[0] in ("路径",):
            continue
        rows.append(cells)
    return rows


def load_zone_table(root):
    path = root / ZONES_FILE
    if not path.is_file():
        return None
    lines = path.read_text(encoding="utf-8").splitlines()
    entries = []
    for cells in _parse_table(lines, "## 1."):
        if len(cells) < 3:
            continue
        entries.append({"path": cells[0], "zone": cells[1], "level": cells[2]})
    return entries


def load_data_table(root):
    path = root / ZONES_FILE
    if not path.is_file():
        return None
    lines = path.read_text(encoding="utf-8").splitlines()
    entries = []
    for cells in _parse_table(lines, "## 2."):
        if len(cells) < 3:
            continue
        entries.append({"path": cells[0], "kind": cells[1], "target": cells[2]})
    return entries


def _match(rel, table):
    best = None
    for entry in table:
        prefix = entry["path"]
        if prefix == "./":
            matched = "/" not in rel
        elif prefix.endswith("/"):
            matched = rel.startswith(prefix)
        else:
            matched = rel == prefix
        if matched and (best is None or len(prefix) > len(best["path"])):
            best = entry
    return best


def _schema_path(root, target):
    target = target.strip().strip("`").strip()
    return root / target


def _load_schema(root, rel, findings):
    path = _schema_path(root, rel)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        findings.append(
            Finding("RM-SCHEMA", rel, None, f"schema 不可读取或不可解析：{exc}")
        )
        return None


def _type_ok(value, expected):
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    py = TYPE_MAP.get(expected)
    return py is None or isinstance(value, py)


def validate(value, schema, pointer="$", root=None):
    """校验本仓库用到的 JSON Schema 子集，返回 [(keyword, pointer, message)]。"""
    errors = []
    if not isinstance(schema, dict):
        return errors
    if root is None:
        root = schema

    ref = schema.get("$ref")
    if isinstance(ref, str) and ref.startswith("#/$defs/"):
        target = (root.get("$defs") or {}).get(ref.rsplit("/", 1)[-1])
        if isinstance(target, dict):
            # 同级关键字不能静默丢弃：先按被引用定义校验，再继续执行兄弟关键字。
            errors.extend(validate(value, target, pointer, root))
        else:
            errors.append(("$ref", pointer, f"无法解析 {ref}"))
            return errors

    if "type" in schema:
        expected = schema["type"]
        options = expected if isinstance(expected, list) else [expected]
        if not any(_type_ok(value, option) for option in options):
            errors.append(("type", pointer, f"类型应为 {options}，实际 {type(value).__name__}"))
            return errors

    if "const" in schema and value != schema["const"]:
        errors.append(("const", pointer, f"应为常量 {schema['const']!r}"))

    if "enum" in schema and value not in schema["enum"]:
        errors.append(("enum", pointer, f"取值 {value!r} 不在 {schema['enum']}"))

    for key in COMBINATORS:
        if key not in schema:
            continue
        matched = [
            sub for sub in schema[key]
            if not validate(value, sub, pointer, root)
        ]
        if key == "oneOf":
            if len(matched) != 1:
                errors.append(
                    ("oneOf", pointer,
                     f"oneOf 必须恰好命中 1 个分支，实际 {len(matched)} 个")
                )
        elif not matched:
            errors.append((key, pointer, f"不满足 {key} 的任何分支"))

    if "not" in schema and not validate(value, schema["not"], pointer, root):
        errors.append(("not", pointer, "命中了禁止分支"))

    if "if" in schema:
        branch = "then" if not validate(value, schema["if"], pointer, root) else "else"
        if branch in schema:
            errors.extend(validate(value, schema[branch], pointer, root))

    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                errors.append(("required", f"{pointer}.{key}", "缺少必填键"))
        if "maxProperties" in schema and len(value) > schema["maxProperties"]:
            errors.append(
                ("maxProperties", pointer,
                 f"键数 {len(value)} 多于 {schema['maxProperties']}")
            )
        if isinstance(schema.get("propertyNames"), dict):
            for key in value:
                errors.extend(
                    validate(key, schema["propertyNames"], f"{pointer}.<键>", root)
                )
        properties = schema.get("properties", {})
        for key, sub in properties.items():
            if key in value:
                errors.extend(validate(value[key], sub, f"{pointer}.{key}", root))
        additional = schema.get("additionalProperties", True)
        unknown = [k for k in value if k not in properties]
        if additional is False:
            for key in unknown:
                errors.append(("additionalProperties", f"{pointer}.{key}", "schema 未登记的键"))
        elif isinstance(additional, dict):
            for key in unknown:
                errors.extend(validate(value[key], additional, f"{pointer}.{key}", root))

    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            errors.append(("minItems", pointer, f"元素数 {len(value)} 少于 {schema['minItems']}"))
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            errors.append(("maxItems", pointer, f"元素数 {len(value)} 多于 {schema['maxItems']}"))
        if isinstance(schema.get("items"), dict):
            for index, item in enumerate(value):
                errors.extend(validate(item, schema["items"], f"{pointer}[{index}]", root))

    if isinstance(value, str):
        if "minLength" in schema and len(value) < schema["minLength"]:
            errors.append(("minLength", pointer, f"长度 {len(value)} 少于 {schema['minLength']}"))
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            errors.append(("maxLength", pointer, f"长度 {len(value)} 超过 {schema['maxLength']}"))
        if "pattern" in schema and re.search(schema["pattern"], value) is None:
            errors.append(("pattern", pointer, f"不匹配模式 {schema['pattern']}"))

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(("minimum", pointer, f"小于 {schema['minimum']}"))
        if "maximum" in schema and value > schema["maximum"]:
            errors.append(("maximum", pointer, f"大于 {schema['maximum']}"))

    return errors


def _lint_node(node, pointer, strict, errors):
    """schema 完整性 lint：数组/字符串/对象必须有上限，不支持的关键字必须报错。

    strict=True 表示“值位置”（根、properties、items、$defs、组合分支），
    此位置必须能独立定出类型与边界；strict=False 用于 `if`/`then`/`else`/`not`
    这类与其他约束叠加的部分断言。
    """
    if not isinstance(node, dict):
        errors.append(f"{pointer}：schema 节点必须是 JSON 对象")
        return

    for key in node:
        if key in UNSUPPORTED_KEYWORDS:
            errors.append(
                f"{pointer}：关键字 `{key}` 本校验器未实现，schema 不得使用"
                "（不支持就必须显式禁用，不能静默降级）"
            )
        elif key not in SUPPORTED_KEYWORDS:
            errors.append(f"{pointer}：关键字 `{key}` 不在支持白名单（拼写错误或未登记扩展）")

    raw_types = node.get("type")
    if raw_types is None:
        types = []
    elif isinstance(raw_types, str):
        types = [raw_types]
    elif isinstance(raw_types, list):
        types = raw_types
    else:
        errors.append(f"{pointer}：`type` 必须是字符串或字符串数组")
        types = ["<非法>"]
    for name in types:
        if name not in JSON_TYPES:
            errors.append(f"{pointer}：`type` 取值 {name!r} 不是合法 JSON 类型")

    if "$ref" in node:
        siblings = sorted(set(node) - ANNOTATIONS - {"$ref"})
        if siblings:
            errors.append(
                f"{pointer}：`$ref` 与同级断言关键字并用（{', '.join(siblings)}）；"
                "本校验器不做隐式合并，请把约束并入 $defs"
            )
        ref = node["$ref"]
        if not (isinstance(ref, str) and ref.startswith("#/$defs/")):
            errors.append(f"{pointer}：`$ref` 只支持 `#/$defs/<名>` 本地引用，实际 {ref!r}")
    else:
        finite = "enum" in node or "const" in node
        if strict and not types and not finite and not any(
            k in node for k in COMBINATORS + CONDITIONALS
        ):
            errors.append(
                f"{pointer}：缺少 `type`，无法证明该值受上限约束"
                "（object/array/string 各有强制上限）"
            )
        if not finite:
            if "array" in types:
                if "maxItems" not in node:
                    errors.append(f"{pointer}：数组缺少 `maxItems`")
                if "items" not in node:
                    errors.append(f"{pointer}：数组缺少 `items`（元素值不受约束）")
            if "string" in types and "maxLength" not in node:
                errors.append(f"{pointer}：字符串缺少 `maxLength`")
            if "object" in types:
                additional = node.get("additionalProperties")
                bounded_map = (
                    isinstance(additional, dict)
                    and "maxProperties" in node
                    and isinstance(node.get("propertyNames"), dict)
                )
                if additional is not False and not bounded_map:
                    errors.append(
                        f"{pointer}：对象必须是 `additionalProperties: false`，"
                        "或受 `maxProperties` + `propertyNames` 约束的映射"
                    )

    for name, sub in (node.get("properties") or {}).items():
        _lint_node(sub, f"{pointer}.properties.{name}", True, errors)
    for name, sub in (node.get("$defs") or {}).items():
        _lint_node(sub, f"{pointer}.$defs.{name}", True, errors)
    if isinstance(node.get("additionalProperties"), dict):
        _lint_node(node["additionalProperties"], f"{pointer}.additionalProperties", True, errors)
    if isinstance(node.get("items"), dict):
        _lint_node(node["items"], f"{pointer}.items", True, errors)
    if isinstance(node.get("propertyNames"), dict):
        _lint_node(node["propertyNames"], f"{pointer}.propertyNames", True, errors)
    for key in COMBINATORS:
        for index, sub in enumerate(node.get(key) or []):
            _lint_node(sub, f"{pointer}.{key}[{index}]", True, errors)
    for key in CONDITIONALS:
        if key in node:
            _lint_node(node[key], f"{pointer}.{key}", False, errors)


def lint_schema_doc(rel, schema):
    """返回 (错误列表, 散文路径表)。散文路径表供配额检查使用。"""
    errors = []
    _lint_node(schema, "$", True, errors)

    specs = schema.get("x-prose-fields")
    prose = []
    if specs is not None:
        if not isinstance(specs, list):
            errors.append("$：`x-prose-fields` 必须是数组")
        else:
            for index, item in enumerate(specs):
                pointer = f"$.x-prose-fields[{index}]"
                if not isinstance(item, dict):
                    errors.append(f"{pointer}：必须是 `{{\"path\": ..., \"maxChars\": ...}}`")
                    continue
                path = item.get("path")
                limit = item.get("maxChars")
                if not isinstance(path, str) or not path:
                    errors.append(f"{pointer}：缺少字符串 `path`")
                if not isinstance(limit, int) or isinstance(limit, bool) or limit <= 0:
                    errors.append(f"{pointer}：`maxChars` 必须是正整数")
                if isinstance(path, str) and path and isinstance(limit, int) and limit > 0:
                    prose.append((path, limit))
        budget = schema.get("x-prose-budget")
        if not isinstance(budget, int) or isinstance(budget, bool) or budget <= 0:
            errors.append("$：声明 `x-prose-fields` 时必须给出正整数 `x-prose-budget`（单条总和兜底）")
        elif prose and budget < max(limit for _, limit in prose):
            errors.append(
                f"$：`x-prose-budget` {budget} 小于单路径最大上限 "
                f"{max(limit for _, limit in prose)}，条目会自相矛盾"
            )
    elif "x-prose-budget" in schema:
        errors.append("$：`x-prose-budget` 只与 `x-prose-fields` 同时使用")
    return errors, prose


def lint_schema_files(root, schema_root=None):
    """对 `contracts/schema/` 下全部文件做完整性 lint，返回 Findings。"""
    base = Path(schema_root) if schema_root else root
    findings = []
    directory = base / "contracts/schema"
    if not directory.is_dir():
        findings.append(
            Finding("RM-SCHEMA-LINT", "contracts/schema", None, "schema 目录缺失，无法评估")
        )
        return findings
    for path in sorted(directory.iterdir()):
        if not path.is_file():
            continue
        rel = f"contracts/schema/{path.name}"
        try:
            schema = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            findings.append(Finding("RM-SCHEMA-LINT", rel, None, f"不可解析：{exc}"))
            continue
        if not isinstance(schema, dict):
            findings.append(Finding("RM-SCHEMA-LINT", rel, None, "顶层必须是对象"))
            continue
        errors, _ = lint_schema_doc(rel, schema)
        for message in errors:
            findings.append(Finding("RM-SCHEMA-LINT", rel, None, message))
    return findings


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


def _parse_records(text, kind):
    stripped = text.lstrip("\ufeff")
    if kind == "jsonl":
        records, lines = [], []
        for lineno, line in enumerate(stripped.splitlines(), 1):
            if not line.strip():
                continue
            records.append(json.loads(line))
            lines.append(lineno)
        return records, lines
    if kind == "yaml-object":
        try:
            import yaml
        except ImportError as exc:  # pragma: no cover - 环境缺失时 fail-closed
            raise ValueError(f"PyYAML 不可用，无法评估：{exc}")
        value = yaml.safe_load(stripped)
    else:
        value = json.loads(stripped)

    if kind == "json-array":
        if not isinstance(value, list):
            raise ValueError("顶层必须是数组")
        return value, [None] * len(value)
    if kind in ("json-object", "yaml-object", "schema-doc"):
        if not isinstance(value, dict):
            raise ValueError("顶层必须是对象")
        return [value], [None]
    raise ValueError(f"未登记的形态 {kind}")


def _prose_values(value, spec):
    """按 `field`、`field.sub`、`list[].field`、`map.*.field` 取值。"""
    parts = spec.split(".")
    current = [value]
    for part in parts:
        nxt = []
        for item in current:
            if part.endswith("[]"):
                key = part[:-2]
                if isinstance(item, dict):
                    seq = item.get(key)
                    if isinstance(seq, list):
                        nxt.extend(seq)
            elif part == "*":
                if isinstance(item, dict):
                    for found in item.values():
                        if isinstance(found, list):
                            nxt.extend([x for x in found if isinstance(x, str)])
                        else:
                            nxt.append(found)
            elif isinstance(item, dict) and part in item:
                found = item[part]
                if isinstance(found, list):
                    nxt.extend([x for x in found if isinstance(x, str)])
                else:
                    nxt.append(found)
        current = nxt
    return [v for v in current if isinstance(v, str)]


def _prose_total(record, specs):
    return sum(
        len(v) for path, _ in specs for v in _prose_values(record, path)
    )


def check_data(rel, text, suffix, entry, schema_root, findings):
    kind = entry["kind"]
    target = entry["target"]
    try:
        records, lines = _parse_records(text, kind)
    except (ValueError, json.JSONDecodeError, TypeError) as exc:
        findings.append(
            Finding("RM-SCHEMA", rel, None, f"{kind} 解析失败：{exc}")
        )
        return

    if kind == "schema-doc":
        for index, record in enumerate(records):
            if "$schema" not in record or "type" not in record:
                findings.append(
                    Finding(
                        "RM-SCHEMA", rel, lines[index],
                        "schema 文件缺少 $schema 或 type",
                    )
                )
        return

    if target.startswith("contracts/schema/"):
        schema = _load_schema(schema_root, target, findings)
        if schema is None:
            return
        lint_errors, prose_fields = lint_schema_doc(rel, schema)
        if lint_errors:
            # schema 自身不完整或散文声明不合法时 fail-closed，不按未声明的配额评估。
            findings.append(
                Finding(
                    "RM-SCHEMA", rel, None,
                    f"schema 未通过完整性 lint（{len(lint_errors)} 项），拒绝评估",
                )
            )
            return
        budget = schema.get("x-prose-budget")
        file_prose = 0
        for index, record in enumerate(records):
            reported = 0
            for keyword, pointer, message in validate(record, schema):
                code = "RM-FIELD" if keyword in FIELD_KEYWORDS else "RM-SCHEMA"
                findings.append(
                    Finding(code, rel, lines[index], f"{pointer}：{message}")
                )
                reported += 1
                if reported >= 12:
                    break
            if prose_fields:
                for path, limit in prose_fields:
                    chars = sum(len(v) for v in _prose_values(record, path))
                    if chars > limit:
                        findings.append(
                            Finding(
                                "RM-FIELD", rel, lines[index],
                                f"路径 {path} 散文字段合计 {chars} 字符，超过 {limit}",
                            )
                        )
                total = _prose_total(record, prose_fields)
                file_prose += total
                if isinstance(budget, int) and total > budget:
                    findings.append(
                        Finding(
                            "RM-FIELD", rel, lines[index],
                            f"单条记录散文字段合计 {total} 字符，超过 {budget}",
                        )
                    )
        if file_prose > MAX_FILE_PROSE_CHARS:
            findings.append(
                Finding(
                    "RM-FIELD", rel, None,
                    f"单文件散文字段合计 {file_prose} 字符，超过 {MAX_FILE_PROSE_CHARS}",
                )
            )
        return

    if target.startswith("生成器 ") or target.startswith("结构化登记"):
        return

    findings.append(
        Finding("RM-SCHEMA", rel, None, f"准入登记未给出 schema 或生成器：{target}")
    )


def _page_dump_run(lines):
    """返回连续页码三元组（`ex:pN pm:page N .`）达到阈值的起始行号。"""
    run = 0
    start = 0
    for index, line in enumerate(lines):
        if PAGE_TRIPLE_RE.match(line):
            if run == 0:
                start = index
            run += 1
            if run >= PAGE_RUN_MIN:
                return start
        else:
            run = 0
    return None


def _definition_blocks(text):
    """按空行切块，返回带定义谓词或页码定位的块（这两类都负有来源义务）。"""
    blocks = [block for block in re.split(r"\n\s*\n", text) if block.strip()]
    return [
        block for block in blocks
        if any(pred in block for pred in DEFINITION_PREDICATES)
        or any(pred in block for pred in PAGE_PREDICATES)
        or "dcterms:source" in block
    ]


def check_ontology(rel, text, suffix, findings):
    lines = text.splitlines()
    head_lower = "\n".join(lines[:40]).lower()
    if suffix in ONTOLOGY_EXTS:
        missing = [
            name for name in ("self-authored", "source_id:", "source_pages:")
            if name not in head_lower
        ]
        if missing:
            findings.append(
                Finding(
                    "RM-ONTO-HEADER", rel, 1,
                    f"头注释缺少 {' / '.join(missing)}（CONSTITUTION 13.6 第 5 项要求三项齐全）",
                )
            )

    # 页码序列转储：真实形态是连续的三元组（`ex:pN pm:page N .`）或逗号数字表；
    # 裸数字串只作兜底。三者任一命中即可。
    run_start = _page_dump_run(lines)
    if run_start is not None:
        findings.append(
            Finding(
                "RM-ONTO-PAGESEQ", rel, run_start + 1,
                f"连续 {PAGE_RUN_MIN} 行以上页码三元组，疑似页码序列转储（CONSTITUTION 13.6 第 3 项）",
            )
        )
    list_match = PAGE_LIST_RE.search(text)
    if list_match is not None:
        findings.append(
            Finding(
                "RM-ONTO-PAGESEQ", rel, text[:list_match.start()].count("\n") + 1,
                "出现 12 个以上逗号分隔页码，疑似页码序列转储（CONSTITUTION 13.6 第 3 项）",
            )
        )
    bare_match = PAGESEQ_RE.search(text)
    if bare_match is not None:
        findings.append(
            Finding(
                "RM-ONTO-PAGESEQ", rel, text[:bare_match.start()].count("\n") + 1,
                "出现 12 个以上连续页码数字，疑似页码序列转储（CONSTITUTION 13.6 第 3 项）",
            )
        )

    # 来源与页码：术语级两项齐全，或由文件头 source_id / source_pages 统一声明。
    declared = SOURCE_PAGES_HEADER_RE.search("\n".join(lines[:40]))
    declared_pages = declared.group(1).strip().lower() if declared else None
    has_page_values = PAGE_VALUE_RE.search(text) is not None
    if declared_pages == "n/a" and has_page_values:
        findings.append(
            Finding(
                "RM-ONTO-PROVENANCE", rel, 1,
                "文件头声明 `source_pages: n/a`，但正文含页码三元组，声明与实际矛盾"
                "（CONSTITUTION 13.6 第 5 项）",
            )
        )
    # `n/a` 是显式声明“本文件不含页码定位”，须与正文一致（上面已校验）；
    # 除此之外，头注释里的范围声明同样视为页码已交代。
    page_declared = declared_pages is not None
    source_declared = "source_id:" in head_lower
    missing_source = []
    missing_page = []
    for block in _definition_blocks(text):
        subject = block.strip().splitlines()[0].strip()
        if not (source_declared or "dcterms:source" in block):
            missing_source.append(subject)
        if not (page_declared or any(pred in block for pred in PAGE_PREDICATES)):
            missing_page.append(subject)
    for label, subjects in (("来源", missing_source), ("页码", missing_page)):
        if not subjects:
            continue
        preview = "、".join(subjects[:3])
        findings.append(
            Finding(
                "RM-ONTO-PROVENANCE", rel, None,
                f"{len(subjects)} 个定义术语既无术语级{label}，也无文件头声明"
                f"（如 {preview}；CONSTITUTION 13.6 第 5 项）",
            )
        )

    literal_spans = []
    for match in LITERAL_RE.finditer(text):
        literal_spans.append((match.start(), match.end()))
        body = match.group(0)
        if body.startswith('"""') or body.startswith("'''"):
            body = body[3:-3]
        else:
            body = body[1:-1]
        prefix = text[max(0, match.start() - 240):match.start()]
        predicate = PREDICATE_RE.search(prefix)
        name = predicate.group(1) if predicate else ""
        limit = (
            MAX_DEFINITION_LITERAL_CHARS
            if name in DEFINITION_PREDICATES
            else MAX_LITERAL_CHARS
        )
        if len(body) > limit:
            lineno = text[: match.start()].count("\n") + 1
            findings.append(
                Finding(
                    "RM-ONTO-LITERAL", rel, lineno,
                    f"{name or '字面量'} 长度 {len(body)} 超过阈值 {limit}",
                )
            )

    def in_literal(position):
        return any(start <= position < end for start, end in literal_spans)

    offset = 0
    for lineno, line in enumerate(lines, 1):
        if DOTLEADER_RE.search(line):
            findings.append(
                Finding("RM-DOTLEADER", rel, lineno, "出现 30 个以上连续点，疑似 PDF 目录转储")
            )
        stripped = line.strip()
        if stripped.startswith("#") and not in_literal(offset):
            body = stripped.lstrip("#").strip()
            if len(body) > MAX_ONTO_COMMENT_CHARS:
                findings.append(
                    Finding(
                        "RM-ONTO-COMMENT", rel, lineno,
                        f"注释行 {len(body)} 字符，超过阈值 {MAX_ONTO_COMMENT_CHARS}",
                    )
                )
        offset += len(line) + 1


def check_prose_or_code(rel, text, zone, findings):
    lines = text.splitlines()
    quote_block = 0
    quote_block_start = None
    for lineno, line in enumerate(lines, 1):
        if len(line) > MAX_LINE_CHARS:
            findings.append(
                Finding(
                    "RM-LONGLINE", rel, lineno,
                    f"单行 {len(line)} 字符，超过阈值 {MAX_LINE_CHARS}",
                )
            )
        if zone != "P":
            continue
        if DOTLEADER_RE.search(line):
            findings.append(
                Finding("RM-DOTLEADER", rel, lineno, "出现 30 个以上连续点，疑似 PDF 目录转储")
            )
        stripped = line.strip()
        if stripped.startswith(">"):
            if quote_block == 0:
                quote_block_start = lineno
            quoted = stripped.lstrip(">").strip()
            quote_block += len(quoted)
            if len(quoted) > MAX_QUOTE_LINE_CHARS:
                findings.append(
                    Finding(
                        "RM-QUOTE", rel, lineno,
                        f"单条引用 {len(quoted)} 字符，超过阈值 {MAX_QUOTE_LINE_CHARS}",
                    )
                )
            if quote_block > MAX_QUOTE_BLOCK_CHARS:
                findings.append(
                    Finding(
                        "RM-QUOTE", rel, quote_block_start,
                        f"连续引用块 {quote_block} 字符，超过阈值 {MAX_QUOTE_BLOCK_CHARS}",
                    )
                )
                quote_block = 0
        else:
            quote_block = 0


def check_file(root, rel, zones, data_table, schema_root=None):
    findings = []
    path = root / rel
    if not path.is_file():
        return findings
    schema_root = schema_root or root
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
            Finding("RM-SIZE", rel, None, f"{size} 字节，超过阈值 {MAX_FILE_BYTES} 字节")
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

    for lineno, line in enumerate(text.splitlines(), 1):
        if CONTROL_RE.search(line):
            findings.append(
                Finding("RM-CONTROL", rel, lineno, "出现 C0 控制字符，疑似二进制/OCR 输出")
            )
        if _base64_suspicious(line):
            findings.append(
                Finding(
                    "RM-BASE64", rel, lineno,
                    "出现 base64 形态长串或解码后命中二进制魔数",
                )
            )

    zone_entry = _match(rel, zones or [])
    if zone_entry is None:
        findings.append(
            Finding(
                "RM-ZONE", rel, None,
                "路径未在 spec/ACCESS_ZONES.md 登记；未归类默认阻断（D-1）",
            )
        )
        return findings

    zone = zone_entry["zone"]
    if zone == "D":
        entry = _match(rel, data_table or [])
        if entry is None:
            findings.append(
                Finding(
                    "RM-SCHEMA", rel, None,
                    "数据区文件未在准入登记表登记；不降级为按文本扫描（D-1）",
                )
            )
            return findings
        check_data(rel, text, suffix, entry, schema_root, findings)
        return findings

    if zone == "O":
        if suffix not in ONTOLOGY_EXTS:
            findings.append(
                Finding(
                    "RM-ZONE", rel, None,
                    f"O 区只允许本体序列化扩展名 {sorted(ONTOLOGY_EXTS)}，实际 {suffix or '（无）'}",
                )
            )
            return findings
        check_ontology(rel, text, suffix, findings)
        return findings

    if zone == "P":
        if suffix not in PROSE_EXTS:
            findings.append(
                Finding(
                    "RM-ZONE", rel, None,
                    f"P 区只允许散文扩展名，实际 {suffix or '（无）'}；数据文件请登记为 D 区",
                )
            )
            return findings
        check_prose_or_code(rel, text, zone, findings)
        return findings

    if zone == "C":
        if suffix not in CODE_EXTS:
            findings.append(
                Finding(
                    "RM-ZONE", rel, None,
                    f"C 区只允许代码与配置扩展名，实际 {suffix or '（无）'}",
                )
            )
            return findings
        check_prose_or_code(rel, text, zone, findings)
        return findings

    findings.append(
        Finding("RM-ZONE", rel, None, f"区取值非法：{zone}（只允许 D/O/P/C）")
    )
    return findings


# ---------------------------------------------------------------------------
# 自测：按新轴重建，不保留已退役启发式的样例；全部用例为合成数据，
# 不依赖本地 PDF 资源，因此不存在“无法评估但返回 0”的路径。
# ---------------------------------------------------------------------------

def _write(root, rel, content):
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(content, encoding="utf-8")
    return path


def _codes(root, rel, zones, data_table, schema_root):
    return {f.code for f in check_file(root, rel, zones, data_table, schema_root)}


def run_self_test():
    print("[自测] 分区准入判据双向覆盖")
    failures = 0
    executed = 0

    def report(case, ok, detail):
        nonlocal failures, executed
        executed += 1
        failures += 0 if ok else 1
        print(f"[{'通过' if ok else '失败'}] {case} {detail}")

    schema_root = Path(__file__).resolve().parent.parent
    zones = [
        {"path": "./", "zone": "P", "level": "P0"},
        {"path": "manifest.json", "zone": "D", "level": "—"},
        {"path": "contracts/examples/", "zone": "D", "level": "—"},
        {"path": "contracts/schema/", "zone": "D", "level": "—"},
        {"path": "knowledge/", "zone": "D", "level": "—"},
        {"path": "ontology/fixtures/manifest.json", "zone": "D", "level": "—"},
        {"path": "ontology/", "zone": "O", "level": "—"},
        {"path": "scripts/", "zone": "C", "level": "—"},
        {"path": "spec/pilot/pilot-artifact.json", "zone": "D", "level": "—"},
        {"path": "spec/pilot/pilot-conflicts.jsonl", "zone": "D", "level": "—"},
        {"path": "spec/pilot/pilot-id-map.json", "zone": "D", "level": "—"},
        {"path": "spec/pilot/pilot-contract.yaml", "zone": "D", "level": "—"},
        {"path": "spec/", "zone": "P", "level": "P1"},
    ]
    data_table = [
        {"path": "knowledge/anchored.jsonl", "kind": "jsonl",
         "target": "contracts/schema/knowledge-entry.schema.json"},
        {"path": "knowledge/bom.jsonl", "kind": "jsonl",
         "target": "contracts/schema/knowledge-entry.schema.json"},
        {"path": "knowledge/legal-long.jsonl", "kind": "jsonl",
         "target": "contracts/schema/knowledge-entry.schema.json"},
        {"path": "knowledge/obj-text.jsonl", "kind": "jsonl",
         "target": "contracts/schema/knowledge-entry.schema.json"},
        {"path": "knowledge/obj-content.jsonl", "kind": "jsonl",
         "target": "contracts/schema/knowledge-entry.schema.json"},
        {"path": "knowledge/obj-chunk.jsonl", "kind": "jsonl",
         "target": "contracts/schema/knowledge-entry.schema.json"},
        {"path": "knowledge/huge.jsonl", "kind": "jsonl",
         "target": "contracts/schema/knowledge-entry.schema.json"},
        {"path": "knowledge/quota.jsonl", "kind": "jsonl",
         "target": "contracts/schema/knowledge-entry.schema.json"},
        {"path": "knowledge/file-quota.jsonl", "kind": "jsonl",
         "target": "contracts/schema/knowledge-entry.schema.json"},
        {"path": "knowledge/missing.jsonl", "kind": "jsonl",
         "target": "contracts/schema/knowledge-entry.schema.json"},
        {"path": "knowledge/sets.jsonl", "kind": "jsonl",
         "target": "contracts/schema/knowledge-entry.schema.json"},
        {"path": "knowledge/long-def.jsonl", "kind": "jsonl",
         "target": "contracts/schema/knowledge-entry.schema.json"},
        {"path": "manifest.json", "kind": "json-object",
         "target": "contracts/schema/package-manifest.schema.json"},
        {"path": "ontology/fixtures/manifest.json", "kind": "json-object",
         "target": "contracts/schema/ontology-fixtures-manifest.schema.json"},
        {"path": "spec/pilot/pilot-artifact.json", "kind": "json-object",
         "target": "contracts/schema/pilot-artifact.schema.json"},
        {"path": "spec/pilot/pilot-id-map.json", "kind": "json-object",
         "target": "contracts/schema/pilot-id-map.schema.json"},
        {"path": "spec/pilot/pilot-conflicts.jsonl", "kind": "jsonl",
         "target": "contracts/schema/pilot-conflict.schema.json"},
        {"path": "spec/pilot/pilot-contract.yaml", "kind": "yaml-object",
         "target": "contracts/schema/pm-slot-contract.schema.json"},
        {"path": "contracts/examples/", "kind": "yaml-object",
         "target": "contracts/schema/pm-slot-contract.schema.json"},
    ]

    filler = "自写结构化探针条目用于验证数据区准入。"
    base_records = []
    for i in range(1, 16):
        base_records.append({
            "term": f"Probe{i}",
            "definition": f"{filler}第 {i} 条，长度足以超过旧判据的行长阈值但仍属合法记录。" * 2,
            "provenance_note": f"探针来源说明 {i}。",
            "relations": {"has_actor": "Actor", "has_outcome": "Outcome"},
            "evidence": [{
                "source_id": "PMBOK8-2025", "locator": "Glossary",
                "page": 100 + i, "precision": "term-level",
                "verification": "local_copy_check",
            }],
        })
    legal = "\n".join(json.dumps(r, ensure_ascii=False) for r in base_records) + "\n"

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)

        # T-NRM-01：合法结构化 JSONL（15 条）与 BOM 变体均放行
        _write(root, "knowledge/anchored.jsonl", legal)
        codes = _codes(root, "knowledge/anchored.jsonl", zones, data_table, schema_root)
        report("T-NRM-01", not codes, f"15 条合法 JSONL 无命中（实际 {sorted(codes) or '无'}）")
        _write(root, "knowledge/bom.jsonl", b"\xef\xbb\xbf" + legal.encode("utf-8"))
        codes = _codes(root, "knowledge/bom.jsonl", zones, data_table, schema_root)
        report("T-NRM-01b", not codes, f"BOM JSONL 无命中（实际 {sorted(codes) or '无'}）")

        # T-NRM-02：退役启发式不再误杀散文与长定义
        prose = "\n".join("自写说明行" * 24 for _ in range(15)) + "\n"
        _write(root, "spec/prose.md", prose)
        codes = _codes(root, "spec/prose.md", zones, data_table, schema_root)
        report("T-NRM-02a", not codes, f"15 行长散文不再报形态判据（实际 {sorted(codes) or '无'}）")
        wrapped = "\n".join("自写说明" * 20 for _ in range(41)) + "\n"
        _write(root, "spec/wrapped.md", wrapped)
        codes = _codes(root, "spec/wrapped.md", zones, data_table, schema_root)
        report("T-NRM-02b", not codes, f"80 列硬换行文档不再报正文页（实际 {sorted(codes) or '无'}）")
        zh = "\n".join("这是自写的中文说明行" * 9 for _ in range(25)) + "\n"
        _write(root, "spec/zh.md", zh)
        codes = _codes(root, "spec/zh.md", zones, data_table, schema_root)
        report("T-NRM-02c", not codes, f"中文正文页不再漏判为通过（无形态判据，实际 {sorted(codes) or '无'}）")
        long_def = [{
            "term": "ProbeLong",
            "definition": "自写定义" * 150,
            "provenance_note": "自写来源说明。",
        }]
        _write(root, "knowledge/legal-long.jsonl",
               "\n".join(json.dumps(r, ensure_ascii=False) for r in long_def) + "\n")
        codes = _codes(root, "knowledge/legal-long.jsonl", zones, data_table, schema_root)
        report("T-NRM-02d", not codes, f"450–1500 字符自写定义放行（实际 {sorted(codes) or '无'}）")

        # T-NRM-03：对象包裹散文由 schema 的未知键拦下
        long_text = (
            "This paragraph is deliberately long enough to exceed one hundred characters "
            "and it continues without a sentence ending so that it looks like a line of text "
            "lifted from a PDF page and wrapped into a JSON field."
        )
        for name, key in (("obj-text.jsonl", "text"), ("obj-content.jsonl", "content")):
            lines = [json.dumps({key: long_text}, ensure_ascii=False) for _ in range(15)]
            _write(root, f"knowledge/{name}", "\n".join(lines) + "\n")
            codes = _codes(root, f"knowledge/{name}", zones, data_table, schema_root)
            report(f"T-NRM-03[{key}]", "RM-SCHEMA" in codes,
                   f"未知键对象被 schema 拦下（命中 {sorted(codes) or '无'}）")
        chunk = base64.b64encode(b"%PDF-1.7\n" + b"A" * 300).decode("ascii")
        lines = [json.dumps({"chunk": chunk}, ensure_ascii=False) for _ in range(15)]
        _write(root, "knowledge/obj-chunk.jsonl", "\n".join(lines) + "\n")
        codes = _codes(root, "knowledge/obj-chunk.jsonl", zones, data_table, schema_root)
        report("T-NRM-03[chunk]", "RM-SCHEMA" in codes and "RM-BASE64" in codes,
               f"base64 分块同时命中未知键与 base64（命中 {sorted(codes) or '无'}）")

        # T-NRM-04：schema 与配额
        cases = {
            "knowledge/quota.jsonl": [{"term": "ProbeQ", "definition": "自写" * 1300}],
            "knowledge/missing.jsonl": [{"term": "ProbeM"}],
        }
        for name, records in cases.items():
            _write(root, name, "\n".join(json.dumps(r, ensure_ascii=False) for r in records) + "\n")
            codes = _codes(root, name, zones, data_table, schema_root)
            expected = "RM-FIELD" if "quota" in name else "RM-SCHEMA"
            report(f"T-NRM-04[{name.split('/')[-1]}]", expected in codes,
                   f"期望 {expected}（命中 {sorted(codes) or '无'}）")
        file_quota = [
            {"term": f"ProbeF{i}", "definition": "自写" * 700}
            for i in range(15)
        ]
        _write(root, "knowledge/file-quota.jsonl",
               "\n".join(json.dumps(r, ensure_ascii=False) for r in file_quota) + "\n")
        codes = _codes(root, "knowledge/file-quota.jsonl", zones, data_table, schema_root)
        report("T-NRM-04[file-quota]", "RM-FIELD" in codes,
               f"单文件散文字段合计超 20 KiB 被拦（命中 {sorted(codes) or '无'}）")

        # T-NRM-05：单行、base64、引用
        _write(root, "spec/huge.txt", "A" * 300000 + "\n")
        codes = _codes(root, "spec/huge.txt", zones, data_table, schema_root)
        report("T-NRM-05[huge-line]", "RM-LONGLINE" in codes and "RM-PROSEBLOCK" not in codes,
               f"30 万字符单行只报长行（命中 {sorted(codes) or '无'}）")
        _write(root, "knowledge/huge.jsonl",
               json.dumps({"term": "ProbeH", "definition": "A" * 300000}) + "\n")
        codes = _codes(root, "knowledge/huge.jsonl", zones, data_table, schema_root)
        report("T-NRM-05[huge-field]", "RM-FIELD" in codes,
               f"超长字段按配额拦下（命中 {sorted(codes) or '无'}）")
        _write(root, "spec/base64.txt", chunk + "\n")
        codes = _codes(root, "spec/base64.txt", zones, data_table, schema_root)
        report("T-NRM-05[base64]", "RM-BASE64" in codes,
               f"base64 PDF 头被识别（命中 {sorted(codes) or '无'}）")
        _write(root, "spec/quote.md", "> " + "自写引证" * 120 + "\n")
        codes = _codes(root, "spec/quote.md", zones, data_table, schema_root)
        report("T-NRM-05[quote]", "RM-QUOTE" in codes,
               f"单条引用超 400 字符被拦（命中 {sorted(codes) or '无'}）")

        # T-NRM-06：魔数与扩展名
        _write(root, "spec/pdf.dat", b"%PDF-1.7\n" + b"\x00" * 300)
        codes = _codes(root, "spec/pdf.dat", zones, data_table, schema_root)
        report("T-NRM-06[pdf]", "RM-MAGIC" in codes,
               f"PDF 头改名 .dat 被拦（命中 {sorted(codes) or '无'}）")
        _write(root, "spec/gz.dat", b"\x1f\x8b\x08\x00" + b"\x00" * 300)
        codes = _codes(root, "spec/gz.dat", zones, data_table, schema_root)
        report("T-NRM-06[gzip]", "RM-MAGIC" in codes,
               f"gzip 头改名 .dat 被拦（命中 {sorted(codes) or '无'}）")
        _write(root, "spec/file.pdf", b"%PDF")
        codes = _codes(root, "spec/file.pdf", zones, data_table, schema_root)
        report("T-NRM-06[ext]", "RM-EXT" in codes,
               f"禁止扩展名被拦（命中 {sorted(codes) or '无'}）")

        # T-NRM-07：未归类与未登记 fail-closed
        _write(root, "unknown/file.md", "自写说明。\n")
        codes = _codes(root, "unknown/file.md", zones, data_table, schema_root)
        report("T-NRM-07[zone]", "RM-ZONE" in codes,
               f"未归类路径被阻断（命中 {sorted(codes) or '无'}）")
        _write(root, "knowledge/unregistered.json", "{}\n")
        codes = _codes(root, "knowledge/unregistered.json", zones, data_table, schema_root)
        report("T-NRM-07[data]", "RM-SCHEMA" in codes,
               f"数据区未登记文件被阻断（命中 {sorted(codes) or '无'}）")
        _write(root, "ontology/data.txt", "自写说明。\n")
        codes = _codes(root, "ontology/data.txt", zones, data_table, schema_root)
        report("T-NRM-07[onto-ext]", "RM-ZONE" in codes,
               f"O 区非本体扩展名被阻断（命中 {sorted(codes) or '无'}）")

        # T-NRM-08：本体字面量分档与注释上限
        header = (
            "# self-authored: true\n# source_id: PMBOK8-2025\n"
            "# source_pages: 1-100\n"
        )
        header_no_pages = "# self-authored: true\n# source_id: PMBOK8-2025\n"
        header_bare = "# self-authored: true\n"
        ttl_ok = header + 'ex:Project a skos:Concept ;\n  skos:definition "' + "自写定义" * 300 + '" .\n'
        _write(root, "ontology/ok.ttl", ttl_ok)
        codes = _codes(root, "ontology/ok.ttl", zones, data_table, schema_root)
        report("T-NRM-08[definition-ok]", not codes,
               f"1500 字符 skos:definition 放行（实际 {sorted(codes) or '无'}）")
        ttl_bad = header + 'ex:Project a skos:Concept ;\n  skos:definition "' + "自写定义" * 600 + '" .\n'
        _write(root, "ontology/bad.ttl", ttl_bad)
        codes = _codes(root, "ontology/bad.ttl", zones, data_table, schema_root)
        report("T-NRM-08[definition-bad]", "RM-ONTO-LITERAL" in codes,
               f"2400 字符 skos:definition 被拦（命中 {sorted(codes) or '无'}）")
        ttl_other = header + 'ex:Project ex:note "' + "自写" * 250 + '" .\n'
        _write(root, "ontology/other.ttl", ttl_other)
        codes = _codes(root, "ontology/other.ttl", zones, data_table, schema_root)
        report("T-NRM-08[other-literal]", "RM-ONTO-LITERAL" in codes,
               f"500 字符非定义字面量被拦（命中 {sorted(codes) or '无'}）")
        _write(root, "ontology/comment.ttl", header + "# " + "自写注释" * 210 + "\n")
        codes = _codes(root, "ontology/comment.ttl", zones, data_table, schema_root)
        report("T-NRM-08[comment-bad]", "RM-ONTO-COMMENT" in codes,
               f"800 字符以上注释被拦（命中 {sorted(codes) or '无'}）")
        _write(root, "ontology/noheader.ttl", 'ex:x a skos:Concept .\n')
        codes = _codes(root, "ontology/noheader.ttl", zones, data_table, schema_root)
        report("T-NRM-08[header]", "RM-ONTO-HEADER" in codes,
               f"缺少头注释被拦（命中 {sorted(codes) or '无'}）")

        # T-NRM-10：复核补漏——人工维护 D 文件、集合字段、配额边界与归区表指纹
        manifest = {
            "package": "probe-package",
            "package_version": "1.0.0",
            "release_tag": "v1.0.0",
            "release_state": "development",
            "entrypoint": "AGENTS.md",
            "state_ledger": "STATE.md",
            "contract_schema": "contracts/schema/pm-slot-contract.schema.json",
            "pm_contract_version": "0.1",
        }
        _write(
            root, "manifest.json",
            json.dumps({**manifest, "notes": "A" * 300000}, ensure_ascii=False) + "\n",
        )
        codes = _codes(root, "manifest.json", zones, data_table, schema_root)
        report("T-NRM-10[manifest-prose]", "RM-SCHEMA" in codes,
               f"300 KB 散文塞入 manifest 被未知键拦下（命中 {sorted(codes) or '无'}）")
        _write(root, "manifest.json", json.dumps(manifest, ensure_ascii=False) + "\n")
        codes = _codes(root, "manifest.json", zones, data_table, schema_root)
        report("T-NRM-10[manifest-ok]", not codes,
               f"合法 manifest 放行（实际 {sorted(codes) or '无'}）")

        contract = {
            "skill_id": "probe-skill",
            "pm_contract_version": "0.1",
            "authoritative": False,
            "slots": {
                "subject_type": "ProbeSubject",
                "deliverable_forms": ["Document"],
                "constraint_domains": [{
                    "name": "goal",
                    "relation_to_generic": "specializes",
                    "generic_class": "goal",
                    "grounding_ref": None,
                }],
                "assertion_vocabulary": [{"name": "what_is", "maps_to": "what_is"}],
                "evidence_forms": ["document"],
            },
        }
        huge_contract = json.loads(json.dumps(contract))
        huge_contract["slots"]["subject_type"] = "长" * 50000
        _write(
            root, "spec/pilot/pilot-contract.yaml",
            json.dumps(huge_contract, ensure_ascii=False) + "\n",
        )
        codes = _codes(root, "spec/pilot/pilot-contract.yaml", zones, data_table, schema_root)
        report("T-NRM-10[pilot-contract]", "RM-FIELD" in codes,
               f"5 万字符契约字段被 maxLength 拦下（命中 {sorted(codes) or '无'}）")

        huge_statement = json.loads(json.dumps(contract))
        huge_statement["assumption_refs"] = [{
            "id": "A-CONTRACT-X",
            "statement": "长" * 50000,
            "verification": {
                "type": "alignment_check",
                "target_document": "AGENTS.md",
                "alignment_criterion": "自写判据",
            },
        }]
        _write(
            root, "contracts/examples/contract.yaml",
            json.dumps(huge_statement, ensure_ascii=False) + "\n",
        )
        codes = _codes(root, "contracts/examples/contract.yaml", zones, data_table, schema_root)
        report("T-NRM-10[examples-statement]", "RM-FIELD" in codes,
               f"5 万字符 statement 被 maxLength 与散文字段配额拦下（命中 {sorted(codes) or '无'}）")

        set_records = {
            "knowledge/sets.jsonl": [
                {"term": "ProbeR", "definition": "自写定义。",
                 "relations": {f"k{i}": "v" for i in range(200)}},
                {"term": "ProbeE", "definition": "自写定义。",
                 "evidence": [{"source_id": "PMBOK8-2025", "locator": "Glossary"} for _ in range(100)]},
                {"term": "ProbeC", "definition": "自写定义。",
                 "claim_mapping": ["claim"] * 100},
                {"term": "ProbeS", "definition": "自写定义。", "definitionStatus": "compleat"},
            ],
            "knowledge/long-def.jsonl": [
                {"term": "ProbeL", "definition": "自" * 2000, "provenance_note": "注" * 800},
            ],
        }
        for name, records in set_records.items():
            _write(root, name, "\n".join(json.dumps(r, ensure_ascii=False) for r in records) + "\n")
        codes = _codes(root, "knowledge/sets.jsonl", zones, data_table, schema_root)
        report("T-NRM-10[relations-200]", "RM-FIELD" in codes,
               f"200 键 relations 被键白名单与 maxProperties 拦下（命中 {sorted(codes) or '无'}）")
        _write(root, "knowledge/sets.jsonl",
               json.dumps(set_records["knowledge/sets.jsonl"][1], ensure_ascii=False) + "\n")
        codes = _codes(root, "knowledge/sets.jsonl", zones, data_table, schema_root)
        report("T-NRM-10[evidence-100]", "RM-FIELD" in codes,
               f"100 条 evidence 被 maxItems 拦下（命中 {sorted(codes) or '无'}）")
        _write(root, "knowledge/sets.jsonl",
               json.dumps(set_records["knowledge/sets.jsonl"][2], ensure_ascii=False) + "\n")
        codes = _codes(root, "knowledge/sets.jsonl", zones, data_table, schema_root)
        report("T-NRM-10[claim-100]", "RM-FIELD" in codes,
               f"100 条 claim_mapping 被 maxItems 拦下（命中 {sorted(codes) or '无'}）")
        _write(root, "knowledge/sets.jsonl",
               json.dumps(set_records["knowledge/sets.jsonl"][3], ensure_ascii=False) + "\n")
        codes = _codes(root, "knowledge/sets.jsonl", zones, data_table, schema_root)
        report("T-NRM-10[definition-status]", "RM-SCHEMA" in codes,
               f"非法 definitionStatus 被枚举拦下（命中 {sorted(codes) or '无'}）")
        codes = _codes(root, "knowledge/long-def.jsonl", zones, data_table, schema_root)
        report("T-NRM-10[long-def-ok]", "RM-FIELD" not in codes,
               f"2000 定义 + 800 说明（共 2800）不被单条配额误杀（命中 {sorted(codes) or '无'}）")

        pinned = json.loads(
            (schema_root / "scripts/spec-pins.json").read_text(encoding="utf-8")
        ).get("sections", {})
        pinned_ok = (
            "spec/ACCESS_ZONES.md" in pinned
            and "contracts/schema/pm-slot-contract.schema.json" in pinned
        )
        report("T-NRM-10[zone-pin]", pinned_ok,
               "归区表与契约 schema 已纳入规格指纹（插行换区需复核记录）")

        pageseq = header + "# " + " ".join(str(i) for i in range(1, 200)) + "\n"
        _write(root, "ontology/pageseq.ttl", pageseq)
        codes = _codes(root, "ontology/pageseq.ttl", zones, data_table, schema_root)
        report("T-NRM-10[pageseq]", "RM-ONTO-PAGESEQ" in codes,
               f"裸数字页码序列被拦下（命中 {sorted(codes) or '无'}）")
        triple_dump = header + "".join(
            f"ex:p{i} pm:page {i} .\n" for i in range(1, 300)
        )
        _write(root, "ontology/pageseq-triples.ttl", triple_dump)
        codes = _codes(root, "ontology/pageseq-triples.ttl", zones, data_table, schema_root)
        report("T-NRM-10[pageseq-triples]", "RM-ONTO-PAGESEQ" in codes,
               f"299 行 TTL 页码三元组转储被拦下（命中 {sorted(codes) or '无'}）")
        provenance = header_no_pages + 'ex:x a skos:Concept ;\n  dcterms:source "PMBOK8-2025" .\n'
        _write(root, "ontology/provenance.ttl", provenance)
        codes = _codes(root, "ontology/provenance.ttl", zones, data_table, schema_root)
        report("T-NRM-10[provenance]", "RM-ONTO-PROVENANCE" in codes,
               f"有来源无页码被拦下（命中 {sorted(codes) or '无'}）")
        both_missing = header_bare + 'ex:y a skos:Concept ;\n  skos:definition "未标来源也未标页码。" .\n'
        _write(root, "ontology/provenance-both.ttl", both_missing)
        codes = _codes(root, "ontology/provenance-both.ttl", zones, data_table, schema_root)
        report("T-NRM-10[provenance-both]", "RM-ONTO-PROVENANCE" in codes,
               f"来源与页码两项都缺被拦下（命中 {sorted(codes) or '无'}）")
        _write(root, "ontology/noheader.jsonld", '{"@id": "ex:x"}\n')
        codes = _codes(root, "ontology/noheader.jsonld", zones, data_table, schema_root)
        report("T-NRM-10[header-ext]", "RM-ONTO-HEADER" in codes,
               f"非 .ttl 本体扩展名同样要求头注释（命中 {sorted(codes) or '无'}）")
        real_onto = []
        for path in sorted((schema_root / "ontology").glob("*.ttl")):
            rel = f"ontology/{path.name}"
            check_ontology(rel, path.read_text(encoding="utf-8"), ".ttl", real_onto)
        report("T-NRM-10[real-ttl-clean]", not real_onto,
               f"5 份真实 TTL 召回 0（{len(real_onto)} 条命中），规则不再空转")

        # T-NRM-11：完整性 lint、按路径配额与复核攻击输入
        real_lint = lint_schema_files(schema_root)
        report("T-NRM-11[lint-real]", not real_lint,
               f"仓库内 7 份 schema 全部通过完整性 lint（问题 {len(real_lint)}）")

        weaken = json.loads(
            (schema_root / "contracts/schema/package-manifest.schema.json")
            .read_text(encoding="utf-8")
        )
        weaken["additionalProperties"] = True
        lint_errors, _ = lint_schema_doc("package-manifest", weaken)
        report("T-NRM-11[weaken-manifest]",
               any("additionalProperties" in message for message in lint_errors),
               f"package-manifest 削弱为 additionalProperties:true 被 lint 拦下（{lint_errors[:1]}）")

        broken = {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "tags": {"type": "array", "items": {"type": "string"}},
                "label": {"type": "string"},
                "meta": {"type": "object", "properties": {"x": {"type": "string", "maxLength": 10}}},
            },
        }
        lint_errors, _ = lint_schema_doc("broken", broken)
        report("T-NRM-11[lint-limits]",
               sum("缺少" in message for message in lint_errors) == 3,
               f"数组/字符串/对象三类缺上限各报一条（{len(lint_errors)} 条：{lint_errors}）")

        misspelled = {"type": "object", "additionalProperties": False,
                      "properties": {"a": {"type": "string", "mxLength": 10}}}
        lint_errors, _ = lint_schema_doc("misspelled", misspelled)
        report("T-NRM-11[lint-unknown]",
               any("不在支持白名单" in message for message in lint_errors),
               f"拼错的关键字 `mxLength` 被拦（{lint_errors[:1]}）")

        unsupported = {"type": "object", "additionalProperties": False,
                       "patternProperties": {"^x": {"type": "string", "maxLength": 10}}}
        lint_errors, _ = lint_schema_doc("unsupported", unsupported)
        report("T-NRM-11[lint-unsupported]",
               any("未实现" in message for message in lint_errors),
               f"未实现关键字 `patternProperties` 被拦（{lint_errors[:1]}）")

        ref_sibling = {
            "type": "object",
            "additionalProperties": False,
            "properties": {"a": {"$ref": "#/$defs/v", "maxLength": 5}},
            "$defs": {"v": {"type": "string", "maxLength": 10}},
        }
        lint_errors, _ = lint_schema_doc("ref-sibling", ref_sibling)
        report("T-NRM-11[lint-ref-sibling]",
               any("$ref` 与同级断言关键字并用" in message for message in lint_errors),
               f"`$ref` 与同级关键字并用被拦（{lint_errors[:1]}）")

        one_of_schema = {"oneOf": [{"type": "number"}, {"type": "integer"}]}
        collisions = validate(3, one_of_schema, root=one_of_schema)
        report("T-NRM-11[oneof-exclusive]",
               any("恰好命中 1 个分支" in message for _, _, message in collisions),
               f"oneOf 命中 2 个分支即失败，不再退化为 anyOf（{len(collisions)} 条）")

        contract_many = json.loads(json.dumps(contract))
        contract_many["assumption_refs"] = [
            {
                "id": f"A-CONTRACT-{i}",
                "statement": "假" * 800,
                "verification": {
                    "type": "alignment_check",
                    "target_document": "AGENTS.md",
                    "alignment_criterion": "判" * 600,
                },
            }
            for i in range(1, 4)
        ]
        _write(root, "contracts/examples/three-assumptions.yaml",
               json.dumps(contract_many, ensure_ascii=False) + "\n")
        codes = _codes(root, "contracts/examples/three-assumptions.yaml",
                       zones, data_table, schema_root)
        report("T-NRM-11[assumptions-3]",
               "RM-FIELD" not in codes,
               f"3 条假设 × 1400（合计 4200）不被误杀（命中 {sorted(codes) or '无'}）")

        id_map = {
            "authoritative": False,
            "purpose": "目" * 800,
            "batch": "M3",
            "generated": "2026-11-15",
            "d4_status": "未定",
            "formal_id_status": "待定",
            "notes": ["注" * 400 for _ in range(12)],
            "entries": [{
                "draft_id": "D-1", "knowledge_ref": "K-1", "entry_type": "term",
                "term": "探针", "candidate_iri": None,
                "candidate_iri_status": "pending", "candidate_iri_reason": None,
                "natural_key": "probe", "formal_id": None, "formal_id_status": "待定",
            }],
            "reverse_index": {},
            "rule_bindings": {},
            "reverse_rule_index": {},
            "statistics": {},
            "grounding_ref_semantics": "语" * 600,
        }
        _write(root, "spec/pilot/pilot-id-map.json",
               json.dumps(id_map, ensure_ascii=False) + "\n")
        codes = _codes(root, "spec/pilot/pilot-id-map.json", zones, data_table, schema_root)
        report("T-NRM-11[idmap-6200]",
               "RM-FIELD" not in codes,
               f"12 条 notes 的 id-map（合计 6200）不被误杀（命中 {sorted(codes) or '无'}）")

        conflicts = {
            "conflict_id": "C-1", "topic": "探针", "draft_ref": "K-1",
            "positions": [
                {"source_id": "PMBOK8-2025", "page": 10, "stance": "场" * 400}
                for _ in range(300)
            ],
            "relation": "contradicts", "recorded_fields": ["stance"],
            "note": "自写说明。",
        }
        _write(root, "spec/pilot/pilot-conflicts.jsonl",
               json.dumps(conflicts, ensure_ascii=False) + "\n")
        codes = _codes(root, "spec/pilot/pilot-conflicts.jsonl",
                       zones, data_table, schema_root)
        report("T-NRM-11[positions-300x400]", "RM-FIELD" in codes,
               f"positions 300×400 被 maxItems 与路径配额拦下（命中 {sorted(codes) or '无'}）")

        conflicts["positions"] = [{"source_id": "PMBOK8-2025", "page": 10, "stance": "场"}]
        conflicts["recorded_fields"] = ["字" * 120 for _ in range(200)]
        _write(root, "spec/pilot/pilot-conflicts.jsonl",
               json.dumps(conflicts, ensure_ascii=False) + "\n")
        codes = _codes(root, "spec/pilot/pilot-conflicts.jsonl",
                       zones, data_table, schema_root)
        report("T-NRM-11[recorded-200x120]", "RM-FIELD" in codes,
               f"recorded_fields 200×120 被 maxItems 拦下（命中 {sorted(codes) or '无'}）")

        tmp_schema = Path(tmp) / "schema-root"
        (tmp_schema / "contracts/schema").mkdir(parents=True)
        (tmp_schema / "contracts/schema/package-manifest.schema.json").write_text(
            json.dumps(weaken, ensure_ascii=False), encoding="utf-8"
        )
        codes = _codes(root, "manifest.json", zones, data_table, tmp_schema)
        report("T-NRM-11[weaken-fail-closed]", "RM-SCHEMA" in codes,
               f"被削弱的 schema 使数据文件 fail-closed（命中 {sorted(codes) or '无'}）")

        # T-NRM-09：归区表最长前缀与全仓覆盖
        real_zones = load_zone_table(schema_root)
        real_data = load_data_table(schema_root)
        checks = [
            ("scripts/README.md", "P"),
            ("ontology/fixtures/manifest.json", "D"),
            ("spec/pilot/pilot-entries.json", "D"),
            ("scripts/check_no_raw_material.py", "C"),
            ("ontology/core.ttl", "O"),
        ]
        ok = real_zones is not None
        for rel, expected in checks:
            entry = _match(rel, real_zones or [])
            ok = ok and entry is not None and entry["zone"] == expected
        report("T-NRM-09[prefix]", ok, "最长前缀归区符合预期")
        files = tracked_files(schema_root)
        unresolved = [f for f in files if _match(f, real_zones or []) is None]
        report("T-NRM-09[coverage]", not unresolved,
               f"全部 {len(files)} 个跟踪文件已归区（未归类 {len(unresolved)}）")
        if real_data is not None:
            d_files = [f for f in files if (_match(f, real_zones) or {}).get("zone") == "D"]
            unregistered = [f for f in d_files if _match(f, real_data) is None]
            report("T-NRM-09[registry]", not unregistered,
                   f"{len(d_files)} 个数据区文件均已登记（未登记 {len(unregistered)}）")
        else:
            report("T-NRM-09[registry]", False, "D 区准入登记表不可解析")

    print(f"自测结论：{executed - failures}/{executed} 通过")
    return 0 if failures == 0 else 1


def main():
    parser = argparse.ArgumentParser(description="按目录分区检查原始资料准入")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parent.parent))
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="运行分区准入判据双向覆盖自测（合成数据，不依赖本地 PDF）",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if args.self_test:
        return run_self_test()

    if not (root / ".git").exists():
        print(f"[错误] 不是 git 仓库：{root}", file=sys.stderr)
        return 2

    zones = load_zone_table(root)
    data_table = load_data_table(root)
    if zones is None or data_table is None:
        print(
            f"[错误] 无法解析 {ZONES_FILE} 的归区表或准入登记表；"
            "无法评估不等于通过。",
            file=sys.stderr,
        )
        return 2

    findings = []
    findings.extend(lint_schema_files(root))
    files = tracked_files(root)
    for rel in files:
        path = root / rel
        if path.is_symlink() or not path.is_file():
            findings.append(
                Finding(
                    "RM-ZONE", rel, None,
                    "非普通文件（子模块 gitlink、符号链接或缺失路径）；"
                    "D-8 只作声明式排除，出现即需重新裁定扫描范围",
                )
            )
            continue
        findings.extend(check_file(root, rel, zones, data_table))

    for f in findings:
        print(f.render())

    zone_counts = {"D": 0, "O": 0, "P": 0, "C": 0, "未归类": 0}
    for rel in files:
        entry = _match(rel, zones)
        zone_counts[entry["zone"] if entry else "未归类"] += 1

    print(
        f"原始资料入库检查：{len(files)} 个跟踪文件"
        f"（D {zone_counts['D']} / O {zone_counts['O']} / P {zone_counts['P']} / "
        f"C {zone_counts['C']} / 未归类 {zone_counts['未归类']}）；"
        f"{len(findings)} 个错误，阈值（体积 {MAX_FILE_BYTES}B / 单行 "
        f"{MAX_LINE_CHARS} 字符 / base64 {BASE64_RUN_CHARS} 字符 / 单条引用 "
        f"{MAX_QUOTE_LINE_CHARS} 字符 / 引用块 {MAX_QUOTE_BLOCK_CHARS} 字符 / "
        f"单条散文按 schema 的 x-prose-fields 逐路径计量 / 单文件散文字段 "
        f"{MAX_FILE_PROSE_CHARS} / 本体定义字面量 {MAX_DEFINITION_LITERAL_CHARS} / "
        f"其他字面量 {MAX_LITERAL_CHARS} / 本体注释 {MAX_ONTO_COMMENT_CHARS}）"
    )
    if findings:
        print("[阻断] CONSTITUTION 第 13 条：上述内容不得提交。", file=sys.stderr)
        return 1
    print("[通过] 已登记的结构条件成立；未命中不等于合规（见 13.3 第 5 项）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
