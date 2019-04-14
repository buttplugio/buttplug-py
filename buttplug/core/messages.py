from json import JSONEncoder

class ButtplugMessageEncoder(JSONEncoder):
    def pascal_case(self, cc_string):
        return ''.join(x.title() for x in cc_string.split('_'))

    def build_obj_dict(self, obj):
        # Build camel case versions of our internal variables
        return dict((self.pascal_case(key), value) for (key, value) in obj.__dict__.items())

    def default(self, obj):
        return { type(obj).__name__ : self.build_obj_dict(obj) }

class ButtplugMessage(object):
    SYSTEM_ID = 0
    DEFAULT_ID = 1

    def __init__(self, id = DEFAULT_ID):
        self.id = id

    def as_json(self):
        return ButtplugMessageEncoder().encode(self)

class ButtplugDeviceMessage(ButtplugMessage):
    def __init__(self, id, device_id):
        super(self, id)
        self.device_id = device_id

class ButtplugOutgoingOnlyMessage(object):
    pass

class ButtplugDeviceInfoMessage(object):
    pass

class Ok(ButtplugOutgoingOnlyMessage, ButtplugMessage):
    def __init__(self, id = ButtplugMessage.DEFAULT_ID):
        super(Ok, self).__init__(id)

class Error(ButtplugOutgoingOnlyMessage, ButtplugMessage):
    def __init__(self, error_message, error_code, id = ButtplugMessage.DEFAULT_ID):
        super(Ok, self).__init__(id)
        self.error_message = error_message
        self.error_code = error_code

class Test(ButtplugMessage):
    def __init__(self, test_string, id = ButtplugMessage.DEFAULT_ID):
        super(Ok, self).__init__(id)
        self.test_string = test_string

class RequestServerInfo(ButtplugMessage):
    def __init__(self, client_name, message_version = 1, id = ButtplugMessage.DEFAULT_ID):
        super(Ok, self).__init__(id)
        self.client_name = client_name
        self.message_version = message_version

class ServerInfo(ButtplugMessage):
    def __init__(self, server_name, major_version, minor_version,
                 build_version, message_version = 1, max_ping_time = 0,
                 id = ButtplugMessage.DEFAULT_ID):
        super(Ok, self).__init__(id)
        self.server_name = server_name
        self.major_version = major_version
        self.minor_version = minor_version
        self.build_version = build_version
        self.message_version = message_version
        self.max_ping_time = max_ping_time

class DeviceList(ButtplugMessage, ButtplugOutgoingOnlyMessage):
    pass

class DeviceAdded(ButtplugDeviceInfoMessage, ButtplugOutgoingOnlyMessage):
    pass

class DeviceRemoved(ButtplugDeviceInfoMessage, ButtplugOutgoingOnlyMessage):
    pass

class RequestDeviceList(ButtplugMessage):
    pass

class StartScanning(ButtplugMessage):
    pass

class StopScanning(ButtplugMessage):
    pass

class ScanningFinished(ButtplugMessage, ButtplugOutgoingOnlyMessage):
    pass

class RequestLog(ButtplugMessage):
    pass

class Log(ButtplugMessage, ButtplugOutgoingOnlyMessage):
    pass

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

