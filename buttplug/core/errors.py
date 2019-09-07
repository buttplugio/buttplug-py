class ButtplugError(Exception):
    """Base Class for Buttplug Errors.

    Attributes:

        message (str): Describes the nature of the exception
    """
    def __init__(self, message: str):
        self.message = message


class ButtplugHandshakeError(ButtplugError):
    """Error thrown when errors happen during initial connection

    Attributes:

        message (str): Describes the nature of the exception
    """
    pass


class ButtplugDeviceError(ButtplugError):
    """Error thrown when errors happen during device operations, including
    discovery, sending commands, etc.

    Attributes:

        message (str): Describes the nature of the exception
    """
    pass


class ButtplugMessageError(ButtplugError):
    """Error thrown when a message is incomplete or incorrectly formed.

    Attributes:

        message (str): Describes the nature of the exception
    """
    pass


class ButtplugPingError(ButtplugError):
    """Error thrown when a ping timeout request from the server is not met.

    Attributes:

        message (str): Describes the nature of the exception
    """
    pass


class ButtplugUnknownError(ButtplugError):
    """Unknown error, see message for more info.

    Attributes:

        message (str): Describes the nature of the exception
    """
    pass
