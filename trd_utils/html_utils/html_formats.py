import html


def camel_to_snake(str_value: str) -> str:
    """
    Convert CamelCase to snake_case.
    https://stackoverflow.com/a/44969381/16518789
    """
    return "".join(["_" + c.lower() if c.isupper() else c for c in str_value]).lstrip("_")


def to_camel_case(snake_str: str) -> str:
    """
    Convert snake_case to CamelCase.
    https://stackoverflow.com/a/19053800/16518789
    """
    return "".join(x.capitalize() for x in snake_str.lower().split("_"))


def to_lower_camel_case(snake_str: str) -> str:
    # We capitalize the first letter of each component except the first one
    # with the 'capitalize' method and join them together.
    camel_string = to_camel_case(snake_str)
    return snake_str[0].lower() + camel_string[1:]


def to_unicode_escape(text):
    """
    Converts a string into a sequence of \\uXXXX format.
    """
    # We use f-strings to format the ordinal value of each char
    # into 4-digit hexadecimal
    return "".join(f"\\u{ord(char):04x}" for char in text)


def _format_html_attr(value: str) -> str:
    """
    Escape an HTML attribute value and wrap it in double quotes.

    If callers pass an already-quoted attribute value, one matching pair of
    surrounding single or double quotes is stripped before escaping.
    """
    value = str(value).strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        value = value[1:-1]
    return f'"{html.escape(value, quote=True)}"'


def get_html_normal(*argv) -> str:
    """
    Join and escape extra values appended after formatted HTML fragments.
    """
    if argv is None or len(argv) == 0:
        return ""

    my_str = ""
    for value in argv:
        if not value:
            continue
        my_str += html.escape(str(value))

    return my_str


def html_normal(value, *argv) -> str:
    my_str = html.escape(str(value))
    for value in argv:
        if value:
            my_str += html.escape(str(value))
    return my_str


def html_mono(value, *argv) -> str:
    return f"<code>{html.escape(str(value))}</code>" + get_html_normal(*argv)


def html_in_parenthesis(value) -> str:
    if not value:
        return ": "
    return f" ({html.escape(str(value))}): "


def html_bold(value, *argv) -> str:
    return f"<b>{html.escape(str(value))}</b>" + get_html_normal(*argv)


def html_italic(value, *argv) -> str:
    return f"<i>{html.escape(str(value))}</i>" + get_html_normal(*argv)


def html_link(value, link: str, *argv) -> str:
    if not isinstance(link, str) or len(link) == 0:
        return html_mono(value, *argv)
    return f"<a href={_format_html_attr(link)}>{html.escape(str(value))}</a>" + get_html_normal(
        *argv
    )


def html_code_snippets(value, language: str, *argv):
    return html_pre(value, language, *argv)


def html_pre(value, language: str, *argv):
    return (
        f"<pre><code class={_format_html_attr(f'language-{language}')}>"
        f"{html.escape(str(value))}</code></pre>"
    ) + get_html_normal(*argv)


def html_spoiler(value, *argv):
    return f"<tg-spoiler>{html.escape(str(value))}</tg-spoiler>" + get_html_normal(*argv)


def html_blockquote(value, *argv, expandable: bool = False):
    attr = " expandable" if expandable else ""
    return f"<blockquote{attr}>{html.escape(str(value))}</blockquote>" + get_html_normal(*argv)


def html_expandable_blockquote(value, *argv):
    return html_blockquote(value, *argv, expandable=True)
