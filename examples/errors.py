"""Error Handling - Handle errors gracefully.

This example shows how to handle various error conditions:
- Connection failures
- Device communication errors
- Server disconnections

Prerequisites:
1. Install Intiface Central: https://intiface.com/central/
2. Run this script (server doesn't need to be running to see error handling)
"""

import asyncio

from buttplug import (
    ButtplugClient,
    ButtplugConnectionError,
    ButtplugDeviceError,
    ButtplugError,
    ButtplugHandshakeError,
    ButtplugPingError,
)


async def main() -> None:
    client = ButtplugClient("Error Handling Example")

    # Handle disconnection events
    def on_disconnect() -> None:
        print("Server disconnected unexpectedly!")

    client.on_disconnect = on_disconnect

    # Try to connect with error handling
    try:
        print("Attempting to connect to server...")
        await client.connect("ws://127.0.0.1:12345")
        print(f"Connected to: {client.server_name}")

    except ButtplugConnectionError as e:
        # Server not running or network issue
        print(f"Connection failed: {e}")
        print("Is Intiface Central running?")
        return

    except ButtplugHandshakeError as e:
        # Server rejected the connection (version mismatch, etc.)
        print(f"Handshake failed: {e}")
        return

    except ButtplugError as e:
        # Catch-all for other Buttplug errors
        print(f"Unexpected error: {e}")
        return

    # Scan and control devices with error handling
    try:
        print("\nScanning for devices...")
        await client.start_scanning()
        await asyncio.sleep(3)
        await client.stop_scanning()

        for device in client.devices.values():
            print(f"\nControlling: {device.name}")
            try:
                await device.vibrate(0.5)
                await asyncio.sleep(1)
                await device.stop()
                print("  Control successful!")

            except ButtplugDeviceError as e:
                # Device-specific error (disconnected, doesn't support command)
                print(f"  Device error: {e}")

    except ButtplugPingError:
        # Server stopped responding
        print("Server ping timeout - connection lost")

    except ButtplugError as e:
        print(f"Error during operation: {e}")

    finally:
        if client.connected:
            await client.disconnect()
            print("\nDisconnected cleanly.")


if __name__ == "__main__":
    asyncio.run(main())
