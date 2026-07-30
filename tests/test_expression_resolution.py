"""dtml.expressions — literal Expressions resolve to plain values;
formula/rule_reference raise UnsupportedExpressionForm with the exact
path. See docs/Specifications/ResolverSpecification.md, stage 4.
"""
import pytest

from dtml.errors import UnsupportedExpressionForm
from dtml.expressions import is_expression, resolve_value


def test_literal_resolves_to_plain_value():
    node = {"literal": {"value": 20, "unit": "mm"}}
    assert resolve_value(node, "$.x") == 20


def test_formula_raises_unsupported_with_path():
    node = {"formula": {"formula": "a - b", "unit": "mm"}}
    with pytest.raises(UnsupportedExpressionForm) as exc_info:
        resolve_value(node, "$.thickness")
    assert exc_info.value.path == "$.thickness"
    assert exc_info.value.form == "formula"


def test_rule_reference_raises_unsupported():
    node = {"rule_reference": {"ref": "cuttingedgebespoke.rule.foo", "object_version": "1.0.0"}}
    with pytest.raises(UnsupportedExpressionForm) as exc_info:
        resolve_value(node, "$.pitch")
    assert exc_info.value.form == "rule_reference"


def test_recurses_into_plain_nested_dict_not_treated_as_expression():
    # {axis, sense} has two keys, neither of which is literal/formula/
    # rule_reference — must be recursed into, not mistaken for an
    # Expression.
    node = {"axis": "y", "sense": "positive"}
    assert not is_expression(node)
    assert resolve_value(node, "$.direction") == {"axis": "y", "sense": "positive"}


def test_recurses_into_reference_object_leaving_values_untouched():
    # {ref, object_version} also has two keys — must not be misidentified
    # as an Expression even though "ref" and "value" sound similar.
    node = {"ref": "cuttingedgebespoke.feature.shelf_pin_array", "object_version": "1.0.0"}
    assert not is_expression(node)
    assert resolve_value(node, "$.feature") == node


def test_resolves_nested_dict_of_expressions():
    node = {
        "x": {"literal": {"value": 20, "unit": "mm"}},
        "y": {"literal": {"value": 20, "unit": "mm"}},
    }
    assert resolve_value(node, "$.position") == {"x": 20, "y": 20}


def test_resolves_list_of_expressions():
    node = [{"literal": {"value": 1, "unit": "mm"}}, {"literal": {"value": 2, "unit": "mm"}}]
    assert resolve_value(node, "$.items") == [1, 2]


def test_unsupported_form_deep_inside_a_dict_reports_full_path():
    node = {"parameters": {"count": {"formula": {"formula": "n", "unit": "count"}}}}
    with pytest.raises(UnsupportedExpressionForm) as exc_info:
        resolve_value(node, "$")
    assert exc_info.value.path == "$.parameters.count"
