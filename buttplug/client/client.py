# Buttplug Python
# Client Module
# Copyright 2019 Nonpolynomial
# 3-Clause BSD Licensed

from .connector import (ButtplugClientConnector,
                        ButtplugClientConnectorObserver,
                        ButtplugClientConnectorError)
from ..core import (ButtplugMessage, StartScanning, StopScanning, Ok,
                    RequestServerInfo, Error, ServerInfo,
                    ButtplugMessageError, RequestLog, DeviceAdded,
                    DeviceList, DeviceRemoved, ScanningFinished, DeviceInfo,
                    MessageAttributes, VibrateCmd, SpeedSubcommand,
                    RequestDeviceList, RotateSubcommand, LinearSubcommand,
                    RotateCmd, LinearCmd, StopDeviceCmd, ButtplugErrorCode,
                    ButtplugError, Log, ButtplugDeviceError,
                    ButtplugHandshakeError, ButtplugPingError,
                    ButtplugUnknownError)
from ..utils import EventHandler
from typing import Dict, List, Tuple, Union
from asyncio import Future, get_event_loop


class ButtplugClient(ButtplugClientConnectorObserver):
    """Used to connect to Buttplug Servers.

    Attributes:

        name (string):
            name of the client, which the server can use to show
            with connection status.

        devices (Dict[int, ButtplugClientDevice]):
            dict of devices currently connected to the Buttplug Server, indexed
            by their server-provisioned numerical index.

        device_added_handler (buttplug.utils.EventHandler):
            Takes functions of the format f(a: ButtplugClientDevice) -> void.
            Calls handlers whenever a new device is found by the Buttplug
            Server.

        device_removed_handler (buttplug.utils.EventHandler):
            Takes functions of the format f(a: ButtplugClientDevice) -> void.
            Calls handlers whenever a device has disconnected from the Buttplug
            server.

        scanning_finished_handler (buttplug.utils.EventHandler):
            Takes functions of the format f() -> void. Calls handlers whenever
            the server has finished scanning for devices.

        log_handler (buttplug.utils.EventHandler):
            Takes functions of the format f(a: Log) -> void. Calls handlers
            whenever a new log message is received.
    """
    def __init__(self, name: str):
        self.name: str = name
        self.connector: ButtplugClientConnector = None
        self.devices: Dict[int, ButtplugClientDevice] = {}
        self.scanning_finished_handler: EventHandler = EventHandler(self)
        self.device_added_handler: EventHandler = EventHandler(self)
        self.device_removed_handler: EventHandler = EventHandler(self)
        self.log_handler: EventHandler = EventHandler(self)
        self._msg_tasks: Dict[int, Future] = {}
        self._msg_counter: int = 1

    async def connect(self, connector):
        """Connects to a Buttplug Server, using the connector passed to it.

        Asynchronous function that connects to a Buttplug Server.

        Args:
            connector (ButtplugConnector):
                Connector to use to contact the server.

        Returns:
            void:
                Should just return on successful connect.

        Raises:
            buttplug.client.ButtplugClientConnectorError:
                On failed connect. Check message for context.
        """
        self.connector = connector
        self.connector.add_observer(self)
        await self.connector.connect()
        await self._init()

    async def _init(self):
        initmsg = RequestServerInfo(self.name)
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
        """Disconnect from the remote server.
        """
        if not self.connector.connected:
            return
        await self.connector.disconnect()

    async def start_scanning(self):
        """Request that the server starts scanning for devices.
        """
        await self._send_message_expect_ok(StartScanning())

    async def stop_scanning(self):
        """Request that the server stops scanning for devices.
        """
        await self._send_message_expect_ok(StopScanning())

    async def request_log(self, log_level: str):
        """Request that the server sends logs at the requested level or higher to the
        client.

        To stop logs from being sent, call request_log again with the "Off"
        level.

        Args:
            log_level (string):
                Log level to receive. Send "Off" to stop logs from being sent.
        """
        await self._send_message_expect_ok(RequestLog(log_level))

    async def _send_message(self, msg: ButtplugMessage):
        msg.id = self._msg_counter
        self._msg_counter += 1
        await self.connector.send(msg)

    async def _parse_message(self, msg: ButtplugMessage):
        if isinstance(msg, DeviceAdded):
            da: DeviceAdded = msg
            self.devices[da.device_index] = ButtplugClientDevice(self, da)
            self.device_added_handler(self.devices[da.device_index])
        elif isinstance(msg, DeviceRemoved):
            dr: DeviceRemoved = msg
            self.devices.pop(dr.device_index)
            self.device_removed_handler(dr.device_index)
        elif isinstance(msg, ScanningFinished):
            self.scanning_finished_handler()
        elif isinstance(msg, Log):
            self.log_handler(Log)

    # What kinda typing should expectedClass be here? Could we make this a
    # generic function?
    async def _send_message_expect_reply(self,
                                         msg: ButtplugMessage,
                                         expectedClass) -> ButtplugMessage:
        if not self.connector.connected:
            raise ButtplugClientConnectorError("Client not connected to server")
        f = get_event_loop().create_future()
        await self._send_message(msg)
        self._msg_tasks[msg.id] = f
        retmsg = await f
        if not isinstance(retmsg, expectedClass):
            if isinstance(retmsg, Error):
                # This will always throw
                self._throw_error_msg_exception(retmsg)
            raise ButtplugMessageError("Unexpected message" + retmsg)
        return retmsg

    async def _send_message_expect_ok(self, msg: ButtplugMessage) -> None:
        await self._send_message_expect_reply(msg, Ok)

    async def _handle_message(self, msg: ButtplugMessage):
        if msg.id in self._msg_tasks.keys():
            self._msg_tasks[msg.id].set_result(msg)
            return
        await self._parse_message(msg)

    def _throw_error_msg_exception(self, msg: Error):
        if msg.error_code == ButtplugErrorCode.ERROR_UNKNOWN:
            raise ButtplugUnknownError(msg)
        elif msg.error_code == ButtplugErrorCode.ERROR_DEVICE:
            raise ButtplugDeviceError(msg)
        elif msg.error_code == ButtplugErrorCode.ERROR_MSG:
            raise ButtplugMessageError(msg)
        elif msg.error_code == ButtplugErrorCode.ERROR_PING:
            raise ButtplugPingError(msg)
        elif msg.error_code == ButtplugErrorCode.ERROR_INIT:
            raise ButtplugHandshakeError(msg)
        raise ButtplugError(msg)


class ButtplugClientDevice(object):
    """Represents a device that is connected to the Buttplug Server.

    Attributes:

        name (string):
            Name of the device

        allowed_messages (Dict[str, MessageAttributes]):
            Dictionary that matches message names to attributes. For instance,
            if a device can vibrate, it will have a dictionary entry for
            "VibrateCmd", as well as a MessageAttribute for "FeatureCount" that
            says how many vibrators are in the device.
    """
    def __init__(self, client: ButtplugClient, device_msg: Union[DeviceInfo,
                                                                 DeviceAdded]):
        self._client = client
        if isinstance(device_msg, DeviceInfo):
            device_info: DeviceInfo = device_msg
            self.name = device_info.device_name
            self._index = device_info.device_index
            self.allowed_messages: Dict[str, MessageAttributes] = {}
            for (msg_name, attrs) in device_info.device_messages.items():
                self.allowed_messages[msg_name] = MessageAttributes(attrs.get("FeatureCount"))
        elif isinstance(device_msg, DeviceAdded):
            device_info: DeviceAdded = device_msg
            self.name = device_info.device_name
            self._index = device_info.device_index
            self.allowed_messages: Dict[str, MessageAttributes] = {}
            print(device_info.device_messages)
            for (msg_name, attrs) in device_info.device_messages.items():
                self.allowed_messages[msg_name] = MessageAttributes(attrs.get("FeatureCount"))
        else:
            raise ButtplugDeviceError(
                "Cannot create device from message {}".format(device_msg.__name__))

    async def send_vibrate_cmd(self, speeds: Union[float,
                                                   List[float],
                                                   Dict[int, float]]):
        """Tell the server to make a device vibrate at a certain speed. 0.0 for speed
        or using send_stop_device_cmd will stop the hardware from vibrating.

        Args:
            speeds (Union[float, List[float], Dict[int, float]]):
                Speed, or speeds, to set the vibrators to, assuming the
                hardware supports vibration. Range is from 0.0 <= x <= 1.0.

                Types accepted:

                - a single float, which all vibration motors will be set to

                - a list of floats, mapping to the motor indexes in the
                  hardware, i.e. [0.5, 1.0] will set motor 0 to 0.5, motor 1 to
                  1.

                - a dict of int to float, which maps motor index to speed. i.e.
                  { 0: 0.5, 1: 1.0 } will set motor 0 to 0.5, motor 1 to 1.

        """
        if "VibrateCmd" not in self.allowed_messages.keys():
            raise ButtplugDeviceError("VibrateCmd not supported by device")
        speeds_obj = []
        if isinstance(speeds, (float, int)):
            speeds_obj = [SpeedSubcommand(0, speeds)]
        elif isinstance(speeds, list):
            speeds_obj = [SpeedSubcommand(x, speed)
                          for x, speed in enumerate(speeds)]
        elif isinstance(speeds, dict):
            speeds_obj = [SpeedSubcommand(x, speed)
                          for x, speed in speeds.items()]

        msg = VibrateCmd(self._index,
                         speeds_obj)
        await self._client._send_message_expect_ok(msg)

    async def send_rotate_cmd(self, rotations: Union[Tuple[float, bool],
                                                     List[Tuple[float, bool]],
                                                     Dict[int, Tuple[float, bool]]]):
        """Tell the server to make a device rotate at a certain speed. 0.0 for speed or
        using send_stop_device_cmd will stop the hardware from rotating.

        Args:
            rotations (Union[Tuple[float, bool], List[Tuple[float, bool]], Dict[int, Tuple[float, bool]]]):
                Rotation speed(s) and directions, to set the hardware to,
                assuming the hardware supports rotation.. Range is from 0.0 <=
                x <= 1.0 for speeds. For bool, True is clockwise direction,
                False is counterclockwise.

                Types accepted:

                - a Tuple of [float, bool], which all rotators will be set to

                - a list of Tuple[float, bool], mapping to the rotator indexes
                  in the hardware, i.e. [(0.5, False), (1.0, True)] will set
                  motor 0 to 50% speed going counterclockwise, motor 1 to 100%
                  speed going clockwise.

                - a dict of int to Tuple[float, bool], mapping rotator indexes
                  in the hardware, i.e. { 0: (0.5, False), 1: (1.0, True)} will
                  set motor 0 to 50% speed going counterclockwise, motor 1 to
                  100% speed going clockwise.

        """
        if "RotateCmd" not in self.allowed_messages.keys():
            raise ButtplugDeviceError("RotateCmd not supported by device")
        rotations_obj = []
        if isinstance(rotations, tuple):
            rotations_obj = [RotateSubcommand(0, rotations[0], rotations[1])]
        elif isinstance(rotations, list):
            rotations_obj = [RotateSubcommand(x, rot[0], rot[1])
                             for x, rot in enumerate(rotations)]
        elif isinstance(rotations, dict):
            rotations_obj = [RotateSubcommand(x, rot[0], rot[1])
                             for x, rot in rotations.items()]

        msg = RotateCmd(self._index,
                        rotations_obj)
        await self._client._send_message_expect_ok(msg)

    async def send_linear_cmd(self, linear: Union[Tuple[int, float],
                                                  List[Tuple[int, float]],
                                                  Dict[int, Tuple[int, float]]]):
        """Tell the server to make a device stroke (move linearly) at a certain speed.
        Use StopDeviceCmd to stop the device from moving.

        Args:
            linear (Union[Tuple[int, float], List[Tuple[int, float]], Dict[int, Tuple[int, float]]]):

                Linear position(s) and movement duration(s), to set the
                hardware to, assuming the hardware supports linear movement.
                Position range is from 0.0 <= x <= 1.0. Duration is in
                milliseconds, 1000ms = 1s.

                Types accepted:

                - a Tuple of [int, float], which all linear hardware is set to.

                - a list of Tuple[int, float], mapping to the linear indexes in
                  the hardware, i.e. [(1000, 0.9), (500, 0.1)] will set linear
                  movement 0 to 90% position and move to it over 1s, while
                  linear movement 1 will move to 10% position over 0.5s

                - a dict of Tuple[int, float], mapping to the linear indexes in
                  the hardware, i.e. {0: (1000, 0.9), 1: (500, 0.1)} will set
                  linear movement 0 to 90% position and move to it over 1s,
                  while linear movement 1 will move to 10% position over 0.5s

        """
        if "LinearCmd" not in self.allowed_messages.keys():
            raise ButtplugDeviceError("LinearCmd not supported by device")
        linear_obj = []
        if isinstance(linear, tuple):
            linear_obj = [LinearSubcommand(0, linear[0], linear[1])]
        elif isinstance(linear, list):
            linear_obj = [LinearSubcommand(x, l[0], l[1])
                          for x, l in enumerate(linear)]
        elif isinstance(linear, dict):
            linear_obj = [LinearSubcommand(x, l[0], l[1])
                          for x, l in linear.items()]

        msg = LinearCmd(self._index,
                        linear_obj)
        await self._client._send_message_expect_ok(msg)

    async def send_stop_device_cmd(self):
        """Tell the server to stop whatever device movements may be happening.
        """
        await self._client._send_message_expect_ok(StopDeviceCmd(self._index))
