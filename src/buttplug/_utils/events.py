"""Event handling utilities."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Generic, TypeVar

T = TypeVar("T")

# Type alias for event callbacks (sync or async)
Callback = Callable[[T], None] | Callable[[T], Awaitable[None]]


class EventHandler(Generic[T]):
    """Simple event handler supporting both sync and async callbacks.

    Example:
        handler: EventHandler[str] = EventHandler()
        handler += lambda msg: print(msg)
        await handler.emit("Hello")
    """

    def __init__(self) -> None:
        self._callbacks: list[Callback[T]] = []

    def __iadd__(self, callback: Callback[T]) -> EventHandler[T]:
        """Add a callback using += operator."""
        self._callbacks.append(callback)
        return self

    def __isub__(self, callback: Callback[T]) -> EventHandler[T]:
        """Remove a callback using -= operator."""
        try:
            self._callbacks.remove(callback)
        except ValueError:
            pass
        return self

    async def emit(self, value: T) -> None:
        """Emit event to all registered callbacks."""
        import inspect

        for callback in self._callbacks:
            result = callback(value)
            if inspect.isawaitable(result):
                await result

    def clear(self) -> None:
        """Remove all callbacks."""
        self._callbacks.clear()

    def __bool__(self) -> bool:
        """True if any callbacks are registered."""
        return len(self._callbacks) > 0
