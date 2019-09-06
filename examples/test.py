from buttplug.client import (ButtplugClientWebsocketConnector, ButtplugClient,
                             ButtplugClientDevice)
import asyncio
# import signal
# import sys


async def cancel_me():
    print('cancel_me(): before sleep')

    try:
        await asyncio.sleep(3600)
    except asyncio.CancelledError:
        pass


# def signal_handler(sig, frame):
#     print('You pressed Ctrl+C!')
#     sys.exit(0)

async def run_vibration(dev: ButtplugClientDevice):
    await dev.send_vibrate_cmd(0.5)


async def stop_vibration(dev: ButtplugClientDevice):
    await dev.send_vibrate_cmd(0)


async def run_linear(dev: ButtplugClientDevice):
    await dev.send_linear_cmd((1000, 0.9))


async def stop_linear(dev: ButtplugClientDevice):
    await dev.send_linear_cmd((1000, 0))


async def device_added_task(dev: ButtplugClientDevice):
    print("Device Added!")
    print(dev.name)
    if "VibrateCmd" in dev.messages.keys():
        await run_vibration(dev)
        await asyncio.sleep(1)
        await stop_vibration(dev)
    if "LinearCmd" in dev.messages.keys():
        await run_linear(dev)
        await asyncio.sleep(1)
        await stop_linear(dev)


def device_added(emitter, dev: ButtplugClientDevice):
    asyncio.create_task(device_added_task(dev))


async def main():
    # signal.signal(signal.SIGINT, signal_handler)
    client = ButtplugClient("Test Client")
    connector = ButtplugClientWebsocketConnector("ws://127.0.0.1:12345")
    client.device_added_handler += device_added
    await client.connect(connector)
    await client.start_scanning()
    task = asyncio.create_task(cancel_me())
    try:
        await task
    except asyncio.CancelledError:
        pass
    await client.stop_scanning()
    await client.disconnect()

asyncio.run(main(), debug=True)
