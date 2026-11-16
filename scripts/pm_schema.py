#!/usr/bin/env python3
"""运行期工件契约的 schema 校验内核（批次 0095）。

零第三方依赖：只实现本仓运行期契约实际用到的 JSON Schema 子集。
依据 `spec/D6_REBASELINE_PROPOSAL.md` 4.3(2)：工件契约是 JSON，且 `x-checks`
与 `x-provenance` 是强制字段（没有绑定校验的 schema 不得进入运行期）。

实现的关键字闭集：`type`、`properties`、`required`、`additionalProperties`、
`propertyNames`、`items`、`minItems`、`maxItems`、`uniqueItems`、`enum`、
`const`、`minimum`、`maximum`、`exclusiveMinimum`、`exclusiveMaximum`、
`minLength`、`maxLength`、`pattern`、`minProperties`、`maxProperties`、
`allOf`、`anyOf`、`oneOf`、`if`/`then`/`else`、本地 `$ref`（`#/$defs/...`）。

`default`、`$comment`、`description`、`title`、`examples`、`x-checks`、
`x-provenance` 不参与实例校验：它们是给装配层与解释器读的元数据。
遇到未实现关键字直接报错，不静默忽略——静默忽略会让“schema 通过”变成假绿。

用法（被 `scripts/pm_check.py` 与 `scripts/pm_config.py` 引用）：
  from pm_schema import validate, contract_errors, canonical_bytes, digest
"""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any

TYPE_NAMES = {
    "object",
    "array",
    "string",
    "integer",
    "number",
    "boolean",
    "null",
}

# 明确不参与实例校验的注释/元数据关键字。
ANNOTATIONS = {
    "$schema",
    "$id",
    "$comment",
    "title",
    "description",
    "default",
    "examples",
    "x-checks",
    "x-provenance",
}

# 本内核已实现的关键字；白名单外一律报错（防止未知关键字被静默跳过）。
IMPLEMENTED = {
    "type",
    "properties",
    "required",
    "additionalProperties",
    "propertyNames",
    "items",
    "minItems",
    "maxItems",
    "uniqueItems",
    "enum",
    "const",
    "minimum",
    "maximum",
    "exclusiveMinimum",
    "exclusiveMaximum",
    "minLength",
    "maxLength",
    "pattern",
    "minProperties",
    "maxProperties",
    "allOf",
    "anyOf",
    "oneOf",
    "if",
    "then",
    "else",
    "definitions",
    "$defs",
    "$ref",
}

MAX_DEPTH = 64


class SchemaError(Exception):
    """schema 自身不合法（不是实例不合法）。"""


def canonical_bytes(value: object) -> bytes:
    """规范化 JSON：键排序、无多余空白、保留非 ASCII。"""
    return json.dumps(
        value, sort_keys=True, ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")


def digest(value: object) -> str:
    """对象的 `sha256:<64 hex>` 摘要。"""
    return "sha256:" + hashlib.sha256(canonical_bytes(value)).hexdigest()


def _resolve_ref(root: dict, ref: str) -> dict:
    """只接受本地 `#/...` 引用；跨文件引用在此实现下不可解析。"""
    if not isinstance(ref, str) or not ref.startswith("#/"):
        raise SchemaError(f"只支持本地 $ref，实得 {ref!r}")
    node: Any = root
    for part in ref[2:].split("/"):
        key = part.replace("~1", "/").replace("~0", "~")
        if not isinstance(node, dict) or key not in node:
            raise SchemaError(f"$ref 无法解析：{ref}")
        node = node[key]
    if not isinstance(node, dict):
        raise SchemaError(f"$ref 目标不是对象：{ref}")
    return node


def _type_ok(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    raise SchemaError(f"未实现的 type：{expected}")


def _check_keywords(schema: dict) -> None:
    """schema 自身的结构自检：未实现关键字、非法 type 必须当场报错。"""
    for key in schema:
        if key not in IMPLEMENTED and key not in ANNOTATIONS:
            raise SchemaError(f"未实现的 schema 关键字：{key}")
    expected = schema.get("type")
    if expected is not None:
        names = [expected] if isinstance(expected, str) else list(expected)
        for name in names:
            if name not in TYPE_NAMES:
                raise SchemaError(f"非法的 type：{name!r}")


def _validate(
    value: Any, schema: dict, root: dict, path: str, depth: int
) -> list[dict]:
    if depth > MAX_DEPTH:
        raise SchemaError("schema 嵌套超过上限（疑似循环 $ref）")
    if not isinstance(schema, dict):
        raise SchemaError(f"{path} 的 schema 不是对象")
    _check_keywords(schema)

    if "$ref" in schema:
        return _validate(value, _resolve_ref(root, schema["$ref"]), root, path, depth + 1)

    errors: list[dict] = []

    expected = schema.get("type")
    if expected is not None:
        names = [expected] if isinstance(expected, str) else list(expected)
        if not any(_type_ok(value, name) for name in names):
            errors.append(
                {
                    "path": path,
                    "message": f"应为 {'/'.join(names)}，实得 {type(value).__name__}",
                }
            )
            return errors

    if "enum" in schema:
        try:
            if value not in schema["enum"]:
                errors.append({"path": path, "message": f"取值不在 {schema['enum']} 内"})
        except TypeError:
            errors.append({"path": path, "message": "取值类型不可与 enum 比较"})

    if "const" in schema and value != schema["const"]:
        errors.append({"path": path, "message": f"必须为 {schema['const']!r}"})

    if isinstance(value, dict):
        properties = schema.get("properties", {})
        for name in schema.get("required", []):
            if name not in value:
                errors.append({"path": f"{path}.{name}", "message": "必填字段缺失"})
        for name, child in value.items():
            if name in properties:
                errors.extend(
                    _validate(child, properties[name], root, f"{path}.{name}", depth + 1)
                )
                continue
            extra = schema.get("additionalProperties", True)
            if extra is False:
                errors.append({"path": f"{path}.{name}", "message": "未注册字段"})
            elif isinstance(extra, dict):
                errors.extend(
                    _validate(child, extra, root, f"{path}.{name}", depth + 1)
                )
        names_schema = schema.get("propertyNames")
        if isinstance(names_schema, dict):
            for name in value:
                errors.extend(
                    _validate(name, names_schema, root, f"{path}.<key:{name}>", depth + 1)
                )
        if "minProperties" in schema and len(value) < schema["minProperties"]:
            errors.append(
                {"path": path, "message": f"至少 {schema['minProperties']} 个键"}
            )
        if "maxProperties" in schema and len(value) > schema["maxProperties"]:
            errors.append(
                {"path": path, "message": f"至多 {schema['maxProperties']} 个键"}
            )

    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            errors.append({"path": path, "message": f"至少 {schema['minItems']} 项"})
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            errors.append({"path": path, "message": f"至多 {schema['maxItems']} 项"})
        if schema.get("uniqueItems"):
            seen: set[bytes] = set()
            for index, item in enumerate(value):
                key = canonical_bytes(item)
                if key in seen:
                    errors.append(
                        {"path": f"{path}[{index}]", "message": "数组元素重复"}
                    )
                seen.add(key)
        items = schema.get("items")
        if isinstance(items, dict):
            for index, item in enumerate(value):
                errors.extend(
                    _validate(item, items, root, f"{path}[{index}]", depth + 1)
                )
        elif items is not None:
            raise SchemaError(f"{path}：只实现对象形式的 items")

    if isinstance(value, str):
        if "minLength" in schema and len(value) < schema["minLength"]:
            errors.append({"path": path, "message": f"长度小于 {schema['minLength']}"})
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            errors.append({"path": path, "message": f"长度超过 {schema['maxLength']}"})
        if "pattern" in schema and re.fullmatch(schema["pattern"], value) is None:
            errors.append({"path": path, "message": f"不匹配 {schema['pattern']}"})

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append({"path": path, "message": f"小于下限 {schema['minimum']}"})
        if "maximum" in schema and value > schema["maximum"]:
            errors.append({"path": path, "message": f"大于上限 {schema['maximum']}"})
        if "exclusiveMinimum" in schema and value <= schema["exclusiveMinimum"]:
            errors.append(
                {"path": path, "message": f"必须大于 {schema['exclusiveMinimum']}"}
            )
        if "exclusiveMaximum" in schema and value >= schema["exclusiveMaximum"]:
            errors.append(
                {"path": path, "message": f"必须小于 {schema['exclusiveMaximum']}"}
            )

    for child in schema.get("allOf", []):
        errors.extend(_validate(value, child, root, path, depth + 1))

    if "anyOf" in schema:
        branches = [
            _validate(value, child, root, path, depth + 1)
            for child in schema["anyOf"]
        ]
        if all(branch for branch in branches):
            errors.append({"path": path, "message": "anyOf 无任何分支命中"})

    if "oneOf" in schema:
        branches = [
            _validate(value, child, root, path, depth + 1)
            for child in schema["oneOf"]
        ]
        hits = sum(1 for branch in branches if not branch)
        if hits != 1:
            errors.append(
                {"path": path, "message": f"oneOf 要求恰好命中 1 个分支，实得 {hits}"}
            )

    if "if" in schema:
        condition = _validate(value, schema["if"], root, path, depth + 1)
        branch = schema.get("then") if not condition else schema.get("else")
        if isinstance(branch, dict):
            errors.extend(_validate(value, branch, root, path, depth + 1))

    return errors


def validate(instance: Any, schema: dict) -> list[dict]:
    """返回错误清单；空清单表示通过。schema 自身非法时抛 `SchemaError`。"""
    if not isinstance(schema, dict):
        raise SchemaError("schema 顶层必须是对象")
    return _validate(instance, schema, schema, "$", 0)


def contract_errors(schema: dict) -> list[str]:
    """核验工件契约的强制字段：`x-checks` 与 `x-provenance` 缺一不可。

    返回值是契约缺陷（不是实例缺陷）的说明清单。`pm_check` 在加载任何
    工件 schema 前先调用本函数：没有绑定校验的 schema 不得进入运行期。
    """
    errors: list[str] = []
    checks = schema.get("x-checks")
    if not isinstance(checks, list) or not checks:
        errors.append("缺少非空 x-checks：没有绑定校验的 schema 不得进入运行期")
    elif not all(isinstance(item, str) and item for item in checks):
        errors.append("x-checks 必须是非空字符串数组")
    provenance = schema.get("x-provenance")
    if not isinstance(provenance, dict):
        errors.append("缺少 x-provenance 对象")
    else:
        requires = provenance.get("requires")
        if not isinstance(requires, list) or not requires:
            errors.append("x-provenance.requires 必须是非空数组")
        elif not all(isinstance(item, str) and item for item in requires):
            errors.append("x-provenance.requires 必须是字符串数组")
        extra = set(provenance) - {"requires", "$comment"}
        if extra:
            errors.append(f"x-provenance 含未登记字段：{sorted(extra)}")
    return errors
