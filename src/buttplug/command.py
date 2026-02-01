"""Device output command for unified output control."""

from __future__ import annotations

from dataclasses import dataclass

from buttplug.enums import OutputType
from buttplug.feature import CommandValue


@dataclass(frozen=True)
class DeviceOutputCommand:
    """A command to send to a device output.

    Args:
        output_type: The type of output to control (e.g., OutputType.VIBRATE).
        value: Float 0.0-1.0 (percent) or int (step value).
        duration: Duration in ms, only for POSITION_WITH_DURATION.
    """

    output_type: OutputType
    value: CommandValue
    duration: int | None = None
