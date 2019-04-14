import unittest
from buttplug.core import ButtplugMessage, Ok


class TestMessages(unittest.TestCase):
    def test_message_serialization(self):
        ok = Ok(ButtplugMessage.DEFAULT_ID)
        assert ok.as_json() == "{\"Ok\": {\"Id\": 1}}"

    def test_message_deserialization(self):
        assert ButtplugMessage.from_json("{\"Ok\": {\"Id\": 1}}") == Ok(ButtplugMessage.DEFAULT_ID)
