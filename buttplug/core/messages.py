# TODO Maybe use marshmallow?

from dataclasses import dataclass
import json
import sys
from typing import Dict, List, Any
from .enums import ButtplugErrorCode

class ButtplugMessageEncoder(json.JSONEncoder):
    """Used for serializing ButtplugMessage types into Buttplug protocol JSON line
    format.

    """
    def pascal_case(self, cc_string):
        return ''.join(x.title() for x in cc_string.split('_'))

    def build_obj_dict(self, obj):
        # Build camel case versions of our internal variables
        return dict((self.pascal_case(key), value)
                    for (key, value) in obj.__dict__.items())

    def default(self, obj):
        # Helper classes should drop their names
        if isinstance(obj, (MessageAttributes, DeviceInfo,
                            SpeedSubcommand, LinearSubcommand,
                            RotateSubcommand)):
            return self.build_obj_dict(obj)
        return {type(obj).__name__: self.build_obj_dict(obj)}


# ButtplugMessage isn't a dataclass, because we usually set id later than
# message construction, and don't want to require it in constructors
class ButtplugMessage(object):
    SYSTEM_ID = 0
    DEFAULT_ID = 1

    def __init__(self):
        self.id = ButtplugMessage.DEFAULT_ID

    def as_json(self):
        return ButtplugMessageEncoder().encode(self)

    @staticmethod
    def from_json(json_str: str):
        d = json.loads(json_str)
        return ButtplugMessage.from_dict(d)

    @staticmethod
    def from_dict(msg_dict: dict):
        classname = list(msg_dict.keys())[0]
        cls = getattr(sys.modules[__name__], classname)
        d = list(msg_dict.values())[0]
        msg = cls.from_dict(d)
        msg.id = d["Id"]
        return msg


@dataclass
class ButtplugDeviceMessage(ButtplugMessage):
    device_index: int


class ButtplugOutgoingOnlyMessage(object):
    pass


@dataclass
class Ok(ButtplugOutgoingOnlyMessage, ButtplugMessage):
    @staticmethod
    def from_dict(d: dict) -> "Ok":
        return Ok()


@dataclass
class Error(ButtplugOutgoingOnlyMessage, ButtplugMessage):
    error_message: str
    error_code: int

    @staticmethod
    def from_dict(d: dict) -> "Error":
        return Error(d['ErrorMessage'], d['ErrorCode'])


@dataclass
class Test(ButtplugMessage):
    test_string: str

    @staticmethod
    def from_dict(d: dict) -> "Test":
        return Test(d['TestString'])


@dataclass
class RequestServerInfo(ButtplugMessage):
    client_name: str
    message_version: int = 1

    @staticmethod
    def from_dict(d: dict) -> "RequestServerInfo":
        return RequestServerInfo(d['ClientName'], d['MessageVersion'])


@dataclass
class ServerInfo(ButtplugMessage):
    server_name: str
    major_version: int
    minor_version: int
    build_version: int
    message_version: int = 1
    max_ping_time: int = 0

    @staticmethod
    def from_dict(d: dict) -> "ServerInfo":
        return ServerInfo(d['ServerName'], d['MajorVersion'],
                          d['MinorVersion'], d['BuildVersion'],
                          d['MessageVersion'], d['MaxPingTime'])


@dataclass
class RequestDeviceList(ButtplugMessage):
    pass


class MessageAttributes:
    def __init__(self, count: int = None):
        if count is not None:
            self.feature_count = count

    @staticmethod
    def from_dict(d: dict) -> "MessageAttributes":
        return MessageAttributes(d["FeatureCount"])


@dataclass
class DeviceInfo:
    device_name: str
    device_index: int
    # TODO Make this use MessageAttributes, currently just a dict because serialization was broken.
    device_messages: Dict[str, Dict[str, Any]]

    @staticmethod
    def from_dict(d: dict) -> "DeviceInfo":
        attrs = dict([(k, v) for k, v in d["DeviceMessages"].items()])
        return DeviceInfo(d["DeviceName"], d["DeviceIndex"], attrs)


@dataclass
class DeviceList(ButtplugMessage, ButtplugOutgoingOnlyMessage):
    devices: List[DeviceInfo]

    @staticmethod
    def from_dict(d: dict) -> "DeviceList":
        return DeviceList([DeviceInfo(x["DeviceName"],
                                      x["DeviceIndex"],
                                      x["DeviceMessages"])
                           for x in d["Devices"]])


# TODO Make this just be a DeviceInfo, currently own class because serialization was broken.
@dataclass
class DeviceAdded(ButtplugMessage, ButtplugOutgoingOnlyMessage):
    device_name: str
    device_index: int
    # TODO Make this use MessageAttributes, currently just a dict because serialization was broken.
    device_messages: Dict[str, Dict[str, Any]]

    @staticmethod
    def from_dict(d: dict) -> "DeviceAdded":
        attrs = dict([(k, v) for k, v in d["DeviceMessages"].items()])
        return DeviceAdded(d["DeviceName"], d["DeviceIndex"], attrs)


@dataclass
class DeviceRemoved(ButtplugMessage, ButtplugOutgoingOnlyMessage):
    device_index: int

    @staticmethod
    def from_dict(d: dict) -> "DeviceRemoved":
        return DeviceRemoved(d["DeviceIndex"])


@dataclass
class StartScanning(ButtplugMessage):
    @staticmethod
    def from_dict(d: dict) -> "StartScanning":
        return StartScanning()


@dataclass
class StopScanning(ButtplugMessage):
    @staticmethod
    def from_dict(d: dict) -> "StopScanning":
        return StopScanning()


@dataclass
class ScanningFinished(ButtplugMessage, ButtplugOutgoingOnlyMessage):
    @staticmethod
    def from_dict(d: dict) -> "ScanningFinished":
        return ScanningFinished()


@dataclass
class RequestLog(ButtplugMessage):
    log_level: str

    @staticmethod
    def from_dict(d: dict) -> "RequestLog":
        return RequestLog(d["LogLevel"])


@dataclass
class Log(ButtplugMessage, ButtplugOutgoingOnlyMessage):
    log_level: str
    log_message: str

    @staticmethod
    def from_dict(d: dict) -> "Log":
        return Log(d["LogLevel"], d["LogMessage"])


@dataclass
class Ping(ButtplugMessage):
    @staticmethod
    def from_dict(d: dict) -> "Ping":
        return Ping()


@dataclass
class FleshlightLaunchFW12Cmd(ButtplugDeviceMessage):
    position: int
    speed: int


@dataclass
class LovenseCmd(ButtplugDeviceMessage):
    command: str


@dataclass
class KiirooCmd(ButtplugDeviceMessage):
    command: str


@dataclass
class VorzeA10CycloneCmd(ButtplugMessage):
    speed: int
    clockwise: bool


@dataclass
class SpeedSubcommand:
    index: int
    speed: float


@dataclass
class VibrateCmd(ButtplugDeviceMessage):
    speeds: List[SpeedSubcommand]

    @staticmethod
    def from_dict(d: dict) -> "VibrateCmd":
        speeds = []
        for cmd in d["Speeds"]:
            speeds.append(SpeedSubcommand(cmd["Index"], cmd["Speed"]))
        return VibrateCmd(d["DeviceIndex"], speeds)


@dataclass
class RotateSubcommand:
    index: int
    speed: float
    clockwise: bool


@dataclass
class RotateCmd(ButtplugDeviceMessage):
    rotations: List[RotateSubcommand]

    @staticmethod
    def from_dict(d: dict) -> "RotateCmd":
        rotations = []
        for cmd in d["Rotations"]:
            rotations.append(RotateSubcommand(cmd["Index"], cmd["Speed"],
                                              cmd["Clockwise"]))
        return RotateCmd(d["DeviceIndex"], rotations)


@dataclass
class LinearSubcommand:
    index: int
    duration: int
    position: float


@dataclass
class LinearCmd(ButtplugDeviceMessage):
    vectors: List[LinearSubcommand]

    @staticmethod
    def from_dict(d: dict) -> "LinearCmd":
        vectors = []
        for cmd in d["Vectors"]:
            vectors.append(LinearSubcommand(cmd["Index"], cmd["Duration"],
                                            cmd["Position"]))
        return LinearCmd(d["DeviceIndex"], vectors)


class StopDeviceCmd(ButtplugDeviceMessage):
    pass


class StopAllDevices(ButtplugMessage):
    pass
