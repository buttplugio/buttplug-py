# buttplug-py

[![PyPi version](https://img.shields.io/pypi/v/buttplug)](http://pypi.org/project/buttplug)
[![Python version](https://img.shields.io/pypi/pyversions/buttplug)](http://pypi.org/project/buttplug)

[![Patreon donate button](https://img.shields.io/badge/patreon-donate-yellow.svg)](https://www.patreon.com/qdot)
[![Discord](https://img.shields.io/discord/353303527587708932.svg?logo=discord)](https://discord.buttplug.io)
[![Twitter](https://img.shields.io/twitter/follow/buttplugio.svg?style=social&logo=twitter)](https://twitter.com/buttplugio)

Python client library for the [Buttplug](https://buttplug.io) Intimate Hardware Control Protocol (v4).

## Installation

```bash
pip install buttplug
```

Or with [uv](https://github.com/astral-sh/uv):

```bash
uv add buttplug
```

## Quick Start

1. **Install and start [Intiface Central](https://intiface.com/central/)** - This is the server that connects to your devices.

2. **Connect and control devices:**

```python
import asyncio
from buttplug import ButtplugClient, DeviceOutputCommand, OutputType

async def main():
    # Create a client
    client = ButtplugClient("My App")

    # Connect to Intiface Central (default address)
    await client.connect("ws://127.0.0.1:12345")

    # Scan for devices
    await client.start_scanning()
    await asyncio.sleep(5)  # Wait for devices to be found
    await client.stop_scanning()

    # Control devices
    for device in client.devices.values():
        print(f"Found: {device.name}")

        if device.has_output(OutputType.VIBRATE):
            await device.run_output(DeviceOutputCommand(OutputType.VIBRATE, 0.5))
            await asyncio.sleep(2)
            await device.stop()

    await client.disconnect()

asyncio.run(main())
```

## Features

- **Simple API**: Unified `run_output()` method for all output types
- **Full Protocol Support**: Implements Buttplug protocol v4
- **Type Hints**: Full typing support for IDE autocomplete and type checking
- **Async/Await**: Modern Python async API
- **Event Callbacks**: Get notified when devices connect/disconnect

## Device Control

```python
from buttplug import DeviceOutputCommand, OutputType

# Check device capabilities and send commands
if device.has_output(OutputType.VIBRATE):
    await device.run_output(DeviceOutputCommand(OutputType.VIBRATE, 0.75))

if device.has_output(OutputType.ROTATE):
    await device.run_output(DeviceOutputCommand(OutputType.ROTATE, 0.5))

if device.has_output(OutputType.POSITION_WITH_DURATION):
    await device.run_output(
        DeviceOutputCommand(OutputType.POSITION_WITH_DURATION, 1.0, duration=500)
    )

# Read sensors
if device.has_input(InputType.BATTERY):
    battery = await device.battery()
    print(f"Battery: {battery * 100:.0f}%")

# Stop device
await device.stop()
```

## Event Handling

```python
# Set up callbacks before connecting
client.on_device_added = lambda d: print(f"Connected: {d.name}")
client.on_device_removed = lambda d: print(f"Disconnected: {d.name}")
client.on_scanning_finished = lambda: print("Scan complete")
client.on_server_disconnect = lambda: print("Server disconnected!")

# Async callbacks are also supported
async def on_device_added(device):
    if device.has_output(OutputType.VIBRATE):
        await device.run_output(DeviceOutputCommand(OutputType.VIBRATE, 0.25))

client.on_device_added = on_device_added
```

## Examples

See the [examples/](examples/) directory for more detailed examples:

- `application.py` - Complete application workflow
- `connection.py` - Connecting to a server
- `device_control.py` - Vibrate, rotate, and position commands
- `device_enumeration.py` - Discovering devices
- `device_info.py` - Inspecting device features
- `sensors.py` - Battery and signal strength
- `errors.py` - Error handling

To run examples from within the repo:

```bash
uv sync
uv run python examples/application.py
```

## Requirements

- Python 3.10+
- [Intiface Central](https://intiface.com/central/) or another Buttplug server

## Documentation

- [Buttplug Developer Guide](https://docs.buttplug.io)
- [Protocol Specification](https://docs.buttplug.io/docs/spec)

## Support

- [Discord](https://discord.buttplug.io) - Community chat and support
- [GitHub Issues](https://github.com/buttplugio/buttplug-py/issues) - Bug reports and feature requests
- [Patreon](https://patreon.com/qdot) / [GitHub Sponsors](https://github.com/sponsors/qdot) - Support development

## License

BSD 3-Clause. See [LICENSE](LICENSE) for details.
