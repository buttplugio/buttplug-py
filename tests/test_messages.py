import unittest
from buttplug.core import messages

class TestMessages(unittest.TestCase):
    def test_message_serialization(self):
        ok = messages.Ok()
        assert ok.as_json() == "{\"Ok\": {\"Id\": 1}}"
