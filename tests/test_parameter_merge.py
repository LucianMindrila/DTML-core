"""dtml.merge.deep_merge — plain recursive dict merge over already-resolved
values. See docs/Specifications/ResolverSpecification.md, stage 5.
"""
from dtml.merge import deep_merge


def test_override_scalar_wins():
    base = {"count": 5, "pitch": 32}
    override = {"count": 3}
    assert deep_merge(base, override) == {"count": 3, "pitch": 32}


def test_unspecified_keys_keep_base_default():
    base = {"count": 5, "pitch": 32, "start_offset": 100}
    override = {"count": 3}
    merged = deep_merge(base, override)
    assert merged["pitch"] == 32
    assert merged["start_offset"] == 100


def test_nested_dict_merges_key_by_key():
    base = {"direction": {"axis": "y", "sense": "positive"}}
    override = {"direction": {"sense": "negative"}}
    merged = deep_merge(base, override)
    assert merged["direction"] == {"axis": "y", "sense": "negative"}


def test_new_key_in_override_is_added():
    base = {"count": 5}
    override = {"start_offset": 100}
    assert deep_merge(base, override) == {"count": 5, "start_offset": 100}


def test_does_not_mutate_base():
    base = {"direction": {"axis": "y", "sense": "positive"}}
    override = {"direction": {"sense": "negative"}}
    deep_merge(base, override)
    assert base == {"direction": {"axis": "y", "sense": "positive"}}


def test_empty_override_returns_equivalent_of_base():
    base = {"count": 5, "pitch": 32}
    assert deep_merge(base, {}) == base
