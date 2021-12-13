# buttplug-py example code
#
# Buttplug Clients are fairly simple things, in charge of the following
# tasks:
#
# - Connect to a Buttplug Server and Identify Itself
# - Enumerate Devices
# - Control Found Devices
#
# That's about it, really.
#
# This is a program that connects to a server, scans for devices, and runs
# commands on them when they are found. It'll be copiously commented so you
# have some idea of what's going on and can maybe make something yourself.
#
# NOTE: We'll be talking about this in terms of execution flow, so you'll want
# to start at the bottom and work your way up.

# These are really the only things you actually need out of the library. The
# Client and ClientDevice classes wrap all of the functionality you'll need to
# talk to servers and access toys.
from buttplug.client import (ButtplugClientWebsocketConnector, ButtplugClient,
                             ButtplugClientDevice, ButtplugClientConnectorError)
from buttplug.core import ButtplugLogLevel
import asyncio
import logging
import sys

async def cancel_me():
    logging.debug('cancel_me(): before sleep')

    try:
        await asyncio.sleep(3600)
    except asyncio.CancelledError:
        pass


async def device_added_task(dev: ButtplugClientDevice):
    # Ok, so we got a new device in! Neat!
    #
    # First off, we'll print the name of the devices.

    logging.info("Device Added: {}".format(dev.name))

    # Once we've done that, we can send some commands to the device, depending
    # on what it can do. As of the current version I'm writing this for
    # (v0.0.3), all the client can send to devices are generic messages.
    # Specifically:
    #
    # - VibrateCmd
    # - RotateCmd
    # - LinearCmd
    #
    # However, this is good enough to still do a lot of stuff.
    #
    # These capabilities are held in the "messages" member of the
    # ButtplugClientDevice.

    if "VibrateCmd" in dev.allowed_messages.keys():
        # If we see that "VibrateCmd" is an allowed message, it means the
        # device can vibrate. We can call send_vibrate_cmd on the device and
        # it'll tell the server to make the device start vibrating.
        await dev.send_vibrate_cmd(0.5)
        # We let it vibrate at 50% speed for 1 second, then we stop it.
        await asyncio.sleep(1)
        # We can use send_stop_device_cmd to stop the device from vibrating, as
        # well as anything else it's doing. If the device was vibrating AND
        # rotating, we could use send_vibrate_cmd(0) to just stop the
        # vibration.
        await dev.send_stop_device_cmd()
    if "LinearCmd" in dev.allowed_messages.keys():
        # If we see that "LinearCmd" is an allowed message, it means the device
        # can move back and forth. We can call send_linear_cmd on the device
        # and it'll tell the server to make the device move to 90% of the
        # maximum position over 1 second (1000ms).
        await dev.send_linear_cmd((1000, 0.9))
        # We wait 1 second for the move, then we move it back to the 0%
        # position.
        await asyncio.sleep(1)
        await dev.send_linear_cmd((1000, 0))


def device_added(emitter, dev: ButtplugClientDevice):
    asyncio.create_task(device_added_task(dev))

def device_removed(emitter, dev: ButtplugClientDevice):
    logging.info("Device removed: ", dev)

async def main():
    # And now we're in the main function.
    #
    # First, we'll need to set up a client object. This is our conduit to the
    # server.
    #
    # We create a Client object, passing it the name we want for the client.
    # Names are shown in things like the Intiface Desktop Server GUI.

    client = ButtplugClient("Test Client")

    # Now we have a client called "Test Client", but it's not connected to
    # anything yet. We can fix that by creating a connector. Connectors
    # allow clients to talk to servers through different methods, including:
    #
    # - Websockets
    # - IPC (Not currently available in Python)
    # - WebRTC (Not currently available in Python)
    # - TCP/UDP (Not currently available in Python)
    #
    # For now, all we've implemented in python is a Websocket connector, so
    # we'll use that.

    connector = ButtplugClientWebsocketConnector("ws://127.0.0.1:12345")

    # This connector will connect to Intiface Desktop on the local machine,
    # using the default port for insecure websockets.
    #
    # There's one more step before we connect to a client, and that's
    # setting up an event handler.

    client.device_added_handler += device_added
    client.device_removed_handler += device_removed

    # Whenever we connect to a client, we'll instantly get a list of devices
    # already connected (yes, this sometimes happens, mostly due to windows
    # weirdness). We'll want to make sure we know about those.
    #
    # Finally, we connect.

    try:
        await client.connect(connector)
    except ButtplugClientConnectorError as e:
        logging.error("Could not connect to server, exiting: {}".format(e.message))
        return

    # If this succeeds, we'll be connected. If not, we'll probably have some
    # sort of exception thrown of type ButtplugClientConnectorException
    #
    # Let's receive log messages, since they're a handy way to find out what
    # the server is doing. We can choose the level from the ButtplugLogLevel
    # object.

    # await client.request_log(ButtplugLogLevel.info)

    # Now we move on to looking for devices.

    await client.start_scanning()

    # This will tell the server to start scanning for devices, and returns
    # while it's scanning. If we get any new devices, the device_added_task
    # function that we assigned as an event handler earlier will be called.
    #
    # Since everything interesting happens after devices have connected, now
    # all we have to do here is wait. So we do, asynchronously, so other things
    # can continue running. Now that you've made it this far, go look at what
    # the device_added_task does.

    task = asyncio.create_task(cancel_me())
    try:
        await task
    except asyncio.CancelledError:
        pass

    # Ok so someone hit Ctrl-C or something and we've broken out of our task
    # wait. Let's tell the server to stop scanning.
    await client.stop_scanning()

    # Now that we've done that, we just disconnect and we're done!
    await client.disconnect()
    logging.info("Disconnected, quitting")

# Here we are. The beginning. We'll spin up an asyncio event loop that runs the
# main function. Remember that if you don't want to make your whole program
# async (because, for instance, it's already written in a non-async way), you
# can always create a thread for the asyncio loop to run in, and do some sort
# of communication in/out of that thread to the rest of your program.
#
# But first, set up logging
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
asyncio.run(main(), debug=True)
