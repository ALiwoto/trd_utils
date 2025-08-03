
from typing import Type, TypeVar

from trd_utils.types_helper.model_config import ModelConfig
from trd_utils.types_helper.utils import AbstractModel


T = TypeVar('T', bound=AbstractModel)

def ignore_json_fields(fields: list[str]):
    def wrapper(cls: Type[T]) -> Type[T]:
        config = getattr(cls, "_model_config", None)
        if not config:
            config = ModelConfig()
        
        config.ignored_fields = fields.copy()
        setattr(cls, "_model_config", config)
        return cls
    return wrapper

