"""Sensors - Read battery level and signal strength.

This example shows how to read sensor data from devices:
- Battery level (most Bluetooth devices)
- RSSI (Bluetooth signal strength)

Not all devices have sensors. The example checks what each device
supports before trying to read.

Prerequisites:
1. Install Intiface Central: https://intiface.com/central/
2. Start Intiface Central and click "Start Server"
3. Have a supported device connected
4. Run this script: python sensors.py
"""

import asyncio

from buttplug import ButtplugClient, InputType


async def main() -> None:
    client = ButtplugClient("Sensor Reading Example")

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

    # Read sensors from each device
    for device in client.devices.values():
        print(f"\n{device.name}:")

        # Battery level
        if device.has_input(InputType.BATTERY):
            try:
                battery = await device.battery()
                print(f"  Battery: {battery * 100:.0f}%")
            except Exception as e:
                print(f"  Battery read failed: {e}")
        else:
            print("  No battery sensor")

        # Signal strength (RSSI)
        if device.has_input(InputType.RSSI):
            try:
                rssi = await device.rssi()
                # RSSI is typically -10 (excellent) to -100 (poor) dBm
                if rssi > -50:
                    quality = "Excellent"
                elif rssi > -70:
                    quality = "Good"
                elif rssi > -80:
                    quality = "Fair"
                else:
                    quality = "Poor"
                print(f"  Signal: {rssi} dBm ({quality})")
            except Exception as e:
                print(f"  RSSI read failed: {e}")
        else:
            print("  No signal strength sensor")

    await client.disconnect()
    print("\nDone!")


if __name__ == "__main__":
    asyncio.run(main())
