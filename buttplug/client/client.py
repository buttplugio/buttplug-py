from core.messages import *

class ButtplugClient:
    def __init__(self, name, connector):
        self.name = name
        self.connector = connector

    def connect(self):
        self.connector.connect();

    def disconnect(self):
        pass

    def start_scanning(self):
        pass

    def stop_scanning(self):
        pass

    def request_log(self):
        pass

    def send_message(self):
        pass

    def send_device_message(self):
        pass

    def send_message_expect_ok(self):
        pass
