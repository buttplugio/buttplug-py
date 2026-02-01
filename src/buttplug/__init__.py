"""Buttplug - Intimate Hardware Control Library.

A Python client library for the Buttplug protocol v4.

Basic usage:
    from buttplug import ButtplugClient, DeviceOutputCommand, OutputType

    async def main():
        client = ButtplugClient("My App")
        await client.connect("ws://127.0.0.1:12345")

        await client.start_scanning()
        await asyncio.sleep(5)
        await client.stop_scanning()

        for device in client.devices.values():
            if device.has_output(OutputType.VIBRATE):
                await device.run_output(DeviceOutputCommand(OutputType.VIBRATE, 0.5))
                await asyncio.sleep(1)
                await device.stop()

        await client.disconnect()

    asyncio.run(main())
"""

__version__ = "1.0.0"

# Client and Device (public API)
from buttplug.client import ButtplugClient
from buttplug.command import DeviceOutputCommand
from buttplug.device import ButtplugDevice
from buttplug.enums import ErrorCode, InputCommandType, InputType, OutputType

# Errors (public API)
from buttplug.errors import (
    ButtplugConnectorError,
    ButtplugDeviceError,
    ButtplugError,
    ButtplugHandshakeError,
    ButtplugMessageError,
    ButtplugPingError,
    ButtplugUnknownError,
)

# Feature-level control (advanced API)
from buttplug.feature import CommandValue, DeviceFeature

__all__ = [
    # Version
    "__version__",
    # Enums
    "OutputType",
    "InputType",
    "InputCommandType",
    "ErrorCode",
    # Errors
    "ButtplugError",
    "ButtplugConnectorError",
    "ButtplugHandshakeError",
    "ButtplugPingError",
    "ButtplugDeviceError",
    "ButtplugMessageError",
    "ButtplugUnknownError",
    # Client and Device
    "ButtplugClient",
    "ButtplugDevice",
    "DeviceOutputCommand",
    # Feature-level control
    "DeviceFeature",
    "CommandValue",
]
