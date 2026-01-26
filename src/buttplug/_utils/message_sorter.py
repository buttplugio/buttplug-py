"""Message sorting and request/response correlation."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from buttplug._messages.base import ButtplugMessage


class MessageSorter:
    """Correlates outgoing requests with incoming responses by message Id.

    Thread-safe for concurrent request handling.
    """

    def __init__(self) -> None:
        self._next_id = 1
        self._pending: dict[int, asyncio.Future[ButtplugMessage]] = {}
        self._lock = asyncio.Lock()

    def get_next_id(self) -> int:
        """Get next available message ID."""
        msg_id = self._next_id
        self._next_id += 1
        if self._next_id > 4294967295:  # Protocol max
            self._next_id = 1
        return msg_id

    async def wait_for_response(self, msg_id: int, timeout: float = 30.0) -> ButtplugMessage:
        """Wait for response with matching message ID.

        Args:
            msg_id: Message ID to wait for.
            timeout: Maximum seconds to wait.

        Returns:
            Response message.

        Raises:
            asyncio.TimeoutError: If timeout expires.
            asyncio.CancelledError: If cancelled.
        """
        future: asyncio.Future[ButtplugMessage] = asyncio.get_event_loop().create_future()

        async with self._lock:
            self._pending[msg_id] = future

        try:
            return await asyncio.wait_for(future, timeout=timeout)
        finally:
            async with self._lock:
                self._pending.pop(msg_id, None)

    async def resolve(self, msg_id: int, response: ButtplugMessage) -> bool:
        """Resolve pending request with response.

        Args:
            msg_id: Message ID of request.
            response: Response message.

        Returns:
            True if a pending request was resolved, False otherwise.
        """
        async with self._lock:
            future = self._pending.get(msg_id)
            if future and not future.done():
                future.set_result(response)
                return True
        return False

    async def reject_all(self, error: Exception) -> None:
        """Reject all pending requests with an error."""
        async with self._lock:
            for future in self._pending.values():
                if not future.done():
                    future.set_exception(error)
            self._pending.clear()

    @property
    def pending_count(self) -> int:
        """Number of pending requests."""
        return len(self._pending)
