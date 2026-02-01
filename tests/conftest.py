"""Test configuration and fixtures."""

import pytest


@pytest.fixture
def sample_device_list_data() -> dict:
    """Sample DeviceList message data from protocol."""
    return {
        "Id": 1,
        "Devices": {
            "0": {
                "DeviceName": "Test Vibrator",
                "DeviceIndex": 0,
                "DeviceMessageTimingGap": 50,
                "DeviceDisplayName": "My Vibrator",
                "DeviceFeatures": {
                    "0": {
                        "FeatureIndex": 0,
                        "FeatureDescription": "Clitoral Stimulator",
                        "Output": {"Vibrate": {"Value": [0, 20]}},
                    },
                    "1": {
                        "FeatureIndex": 1,
                        "FeatureDescription": "G-Spot Motor",
                        "Output": {"Vibrate": {"Value": [0, 20]}},
                    },
                    "2": {
                        "FeatureIndex": 2,
                        "FeatureDescription": "Battery",
                        "Input": {"Battery": {"Value": [[0, 100]], "Command": ["Read"]}},
                    },
                },
            },
            "1": {
                "DeviceName": "Test Stroker",
                "DeviceIndex": 1,
                "DeviceMessageTimingGap": 100,
                "DeviceFeatures": {
                    "0": {
                        "FeatureIndex": 0,
                        "FeatureDescription": "Stroker",
                        "Output": {
                            "HwPositionWithDuration": {"Value": [0, 100], "Duration": [0, 1000]}
                        },
                    }
                },
            },
        },
    }


@pytest.fixture
def sample_input_reading_data() -> dict:
    """Sample InputReading message data from protocol."""
    return {"Id": 5, "DeviceIndex": 0, "FeatureIndex": 2, "Reading": {"Battery": {"Value": 75}}}
