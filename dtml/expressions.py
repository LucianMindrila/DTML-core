"""Stage 4 — resolve literal Expressions to plain values.

An Expression is exactly one of {literal, formula, rule_reference}
(expression.schema.yaml). Resolver v0.1 only evaluates `literal`; a
`formula` or `rule_reference` anywhere raises UnsupportedExpressionForm
with the exact document path — both are valid DTML, just not evaluated
by this resolver version (see ResolverSpecification.md).
"""
from __future__ import annotations

from typing import Any

from .errors import UnsupportedExpressionForm

_EXPRESSION_KEYS = {"literal", "formula", "rule_reference"}


def is_expression(node: Any) -> bool:
    """A single-key dict whose one key is literal/formula/rule_reference.
    A two-key dict like {ref, object_version} or {axis, sense} is never an
    Expression, however similar it looks — it's recursed into as a plain
    nested object instead."""
    return (
        isinstance(node, dict)
        and len(node) == 1
        and next(iter(node)) in _EXPRESSION_KEYS
    )


def resolve_value(node: Any, path: str) -> Any:
    """Recursively resolve every Expression leaf in `node` to a plain
    value (dropping its unit — see ResolverSpecification.md's worked
    output example, which reports plain numbers)."""
    if is_expression(node):
        form = next(iter(node))
        if form != "literal":
            raise UnsupportedExpressionForm(path, form)
        return node["literal"]["value"]
    if isinstance(node, dict):
        return {key: resolve_value(value, f"{path}.{key}") for key, value in node.items()}
    if isinstance(node, list):
        return [resolve_value(value, f"{path}[{i}]") for i, value in enumerate(node)]
    return node
