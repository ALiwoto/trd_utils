from typing import (
    get_type_hints,
)

class AbstractModel:
    pass

def get_real_attr(cls, attr_name):
    if cls is None:
        return None

    if isinstance(cls, dict):
        return cls.get(attr_name, None)

    if hasattr(cls, attr_name):
        return getattr(cls, attr_name)

    return None

def get_my_field_types(cls):
    type_hints = {}
    for current_cls in cls.__class__.__mro__:
        if current_cls is object or current_cls is AbstractModel:
            break
        type_hints.update(get_type_hints(current_cls))
    return type_hints


