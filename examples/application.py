"""Buttplug Python - Complete Application Example

This is a complete, working example that demonstrates the full workflow
of a Buttplug application. If you're new to Buttplug, start here!

Prerequisites:
1. Install Intiface Central: https://intiface.com/central
2. Start the server in Intiface Central (click "Start Server")
3. Run: python application.py
"""

import asyncio

from buttplug import ButtplugClient, DeviceOutputCommand, InputType, OutputType
from buttplug.errors import ButtplugDeviceError, ButtplugError


def print_device_capabilities(device) -> None:
    """Print the capabilities of a device."""
    print(f"  {device.name}")

    # Check output capabilities (things we can make the device do)
    outputs = []
    if device.has_output(OutputType.VIBRATE):
        outputs.append("Vibrate")
    if device.has_output(OutputType.ROTATE):
        outputs.append("Rotate")
    if device.has_output(OutputType.OSCILLATE):
        outputs.append("Oscillate")
    if device.has_output(OutputType.POSITION) or device.has_output(
        OutputType.POSITION_WITH_DURATION
    ):
        outputs.append("Position")
    if device.has_output(OutputType.CONSTRICT):
        outputs.append("Constrict")

    if outputs:
        print(f"    Outputs: {', '.join(outputs)}")

    # Check input capabilities (sensors we can read)
    inputs = []
    if device.has_input(InputType.BATTERY):
        inputs.append("Battery")
    if device.has_input(InputType.RSSI):
        inputs.append("RSSI")

    if inputs:
        print(f"    Inputs: {', '.join(inputs)}")

    print()


async def main() -> None:
    print("===========================================")
    print("  Buttplug Python Application Example")
    print("===========================================\n")

    # Step 1: Create a client
    # The client name identifies your application to the server.
    client = ButtplugClient("My Buttplug Application")

    # Step 2: Set up event handlers
    # Always do this BEFORE connecting to avoid missing events.
    client.on_device_added = lambda d: print(f"[+] Device connected: {d.name}")
    client.on_device_removed = lambda d: print(f"[-] Device disconnected: {d.name}")
    client.on_disconnect = lambda: print("[!] Server connection lost!")

    # Step 3: Connect to the server
    print("Connecting to Intiface Central...")
    try:
        await client.connect("ws://127.0.0.1:12345")
    except ButtplugError as e:
        print("ERROR: Could not connect to Intiface Central!")
        print("Make sure Intiface Central is running and the server is started.")
        print("Default address: ws://127.0.0.1:12345")
        print(f"Error: {e}")
        return
    print("Connected!\n")

    # Step 4: Scan for devices
    print("Scanning for devices...")
    print("Turn on your Bluetooth/USB devices now.\n")
    await client.start_scanning()

    # Wait for devices (in a real app, you might use a UI or timeout)
    input("Press Enter when your devices are connected...")
    await client.stop_scanning()

    # Step 5: Check what devices we found
    devices = list(client.devices.values())
    if not devices:
        print("No devices found. Make sure your device is:")
        print("  - Turned on")
        print("  - In pairing/discoverable mode")
        print("  - Supported by Buttplug (check https://iostindex.com)")
        await client.disconnect()
        return

    print(f"\nFound {len(devices)} device(s):\n")

    # Step 6: Display device capabilities
    for device in devices:
        print_device_capabilities(device)

    # Step 7: Interactive device control
    print("=== Interactive Control ===")
    print("Commands:")
    print("  v <0-100>  - Vibrate all devices at percentage")
    print("  s          - Stop all devices")
    print("  b          - Read battery levels")
    print("  q          - Quit\n")

    while True:
        try:
            user_input = input("> ").strip().lower()
        except EOFError:
            break

        if not user_input:
            continue

        try:
            if user_input.startswith("v "):
                # Vibrate command
                try:
                    percent = int(user_input[2:])
                    if 0 <= percent <= 100:
                        intensity = percent / 100.0
                        for device in devices:
                            if device.has_output(OutputType.VIBRATE):
                                await device.run_output(
                                    DeviceOutputCommand(OutputType.VIBRATE, intensity)
                                )
                                print(f"  {device.name}: vibrating at {percent}%")
                    else:
                        print("  Usage: v <0-100>")
                except ValueError:
                    print("  Usage: v <0-100>")

            elif user_input == "s":
                # Stop all devices
                await client.stop_all_devices()
                print("  All devices stopped.")

            elif user_input == "b":
                # Read battery levels
                for device in devices:
                    if device.has_input(InputType.BATTERY):
                        try:
                            battery = await device.battery()
                            print(f"  {device.name}: {battery * 100:.0f}% battery")
                        except ButtplugDeviceError as e:
                            print(f"  {device.name}: could not read battery - {e}")
                    else:
                        print(f"  {device.name}: no battery sensor")

            elif user_input == "q":
                break

            else:
                print("  Unknown command. Use v, s, b, or q.")

        except ButtplugDeviceError as e:
            print(f"  Device error: {e}")
        except ButtplugError as e:
            print(f"  Error: {e}")

    # Step 8: Clean up
    print("\nStopping devices and disconnecting...")
    await client.stop_all_devices()
    await client.disconnect()
    print("Goodbye!")


if __name__ == "__main__":
    asyncio.run(main())
