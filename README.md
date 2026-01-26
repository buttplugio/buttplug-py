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
from buttplug import ButtplugClient, OutputType

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
            await device.vibrate(0.5)  # 50% intensity
            await asyncio.sleep(2)
            await device.stop()

    await client.disconnect()

asyncio.run(main())
```

## Features

- **Simple API**: Easy-to-use methods like `vibrate()`, `rotate()`, `position()`
- **Full Protocol Support**: Implements Buttplug protocol v4
- **Type Hints**: Full typing support for IDE autocomplete and type checking
- **Async/Await**: Modern Python async API
- **Event Callbacks**: Get notified when devices connect/disconnect

## Device Control

```python
# Check device capabilities
if device.has_output(OutputType.VIBRATE):
    await device.vibrate(0.75)  # 0.0 to 1.0

if device.has_output(OutputType.ROTATE):
    await device.rotate(0.5, clockwise=True)

if device.has_output(OutputType.POSITION):
    await device.position(1.0, duration_ms=500)  # Move over 500ms

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
        await device.vibrate(0.25)

client.on_device_added = on_device_added
```

## Examples

See the [examples/](examples/) directory for more detailed examples:

- `01_hello_world.py` - Connect and list devices
- `02_device_control.py` - Vibrate, rotate, and position commands
- `03_reading_sensors.py` - Battery and signal strength
- `04_advanced_features.py` - Low-level feature access

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
