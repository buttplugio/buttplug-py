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
from buttplug.enums import InputType, OutputType
from buttplug.errors import ButtplugDeviceError, error_from_code
from buttplug.feature import CommandValue, DeviceFeature

if TYPE_CHECKING:
    from buttplug.client import ButtplugClient


class ButtplugDevice:
    """Represents a connected Buttplug device.

    Provides both device-level convenience methods (vibrate(), rotate(), etc.) that
    control all matching features, and per-feature access for fine-grained control.

    Command values can be specified as:
    - float: Normalized percentage from 0.0 to 1.0 (e.g., 0.5 = 50%)
    - int: Direct step value (e.g., 10 out of 20 steps)

    Example:
        # Device-level: control all vibrators at once
        await device.vibrate(0.5)  # 50% on all vibrators

        # Feature-level: control specific motor
        feature = device.features[0]
        await feature.vibrate(0.75)  # 75% on motor 0 only

        # Using steps instead of percent
        step_count = feature.step_count(OutputType.VIBRATE)
        await feature.vibrate(step_count // 2)  # Half power via steps
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

    # ============ Device-Level Convenience Methods ============
    # These control ALL matching features on the device

    async def vibrate(self, value: CommandValue) -> None:
        """Set vibration level on all vibrator features.

        Args:
            value: Float 0.0-1.0 (percent) or int (step value).

        Raises:
            ButtplugDeviceError: If device has no vibration features.
        """
        await self._send_to_all_features(OutputType.VIBRATE, value)

    async def rotate(self, value: CommandValue, clockwise: bool = True) -> None:
        """Set rotation on all rotation features.

        Args:
            value: Float 0.0-1.0 (percent) or int (step value).
            clockwise: Rotation direction.

        Raises:
            ButtplugDeviceError: If device has no rotation features.
        """
        # Prefer RotateWithDirection, fall back to Rotate
        features = self.get_features_with_output(OutputType.ROTATE_WITH_DIRECTION)
        if features:
            await asyncio.gather(*[f.rotate(value, clockwise) for f in features])
        else:
            await self._send_to_all_features(OutputType.ROTATE, value)

    async def oscillate(self, value: CommandValue) -> None:
        """Set oscillation on all oscillation features.

        Args:
            value: Float 0.0-1.0 (percent) or int (step value).

        Raises:
            ButtplugDeviceError: If device has no oscillation features.
        """
        await self._send_to_all_features(OutputType.OSCILLATE, value)

    async def constrict(self, value: CommandValue) -> None:
        """Set constriction on all constriction features.

        Args:
            value: Float 0.0-1.0 (percent) or int (step value).

        Raises:
            ButtplugDeviceError: If device has no constriction features.
        """
        await self._send_to_all_features(OutputType.CONSTRICT, value)

    async def position(self, value: CommandValue, duration_ms: int = 0) -> None:
        """Move to position on all position features.

        Args:
            value: Float 0.0-1.0 (percent) or int (step value).
            duration_ms: Time in ms to reach position (0 = instant).

        Raises:
            ButtplugDeviceError: If device has no position features.
        """
        # Prefer HwPositionWithDuration, fall back to Position
        features = self.get_features_with_output(OutputType.POSITION_WITH_DURATION)
        if features:
            await asyncio.gather(*[f.position(value, duration_ms) for f in features])
        else:
            await self._send_to_all_features(OutputType.POSITION, value)

    async def stop(self) -> None:
        """Stop all device outputs."""
        msg = StopCmd(id=0, device_index=self.index, outputs=True, inputs=False)
        response = await self._client._send_device_message(msg)
        self._check_response(response)

    async def stop_features(self, inputs: bool = True, outputs: bool = True) -> None:
        """Stop device outputs and/or unsubscribe from inputs.

        Args:
            inputs: If True, unsubscribe from all input subscriptions.
            outputs: If True, stop all outputs.
        """
        msg = StopCmd(id=0, device_index=self.index, inputs=inputs, outputs=outputs)
        response = await self._client._send_device_message(msg)
        self._check_response(response)

    # ============ Sensor Convenience Methods ============

    def has_battery_level(self) -> bool:
        """Check if device has a battery level sensor."""
        return self.has_input(InputType.BATTERY)

    async def battery_level(self) -> float:
        """Read battery level from first battery sensor.

        Returns:
            Battery level from 0.0 (empty) to 1.0 (full).

        Raises:
            ButtplugDeviceError: If device has no battery sensor.
        """
        features = self.get_features_with_input(InputType.BATTERY)
        if not features:
            raise ButtplugDeviceError("Device has no battery sensor")
        return await features[0].battery_level()

    def has_rssi_level(self) -> bool:
        """Check if device has an RSSI sensor."""
        return self.has_input(InputType.RSSI)

    async def rssi_level(self) -> int:
        """Read RSSI signal strength from first RSSI sensor.

        Returns:
            RSSI value (typically -10 to -100 dBm).

        Raises:
            ButtplugDeviceError: If device has no RSSI sensor.
        """
        features = self.get_features_with_input(InputType.RSSI)
        if not features:
            raise ButtplugDeviceError("Device has no RSSI sensor")
        return await features[0].rssi_level()

    # ============ Internal Methods ============

    async def _send_to_all_features(self, output_type: OutputType, value: CommandValue) -> None:
        """Send output command to all features with the specified output type."""
        features = self.get_features_with_output(output_type)
        output_name = output_type.value

        if not features:
            raise ButtplugDeviceError(f"Device has no {output_name} features")

        # Send to all matching features in parallel
        await asyncio.gather(*[f._send_output(output_type, value) for f in features])

    def _check_response(self, response: ButtplugMessage) -> None:
        """Check response and raise if error."""
        if isinstance(response, Error):
            raise error_from_code(response.error_code, response.error_message)
        if not isinstance(response, Ok):
            raise ButtplugDeviceError(f"Unexpected response: {type(response).__name__}")
