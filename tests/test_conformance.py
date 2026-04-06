"""Conformance tests for ButtplugClient against the Rust conformance harness.

These tests run the Rust conformance harness binary as a real ButtplugServer
and connect the Python ButtplugClient to it. The harness validates server-side
state (hardware write logs, device handles) while the client drives all
protocol messages.

The harness binary must be built first:
    cargo build -p buttplug_client_conformance_test

Set BUTTPLUG_CONFORMANCE_BINARY to override the binary path.

Skipped automatically if the binary is not found.
"""

from __future__ import annotations

import asyncio
import json
import os
import random
import subprocess
from dataclasses import dataclass
from pathlib import Path

import pytest

from buttplug import (
    ButtplugClient,
    ButtplugDevice,
    DeviceOutputCommand,
    OutputType,
)

# ─── Binary discovery ─────────────────────────────────────────────────────────

HARNESS_BINARY = os.environ.get(
    "BUTTPLUG_CONFORMANCE_BINARY",
    str(
        Path(__file__).resolve().parents[2]
        / "buttplug"
        / "target"
        / "debug"
        / "buttplug-client-conformance-test"
    ),
)
HARNESS_AVAILABLE = Path(HARNESS_BINARY).exists()
# Randomize port base to avoid TIME_WAIT conflicts between test runs
HARNESS_PORT_BASE = 16000 + random.randint(0, 1000) * 10

pytestmark = pytest.mark.skipif(
    not HARNESS_AVAILABLE,
    reason=f"Conformance harness binary not found at {HARNESS_BINARY}",
)


# ─── Report types ─────────────────────────────────────────────────────────────


@dataclass
class StepResult:
    step_name: str
    passed: bool
    error: str | None
    duration_ms: float


@dataclass
class SequenceResult:
    sequence_name: str
    passed: bool
    steps: list[StepResult]


@dataclass
class HarnessReport:
    sequences: list[SequenceResult]


def parse_harness_output(stdout: str) -> HarnessReport:
    """Extract the JSON report from harness stdout (has header text before it)."""
    lines = stdout.split("\n")
    json_start = next((i for i, line in enumerate(lines) if line.strip() == "{"), None)
    if json_start is None:
        raise ValueError(f"No JSON block in harness output:\n{stdout}")
    raw = json.loads("\n".join(lines[json_start:]))
    return HarnessReport(
        sequences=[
            SequenceResult(
                sequence_name=seq["sequence_name"],
                passed=seq["passed"],
                steps=[
                    StepResult(
                        step_name=s["step_name"],
                        passed=s["passed"],
                        error=s.get("error"),
                        duration_ms=s.get("duration_ms", 0),
                    )
                    for s in seq["steps"]
                ],
            )
            for seq in raw["sequences"]
        ]
    )


# ─── Harness launcher ────────────────────────────────────────────────────────


class HarnessProcess:
    """Manages a conformance harness subprocess.

    Uses a sync subprocess to avoid asyncio event loop interference.
    The harness output is collected when wait_for_report() is called.
    """

    def __init__(self, sequence: str, port: int, timeout_ms: int = 10000) -> None:
        self.proc = subprocess.Popen(
            [
                HARNESS_BINARY,
                "--port", str(port),
                "--sequence", sequence,
                "--format", "json",
                "--timeout", str(timeout_ms),
                "--client-driven",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    async def wait_for_report(self) -> HarnessReport:
        """Wait for the harness to exit and parse its report.

        Runs the blocking wait in an executor to avoid blocking the event loop.
        """
        loop = asyncio.get_running_loop()
        stdout_bytes, stderr_bytes = await loop.run_in_executor(None, self.proc.communicate)
        stdout = stdout_bytes.decode()
        if stderr_bytes:
            print(f"Harness stderr:\n{stderr_bytes.decode()}")
        return parse_harness_output(stdout)


async def connect_with_retry(
    client: ButtplugClient, url: str, retries: int = 10, delay: float = 0.3
) -> None:
    """Connect to the harness, retrying until it's ready."""
    for attempt in range(retries):
        try:
            await client.connect(url)
            return
        except Exception:
            if attempt == retries - 1:
                raise
            await asyncio.sleep(delay)


def log_sequence(result: SequenceResult) -> None:
    """Print step-by-step results for debugging."""
    for step in result.steps:
        icon = "✓" if step.passed else "✗"
        err = f" — {step.error}" if step.error else ""
        print(f"    {icon} {step.step_name}{err}")


# ─── Helpers ──────────────────────────────────────────────────────────────────


async def wait_for_devices(
    client: ButtplugClient,
    count: int,
    devices_by_name: dict[str, ButtplugDevice],
    timeout: float = 15.0,
) -> None:
    """Poll until `count` devices are discovered, requesting device list periodically.

    The conformance server sends DeviceList messages incrementally as devices
    are created. We poll with explicit RequestDeviceList calls to ensure we
    pick up all devices even if unsolicited notifications are missed.
    """
    loop = asyncio.get_running_loop()
    deadline = loop.time() + timeout
    while len(devices_by_name) < count:
        if loop.time() > deadline:
            raise TimeoutError(
                f"Timed out waiting for {count} devices "
                f"(got {len(devices_by_name)}: {list(devices_by_name.keys())})"
            )
        # Explicitly request device list to pick up any devices we missed
        await client._request_device_list()  # noqa: SLF001
        await asyncio.sleep(0.5)


# ─── Tests ────────────────────────────────────────────────────────────────────


async def test_core_protocol() -> None:
    """Connect, scan, send all output command types, stop devices.

    The harness polls its ValidateDeviceCommand steps until the client's
    OutputCmd messages produce the expected hardware write log entries.
    """
    port = HARNESS_PORT_BASE
    harness = HarnessProcess("core_protocol", port, 10000)

    client = ButtplugClient("Python Conformance Test")
    client.on_server_disconnect = lambda: None

    # Capture device references from on_device_added — the harness may
    # execute RemoveDevice before client.devices can be queried later.
    devices_by_name: dict[str, ButtplugDevice] = {}

    def on_device_added(device: ButtplugDevice) -> None:
        devices_by_name[device.name] = device

    client.on_device_added = on_device_added

    await connect_with_retry(client, f"ws://127.0.0.1:{port}")
    await client.start_scanning()
    await wait_for_devices(client, 3, devices_by_name)

    vibrator = devices_by_name["Conformance Test Vibrator"]
    positioner = devices_by_name["Conformance Test Positioner"]
    multi = devices_by_name["Conformance Test Multi"]

    # Device 0: Vibrate feature 0, Vibrate feature 1, Rotate feature 2
    await vibrator.features[0].run_output(DeviceOutputCommand(OutputType.VIBRATE, 0.5))
    await vibrator.features[1].run_output(DeviceOutputCommand(OutputType.VIBRATE, 0.75))
    await vibrator.features[2].run_output(DeviceOutputCommand(OutputType.ROTATE, 0.5))

    # Device 1: Oscillate feature 2, Position feature 0
    await positioner.features[2].run_output(DeviceOutputCommand(OutputType.OSCILLATE, 0.5))
    await positioner.features[0].run_output(DeviceOutputCommand(OutputType.POSITION, 0.5))

    # Device 2: Constrict, Spray, Temperature, Led
    await multi.features[0].run_output(DeviceOutputCommand(OutputType.CONSTRICT, 0.5))
    await multi.features[1].run_output(DeviceOutputCommand(OutputType.SPRAY, 0.5))
    await multi.features[2].run_output(DeviceOutputCommand(OutputType.TEMPERATURE, 0.5))
    await multi.features[3].run_output(DeviceOutputCommand(OutputType.LED, 0.5))

    # Stop — satisfies "Stop Single Device" and "Stop All Devices" steps
    await vibrator.stop()
    await client.stop_all_devices()

    report = await harness.wait_for_report()
    result = report.sequences[0]
    log_sequence(result)
    assert result.passed, f"core_protocol failed: {[s for s in result.steps if not s.passed]}"


async def test_error_handling() -> None:
    """Connect, scan, then send valid OutputCmds.

    The error-causing commands (invalid device/feature indices) are
    SendClientMessage side effects that are skipped in client-driven mode.
    The Custom validators just check that the server is still connected.
    """
    port = HARNESS_PORT_BASE + 1
    harness = HarnessProcess("error_handling", port, 10000)

    client = ButtplugClient("Python Conformance Test")
    client.on_server_disconnect = lambda: None

    # Set up callback before scanning to capture all devices
    error_devices: dict[str, ButtplugDevice] = {}

    def on_device_added(device: ButtplugDevice) -> None:
        error_devices[device.name] = device

    client.on_device_added = on_device_added

    await connect_with_retry(client, f"ws://127.0.0.1:{port}")
    await client.start_scanning()
    await wait_for_devices(client, 3, error_devices)

    # Send valid OutputCmds — the harness polls ValidateDeviceCommand steps
    vibrator = next(d for d in error_devices.values() if "Vibrator" in d.name)
    await vibrator.features[0].run_output(DeviceOutputCommand(OutputType.VIBRATE, 0.5))
    await vibrator.features[2].run_output(DeviceOutputCommand(OutputType.ROTATE, 0.75))

    report = await harness.wait_for_report()
    result = report.sequences[0]
    log_sequence(result)
    assert result.passed, f"error_handling failed: {[s for s in result.steps if not s.passed]}"
