from connector import ButtplugClientConnector
from ..core.messages import ButtplugMessage, StartScanning, StopScanning, Ok, Error


class ButtplugClient(object):
    def __init__(self, name: str, connector: ButtplugClientConnector):
        self.name = name
        self.connector = connector

    async def connect(self):
        await self.connector.connect()

    async def disconnect(self):
        await self.connector.disconnect()

    async def start_scanning(self):
        await self._send_message(StartScanning(1))

    async def stop_scanning(self):
        await self._send_message(StopScanning(1))

    async def request_log(self):
        pass

    async def _send_message(self, msg: ButtplugMessage):
        await self.connector.send(msg)

    async def send_device_message(self):
        pass

    async def send_message_expect_ok(self):
        pass
