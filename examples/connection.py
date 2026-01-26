"""Connection - Connect to a Buttplug server.

This is the simplest possible Buttplug example. It connects to a
Buttplug server (like Intiface Central) and shows connection status.

Prerequisites:
1. Install Intiface Central: https://intiface.com/central/
2. Start Intiface Central and click "Start Server"
3. Run this script: python connection.py
"""

import asyncio

from buttplug import ButtplugClient, ButtplugError


async def main() -> None:
    # Create a client with your application's name
    client = ButtplugClient("Connection Example")

    try:
        # Connect to the server (Intiface Central default address)
        print("Connecting to server...")
        await client.connect("ws://127.0.0.1:12345")
        print(f"Connected to: {client.server_name}")

        # Connection is established - you can now scan for devices
        print("Connection successful!")

    except ButtplugError as e:
        # Handle connection errors
        print(f"Failed to connect: {e}")
        return

    finally:
        # Always disconnect when done
        if client.connected:
            await client.disconnect()
            print("Disconnected.")


if __name__ == "__main__":
    asyncio.run(main())
