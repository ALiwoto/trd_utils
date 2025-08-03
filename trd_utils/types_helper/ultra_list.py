

from typing import Any
from trd_utils.types_helper.utils import get_my_field_types, get_real_attr


class UltraList(list):
    def __getattr__(self, attr):
        if len(self) == 0:
            return None
        return UltraList([get_real_attr(item, attr) for item in self])


def convert_to_ultra_list(value: Any) -> UltraList:
    if not value:
        return UltraList()

    # Go through all fields of the value and convert them to
    # UltraList if they are lists

    try:
        if isinstance(value, list):
            return UltraList([convert_to_ultra_list(item) for item in value])
        elif isinstance(value, dict):
            return {k: convert_to_ultra_list(v) for k, v in value.items()}
        elif isinstance(value, tuple):
            return tuple(convert_to_ultra_list(v) for v in value)
        elif isinstance(value, set):
            return {convert_to_ultra_list(v) for v in value}

        for attr, attr_value in get_my_field_types(value).items():
            if isinstance(attr_value, list):
                setattr(value, attr, convert_to_ultra_list(getattr(value, attr)))

        return value
    except Exception:
        return value



