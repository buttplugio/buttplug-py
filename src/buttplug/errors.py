"""Exception hierarchy for Buttplug errors."""

from buttplug.enums import ErrorCode


class ButtplugError(Exception):
    """Base exception for all Buttplug errors."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class ButtplugConnectorError(ButtplugError):
    """Connection-related errors (WebSocket failures, disconnections)."""

    pass


class ButtplugHandshakeError(ButtplugError):
    """Handshake failed (version mismatch, server rejection)."""

    pass


class ButtplugPingError(ButtplugError):
    """Ping timeout - server didn't receive ping in time."""

    pass


class ButtplugDeviceError(ButtplugError):
    """Device command failed (device disconnected, invalid command)."""

    pass


class ButtplugMessageError(ButtplugError):
    """Message parsing or permission error."""

    pass


class ButtplugUnknownError(ButtplugError):
    """Unknown error from server."""

    pass


def error_from_code(code: ErrorCode, message: str) -> ButtplugError:
    """Create appropriate exception from error code."""
    match code:
        case ErrorCode.INIT:
            return ButtplugHandshakeError(message)
        case ErrorCode.PING:
            return ButtplugPingError(message)
        case ErrorCode.MSG:
            return ButtplugMessageError(message)
        case ErrorCode.DEVICE:
            return ButtplugDeviceError(message)
        case _:
            return ButtplugUnknownError(message)
