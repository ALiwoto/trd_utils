from typing import (
    get_type_hints,
)

class AbstractModel:
    pass

def is_type_optional(target: type) -> bool:
    if getattr(target, "__name__", None) == "Optional":
        # e.g: my_field: Optional[str] = None
        return True
    
    target_args = getattr(target, "__args__", None)
    if target_args and len(target_args) > 1 and target_args[1] is type(None):
        # e.g: my_field: Decimal | None = None
        return True
    
    return False

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


