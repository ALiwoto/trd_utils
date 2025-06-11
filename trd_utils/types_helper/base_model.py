from decimal import Decimal
import json
from typing import (
    Union,
    get_type_hints,
    Any,
    get_args as get_type_args,
)

from trd_utils.html_utils.html_formats import camel_to_snake

# Whether to use ultra-list instead of normal python list or not.
# This might be convenient in some cases, but it is not recommended
# to use it in production code because of the performance overhead.
ULTRA_LIST_ENABLED: bool = False

# Whether to also set the camelCase attribute names for the model.
# This is useful when the API returns camelCase attribute names
# and you want to use them as is in the model; by default, the
# attribute names are converted to snake_case.
SET_CAMEL_ATTR_NAMES = False


def get_my_field_types(cls):
    type_hints = {}
    for current_cls in cls.__class__.__mro__:
        if current_cls is object or current_cls is BaseModel:
            break
        type_hints.update(get_type_hints(current_cls))
    return type_hints


def get_real_attr(cls, attr_name):
    if cls is None:
        return None

    if isinstance(cls, dict):
        return cls.get(attr_name, None)

    if hasattr(cls, attr_name):
        return getattr(cls, attr_name)

    return None


def is_any_type(target_type: type) -> bool:
    return target_type == Any or target_type is type(None)


# TODO: add support for max_depth for this...
def value_to_normal_obj(value):
    """
    Converts a custom value, to a corresponding "normal object" which can be used
    in dict.
    """
    if isinstance(value, BaseModel):
        return value.to_dict()

    if isinstance(value, list):
        results = []
        for current in value:
            results.append(value_to_normal_obj(current))
        return results

    if isinstance(value, (int, str)) or value is None:
        return value

    if isinstance(value, Decimal):
        return str(value)

    if isinstance(value, dict):
        result = {}
        for inner_key, inner_value in value.items():
            result[inner_key] = value_to_normal_obj(inner_value)

        return result

    raise TypeError(f"unsupported type provided: {type(value)}")


def generic_obj_to_value(
    expected_type: type,
    expected_type_args: tuple[type],
    value: Any,
):
    """
    Converts a normal JSON-compatible "object" to a customized python value.
    """
    if not expected_type_args:
        expected_type_args = get_type_args(expected_type)

    if isinstance(value, list):
        result = []
        for current in value:
            result.append(generic_obj_to_value(
                expected_type=expected_type_args[0],
                expected_type_args=expected_type_args[1:],
                value=current,
            ))
        return result

    expected_type_name = getattr(expected_type, "__name__", None)
    if expected_type_name == "dict" and isinstance(value, dict):
        result = {}
        for inner_key, inner_value in value.items():
            result[expected_type_args[0](inner_key)] = generic_obj_to_value(
                expected_type=expected_type_args[1],
                expected_type_args=expected_type_args[1:],
                value=inner_value,
            )
        return result

    if isinstance(value, dict) and issubclass(expected_type, BaseModel):
        if len(expected_type_args) > 1:
            raise ValueError(
                "unsupported operation: at this time we cannot have"
                " expected type args at all...",
            )
        return expected_type(**value)

    if not expected_type_args:
        if isinstance(value, expected_type):
            return value
        return expected_type(value)

    raise TypeError(f"unsupported type: {type(value)}")


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


class BaseModel:
    def __init__(self, **kwargs):
        annotations = get_my_field_types(self)
        # annotations = self.__annotations__
        for key, value in kwargs.items():
            corrected_key = key
            if key not in annotations:
                # key does not exist, try converting it to snake_case
                corrected_key = camel_to_snake(key)
                if corrected_key not in annotations:
                    # just ignore and continue
                    annotations[key] = Any
                    annotations[corrected_key] = Any

            expected_type = annotations[corrected_key]
            if hasattr(self, "_get_" + corrected_key + "_type"):
                try:
                    overridden_type = getattr(self, "_get_" + corrected_key + "_type")(
                        kwargs
                    )
                    if overridden_type:
                        expected_type = overridden_type
                except Exception:
                    pass

            expected_type_args = get_type_args(expected_type)
            expected_type_name = getattr(expected_type, "__name__", None)
            is_optional_type = expected_type_name == "Optional"
            is_dict_type = expected_type_name == "dict"
            # maybe in the future we can have some other usages for is_optional_type
            # variable or something like that.
            if is_optional_type:
                try:
                    expected_type = expected_type_args[0]
                except Exception:
                    # something went wrong, just ignore and continue
                    expected_type = Any

            if value is None:
                # just skip...
                pass
            elif isinstance(value, dict) and is_dict_type:
                value = generic_obj_to_value(
                    expected_type=expected_type,
                    expected_type_args=expected_type_args,
                    value=value,
                )

            # Handle nested models
            elif isinstance(value, dict) and issubclass(expected_type, BaseModel):
                value = expected_type(**value)

            elif isinstance(value, list):
                if not expected_type_args:
                    # if it's Any, it means we shouldn't really care about the type
                    if expected_type != Any:
                        value = expected_type(value)
                else:
                    value = generic_obj_to_value(
                        expected_type=expected_type,
                        expected_type_args=expected_type_args,
                        value=value,
                    )

                if ULTRA_LIST_ENABLED and isinstance(value, list):
                    value = convert_to_ultra_list(value)

            # Type checking
            elif not (is_any_type(expected_type) or isinstance(value, expected_type)):
                try:
                    value = expected_type(value)
                except Exception:
                    raise TypeError(
                        f"Field {corrected_key} must be of type {expected_type},"
                        + f" but it's {type(value)}"
                    )

            setattr(self, corrected_key, value)
            if SET_CAMEL_ATTR_NAMES and key != corrected_key:
                setattr(self, key, value)

        # Check if all required fields are present
        # for field in self.__annotations__:
        #     if not hasattr(self, field):
        #         raise ValueError(f"Missing required field: {field}")

    @classmethod
    def deserialize(cls, json_data: Union[str, dict]):
        if isinstance(json_data, str):
            data = json.loads(json_data)
        else:
            data = json_data
        return cls(**data)

    def serialize(
        self,
        separators=(",", ":"),
        ensure_ascii=True,
        sort_keys=True,
    ) -> bytes:
        return json.dumps(
            obj=self.to_dict(),
            ensure_ascii=ensure_ascii,
            separators=separators,
            sort_keys=sort_keys,
        )

    def to_dict(self) -> dict:
        annotations = get_my_field_types(self)
        result_dict = {}
        for key, _ in annotations.items():
            if not isinstance(key, str):
                continue

            if key.startswith("__") or key.startswith(f"_{self.__class__.__name__}__"):
                # ignore private attributes
                continue

            result_dict[key] = value_to_normal_obj(getattr(self, key))
        return result_dict
