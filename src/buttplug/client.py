"""Buttplug client for connecting to Buttplug servers."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING

from buttplug._messages import (
    DeviceList,
    Error,
    Ping,
    RequestDeviceList,
    RequestServerInfo,
    ScanningFinished,
    ServerInfo,
    StartScanning,
    StopCmd,
    StopScanning,
)
from buttplug._messages.base import ButtplugMessage
from buttplug.connector import WebSocketConnector
from buttplug.errors import (
    ButtplugConnectorError,
    ButtplugHandshakeError,
    ButtplugPingError,
    error_from_code,
)

if TYPE_CHECKING:
    from buttplug.device import ButtplugDevice


class ButtplugClient:
    """Client for connecting to and interacting with Buttplug servers.

    Example:
        client = ButtplugClient("My App")

        # Set up event handlers before connecting
        client.on_device_added = lambda d: print(f"Found: {d.name}")
        client.on_device_removed = lambda d: print(f"Lost: {d.name}")

        await client.connect("ws://127.0.0.1:12345")
        await client.start_scanning()
        # ... use devices ...
        await client.disconnect()
    """

    def __init__(self, name: str) -> None:
        """Initialize client.

        Args:
            name: Client application name (sent to server during handshake).
        """
        self._name = name
        self._connector: WebSocketConnector | None = None
        self._connected = False
        self._scanning = False

        # Server info from handshake
        self._server_name: str | None = None
        self._max_ping_time: int = 0

        # Ping management
        self._ping_task: asyncio.Task[None] | None = None

        # Device tracking
        self._devices: dict[int, ButtplugDevice] = {}

        # Event callbacks
        self._on_device_added: (
            Callable[[ButtplugDevice], None] | Callable[[ButtplugDevice], Awaitable[None]] | None
        ) = None
        self._on_device_removed: (
            Callable[[ButtplugDevice], None] | Callable[[ButtplugDevice], Awaitable[None]] | None
        ) = None
        self._on_scanning_finished: Callable[[], None] | Callable[[], Awaitable[None]] | None = None
        self._on_server_disconnect: Callable[[], None] | Callable[[], Awaitable[None]] | None = None
        self._on_error: (
            Callable[[Exception], None] | Callable[[Exception], Awaitable[None]] | None
        ) = None

    @property
    def name(self) -> str:
        """Client application name."""
        return self._name

    @property
    def connected(self) -> bool:
        """True if connected to a server."""
        return self._connected

    @property
    def server_name(self) -> str | None:
        """Name of connected server, or None if not connected."""
        return self._server_name

    @property
    def devices(self) -> dict[int, ButtplugDevice]:
        """Dictionary of connected devices by device index."""
        return self._devices

    @property
    def scanning(self) -> bool:
        """True if currently scanning for devices."""
        return self._scanning

    # Event callback properties
    @property
    def on_device_added(
        self,
    ) -> Callable[[ButtplugDevice], None] | Callable[[ButtplugDevice], Awaitable[None]] | None:
        """Callback when a device connects."""
        return self._on_device_added

    @on_device_added.setter
    def on_device_added(
        self,
        callback: Callable[[ButtplugDevice], None]
        | Callable[[ButtplugDevice], Awaitable[None]]
        | None,
    ) -> None:
        self._on_device_added = callback

    @property
    def on_device_removed(
        self,
    ) -> Callable[[ButtplugDevice], None] | Callable[[ButtplugDevice], Awaitable[None]] | None:
        """Callback when a device disconnects."""
        return self._on_device_removed

    @on_device_removed.setter
    def on_device_removed(
        self,
        callback: Callable[[ButtplugDevice], None]
        | Callable[[ButtplugDevice], Awaitable[None]]
        | None,
    ) -> None:
        self._on_device_removed = callback

    @property
    def on_scanning_finished(
        self,
    ) -> Callable[[], None] | Callable[[], Awaitable[None]] | None:
        """Callback when device scanning completes."""
        return self._on_scanning_finished

    @on_scanning_finished.setter
    def on_scanning_finished(
        self, callback: Callable[[], None] | Callable[[], Awaitable[None]] | None
    ) -> None:
        self._on_scanning_finished = callback

    @property
    def on_server_disconnect(
        self,
    ) -> Callable[[], None] | Callable[[], Awaitable[None]] | None:
        """Callback when server disconnects unexpectedly."""
        return self._on_server_disconnect

    @on_server_disconnect.setter
    def on_server_disconnect(
        self, callback: Callable[[], None] | Callable[[], Awaitable[None]] | None
    ) -> None:
        self._on_server_disconnect = callback

    @property
    def on_error(
        self,
    ) -> Callable[[Exception], None] | Callable[[Exception], Awaitable[None]] | None:
        """Callback when an error is received from the server."""
        return self._on_error

    @on_error.setter
    def on_error(
        self,
        callback: Callable[[Exception], None] | Callable[[Exception], Awaitable[None]] | None,
    ) -> None:
        self._on_error = callback

    async def connect(self, url: str) -> None:
        """Connect to a Buttplug server.

        Args:
            url: WebSocket URL (e.g., "ws://127.0.0.1:12345")

        Raises:
            ButtplugConnectorError: If connection fails.
            ButtplugHandshakeError: If handshake fails or version mismatch.
        """
        if self._connected:
            return

        # Create connector and set up callbacks
        self._connector = WebSocketConnector(url)
        self._connector.set_message_callback(self._handle_server_message)
        self._connector.set_disconnect_callback(self._handle_disconnect)

        # Connect WebSocket
        await self._connector.connect()

        # Perform handshake
        try:
            request = RequestServerInfo(id=0, client_name=self._name)
            response = await self._connector.send(request)

            if isinstance(response, Error):
                raise ButtplugHandshakeError(response.error_message)

            if not isinstance(response, ServerInfo):
                raise ButtplugHandshakeError(f"Unexpected response: {type(response).__name__}")

            self._server_name = response.server_name
            self._max_ping_time = response.max_ping_time
            self._connected = True

            # Start ping timer if required
            if self._max_ping_time > 0:
                self._start_ping_timer()

            # Request initial device list
            await self._request_device_list()

        except Exception:
            await self._connector.disconnect()
            self._connector = None
            raise

    async def disconnect(self) -> None:
        """Disconnect from the server.

        Automatically stops all devices before disconnecting.
        """
        if not self._connected or not self._connector:
            return

        self._connected = False

        # Stop ping timer
        self._stop_ping_timer()

        # Stop all devices
        try:
            await self.stop_all_devices()
        except Exception:
            pass

        # Disconnect
        await self._connector.disconnect()
        self._connector = None

        # Clear state
        self._devices.clear()
        self._server_name = None
        self._scanning = False

    async def start_scanning(self) -> None:
        """Start scanning for devices.

        New devices will trigger on_device_added callback.

        Raises:
            ButtplugConnectorError: If not connected.
        """
        if not self._connector or not self._connected:
            raise ButtplugConnectorError("Not connected")

        msg = StartScanning(id=0)
        response = await self._connector.send(msg)

        if isinstance(response, Error):
            raise error_from_code(response.error_code, response.error_message)

        self._scanning = True

    async def stop_scanning(self) -> None:
        """Stop scanning for devices.

        Raises:
            ButtplugConnectorError: If not connected.
        """
        if not self._connector or not self._connected:
            raise ButtplugConnectorError("Not connected")

        msg = StopScanning(id=0)
        response = await self._connector.send(msg)

        if isinstance(response, Error):
            raise error_from_code(response.error_code, response.error_message)

        self._scanning = False

    async def stop_all_devices(self) -> None:
        """Stop all devices.

        Raises:
            ButtplugConnectorError: If not connected.
        """
        if not self._connector or not self._connected:
            raise ButtplugConnectorError("Not connected")

        msg = StopCmd(id=0)
        response = await self._connector.send(msg)

        if isinstance(response, Error):
            raise error_from_code(response.error_code, response.error_message)

    async def _request_device_list(self) -> None:
        """Request current device list from server."""
        if not self._connector:
            return

        msg = RequestDeviceList(id=0)
        response = await self._connector.send(msg)

        if isinstance(response, DeviceList):
            await self._handle_device_list(response)

    async def _handle_server_message(self, msg: ButtplugMessage) -> None:
        """Handle unsolicited messages from server."""
        import inspect

        if isinstance(msg, DeviceList):
            await self._handle_device_list(msg)
        elif isinstance(msg, ScanningFinished):
            self._scanning = False
            if self._on_scanning_finished:
                result = self._on_scanning_finished()
                if inspect.isawaitable(result):
                    await result
        elif isinstance(msg, Error):
            error = error_from_code(msg.error_code, msg.error_message)
            if self._on_error:
                result = self._on_error(error)
                if inspect.isawaitable(result):
                    await result

    async def _handle_device_list(self, device_list: DeviceList) -> None:
        """Process device list and emit add/remove events."""
        import inspect

        from buttplug.device import ButtplugDevice

        # Find new and removed devices
        current_indices = set(self._devices.keys())
        new_indices = set(device_list.devices.keys())

        added_indices = new_indices - current_indices
        removed_indices = current_indices - new_indices

        # Process removals first
        for index in removed_indices:
            device = self._devices.pop(index)
            if self._on_device_removed:
                result = self._on_device_removed(device)
                if inspect.isawaitable(result):
                    await result

        # Process additions
        for index in added_indices:
            device_info = device_list.devices[index]
            device = ButtplugDevice(self, device_info)
            self._devices[index] = device
            if self._on_device_added:
                result = self._on_device_added(device)
                if inspect.isawaitable(result):
                    await result

    async def _handle_disconnect(self) -> None:
        """Handle unexpected disconnection from server."""
        import inspect

        self._connected = False
        self._stop_ping_timer()
        self._devices.clear()
        self._scanning = False

        if self._on_server_disconnect:
            result = self._on_server_disconnect()
            if inspect.isawaitable(result):
                await result

    def _start_ping_timer(self) -> None:
        """Start the ping timer task."""
        if self._ping_task:
            return

        self._ping_task = asyncio.create_task(self._ping_loop())

    def _stop_ping_timer(self) -> None:
        """Stop the ping timer task."""
        if self._ping_task:
            self._ping_task.cancel()
            self._ping_task = None

    async def _ping_loop(self) -> None:
        """Background task to send periodic pings."""
        # Ping at half the max ping time for safety margin
        interval = self._max_ping_time / 2000.0  # Convert ms to seconds

        try:
            while self._connected and self._connector:
                await asyncio.sleep(interval)

                if not self._connected or not self._connector:
                    break

                try:
                    msg = Ping(id=0)
                    response = await self._connector.send(msg)

                    if isinstance(response, Error):
                        error = ButtplugPingError(response.error_message)
                        if self._on_error:
                            import inspect

                            result = self._on_error(error)
                            if inspect.isawaitable(result):
                                await result
                except Exception:
                    pass  # Don't crash on ping failures

        except asyncio.CancelledError:
            pass

    async def _send_device_message(self, msg: ButtplugMessage) -> ButtplugMessage:
        """Send a device message and return response.

        Internal method used by ButtplugDevice.

        Raises:
            ButtplugConnectorError: If not connected.
        """
        if not self._connector or not self._connected:
            raise ButtplugConnectorError("Not connected")

        return await self._connector.send(msg)
