from .device import ButtplugClientDevice
from .connector import ButtplugClientConnector, ButtplugClientConnectorObserver
from ..core import ButtplugMessage, StartScanning, StopScanning, Ok, RequestServerInfo, Error, ServerInfo, ButtplugMessageException
from typing import Dict
from asyncio import Future, get_event_loop
from abc import abstractmethod


class ButtplugClientDeviceObserver(object):
    @abstractmethod
    def device_added(self, device: ButtplugClientDevice):
        pass

    @abstractmethod
    def device_removed(self, device: ButtplugClientDevice):
        pass


class ButtplugClient(ButtplugClientConnectorObserver):
    def __init__(self, name: str, connector: ButtplugClientConnector):
        self.name: str = name
        self.connector: ButtplugClientConnector = connector
        self.msg_tasks: Dict[int, Future] = {}
        self.msg_counter: int = 1
        self.devices: Dict[int, ButtplugClientDevice] = {}

    async def connect(self):
        self.connector.add_observer(self)
        await self.connector.connect()
        await self._init()

    async def _init(self):
        initmsg = RequestServerInfo("Client Test")
        msg: ServerInfo = await self._send_message_expect_reply(initmsg,
                                                                ServerInfo)
        print("Connected to server: " + msg.server_name)

    async def disconnect(self):
        await self.connector.disconnect()

    async def start_scanning(self):
        await self._send_message(StartScanning())

    async def stop_scanning(self):
        await self._send_message(StopScanning())

    async def request_log(self):
        pass

    async def _send_message(self, msg: ButtplugMessage):
        msg.id = self.msg_counter
        self.msg_counter += 1
        await self.connector.send(msg)

    async def send_device_message(self):
        pass

    # What kinda typing should expectedClass be here? Could we make this a
    # generic function?
    async def _send_message_expect_reply(self,
                                         msg: ButtplugMessage,
                                         expectedClass) -> ButtplugMessage:
        f = get_event_loop().create_future()
        await self._send_message(msg)
        self.msg_tasks[msg.id] = f
        retmsg = await f
        if not isinstance(retmsg, expectedClass):
            if isinstance(retmsg, Error):
                # This will always throw
                self._throw_error_msg_exception(retmsg)
            raise ButtplugMessageException("Unexpected message" + retmsg)
        return retmsg

    async def _send_message_expect_ok(self, msg: ButtplugMessage) -> None:
        await self._send_message_expect_reply(msg, Ok)

    async def handle_message(self, msg: ButtplugMessage):
        if msg.id not in self.msg_tasks.keys():
            print("Can't find related key!")
            return
        self.msg_tasks[msg.id].set_result(msg)

    def _throw_error_msg_exception(self, msg: Error):
        pass
