"""Device Control - Vibrate, rotate, and position commands.

This example shows how to control different types of devices:
- Vibrators: Set vibration intensity
- Rotators: Set rotation speed and direction
- Strokers: Move to position over time

The example checks what each device supports before sending commands,
so it will work with any device type.

Prerequisites:
1. Install Intiface Central: https://intiface.com/central/
2. Start Intiface Central and click "Start Server"
3. Have a supported device connected
4. Run this script: python device_control.py
"""

import asyncio

from buttplug import ButtplugClient, OutputType


async def main() -> None:
    client = ButtplugClient("Device Control Example")

    # Set up event handlers to see devices as they connect
    client.on_device_added = lambda d: print(f"Device connected: {d.name}")
    client.on_device_removed = lambda d: print(f"Device disconnected: {d.name}")

    print("Connecting to server...")
    await client.connect("ws://127.0.0.1:12345")

    print("Scanning for devices (5 seconds)...")
    await client.start_scanning()
    await asyncio.sleep(5)
    await client.stop_scanning()

    if not client.devices:
        print("No devices found!")
        await client.disconnect()
        return

    # Control each device based on its capabilities
    for device in client.devices.values():
        print(f"\nControlling: {device.name}")

        # Vibration
        if device.has_output(OutputType.VIBRATE):
            print("  Starting vibration at 25%...")
            await device.vibrate(0.25)
            await asyncio.sleep(1)

            print("  Increasing to 50%...")
            await device.vibrate(0.5)
            await asyncio.sleep(1)

            print("  Full power (100%)...")
            await device.vibrate(1.0)
            await asyncio.sleep(1)

        # Rotation
        if device.has_output(OutputType.ROTATE) or device.has_output(
            OutputType.ROTATE_WITH_DIRECTION
        ):
            print("  Rotating clockwise at 50%...")
            await device.rotate(0.5, clockwise=True)
            await asyncio.sleep(2)

            print("  Rotating counter-clockwise...")
            await device.rotate(0.5, clockwise=False)
            await asyncio.sleep(2)

        # Position (strokers/linear devices)
        if device.has_output(OutputType.POSITION) or device.has_output(
            OutputType.POSITION_WITH_DURATION
        ):
            print("  Moving to top position...")
            await device.position(1.0, duration_ms=500)
            await asyncio.sleep(1)

            print("  Moving to bottom position...")
            await device.position(0.0, duration_ms=500)
            await asyncio.sleep(1)

            print("  Moving to middle...")
            await device.position(0.5, duration_ms=250)
            await asyncio.sleep(1)

        # Stop the device
        print("  Stopping device...")
        await device.stop()

    print("\nAll done!")
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
