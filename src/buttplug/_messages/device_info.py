"""Device information and enumeration messages."""

from __future__ import annotations

from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict, Field, model_validator

from buttplug._messages.base import ButtplugMessage


class FeatureOutputDefinition(BaseModel):
    """Output capability definition for a feature."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    value: tuple[int, int] = Field(alias="Value")
    duration: tuple[int, int] | None = Field(default=None, alias="Duration")


class FeatureInputDefinition(BaseModel):
    """Input capability definition for a feature."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    value: list[tuple[int, int]] = Field(alias="Value")
    command: list[str] = Field(alias="Command")


class DeviceFeatureDefinition(BaseModel):
    """Definition of a single device feature."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    feature_index: int = Field(alias="FeatureIndex")
    feature_description: str | None = Field(default=None, alias="FeatureDescription")
    output: dict[str, FeatureOutputDefinition] | None = Field(default=None, alias="Output")
    input: dict[str, FeatureInputDefinition] | None = Field(default=None, alias="Input")


class DeviceInfo(BaseModel):
    """Information about a single device."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    device_name: str = Field(alias="DeviceName")
    device_index: int = Field(alias="DeviceIndex")
    device_message_timing_gap: int = Field(default=0, alias="DeviceMessageTimingGap")
    device_display_name: str | None = Field(default=None, alias="DeviceDisplayName")
    device_features: dict[int, DeviceFeatureDefinition] = Field(
        default_factory=dict, alias="DeviceFeatures"
    )

    @model_validator(mode="before")
    @classmethod
    def parse_features_dict(cls, data: Any) -> Any:
        """Convert string-keyed DeviceFeatures dict to int-keyed."""
        if isinstance(data, dict):
            features = data.get("DeviceFeatures") or data.get("device_features")
            if features and isinstance(features, dict):
                # Protocol uses string keys like "0", "1", etc.
                converted = {}
                for key, value in features.items():
                    converted[int(key)] = value
                if "DeviceFeatures" in data:
                    data["DeviceFeatures"] = converted
                else:
                    data["device_features"] = converted
        return data


class DeviceList(ButtplugMessage):
    """List of connected devices."""

    _message_type: ClassVar[str] = "DeviceList"

    devices: dict[int, DeviceInfo] = Field(default_factory=dict, alias="Devices")

    @model_validator(mode="before")
    @classmethod
    def parse_devices_dict(cls, data: Any) -> Any:
        """Convert string-keyed Devices dict to int-keyed."""
        if isinstance(data, dict):
            devices = data.get("Devices") or data.get("devices")
            if devices and isinstance(devices, dict):
                # Protocol uses string keys like "0", "1", etc.
                converted = {}
                for key, value in devices.items():
                    converted[int(key)] = value
                if "Devices" in data:
                    data["Devices"] = converted
                else:
                    data["devices"] = converted
        return data
