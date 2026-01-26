"""WebSocket connector for Buttplug server communication."""

from __future__ import annotations

import asyncio
import json
from collections.abc import Callable
from typing import TYPE_CHECKING

import websockets
from websockets.asyncio.client import ClientConnection

from buttplug._messages.base import ButtplugMessage, parse_messages
from buttplug._utils.message_sorter import MessageSorter
from buttplug.errors import ButtplugConnectorError

if TYPE_CHECKING:
    from collections.abc import Awaitable


class WebSocketConnector:
    """WebSocket connector for Buttplug server communication.

    Handles WebSocket connection, message serialization/deserialization,
    and request/response correlation.

    Not intended for direct use - ButtplugClient handles this internally.
    """

    def __init__(self, url: str) -> None:
        """Initialize connector.

        Args:
            url: WebSocket URL (e.g., "ws://127.0.0.1:12345")
        """
        self._url = url
        self._ws: ClientConnection | None = None
        self._message_sorter = MessageSorter()
        self._receive_task: asyncio.Task[None] | None = None
        self._connected = False

        # Callbacks for unsolicited messages
        self._on_message: Callable[[ButtplugMessage], Awaitable[None]] | None = None
        self._on_disconnect: Callable[[], Awaitable[None]] | None = None

    @property
    def connected(self) -> bool:
        """True if currently connected."""
        return self._connected and self._ws is not None

    def set_message_callback(self, callback: Callable[[ButtplugMessage], Awaitable[None]]) -> None:
        """Set callback for unsolicited server messages (Id=0)."""
        self._on_message = callback

    def set_disconnect_callback(self, callback: Callable[[], Awaitable[None]]) -> None:
        """Set callback for disconnection events."""
        self._on_disconnect = callback

    async def connect(self) -> None:
        """Connect to the Buttplug server.

        Raises:
            ButtplugConnectorError: If connection fails.
        """
        if self._connected:
            return

        try:
            self._ws = await websockets.connect(self._url)
            self._connected = True
            self._receive_task = asyncio.create_task(self._receive_loop())
        except Exception as e:
            raise ButtplugConnectorError(f"Failed to connect to {self._url}: {e}") from e

    async def disconnect(self) -> None:
        """Disconnect from the server."""
        self._connected = False

        if self._receive_task:
            self._receive_task.cancel()
            try:
                await self._receive_task
            except asyncio.CancelledError:
                pass
            self._receive_task = None

        if self._ws:
            try:
                await self._ws.close()
            except Exception:
                pass
            self._ws = None

        # Reject any pending requests
        await self._message_sorter.reject_all(ButtplugConnectorError("Connection closed"))

    async def send(self, message: ButtplugMessage, timeout: float = 30.0) -> ButtplugMessage:
        """Send message and wait for response.

        Args:
            message: Message to send.
            timeout: Maximum seconds to wait for response.

        Returns:
            Response message from server.

        Raises:
            ButtplugConnectorError: If not connected or send fails.
            asyncio.TimeoutError: If response timeout expires.
        """
        if not self._ws or not self._connected:
            raise ButtplugConnectorError("Not connected")

        # Assign message ID if not set
        msg_id = self._message_sorter.get_next_id()
        message.id = msg_id

        # Serialize and send
        protocol_data = message.to_protocol()
        json_str = json.dumps(protocol_data)

        try:
            await self._ws.send(json_str)
        except Exception as e:
            raise ButtplugConnectorError(f"Failed to send message: {e}") from e

        # Wait for response with matching ID
        return await self._message_sorter.wait_for_response(msg_id, timeout)

    async def send_no_response(self, message: ButtplugMessage) -> None:
        """Send message without waiting for response.

        Used for messages that don't expect a reply (like Ping with manual handling).

        Args:
            message: Message to send.

        Raises:
            ButtplugConnectorError: If not connected or send fails.
        """
        if not self._ws or not self._connected:
            raise ButtplugConnectorError("Not connected")

        # Assign message ID if not set
        if message.id == 0:
            message.id = self._message_sorter.get_next_id()

        protocol_data = message.to_protocol()
        json_str = json.dumps(protocol_data)

        try:
            await self._ws.send(json_str)
        except Exception as e:
            raise ButtplugConnectorError(f"Failed to send message: {e}") from e

    async def _receive_loop(self) -> None:
        """Background task to receive and dispatch messages."""
        try:
            while self._connected and self._ws:
                try:
                    raw = await self._ws.recv()
                except websockets.exceptions.ConnectionClosed:
                    break

                try:
                    data = json.loads(raw)
                    messages = parse_messages(data)
                except (json.JSONDecodeError, ValueError):
                    # Log but don't crash on parse errors
                    continue

                for msg in messages:
                    if msg.id == 0:
                        # Unsolicited message - dispatch to callback
                        if self._on_message:
                            try:
                                await self._on_message(msg)
                            except Exception:
                                pass  # Don't let callback errors crash loop
                    else:
                        # Response to a request - resolve pending future
                        await self._message_sorter.resolve(msg.id, msg)

        finally:
            if self._connected:
                self._connected = False
                if self._on_disconnect:
                    try:
                        await self._on_disconnect()
                    except Exception:
                        pass
