# Buttplug Python
# Client Module
# Copyright 2019 Nonpolynomial
# 3-Clause BSD Licensed

"""
client.py
====================================
Buttplug Client Module
"""

from .connector import ButtplugClientConnector, ButtplugClientConnectorObserver
from ..core import (ButtplugMessage, StartScanning, StopScanning, Ok,
                    RequestServerInfo, Error, ServerInfo,
                    ButtplugMessageException, RequestLog, DeviceAdded,
                    DeviceList, DeviceRemoved, ScanningFinished, DeviceInfo,
                    MessageAttributes, ButtplugDeviceException, VibrateCmd,
                    SpeedSubcommand, RequestDeviceList, RotateSubcommand,
                    LinearSubcommand, RotateCmd, LinearCmd)
from ..utils import EventHandler
from typing import Dict, List, Tuple, Union
from asyncio import Future, get_event_loop


class ButtplugClient(ButtplugClientConnectorObserver):
    """Used to connect to Buttplug Servers.

    Attributes:
        name: Name of the client, which the server can use to show with 
              connection status.
        connector: Connector used to communicate with the Buttplug server.
    """
    def __init__(self, name: str):
        self.name: str = name
        self.connector: ButtplugClientConnector = None
        self.msg_tasks: Dict[int, Future] = {}
        self.msg_counter: int = 1
        self.devices: Dict[int, ButtplugClientDevice] = {}
        self.scanning_finished_handler: EventHandler = EventHandler(self)
        self.device_added_handler: EventHandler = EventHandler(self)
        self.device_removed_handler: EventHandler = EventHandler(self)

    async def connect(self, connector):
        self.connector = connector
        self.connector.add_observer(self)
        await self.connector.connect()
        await self._init()

    async def _init(self):
        initmsg = RequestServerInfo("Client Test")
        msg: ServerInfo = await self._send_message_expect_reply(initmsg,
                                                                ServerInfo)
        print("Connected to server: " + msg.server_name)
        dl: DeviceList = await self._send_message_expect_reply(RequestDeviceList(),
                                                               DeviceList)
        self._handle_device_list(dl)

    def _handle_device_list(self, dl: DeviceList):
        for dev in dl.devices:
            self.devices[dev.device_index] = ButtplugClientDevice(self, dev)
            self.device_added_handler(self.devices[dev.device_index])

    async def disconnect(self):
        await self.connector.disconnect()

    async def start_scanning(self):
        await self._send_message(StartScanning())

    async def stop_scanning(self):
        await self._send_message(StopScanning())

    async def request_log(self, log_level: str):
        await self._send_message(RequestLog(log_level))

    async def _send_message(self, msg: ButtplugMessage):
        msg.id = self.msg_counter
        self.msg_counter += 1
        await self.connector.send(msg)

    async def send_device_message(self):
        pass

    async def _parse_message(self, msg: ButtplugMessage):
        if isinstance(msg, DeviceAdded):
            da: DeviceAdded = msg
            self.devices[da.device_index] = ButtplugClientDevice(self, da)
            self.device_added_handler(self.devices[da.device_index])
        elif isinstance(msg, DeviceRemoved):
            dr: DeviceRemoved = msg
            self.devices.remove(dr.device_index)
            self.device_removed_handler(dr.device_index)
        elif isinstance(msg, ScanningFinished):
            self._scanning_finished_handler()

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
        if msg.id in self.msg_tasks.keys():
            self.msg_tasks[msg.id].set_result(msg)
            return
        await self._parse_message(msg)

    def _throw_error_msg_exception(self, msg: Error):
        pass


class ButtplugClientDevice(object):
    def __init__(self, client: ButtplugClient, device_msg: Union[DeviceInfo, DeviceAdded]):
        self._client = client
        if isinstance(device_msg, DeviceInfo):
            device_info: DeviceInfo = device_msg
            self.name = device_info.device_name
            self.index = device_info.device_index
            self.messages: Dict[str, MessageAttributes] = {}
            for (msg_name, attrs) in device_info.device_messages.items():
                self.messages[msg_name] = MessageAttributes(attrs.get("FeatureCount"))
        elif isinstance(device_msg, DeviceAdded):
            device_info: DeviceAdded = device_msg
            self.name = device_info.device_name
            self.index = device_info.device_index
            self.messages: Dict[str, MessageAttributes] = {}
            print(device_info.device_messages)
            for (msg_name, attrs) in device_info.device_messages.items():
                self.messages[msg_name] = MessageAttributes(attrs.get("FeatureCount"))
        else:
            raise ButtplugDeviceException("Cannot create device from message type" + device_msg.__name__)

    async def send_vibrate_cmd(self, speeds: Union[float,
                                                   List[float],
                                                   Dict[int, float]]):
        speeds_obj = []
        if isinstance(speeds, (float, int)):
            speeds_obj = [SpeedSubcommand(0, speeds)]
        elif isinstance(speeds, list):
            speeds_obj = [SpeedSubcommand(x, speed)
                          for x, speed in enumerate(speeds)]
        elif isinstance(speeds, dict):
            speeds_obj = [SpeedSubcommand(x, speed)
                          for x, speed in speeds.items()]

        msg = VibrateCmd(self.index,
                         speeds_obj)
        await self._client._send_message_expect_ok(msg)

    async def send_rotate_cmd(self, rotations: Union[Tuple[float, bool],
                                                     List[Tuple[float, bool]],
                                                     Dict[int, Tuple[float, bool]]]):
        rotations_obj = []
        if isinstance(rotations, tuple):
            rotations_obj = [RotateSubcommand(0, rotations[0], rotations[1])]
        elif isinstance(rotations, list):
            rotations_obj = [RotateSubcommand(x, rot[0], rot[1])
                             for x, rot in enumerate(rotations)]
        elif isinstance(rotations, dict):
            rotations_obj = [RotateSubcommand(x, rot[0], rot[1])
                             for x, rot in rotations.items()]

        msg = RotateCmd(self.index,
                        rotations_obj)
        await self._client._send_message_expect_ok(msg)

    async def send_linear_cmd(self, linear: Union[Tuple[int, float],
                                                  List[Tuple[int, float]],
                                                  Dict[int, Tuple[int, float]]]):
        linear_obj = []
        if isinstance(linear, tuple):
            linear_obj = [LinearSubcommand(0, linear[0], linear[1])]
        elif isinstance(linear, list):
            linear_obj = [LinearSubcommand(x, l[0], l[1])
                          for x, l in enumerate(linear)]
        elif isinstance(linear, dict):
            linear_obj = [LinearSubcommand(x, l[0], l[1])
                          for x, l in linear.items()]

        msg = LinearCmd(self.index,
                        linear_obj)
        await self._client._send_message_expect_ok(msg)
