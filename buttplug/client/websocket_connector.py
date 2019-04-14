from connector import ButtplugClientConnector
from typings import Any
import websockets


class ButtplugClientWebsocketConnector(ButtplugClientConnector):
    addr: str
    ws: Any

    def __init__(self, addr: str):
        super()
        self.addr = addr

    def connect(self):
        self.ws = websockets.connect(self.addr)
