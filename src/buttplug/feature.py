"""Device feature for low-level access to device capabilities."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from buttplug._messages.device_info import (
    DeviceFeatureDefinition,
    FeatureInputDefinition,
    FeatureOutputDefinition,
)
from buttplug.enums import InputCommandType, InputType, OutputType
from buttplug.errors import ButtplugDeviceError

if TYPE_CHECKING:
    from buttplug.client import ButtplugClient
    from buttplug.command import DeviceOutputCommand


# Type alias for command values - can be float (0.0-1.0 percent) or int (steps)
CommandValue = float | int


class DeviceFeature:
    """Represents a single feature of a device.

    Features are the individual capabilities of a device, such as a vibrator motor,
    a battery sensor, or a rotation mechanism. Each feature has an index, optional
    description, and defines its supported outputs and/or inputs.

    Command values can be specified as:
    - float: Normalized percentage from 0.0 to 1.0 (e.g., 0.5 = 50%)
    - int: Direct step value (e.g., 10 out of 20 steps)

    Example:
        # Using percent (recommended for most cases)
        await feature.run_output(DeviceOutputCommand(OutputType.VIBRATE, 0.5))

        # Using steps (for precise hardware control)
        await feature.run_output(DeviceOutputCommand(OutputType.VIBRATE, 10))

        # Check step range first
        print(f"Steps: {feature.step_count(OutputType.VIBRATE)}")
    """

    def __init__(
        self, client: ButtplugClient, device_index: int, definition: DeviceFeatureDefinition
    ) -> None:
        """Initialize from protocol feature definition."""
        self._client = client
        self._device_index = device_index
        self._definition = definition

    @property
    def index(self) -> int:
        """Feature index (unique within device)."""
        return self._definition.feature_index

    @property
    def description(self) -> str | None:
        """Human-readable feature description (e.g., "Clitoral Stimulator")."""
        return self._definition.feature_description

    @property
    def outputs(self) -> dict[str, FeatureOutputDefinition] | None:
        """Output types supported by this feature, or None if no outputs."""
        return self._definition.output

    @property
    def inputs(self) -> dict[str, FeatureInputDefinition] | None:
        """Input types supported by this feature, or None if no inputs."""
        return self._definition.input

    def has_output(self, output_type: OutputType | str) -> bool:
        """Check if this feature supports a specific output type."""
        if self._definition.output is None:
            return False
        output_name = output_type.value if isinstance(output_type, OutputType) else output_type
        return output_name in self._definition.output

    def has_input(self, input_type: InputType | str) -> bool:
        """Check if this feature supports a specific input type."""
        if self._definition.input is None:
            return False
        input_name = input_type.value if isinstance(input_type, InputType) else input_type
        return input_name in self._definition.input

    def supports_input_command(
        self, input_type: InputType | str, command: InputCommandType
    ) -> bool:
        """Check if this feature supports a specific input command."""
        if self._definition.input is None:
            return False
        input_name = input_type.value if isinstance(input_type, InputType) else input_type
        if input_name not in self._definition.input:
            return False
        return command.value in self._definition.input[input_name].command

    def step_range(self, output_type: OutputType | str) -> tuple[int, int] | None:
        """Get the step value range for an output type.

        Args:
            output_type: Output type (e.g., OutputType.VIBRATE)

        Returns:
            Tuple of (min_step, max_step), or None if output not supported.
        """
        if self._definition.output is None:
            return None
        output_name = output_type.value if isinstance(output_type, OutputType) else output_type
        if output_name not in self._definition.output:
            return None
        return self._definition.output[output_name].value

    def step_count(self, output_type: OutputType | str) -> int | None:
        """Get the number of steps for an output type.

        This is the maximum step value (e.g., 20 means steps 0-20).

        Args:
            output_type: Output type (e.g., OutputType.VIBRATE)

        Returns:
            Maximum step value, or None if output not supported.
        """
        step_range = self.step_range(output_type)
        if step_range is None:
            return None
        return step_range[1]

    def duration_range(self, output_type: OutputType | str) -> tuple[int, int] | None:
        """Get the duration range for an output type (e.g., position with duration).

        Args:
            output_type: Output type (e.g., OutputType.POSITION_WITH_DURATION)

        Returns:
            Tuple of (min_ms, max_ms) duration, or None if not supported.
        """
        if self._definition.output is None:
            return None
        output_name = output_type.value if isinstance(output_type, OutputType) else output_type
        if output_name not in self._definition.output:
            return None
        return self._definition.output[output_name].duration

    def convert_to_step(self, output_type: OutputType | str, value: CommandValue) -> int:
        """Convert a command value (float or int) to a step value.

        Args:
            output_type: The output type to convert for.
            value: Either a float (0.0-1.0 percent) or int (step value).

        Returns:
            The step value to send to the device.

        Raises:
            ButtplugDeviceError: If value is out of range or output not supported.
        """
        step_range = self.step_range(output_type)
        if step_range is None:
            output_name = output_type.value if isinstance(output_type, OutputType) else output_type
            raise ButtplugDeviceError(f"Feature does not support {output_name}")

        min_step, max_step = step_range

        if isinstance(value, float):
            # Validate percent range
            if not -1.0 <= value <= 1.0:
                raise ButtplugDeviceError(f"Float value {value} must be between -1.0 and 1.0")

            # Convert percent to step
            if value >= 0:
                step = int(math.ceil(value * max_step))
            else:
                step = int(math.floor(value * max_step))
        else:
            # Direct step value
            step = value

        # Validate step range
        if not min_step <= step <= max_step:
            raise ButtplugDeviceError(f"Step value {step} out of range [{min_step}, {max_step}]")

        return step

    # ============ Feature-Level Command Methods ============

    async def run_output(self, command: DeviceOutputCommand) -> None:
        """Send an output command to this feature.

        Args:
            command: The output command specifying type, value, and optional duration.

        Raises:
            ButtplugDeviceError: If this feature doesn't support the output type.
        """
        if command.output_type == OutputType.POSITION_WITH_DURATION:
            await self._send_position_with_duration(command.value, command.duration or 0)
        else:
            await self._send_output(command.output_type, command.value)

    async def stop(self) -> None:
        """Stop this feature's outputs."""
        from buttplug._messages import StopCmd

        msg = StopCmd(
            id=0,
            device_index=self._device_index,
            feature_index=self.index,
            outputs=True,
            inputs=False,
        )
        response = await self._client._send_device_message(msg)
        self._check_response(response)

    async def battery(self) -> float:
        """Read battery level (0.0-1.0)."""
        reading = await self._read_input(InputType.BATTERY)
        return reading / 100.0

    async def rssi(self) -> int:
        """Read RSSI signal strength (dBm)."""
        return await self._read_input(InputType.RSSI)

    # ============ Internal Methods ============

    async def _send_output(self, output_type: OutputType, value: CommandValue) -> None:
        """Send an output command to this feature."""
        from buttplug._messages import OutputCmd

        output_name = output_type.value
        step = self.convert_to_step(output_type, value)

        msg = OutputCmd(
            id=0,
            device_index=self._device_index,
            feature_index=self.index,
            command={output_name: {"Value": step}},
        )
        response = await self._client._send_device_message(msg)
        self._check_response(response)

    async def _send_position_with_duration(self, value: CommandValue, duration_ms: int) -> None:
        """Send position with duration command."""
        from buttplug._messages import OutputCmd

        step = self.convert_to_step(OutputType.POSITION_WITH_DURATION, value)

        # Clamp duration to allowed range
        duration_range = self.duration_range(OutputType.POSITION_WITH_DURATION)
        if duration_range:
            min_dur, max_dur = duration_range
            duration_ms = max(min_dur, min(max_dur, duration_ms))

        msg = OutputCmd(
            id=0,
            device_index=self._device_index,
            feature_index=self.index,
            command={"HwPositionWithDuration": {"Value": step, "Duration": duration_ms}},
        )
        response = await self._client._send_device_message(msg)
        self._check_response(response)

    async def _read_input(self, input_type: InputType) -> int:
        """Read raw input value."""
        from buttplug._messages import Error, InputCmd, InputReading

        input_name = input_type.value
        if not self.has_input(input_type):
            raise ButtplugDeviceError(f"Feature does not support {input_name} input")

        msg = InputCmd(
            id=0,
            device_index=self._device_index,
            feature_index=self.index,
            input_type=input_name,
            command=InputCommandType.READ.value,
        )
        response = await self._client._send_device_message(msg)

        if isinstance(response, Error):
            from buttplug.errors import error_from_code

            raise error_from_code(response.error_code, response.error_message)

        if not isinstance(response, InputReading):
            raise ButtplugDeviceError(f"Unexpected response: {type(response).__name__}")

        if input_name not in response.reading:
            raise ButtplugDeviceError(f"Invalid {input_name} reading response")

        return response.reading[input_name].value

    def _check_response(self, response: object) -> None:
        """Check response and raise if error."""
        from buttplug._messages import Error, Ok
        from buttplug.errors import error_from_code

        if isinstance(response, Error):
            raise error_from_code(response.error_code, response.error_message)
        if not isinstance(response, Ok):
            raise ButtplugDeviceError(f"Unexpected response: {type(response).__name__}")
