import pytest

from trd_utils.html_utils.html_formats import (
    get_html_normal,
    html_blockquote,
    html_expandable_blockquote,
    html_link,
    html_mono,
    html_normal,
    html_pre,
    html_spoiler,
    to_unicode_escape,
)


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


def test_get_html_normal_escapes_values():
    assert get_html_normal(" <tag>", 10) == " &lt;tag&gt;10"


def test_html_normal_escapes_suffixes():
    assert html_normal("x < y", " & z") == "x &lt; y &amp; z"


def test_html_mono_escapes_suffixes():
    assert html_mono("x < y", " & z") == "<code>x &lt; y</code> &amp; z"


def test_html_link_quotes_and_escapes_href():
    assert (
        html_link("ALiwoto", '"https://example.com?a=1&b=2"')
        == '<a href="https://example.com?a=1&amp;b=2">ALiwoto</a>'
    )


def test_html_pre_uses_telegram_code_language_class():
    assert (
        html_pre("x < y", "python")
        == '<pre><code class="language-python">x &lt; y</code></pre>'
    )


def test_html_spoiler_uses_telegram_tag():
    assert html_spoiler("x < y") == "<tg-spoiler>x &lt; y</tg-spoiler>"


def test_html_blockquote():
    assert html_blockquote("x < y") == "<blockquote>x &lt; y</blockquote>"


def test_html_expandable_blockquote():
    assert (
        html_expandable_blockquote("x < y")
        == "<blockquote expandable>x &lt; y</blockquote>"
    )
