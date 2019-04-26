import unittest
from buttplug.core import (ButtplugMessage, Ok, Error, ButtplugErrorCode,
                           Test, DeviceAdded, MessageAttributes, DeviceRemoved,
                           DeviceInfo, DeviceList, VibrateCmd, SpeedSubcommand,
                           RotateCmd, RotateSubcommand, LinearCmd,
                           LinearSubcommand)


class TestMessages(unittest.TestCase):

    def run_msg_test(self, msg_obj, msg_json):
        msg_obj.id = ButtplugMessage.DEFAULT_ID
        assert msg_obj.as_json() == msg_json
        assert ButtplugMessage.from_json(msg_json) == msg_obj

    def test_message_ok(self):
        ok = Ok()
        json_msg = "{\"Ok\": {\"Id\": 1}}"
        self.run_msg_test(ok, json_msg)

    def test_message_error(self):
        error = Error("Test", ButtplugErrorCode.ERROR_MSG)
        json_msg = "{\"Error\": {\"ErrorMessage\": \"Test\", \"ErrorCode\": 3, \"Id\": 1}}"
        self.run_msg_test(error, json_msg)

    def test_message_test(self):
        test = Test("Test")
        json_msg = "{\"Test\": {\"TestString\": \"Test\", \"Id\": 1}}"
        self.run_msg_test(test, json_msg)

    def test_device_added(self):
        device_added = DeviceAdded("Test Device",
                                   1,
                                   {"VibrateCmd": {"FeatureCount": 1}})
        json_msg = "{\"DeviceAdded\": {\"DeviceName\": \"Test Device\", \"DeviceIndex\": 1, \"DeviceMessages\": {\"VibrateCmd\": {\"FeatureCount\": 1}}, \"Id\": 1}}"
        self.run_msg_test(device_added, json_msg)

    def test_device_removed(self):
        device_removed = DeviceRemoved(1)
        json_msg = "{\"DeviceRemoved\": {\"DeviceIndex\": 1, \"Id\": 1}}"
        self.run_msg_test(device_removed, json_msg)

    def test_device_list(self):
        device_list = DeviceList([DeviceInfo("TestDevice1",
                                             0,
                                             {"SingleMotorVibrateCmd": {},
                                              "VibrateCmd": {"FeatureCount": 2},
                                              "StopDeviceCmd": {},
                                             }),
                                  DeviceInfo("TestDevice2",
                                             1,
                                             {"FleshlightLaunchFW12Cmd": {},
                                              "LinearCmd": {"FeatureCount": 1},
                                              "StopDeviceCmd": {}})])
        json_msg = "{\"DeviceList\": {\"Devices\": [{\"DeviceName\": \"TestDevice1\", \"DeviceIndex\": 0, \"DeviceMessages\": {\"SingleMotorVibrateCmd\": {}, \"VibrateCmd\": {\"FeatureCount\": 2}, \"StopDeviceCmd\": {}}}, {\"DeviceName\": \"TestDevice2\", \"DeviceIndex\": 1, \"DeviceMessages\": {\"FleshlightLaunchFW12Cmd\": {}, \"LinearCmd\": {\"FeatureCount\": 1}, \"StopDeviceCmd\": {}}}], \"Id\": 1}}"
        self.run_msg_test(device_list,  json_msg)

    def test_vibrate_cmd(self):
        vibrate_cmd = VibrateCmd(0, [SpeedSubcommand(0, 0),
                                     SpeedSubcommand(1, 0.5)])
        json_msg = "{\"VibrateCmd\": {\"DeviceIndex\": 0, \"Speeds\": [{\"Index\": 0, \"Speed\": 0}, {\"Index\": 1, \"Speed\": 0.5}], \"Id\": 1}}"
        self.run_msg_test(vibrate_cmd,  json_msg)

    def test_rotate_cmd(self):
        rotate_cmd = RotateCmd(0, [RotateSubcommand(0, 0, False),
                                   RotateSubcommand(1, 0.5, True)])
        json_msg = "{\"RotateCmd\": {\"DeviceIndex\": 0, \"Rotations\": [{\"Index\": 0, \"Speed\": 0, \"Clockwise\": false}, {\"Index\": 1, \"Speed\": 0.5, \"Clockwise\": true}], \"Id\": 1}}"
        self.run_msg_test(rotate_cmd,  json_msg)

    def test_linear_cmd(self):
        linear_cmd = LinearCmd(0, [LinearSubcommand(0, 100, 1.0),
                                   LinearSubcommand(1, 500, 0.5)])
        json_msg = "{\"LinearCmd\": {\"DeviceIndex\": 0, \"Vectors\": [{\"Index\": 0, \"Duration\": 100, \"Position\": 1.0}, {\"Index\": 1, \"Duration\": 500, \"Position\": 0.5}], \"Id\": 1}}"
        self.run_msg_test(linear_cmd,  json_msg)
