"""Tests for message serialization and deserialization."""

import json

import pytest

from buttplug._messages import (
    DeviceList,
    Error,
    InputCmd,
    InputReading,
    Ok,
    OutputCmd,
    Ping,
    RequestDeviceList,
    RequestServerInfo,
    ScanningFinished,
    ServerInfo,
    StartScanning,
    StopCmd,
    StopScanning,
)
from buttplug._messages.base import parse_message, parse_messages
from buttplug.enums import ErrorCode


class TestHandshakeMessages:
    """Tests for handshake and status messages."""

    def test_request_server_info_serialize(self):
        """RequestServerInfo serializes with PascalCase."""
        msg = RequestServerInfo(id=1, client_name="Test Client")
        result = msg.to_protocol()

        assert result == [
            {
                "RequestServerInfo": {
                    "Id": 1,
                    "ClientName": "Test Client",
                    "ProtocolVersionMajor": 4,
                    "ProtocolVersionMinor": 0,
                }
            }
        ]

    def test_request_server_info_deserialize(self):
        """RequestServerInfo deserializes from PascalCase."""
        data = {
            "RequestServerInfo": {
                "Id": 1,
                "ClientName": "My App",
                "ProtocolVersionMajor": 4,
                "ProtocolVersionMinor": 0,
            }
        }
        msg = parse_message(data)

        assert isinstance(msg, RequestServerInfo)
        assert msg.id == 1
        assert msg.client_name == "My App"
        assert msg.protocol_version_major == 4

    def test_server_info_deserialize(self):
        """ServerInfo deserializes from protocol format."""
        data = {
            "ServerInfo": {
                "Id": 1,
                "ServerName": "Intiface Central",
                "MaxPingTime": 1000,
                "ProtocolVersionMajor": 4,
                "ProtocolVersionMinor": 0,
            }
        }
        msg = parse_message(data)

        assert isinstance(msg, ServerInfo)
        assert msg.server_name == "Intiface Central"
        assert msg.max_ping_time == 1000

    def test_ok_serialize(self):
        """Ok serializes correctly."""
        msg = Ok(id=5)
        result = msg.to_protocol()

        assert result == [{"Ok": {"Id": 5}}]

    def test_error_deserialize(self):
        """Error deserializes with error code."""
        data = {
            "Error": {
                "Id": 0,
                "ErrorMessage": "Ping timeout",
                "ErrorCode": 2,
            }
        }
        msg = parse_message(data)

        assert isinstance(msg, Error)
        assert msg.error_message == "Ping timeout"
        assert msg.error_code == ErrorCode.PING

    def test_ping_roundtrip(self):
        """Ping message round-trips correctly."""
        msg = Ping(id=10)
        protocol = msg.to_protocol()
        parsed = parse_message(protocol[0])

        assert isinstance(parsed, Ping)
        assert parsed.id == 10


class TestScanningMessages:
    """Tests for scanning control messages."""

    def test_start_scanning_serialize(self):
        """StartScanning serializes correctly."""
        msg = StartScanning(id=2)
        result = msg.to_protocol()

        assert result == [{"StartScanning": {"Id": 2}}]

    def test_stop_scanning_serialize(self):
        """StopScanning serializes correctly."""
        msg = StopScanning(id=3)
        result = msg.to_protocol()

        assert result == [{"StopScanning": {"Id": 3}}]

    def test_scanning_finished_deserialize(self):
        """ScanningFinished deserializes correctly."""
        data = {"ScanningFinished": {"Id": 0}}
        msg = parse_message(data)

        assert isinstance(msg, ScanningFinished)
        assert msg.id == 0

    def test_request_device_list_serialize(self):
        """RequestDeviceList serializes correctly."""
        msg = RequestDeviceList(id=4)
        result = msg.to_protocol()

        assert result == [{"RequestDeviceList": {"Id": 4}}]


class TestDeviceListMessage:
    """Tests for DeviceList message parsing."""

    def test_device_list_deserialize(self, sample_device_list_data):
        """DeviceList deserializes complex device structure."""
        data = {"DeviceList": sample_device_list_data}
        msg = parse_message(data)

        assert isinstance(msg, DeviceList)
        assert msg.id == 1
        assert len(msg.devices) == 2

        # Check first device
        device0 = msg.devices[0]
        assert device0.device_name == "Test Vibrator"
        assert device0.device_index == 0
        assert device0.device_message_timing_gap == 50
        assert device0.device_display_name == "My Vibrator"
        assert len(device0.device_features) == 3

        # Check feature with output
        feature0 = device0.device_features[0]
        assert feature0.feature_index == 0
        assert feature0.feature_description == "Clitoral Stimulator"
        assert feature0.output is not None
        assert "Vibrate" in feature0.output
        assert feature0.output["Vibrate"].value == (0, 20)

        # Check feature with input
        feature2 = device0.device_features[2]
        assert feature2.input is not None
        assert "Battery" in feature2.input
        battery_input = feature2.input["Battery"]
        assert battery_input.value == [(0, 100)]
        assert battery_input.command == ["Read"]

        # Check second device (stroker with position)
        device1 = msg.devices[1]
        assert device1.device_name == "Test Stroker"
        feature = device1.device_features[0]
        assert "HwPositionWithDuration" in feature.output
        pos_output = feature.output["HwPositionWithDuration"]
        assert pos_output.value == (0, 100)
        assert pos_output.duration == (0, 1000)

    def test_device_list_empty(self):
        """DeviceList handles empty device dict."""
        data = {"DeviceList": {"Id": 1, "Devices": {}}}
        msg = parse_message(data)

        assert isinstance(msg, DeviceList)
        assert len(msg.devices) == 0


class TestCommandMessages:
    """Tests for device command messages."""

    def test_output_cmd_vibrate_serialize(self):
        """OutputCmd for vibrate serializes correctly."""
        msg = OutputCmd(id=5, device_index=0, feature_index=0, command={"Vibrate": {"Value": 10}})
        result = msg.to_protocol()

        assert result == [
            {
                "OutputCmd": {
                    "Id": 5,
                    "DeviceIndex": 0,
                    "FeatureIndex": 0,
                    "Command": {"Vibrate": {"Value": 10}},
                }
            }
        ]

    def test_output_cmd_position_with_duration(self):
        """OutputCmd for position with duration serializes correctly."""
        msg = OutputCmd(
            id=6,
            device_index=1,
            feature_index=0,
            command={"HwPositionWithDuration": {"Value": 80, "Duration": 250}},
        )
        result = msg.to_protocol()

        expected_cmd = result[0]["OutputCmd"]["Command"]
        assert expected_cmd["HwPositionWithDuration"]["Value"] == 80
        assert expected_cmd["HwPositionWithDuration"]["Duration"] == 250

    def test_input_cmd_serialize(self):
        """InputCmd serializes correctly."""
        msg = InputCmd(id=7, device_index=0, feature_index=2, input_type="Battery", command="Read")
        result = msg.to_protocol()

        assert result == [
            {
                "InputCmd": {
                    "Id": 7,
                    "DeviceIndex": 0,
                    "FeatureIndex": 2,
                    "Type": "Battery",
                    "Command": "Read",
                }
            }
        ]

    def test_input_reading_deserialize(self, sample_input_reading_data):
        """InputReading deserializes correctly."""
        data = {"InputReading": sample_input_reading_data}
        msg = parse_message(data)

        assert isinstance(msg, InputReading)
        assert msg.device_index == 0
        assert msg.feature_index == 2
        assert "Battery" in msg.reading
        assert msg.reading["Battery"].value == 75

    def test_stop_cmd_all_devices(self):
        """StopCmd for all devices serializes correctly."""
        msg = StopCmd(id=8)
        result = msg.to_protocol()

        assert result == [{"StopCmd": {"Id": 8, "Inputs": True, "Outputs": True}}]

    def test_stop_cmd_specific_device(self):
        """StopCmd for specific device serializes correctly."""
        msg = StopCmd(id=9, device_index=0, outputs=True, inputs=False)
        result = msg.to_protocol()

        assert result == [
            {"StopCmd": {"Id": 9, "DeviceIndex": 0, "Inputs": False, "Outputs": True}}
        ]


class TestMessageParsing:
    """Tests for message parsing utilities."""

    def test_parse_messages_array(self):
        """parse_messages handles array of messages."""
        data = [
            {"Ok": {"Id": 1}},
            {"ScanningFinished": {"Id": 0}},
        ]
        messages = parse_messages(data)

        assert len(messages) == 2
        assert isinstance(messages[0], Ok)
        assert isinstance(messages[1], ScanningFinished)

    def test_parse_message_unknown_type(self):
        """parse_message raises for unknown message type."""
        with pytest.raises(ValueError, match="Unknown message type"):
            parse_message({"UnknownType": {"Id": 1}})

    def test_parse_message_multiple_types(self):
        """parse_message raises for multiple types in one dict."""
        with pytest.raises(ValueError, match="Expected single message type"):
            parse_message({"Ok": {"Id": 1}, "Error": {"Id": 1}})

    def test_json_roundtrip(self):
        """Messages survive JSON serialization roundtrip."""
        msg = RequestServerInfo(id=1, client_name="Test")
        json_str = json.dumps(msg.to_protocol())
        parsed_data = json.loads(json_str)
        restored = parse_message(parsed_data[0])

        assert isinstance(restored, RequestServerInfo)
        assert restored.client_name == "Test"
