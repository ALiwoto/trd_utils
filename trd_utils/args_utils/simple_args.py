from __future__ import annotations


class SimpleArgs(dict[str, str]):
    """
    Simple args represents a very simple and painless way of parsing arguments
    passed to us as a text.
    """

    def get_int(self, key: str, default: int | None = None) -> int | None:
        value = self.get(key, default)
        if value == default or isinstance(value, int):
            return value

        try:
            return int(value)
        except Exception:
            return default

    def get_bool(self, key: str, default: bool | None = None) -> bool | None:
        value = self.get(key, default)
        if value == default or isinstance(value, bool):
            return value

        try:
            return bool(value)
        except Exception:
            return default

    @staticmethod
    def parse(input: str | list[str]) -> SimpleArgs:
        result: SimpleArgs = SimpleArgs()
        last_arg_name: str = None
        if isinstance(input, str):
            values = input.split()
        elif isinstance(input, list):
            values = input
        else:
            raise ValueError(
                f"invalid type passed to parse: {type(input)}: '{input}'; "
                "expected str or list"
            )

        for current in values:
            if current.startswith("--"):
                last_arg_name = current.lstrip("--")
                result[last_arg_name] = "1"
                result[last_arg_name.replace("-", "_")] = "1"
                continue
            elif last_arg_name:
                result[last_arg_name] = current
                result[last_arg_name.replace("-", "_")] = current
                last_arg_name = None

        return result
