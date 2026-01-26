"""Device Enumeration - Scan for and list devices.

This example shows how to scan for devices and handle device
connection/disconnection events.

Prerequisites:
1. Install Intiface Central: https://intiface.com/central/
2. Start Intiface Central and click "Start Server"
3. Have a supported device nearby and powered on
4. Run this script: python device_enumeration.py
"""

import asyncio

from buttplug import ButtplugClient, ButtplugDevice


def on_device_added(device: ButtplugDevice) -> None:
    """Called when a device connects."""
    print(f"Device connected: {device.name} (index {device.index})")


def on_device_removed(device: ButtplugDevice) -> None:
    """Called when a device disconnects."""
    print(f"Device disconnected: {device.name}")


async def main() -> None:
    client = ButtplugClient("Device Enumeration Example")

    # Set up event handlers before connecting
    client.on_device_added = on_device_added
    client.on_device_removed = on_device_removed

    print("Connecting to server...")
    await client.connect("ws://127.0.0.1:12345")
    print(f"Connected to: {client.server_name}")

    # Start scanning for devices
    print("\nScanning for devices (5 seconds)...")
    await client.start_scanning()
    await asyncio.sleep(5)
    await client.stop_scanning()

    # List all discovered devices
    if client.devices:
        print(f"\nFound {len(client.devices)} device(s):")
        for device in client.devices.values():
            print(f"  - {device.name}")
            if device.display_name:
                print(f"    Display name: {device.display_name}")
    else:
        print("\nNo devices found.")
        print("Make sure your device is on and in pairing mode.")

    await client.disconnect()
    print("\nDone!")


if __name__ == "__main__":
    asyncio.run(main())
