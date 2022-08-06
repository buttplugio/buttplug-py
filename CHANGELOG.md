# 0.3.0 (2022-08-06)

## Breaking Changes

- device_removed_handlers now correctly receive the removed ButtplugClientDevice rather than its integer id.

# 0.2.1 (2021-12-12)

## Bug Fixes

- Change print statements to logging calls so we don't interrupt other libraries.
- Update to websockets 10 for security issues.

# 0.2.0 (2020-05-10)

## Bug Fixes

- DeviceRemoved event no longer tries to use non-existent dict method
- Fixed wrong enum naming
- Client now actually sends client name

# 0.1.0 (2019-09-07)

## Features

- Add support for request logs/log handling
- Actually raise exceptions on errors
- Lots of documentation additions
- Adjust naming to match other libraries
  (ButtplugDeviceClient.allowed_messages) or python idioms (Exceptions
  end in Error)

# 0.0.2 (2019-09-05)

## Features

- Possibly the most minimal implementation of a Buttplug Client possible
- Supports the handshake/enumeration messages and the basic generic
  messages. That's it.
- Still needs documentation, rest of features, etc... but is very
  basically usable, assuming you are as committed to python 3.7 as I
  am.

# 0.0.1 (2019-04-13)

## Features

- Squatting the name on PyPi
- Get it?
- Squatting
- And the project is named buttplug
- Get it?
