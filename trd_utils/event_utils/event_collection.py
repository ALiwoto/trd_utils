
import inspect
from typing import Callable, Generic, TypeVar

# We define a type variable 'T' that must be a Callable (function/coroutine)
T = TypeVar("T", bound=Callable)

class EventCollection(Generic[T]):
    _handlers: list[T]

    def __init__(self):
        self._handlers = []

    def __iadd__(self, observer: T) -> "EventCollection[T]":
        """Allows: event += callback"""
        if observer not in self._handlers:
            self._handlers.append(observer)
        return self

    def __isub__(self, observer: T) -> "EventCollection[T]":
        """Allows: event -= callback"""
        if observer in self._handlers:
            self._handlers.remove(observer)
        return self

    async def __call__(self, *args, **kwargs):
        """Allows: await event(data)"""
        for observer in self._handlers:
            # Check if the callback is a coroutine (async) or standard function
            if inspect.iscoroutinefunction(observer):
                await observer(*args, **kwargs)
            else:
                observer(*args, **kwargs)

    def __len__(self) -> int:
        return len(self._handlers)

    def clear(self):
        self._handlers.clear()
