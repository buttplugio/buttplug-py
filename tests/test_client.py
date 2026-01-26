"""Tests for ButtplugClient (unit tests without network)."""

import pytest

from buttplug import ButtplugClient
from buttplug.errors import ButtplugConnectorError


class TestButtplugClientInit:
    """Tests for client initialization and properties."""

    def test_client_name(self):
        """Client stores name."""
        client = ButtplugClient("My Test App")
        assert client.name == "My Test App"

    def test_initial_state(self):
        """Client starts in disconnected state."""
        client = ButtplugClient("Test")

        assert client.connected is False
        assert client.server_name is None
        assert client.scanning is False
        assert len(client.devices) == 0

    def test_event_callbacks_none_by_default(self):
        """Event callbacks are None by default."""
        client = ButtplugClient("Test")

        assert client.on_device_added is None
        assert client.on_device_removed is None
        assert client.on_scanning_finished is None
        assert client.on_server_disconnect is None
        assert client.on_error is None

    def test_set_event_callbacks(self):
        """Event callbacks can be set."""
        client = ButtplugClient("Test")

        added_callback = lambda d: None
        removed_callback = lambda d: None
        scanning_callback = lambda: None
        disconnect_callback = lambda: None
        error_callback = lambda e: None

        client.on_device_added = added_callback
        client.on_device_removed = removed_callback
        client.on_scanning_finished = scanning_callback
        client.on_server_disconnect = disconnect_callback
        client.on_error = error_callback

        assert client.on_device_added is added_callback
        assert client.on_device_removed is removed_callback
        assert client.on_scanning_finished is scanning_callback
        assert client.on_server_disconnect is disconnect_callback
        assert client.on_error is error_callback


class TestButtplugClientNotConnected:
    """Tests for client methods when not connected."""

    async def test_start_scanning_not_connected(self):
        """start_scanning raises when not connected."""
        client = ButtplugClient("Test")

        with pytest.raises(ButtplugConnectorError, match="Not connected"):
            await client.start_scanning()

    async def test_stop_scanning_not_connected(self):
        """stop_scanning raises when not connected."""
        client = ButtplugClient("Test")

        with pytest.raises(ButtplugConnectorError, match="Not connected"):
            await client.stop_scanning()

    async def test_stop_all_devices_not_connected(self):
        """stop_all_devices raises when not connected."""
        client = ButtplugClient("Test")

        with pytest.raises(ButtplugConnectorError, match="Not connected"):
            await client.stop_all_devices()

    async def test_disconnect_when_not_connected(self):
        """disconnect is safe to call when not connected."""
        client = ButtplugClient("Test")

        # Should not raise
        await client.disconnect()
        assert client.connected is False
