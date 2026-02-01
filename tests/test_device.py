"""Tests for device feature enumeration and capability checking."""

import pytest

from buttplug._messages.device_info import (
    DeviceFeatureDefinition,
    DeviceInfo,
    FeatureInputDefinition,
    FeatureOutputDefinition,
)
from buttplug.device import ButtplugDevice
from buttplug.enums import InputCommandType, InputType, OutputType
from buttplug.errors import ButtplugDeviceError
from buttplug.feature import DeviceFeature


class MockClient:
    """Mock client for testing features without network."""

    pass


class TestDeviceFeature:
    """Tests for DeviceFeature capability checking."""

    @pytest.fixture
    def mock_client(self) -> MockClient:
        """Mock client for feature testing."""
        return MockClient()

    @pytest.fixture
    def vibrate_feature(self, mock_client: MockClient) -> DeviceFeature:
        """Feature with vibration output."""
        defn = DeviceFeatureDefinition(
            feature_index=0,
            feature_description="Main Motor",
            output={"Vibrate": FeatureOutputDefinition(value=(0, 20), duration=None)},
            input=None,
        )
        return DeviceFeature(mock_client, 0, defn)  # type: ignore[arg-type]

    @pytest.fixture
    def battery_feature(self, mock_client: MockClient) -> DeviceFeature:
        """Feature with battery input."""
        defn = DeviceFeatureDefinition(
            feature_index=1,
            feature_description="Battery",
            output=None,
            input={"Battery": FeatureInputDefinition(value=[(0, 100)], command=["Read"])},
        )
        return DeviceFeature(mock_client, 0, defn)  # type: ignore[arg-type]

    @pytest.fixture
    def position_feature(self, mock_client: MockClient) -> DeviceFeature:
        """Feature with position output including duration."""
        defn = DeviceFeatureDefinition(
            feature_index=0,
            feature_description="Stroker",
            output={
                "HwPositionWithDuration": FeatureOutputDefinition(
                    value=(0, 100), duration=(0, 1000)
                )
            },
            input=None,
        )
        return DeviceFeature(mock_client, 0, defn)  # type: ignore[arg-type]

    def test_feature_index(self, vibrate_feature: DeviceFeature) -> None:
        """Feature exposes index."""
        assert vibrate_feature.index == 0

    def test_feature_description(self, vibrate_feature: DeviceFeature) -> None:
        """Feature exposes description."""
        assert vibrate_feature.description == "Main Motor"

    def test_has_output_true(self, vibrate_feature: DeviceFeature) -> None:
        """has_output returns True for supported output."""
        assert vibrate_feature.has_output(OutputType.VIBRATE) is True
        assert vibrate_feature.has_output("Vibrate") is True

    def test_has_output_false(self, vibrate_feature: DeviceFeature) -> None:
        """has_output returns False for unsupported output."""
        assert vibrate_feature.has_output(OutputType.ROTATE) is False

    def test_has_input_true(self, battery_feature: DeviceFeature) -> None:
        """has_input returns True for supported input."""
        assert battery_feature.has_input(InputType.BATTERY) is True
        assert battery_feature.has_input("Battery") is True

    def test_has_input_false(self, battery_feature: DeviceFeature) -> None:
        """has_input returns False for unsupported input."""
        assert battery_feature.has_input(InputType.RSSI) is False

    def test_supports_input_command(self, battery_feature: DeviceFeature) -> None:
        """supports_input_command checks command support."""
        assert (
            battery_feature.supports_input_command(InputType.BATTERY, InputCommandType.READ) is True
        )
        assert (
            battery_feature.supports_input_command(InputType.BATTERY, InputCommandType.SUBSCRIBE)
            is False
        )

    def test_step_range(self, vibrate_feature: DeviceFeature) -> None:
        """step_range returns value range."""
        range_val = vibrate_feature.step_range(OutputType.VIBRATE)
        assert range_val == (0, 20)

    def test_step_range_not_found(self, vibrate_feature: DeviceFeature) -> None:
        """step_range returns None for unsupported output."""
        assert vibrate_feature.step_range(OutputType.ROTATE) is None

    def test_step_count(self, vibrate_feature: DeviceFeature) -> None:
        """step_count returns max step value."""
        assert vibrate_feature.step_count(OutputType.VIBRATE) == 20

    def test_step_count_not_found(self, vibrate_feature: DeviceFeature) -> None:
        """step_count returns None for unsupported output."""
        assert vibrate_feature.step_count(OutputType.ROTATE) is None

    def test_duration_range(self, position_feature: DeviceFeature) -> None:
        """duration_range returns duration range."""
        duration = position_feature.duration_range(OutputType.POSITION_WITH_DURATION)
        assert duration == (0, 1000)

    def test_duration_range_not_found(self, vibrate_feature: DeviceFeature) -> None:
        """duration_range returns None when no duration."""
        assert vibrate_feature.duration_range(OutputType.VIBRATE) is None

    def test_convert_to_step_float(self, vibrate_feature: DeviceFeature) -> None:
        """convert_to_step converts float percent to steps."""
        # 0.5 * 20 = 10, ceil(10) = 10
        assert vibrate_feature.convert_to_step(OutputType.VIBRATE, 0.5) == 10
        # 0.0 * 20 = 0
        assert vibrate_feature.convert_to_step(OutputType.VIBRATE, 0.0) == 0
        # 1.0 * 20 = 20
        assert vibrate_feature.convert_to_step(OutputType.VIBRATE, 1.0) == 20
        # 0.05 * 20 = 1, ceil(1) = 1
        assert vibrate_feature.convert_to_step(OutputType.VIBRATE, 0.05) == 1

    def test_convert_to_step_int(self, vibrate_feature: DeviceFeature) -> None:
        """convert_to_step passes through int step values."""
        assert vibrate_feature.convert_to_step(OutputType.VIBRATE, 10) == 10
        assert vibrate_feature.convert_to_step(OutputType.VIBRATE, 0) == 0
        assert vibrate_feature.convert_to_step(OutputType.VIBRATE, 20) == 20

    def test_convert_to_step_out_of_range_float(self, vibrate_feature: DeviceFeature) -> None:
        """convert_to_step raises for float out of range."""
        with pytest.raises(ButtplugDeviceError, match="must be between"):
            vibrate_feature.convert_to_step(OutputType.VIBRATE, 1.5)

    def test_convert_to_step_out_of_range_int(self, vibrate_feature: DeviceFeature) -> None:
        """convert_to_step raises for int out of range."""
        with pytest.raises(ButtplugDeviceError, match="out of range"):
            vibrate_feature.convert_to_step(OutputType.VIBRATE, 25)


class TestButtplugDevice:
    """Tests for ButtplugDevice capability checking (no client interaction)."""

    @pytest.fixture
    def mock_client(self) -> MockClient:
        """Mock client for device testing."""
        return MockClient()

    @pytest.fixture
    def multi_feature_device_info(self) -> DeviceInfo:
        """Device info with multiple features."""
        return DeviceInfo(
            device_name="Test Multi-Feature Device",
            device_index=0,
            device_message_timing_gap=50,
            device_display_name="My Device",
            device_features={
                0: DeviceFeatureDefinition(
                    feature_index=0,
                    feature_description="Vibrator 1",
                    output={"Vibrate": FeatureOutputDefinition(value=(0, 20), duration=None)},
                    input=None,
                ),
                1: DeviceFeatureDefinition(
                    feature_index=1,
                    feature_description="Vibrator 2",
                    output={"Vibrate": FeatureOutputDefinition(value=(0, 20), duration=None)},
                    input=None,
                ),
                2: DeviceFeatureDefinition(
                    feature_index=2,
                    feature_description="Rotator",
                    output={"Rotate": FeatureOutputDefinition(value=(0, 10), duration=None)},
                    input=None,
                ),
                3: DeviceFeatureDefinition(
                    feature_index=3,
                    feature_description="Battery",
                    output=None,
                    input={"Battery": FeatureInputDefinition(value=[(0, 100)], command=["Read"])},
                ),
            },
        )

    def test_device_properties(
        self, mock_client: MockClient, multi_feature_device_info: DeviceInfo
    ) -> None:
        """Device exposes basic properties."""
        device = ButtplugDevice(mock_client, multi_feature_device_info)  # type: ignore[arg-type]

        assert device.index == 0
        assert device.name == "Test Multi-Feature Device"
        assert device.display_name == "My Device"
        assert device.message_timing_gap == 50
        assert len(device.features) == 4

    def test_has_output(
        self, mock_client: MockClient, multi_feature_device_info: DeviceInfo
    ) -> None:
        """Device has_output checks all features."""
        device = ButtplugDevice(mock_client, multi_feature_device_info)  # type: ignore[arg-type]

        assert device.has_output(OutputType.VIBRATE) is True
        assert device.has_output(OutputType.ROTATE) is True
        assert device.has_output(OutputType.POSITION) is False

    def test_has_input(
        self, mock_client: MockClient, multi_feature_device_info: DeviceInfo
    ) -> None:
        """Device has_input checks all features."""
        device = ButtplugDevice(mock_client, multi_feature_device_info)  # type: ignore[arg-type]

        assert device.has_input(InputType.BATTERY) is True
        assert device.has_input(InputType.RSSI) is False

    def test_get_features_with_output(
        self, mock_client: MockClient, multi_feature_device_info: DeviceInfo
    ) -> None:
        """get_features_with_output returns matching features."""
        device = ButtplugDevice(mock_client, multi_feature_device_info)  # type: ignore[arg-type]

        vibrate_features = device.get_features_with_output(OutputType.VIBRATE)
        assert len(vibrate_features) == 2

        rotate_features = device.get_features_with_output(OutputType.ROTATE)
        assert len(rotate_features) == 1

        position_features = device.get_features_with_output(OutputType.POSITION)
        assert len(position_features) == 0

    def test_get_features_with_input(
        self, mock_client: MockClient, multi_feature_device_info: DeviceInfo
    ) -> None:
        """get_features_with_input returns matching features."""
        device = ButtplugDevice(mock_client, multi_feature_device_info)  # type: ignore[arg-type]

        battery_features = device.get_features_with_input(InputType.BATTERY)
        assert len(battery_features) == 1

        rssi_features = device.get_features_with_input(InputType.RSSI)
        assert len(rssi_features) == 0

    def test_has_battery(
        self, mock_client: MockClient, multi_feature_device_info: DeviceInfo
    ) -> None:
        """has_battery checks for battery sensor."""
        device = ButtplugDevice(mock_client, multi_feature_device_info)  # type: ignore[arg-type]
        assert device.has_battery() is True

    def test_has_rssi(self, mock_client: MockClient, multi_feature_device_info: DeviceInfo) -> None:
        """has_rssi checks for RSSI sensor."""
        device = ButtplugDevice(mock_client, multi_feature_device_info)  # type: ignore[arg-type]
        assert device.has_rssi() is False

    def test_feature_step_count(
        self, mock_client: MockClient, multi_feature_device_info: DeviceInfo
    ) -> None:
        """Features expose step count for precision control."""
        device = ButtplugDevice(mock_client, multi_feature_device_info)  # type: ignore[arg-type]

        vibrate_feature = device.features[0]
        assert vibrate_feature.step_count(OutputType.VIBRATE) == 20

        rotate_feature = device.features[2]
        assert rotate_feature.step_count(OutputType.ROTATE) == 10
