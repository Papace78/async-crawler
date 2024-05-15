import pytest

from crawler.utils import get_nested


@pytest.mark.parametrize(
    argnames=("payload", "keys", "expected"),
    argvalues=[
        (
            {"top": {"nested": {"subnested": "value"}}},
            ["top", "nested", "subnested"],
            "value",
        ),
        (
            {"top": {"nested": {"subnested": "value"}}},
            ["top", "nested", "missing"],
            "default",
        ),
        ({"top": {"nested": "value"}}, [], {"top": {"nested": "value"}}),
    ],
)
def test_get_nested(payload, keys, expected) -> None:
    actual = get_nested(payload, keys, expected)
    assert actual == expected
