"""Handshake, status, and scanning messages."""

from __future__ import annotations

from typing import ClassVar

from pydantic import Field

from buttplug._messages.base import ButtplugMessage
from buttplug.enums import ErrorCode


class RequestServerInfo(ButtplugMessage):
    """Client identification message sent at connection start."""

    _message_type: ClassVar[str] = "RequestServerInfo"

    client_name: str = Field(alias="ClientName")
    protocol_version_major: int = Field(default=4, alias="ProtocolVersionMajor")
    protocol_version_minor: int = Field(default=0, alias="ProtocolVersionMinor")


class ServerInfo(ButtplugMessage):
    """Server identification response."""

    _message_type: ClassVar[str] = "ServerInfo"

    server_name: str | None = Field(default=None, alias="ServerName")
    max_ping_time: int = Field(alias="MaxPingTime")
    protocol_version_major: int = Field(alias="ProtocolVersionMajor")
    protocol_version_minor: int = Field(alias="ProtocolVersionMinor")


class Ok(ButtplugMessage):
    """Success response from server."""

    _message_type: ClassVar[str] = "Ok"


class Error(ButtplugMessage):
    """Error response from server."""

    _message_type: ClassVar[str] = "Error"

    error_message: str = Field(alias="ErrorMessage")
    error_code: ErrorCode = Field(alias="ErrorCode")


class Ping(ButtplugMessage):
    """Keepalive ping message."""

    _message_type: ClassVar[str] = "Ping"


class Disconnect(ButtplugMessage):
    """Graceful disconnection request."""

    _message_type: ClassVar[str] = "Disconnect"


class StartScanning(ButtplugMessage):
    """Start scanning for devices."""

    _message_type: ClassVar[str] = "StartScanning"


class StopScanning(ButtplugMessage):
    """Stop scanning for devices."""

    _message_type: ClassVar[str] = "StopScanning"


class ScanningFinished(ButtplugMessage):
    """Notification that scanning has completed."""

    _message_type: ClassVar[str] = "ScanningFinished"


class RequestDeviceList(ButtplugMessage):
    """Request list of connected devices."""

    _message_type: ClassVar[str] = "RequestDeviceList"
