"""Base message class and serialization utilities."""

from __future__ import annotations

from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict, Field


class ButtplugMessage(BaseModel):
    """Base class for all Buttplug protocol messages."""

    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid",
    )

    # Message type name used in JSON (set by subclasses)
    _message_type: ClassVar[str] = ""

    id: int = Field(alias="Id")

    def to_protocol(self) -> list[dict[str, Any]]:
        """Serialize message to Buttplug protocol format."""
        return [{self._message_type: self.model_dump(by_alias=True, exclude_none=True)}]

    @classmethod
    def get_message_type(cls) -> str:
        """Get the protocol message type name."""
        return cls._message_type


def parse_message(data: dict[str, Any]) -> ButtplugMessage:
    """Parse a single message from protocol format.

    Args:
        data: A dict with a single key (message type) and value (message fields).

    Returns:
        Parsed message object.

    Raises:
        ValueError: If message type is unknown.
    """
    from buttplug._messages.commands import (
        InputCmd,
        InputReading,
        OutputCmd,
        StopCmd,
    )
    from buttplug._messages.device_info import DeviceList
    from buttplug._messages.handshake import (
        Disconnect,
        Error,
        Ok,
        Ping,
        RequestDeviceList,
        RequestServerInfo,
        ScanningFinished,
        ServerInfo,
        StartScanning,
        StopScanning,
    )

    message_types: dict[str, type[ButtplugMessage]] = {
        "RequestServerInfo": RequestServerInfo,
        "ServerInfo": ServerInfo,
        "Ok": Ok,
        "Error": Error,
        "Ping": Ping,
        "Disconnect": Disconnect,
        "StartScanning": StartScanning,
        "StopScanning": StopScanning,
        "ScanningFinished": ScanningFinished,
        "RequestDeviceList": RequestDeviceList,
        "DeviceList": DeviceList,
        "OutputCmd": OutputCmd,
        "InputCmd": InputCmd,
        "InputReading": InputReading,
        "StopCmd": StopCmd,
    }

    if len(data) != 1:
        msg = f"Expected single message type, got {len(data)}"
        raise ValueError(msg)

    msg_type = next(iter(data.keys()))
    msg_data = data[msg_type]

    if msg_type not in message_types:
        msg = f"Unknown message type: {msg_type}"
        raise ValueError(msg)

    return message_types[msg_type].model_validate(msg_data)


def parse_messages(data: list[dict[str, Any]]) -> list[ButtplugMessage]:
    """Parse an array of messages from protocol format."""
    return [parse_message(msg) for msg in data]
