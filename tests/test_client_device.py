import unittest
import pytest
import logging
from buttplug.core import (ButtplugMessage, Ok, Error, ButtplugErrorCode,
                           Test, DeviceAdded, MessageAttributes, DeviceRemoved,
                           DeviceInfo, DeviceList, VibrateCmd, SpeedSubcommand,
                           RotateCmd, RotateSubcommand, LinearCmd,
                           LinearSubcommand)
from buttplug.client import ButtplugClientDevice


class DummyClient(object):
    def __init__(self):
        self.last_message: ButtplugMessage = None

    async def _send_message_expect_ok(self, msg: ButtplugMessage):
        logging.debug("Got message")
        self.last_message = msg


@pytest.mark.asyncio
async def test_device_vibrate_single_argument():
    client = DummyClient()
    dev = ButtplugClientDevice(client, DeviceInfo("Test Vibration Device",
                                                  0,
                                                  {"VibrateCmd":
                                                   {"FeatureCount": 1}}))
    await dev.send_vibrate_cmd(1.0)
    assert client.last_message == VibrateCmd(0, [SpeedSubcommand(0, 1.0)])


@pytest.mark.asyncio
async def test_device_vibrate_list():
    client = DummyClient()
    dev = ButtplugClientDevice(client, DeviceInfo("Test Vibration Device",
                                                  0,
                                                  {"VibrateCmd":
                                                   {"FeatureCount": 1}}))
    await dev.send_vibrate_cmd([1.0])
    assert client.last_message == VibrateCmd(0, [SpeedSubcommand(0, 1.0)])


@pytest.mark.asyncio
async def test_device_vibrate_dict():
    client = DummyClient()
    dev = ButtplugClientDevice(client, DeviceInfo("Test Vibration Device",
                                                  0,
                                                  {"VibrateCmd":
                                                   {"FeatureCount": 1}}))
    await dev.send_vibrate_cmd({0: 1.0})
    assert client.last_message == VibrateCmd(0, [SpeedSubcommand(0, 1.0)])


@pytest.mark.asyncio
async def test_device_rotate_single_argument():
    client = DummyClient()
    dev = ButtplugClientDevice(client, DeviceInfo("Test Rotation Device",
                                                  0,
                                                  {"RotateCmd":
                                                   {"FeatureCount": 1}}))
    await dev.send_rotate_cmd((1.0, True))
    assert client.last_message == RotateCmd(0, [RotateSubcommand(0, 1.0, True)])


@pytest.mark.asyncio
async def test_device_rotate_list():
    client = DummyClient()
    dev = ButtplugClientDevice(client, DeviceInfo("Test Rotation Device",
                                                  0,
                                                  {"RotateCmd":
                                                   {"FeatureCount": 1}}))
    await dev.send_rotate_cmd([(1.0, True)])
    assert client.last_message == RotateCmd(0, [RotateSubcommand(0, 1.0, True)])


@pytest.mark.asyncio
async def test_device_rotate_dict():
    client = DummyClient()
    dev = ButtplugClientDevice(client, DeviceInfo("Test Rotation Device",
                                                  0,
                                                  {"RotateCmd":
                                                   {"FeatureCount": 1}}))
    await dev.send_rotate_cmd({0: (1.0, True)})
    assert client.last_message == RotateCmd(0, [RotateSubcommand(0, 1.0, True)])


@pytest.mark.asyncio
async def test_device_linear_single_argument():
    client = DummyClient()
    dev = ButtplugClientDevice(client, DeviceInfo("Test Rotation Device",
                                                  0,
                                                  {"LinearCmd":
                                                   {"FeatureCount": 1}}))
    await dev.send_linear_cmd((1000, 1.0))
    assert client.last_message == LinearCmd(0, [LinearSubcommand(0, 1000, 1.0)])


@pytest.mark.asyncio
async def test_device_linear_list():
    client = DummyClient()
    dev = ButtplugClientDevice(client, DeviceInfo("Test Rotation Device",
                                                  0,
                                                  {"LinearCmd":
                                                   {"FeatureCount": 1}}))
    await dev.send_linear_cmd([(1000, 1.0)])
    assert client.last_message == LinearCmd(0, [LinearSubcommand(0, 1000, 1.0)])


@pytest.mark.asyncio
async def test_device_linear_dict():
    client = DummyClient()
    dev = ButtplugClientDevice(client, DeviceInfo("Test Rotation Device",
                                                  0,
                                                  {"LinearCmd":
                                                   {"FeatureCount": 1}}))
    await dev.send_linear_cmd({0: (1000, 1.0)})
    assert client.last_message == LinearCmd(0, [LinearSubcommand(0, 1000, 1.0)])
