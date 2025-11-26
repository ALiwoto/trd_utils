
from typing import Type, TypeVar

from trd_utils.types_helper.model_config import ModelConfig
from trd_utils.types_helper.utils import AbstractModel


T = TypeVar('T', bound=AbstractModel)

def ignore_json_fields(fields: list[str]):
    def wrapper(cls: Type[T]) -> Type[T]:
        config = getattr(cls, "_model_config", None)
        if not config:
            config = ModelConfig()
        
        if not config.ignored_fields:
            config.ignored_fields = []
        for field in fields:
            if field not in config.ignored_fields:
                config.ignored_fields.append(field)
        setattr(cls, "_model_config", config)
        return cls
    return wrapper

def map_json_fields(field_map: dict[str, str]):
    def wrapper(cls: Type[T]) -> Type[T]:
        config = getattr(cls, "_model_config", None)
        if not config:
            config = ModelConfig()
        
        if not config.mapped_fields:
            config.mapped_fields = {}
        for k, v in field_map.items():
            if k not in config.mapped_fields:
                config.mapped_fields[k] = v
        setattr(cls, "_model_config", config)
        return cls
    return wrapper

