# TODO Maybe use marshmallow?

from dataclasses import dataclass
import json
import sys


class ButtplugMessageEncoder(json.JSONEncoder):
    def pascal_case(self, cc_string):
        return ''.join(x.title() for x in cc_string.split('_'))

    def build_obj_dict(self, obj):
        # Build camel case versions of our internal variables
        return dict((self.pascal_case(key), value)
                    for (key, value) in obj.__dict__.items())

    def default(self, obj):
        return {type(obj).__name__: self.build_obj_dict(obj)}


@dataclass
class ButtplugMessage:
    SYSTEM_ID = 0
    DEFAULT_ID = 1

    id: int

    def as_json(self):
        return ButtplugMessageEncoder().encode(self)

    @staticmethod
    def from_json(json_str: str):
        obj = json.loads(json_str)
        classname = list(obj.keys())[0]
        cls = getattr(sys.modules[__name__], classname)
        return cls.from_json(list(obj.values())[0])


@dataclass
class ButtplugDeviceMessage(ButtplugMessage):
    device_id: int


class ButtplugOutgoingOnlyMessage(object):
    pass


class ButtplugDeviceInfoMessage(object):
    pass


@dataclass
class Ok(ButtplugOutgoingOnlyMessage, ButtplugMessage):
    @staticmethod
    def from_json(obj: object):
        return Ok(obj['Id'])


@dataclass
class Error(ButtplugOutgoingOnlyMessage, ButtplugMessage):
    error_message: str
    error_code: int

    @staticmethod
    def from_json(obj: object):
        return Error(obj['Id'], obj['ErrorMessage'], obj['ErrorCode'])


@dataclass
class Test(ButtplugMessage):
    test_string: str

    @staticmethod
    def from_json(obj: object):
        return Test(obj['Id'], obj['TestString'])


@dataclass
class RequestServerInfo(ButtplugMessage):
    client_name: str
    message_version: int

    @staticmethod
    def from_json(obj: object):
        return RequestServerInfo(obj['Id'], obj['ClientName'], obj['MessageVersion'])


@dataclass
class ServerInfo(ButtplugMessage):
    server_name: str
    major_version: int
    minor_version: int
    build_version: int
    message_version: int = 1
    max_ping_time: int = 0

    @staticmethod
    def from_json(obj: object):
        return ServerInfo(obj['Id'], obj['ServerName'], obj['MajorVersion'],
                          obj['MinorVersion'], obj['BuildVersion'],
                          obj['MessageVersion'], obj['MaxPingTime'])


class DeviceList(ButtplugMessage, ButtplugOutgoingOnlyMessage):
    pass


class DeviceAdded(ButtplugDeviceInfoMessage, ButtplugOutgoingOnlyMessage):
    pass


class DeviceRemoved(ButtplugDeviceInfoMessage, ButtplugOutgoingOnlyMessage):
    pass


@dataclass
class RequestDeviceList(ButtplugMessage):
    pass


@dataclass
class StartScanning(ButtplugMessage):
    pass


@dataclass
class StopScanning(ButtplugMessage):
    pass


@dataclass
class ScanningFinished(ButtplugMessage, ButtplugOutgoingOnlyMessage):
    pass


class RequestLog(ButtplugMessage):
    pass


class Log(ButtplugMessage, ButtplugOutgoingOnlyMessage):
    pass


@dataclass
class Ping(ButtplugMessage):
    pass


class FleshlightLaunchFW12Cmd(ButtplugMessage):
    pass


class LovenseCmd(ButtplugMessage):
    pass


class KiirooCmd(ButtplugMessage):
    pass


class VorzeA10CycloneCmd(ButtplugMessage):
    pass


class SingleMotorVibrateCmd(ButtplugMessage):
    pass


class VibrateCmd(ButtplugMessage):
    pass


class RotateCmd(ButtplugMessage):
    pass


class LinearCmd(ButtplugMessage):
    pass


class StopDeviceCmd(ButtplugMessage):
    pass


class StopAllDevices(ButtplugMessage):
    pass
