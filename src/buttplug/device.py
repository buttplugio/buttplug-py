"""Buttplug device for controlling hardware."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from buttplug._messages import (
    ButtplugMessage,
    Error,
    Ok,
    StopCmd,
)
from buttplug._messages.device_info import DeviceInfo
from buttplug.command import DeviceOutputCommand
from buttplug.enums import InputType, OutputType
from buttplug.errors import ButtplugDeviceError, error_from_code
from buttplug.feature import DeviceFeature

if TYPE_CHECKING:
    from buttplug.client import ButtplugClient


class ButtplugDevice:
    """Represents a connected Buttplug device.

    Provides both device-level run_output() that controls all matching features,
    and per-feature access for fine-grained control.

    Command values can be specified as:
    - float: Normalized percentage from 0.0 to 1.0 (e.g., 0.5 = 50%)
    - int: Direct step value (e.g., 10 out of 20 steps)

    Example:
        # Device-level: control all vibrators at once
        await device.run_output(DeviceOutputCommand(OutputType.VIBRATE, 0.5))

        # Feature-level: control specific motor
        feature = device.features[0]
        await feature.run_output(DeviceOutputCommand(OutputType.VIBRATE, 0.75))

        # Using steps instead of percent
        step_count = feature.step_count(OutputType.VIBRATE)
        await feature.run_output(DeviceOutputCommand(OutputType.VIBRATE, step_count // 2))
    """

    def __init__(self, client: ButtplugClient, device_info: DeviceInfo) -> None:
        """Initialize device from protocol device info."""
        self._client = client
        self._info = device_info
        self._features: dict[int, DeviceFeature] = {
            idx: DeviceFeature(client, device_info.device_index, defn)
            for idx, defn in device_info.device_features.items()
        }

    @property
    def index(self) -> int:
        """Device index (unique identifier from server)."""
        return self._info.device_index

    @property
    def name(self) -> str:
        """Device name from server configuration."""
        return self._info.device_name

    @property
    def display_name(self) -> str | None:
        """User-provided display name, or None if not set."""
        return self._info.device_display_name

    @property
    def message_timing_gap(self) -> int:
        """Minimum milliseconds between commands (enforced by server)."""
        return self._info.device_message_timing_gap

    @property
    def features(self) -> dict[int, DeviceFeature]:
        """Dictionary of device features by feature index.

        Use this for per-feature control when a device has multiple
        motors, sensors, or other capabilities.
        """
        return self._features

    def has_output(self, output_type: OutputType | str) -> bool:
        """Check if device has any feature with the specified output type."""
        return any(f.has_output(output_type) for f in self._features.values())

    def has_input(self, input_type: InputType | str) -> bool:
        """Check if device has any feature with the specified input type."""
        return any(f.has_input(input_type) for f in self._features.values())

    def get_features_with_output(self, output_type: OutputType | str) -> list[DeviceFeature]:
        """Get all features that support a specific output type."""
        return [f for f in self._features.values() if f.has_output(output_type)]

    def get_features_with_input(self, input_type: InputType | str) -> list[DeviceFeature]:
        """Get all features that support a specific input type."""
        return [f for f in self._features.values() if f.has_input(input_type)]

    # ============ Device-Level Command Methods ============

    async def run_output(self, command: DeviceOutputCommand) -> None:
        """Send an output command to all features matching the output type.

        Args:
            command: The output command specifying type, value, and optional duration.

        Raises:
            ButtplugDeviceError: If device has no features matching the output type.
        """
        features = self.get_features_with_output(command.output_type)
        if not features:
            raise ButtplugDeviceError(f"Device has no {command.output_type.value} features")
        await asyncio.gather(*[f.run_output(command) for f in features])

    async def stop(self, inputs: bool = True, outputs: bool = True) -> None:
        """Stop device outputs and/or unsubscribe from inputs.

        Args:
            inputs: If True, unsubscribe from all input subscriptions.
            outputs: If True, stop all outputs.
        """
        msg = StopCmd(id=0, device_index=self.index, inputs=inputs, outputs=outputs)
        response = await self._client._send_device_message(msg)
        self._check_response(response)

    # ============ Sensor Convenience Methods ============

    def has_battery(self) -> bool:
        """Check if device has a battery level sensor."""
        return self.has_input(InputType.BATTERY)

    async def battery(self) -> float:
        """Read battery level from first battery sensor.

        Returns:
            Battery level from 0.0 (empty) to 1.0 (full).

        Raises:
            ButtplugDeviceError: If device has no battery sensor.
        """
        features = self.get_features_with_input(InputType.BATTERY)
        if not features:
            raise ButtplugDeviceError("Device has no battery sensor")
        return await features[0].battery()

    def has_rssi(self) -> bool:
        """Check if device has an RSSI sensor."""
        return self.has_input(InputType.RSSI)

    async def rssi(self) -> int:
        """Read RSSI signal strength from first RSSI sensor.

        Returns:
            RSSI value (typically -10 to -100 dBm).

        Raises:
            ButtplugDeviceError: If device has no RSSI sensor.
        """
        features = self.get_features_with_input(InputType.RSSI)
        if not features:
            raise ButtplugDeviceError("Device has no RSSI sensor")
        return await features[0].rssi()

    # ============ Internal Methods ============

    def _check_response(self, response: ButtplugMessage) -> None:
        """Check response and raise if error."""
        if isinstance(response, Error):
            raise error_from_code(response.error_code, response.error_message)
        if not isinstance(response, Ok):
            raise ButtplugDeviceError(f"Unexpected response: {type(response).__name__}")
