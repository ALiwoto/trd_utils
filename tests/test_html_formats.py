import pytest

from trd_utils.html_utils.html_formats import to_unicode_escape


@pytest.mark.parametrize(
    "value,expected",
    [
        ("", ""),
        ("A", "\\u0041"),
        ("ABC", "\\u0041\\u0042\\u0043"),
        ("a1", "\\u0061\\u0031"),
        (" ", "\\u0020"),
        ("ß", "\\u00df"),
        ("Ω", "\\u03a9"),
        ("😀", "\\u1f600"),
        ("AΩ😀", "\\u0041\\u03a9\\u1f600"),
    ],
)
def test_to_unicode_escape(value: str, expected: str):
    assert to_unicode_escape(value) == expected
