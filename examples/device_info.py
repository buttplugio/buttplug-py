"""Device Info - Inspect device capabilities.

This example shows how to inspect device features and capabilities:
- List all available features
- Check output types (vibrate, rotate, position)
- Check input types (battery, sensors)
- Access individual motors on multi-motor devices

Prerequisites:
1. Install Intiface Central: https://intiface.com/central/
2. Start Intiface Central and click "Start Server"
3. Have a supported device connected
4. Run this script: python device_info.py
"""

import asyncio

from buttplug import ButtplugClient, OutputType


async def main() -> None:
    client = ButtplugClient("Device Info Example")

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

    # Inspect each device's features in detail
    for device in client.devices.values():
        print(f"\n{'=' * 50}")
        print(f"Device: {device.name}")
        print(f"Index: {device.index}")
        print(f"Display Name: {device.display_name or '(none)'}")
        print(f"Timing Gap: {device.message_timing_gap}ms")
        print(f"{'=' * 50}")

        # List all features
        print(f"\nFeatures ({len(device.features)}):")
        for feature in device.features.values():
            print(f"\n  Feature {feature.index}: {feature.description or '(no description)'}")

            # Show outputs
            if feature.outputs:
                print("    Outputs:")
                for output_type in feature.outputs:
                    value_range = feature.get_output_range(output_type)
                    duration_range = feature.get_output_duration_range(output_type)
                    print(f"      - {output_type}: values {value_range}", end="")
                    if duration_range:
                        print(f", duration {duration_range}ms", end="")
                    print()

            # Show inputs
            if feature.inputs:
                print("    Inputs:")
                for input_type, input_def in feature.inputs.items():
                    print(f"      - {input_type}: commands {input_def.command}")

        # Show multi-motor info
        vibrate_features = device.get_features_with_output(OutputType.VIBRATE)
        if len(vibrate_features) > 1:
            print(f"\nThis device has {len(vibrate_features)} independent vibrators!")
            print("Use device.send_output() to control them individually.")

    await client.disconnect()
    print("\nDone!")


if __name__ == "__main__":
    asyncio.run(main())
