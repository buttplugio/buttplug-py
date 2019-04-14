import unittest
from buttplug.core import ButtplugMessage, Ok, Error, ButtplugErrorCode, Test


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
