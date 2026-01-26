"""Device control command messages."""

from __future__ import annotations

from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict, Field

from buttplug._messages.base import ButtplugMessage


class OutputCommand(BaseModel):
    """Base for output command payloads."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    value: int = Field(alias="Value")


class OutputCommandWithDuration(OutputCommand):
    """Output command with duration (for position commands)."""

    duration: int = Field(alias="Duration")


class OutputCommandWithDirection(OutputCommand):
    """Output command with direction (for rotate commands)."""

    clockwise: bool = Field(alias="Clockwise")


class OutputCmd(ButtplugMessage):
    """Command to control device output (vibrate, rotate, position, etc.)."""

    _message_type: ClassVar[str] = "OutputCmd"

    device_index: int = Field(alias="DeviceIndex")
    feature_index: int = Field(alias="FeatureIndex")
    command: dict[str, Any] = Field(alias="Command")


class InputCmd(ButtplugMessage):
    """Command to read or subscribe to device sensor."""

    _message_type: ClassVar[str] = "InputCmd"

    device_index: int = Field(alias="DeviceIndex")
    feature_index: int = Field(alias="FeatureIndex")
    input_type: str = Field(alias="Type")
    command: str = Field(alias="Command")


class InputReadingValue(BaseModel):
    """Single input reading value."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    value: int = Field(alias="Value")


class InputReading(ButtplugMessage):
    """Sensor reading from device."""

    _message_type: ClassVar[str] = "InputReading"

    device_index: int = Field(alias="DeviceIndex")
    feature_index: int = Field(alias="FeatureIndex")
    reading: dict[str, InputReadingValue] = Field(alias="Reading")


class StopCmd(ButtplugMessage):
    """Stop device outputs and/or unsubscribe from inputs."""

    _message_type: ClassVar[str] = "StopCmd"

    device_index: int | None = Field(default=None, alias="DeviceIndex")
    feature_index: int | None = Field(default=None, alias="FeatureIndex")
    inputs: bool = Field(default=True, alias="Inputs")
    outputs: bool = Field(default=True, alias="Outputs")
