# DEPRECATION (at some point) WARNING

This project will be deprecated and archived at some point in the future (still not sure when that
is), with the Python implementation of buttplug moving to an FFI layer on top of buttplug-rs. Bugs
are currently being triaged from this library to buttplug-rs-ffi.

The new project will be at

[https://github.com/buttplugio/buttplug-rs-ffi/](https://github.com/buttplugio/buttplug-rs-ffi/)

The API will change, though minimally (mostly connection in methods), and we will most likely still
distribute the pypi package under the same name ("buttplug").

You may continue to use this repo for the time being (so far it's been a year and I've gotten
nowhere on that upgrade, and this library still works fine!), just wanted everyone to be aware of
the changes happening in the near future.

# buttplug-py

[![PyPi version](https://img.shields.io/pypi/v/buttplug)](http://pypi.org/project/buttplug)
[![Python version](https://img.shields.io/pypi/pyversions/buttplug)](http://pypi.org/project/buttplug)

[![Patreon donate button](https://img.shields.io/badge/patreon-donate-yellow.svg)](https://www.patreon.com/qdot)
[![Discord](https://img.shields.io/discord/353303527587708932.svg?logo=discord)](https://discord.buttplug.io)
[![Twitter](https://img.shields.io/twitter/follow/buttplugio.svg?style=social&logo=twitter)](https://twitter.com/buttplugio)

Buttplug-py is a python implementation of the Core and Client portions of the Buttplug Sex Toy
Control Protocol. It allows users to write applications that can connect to Buttplug Servers, such
as the [Intiface Desktop Application](https://github.com/intiface/intiface-desktop) or [Intiface Rust CLI](https://github.com/intiface/intiface-cli-rs).

For more information on the Buttplug project, check out the project website at
[https://buttplug.io](https://buttplug.io).

## Table Of Contents

- [Support The Project](#support-the-project)
- [Documentation](#documentation)
- [Examples](#examples)
- [License](#license)

## Support The Project

If you find this project helpful, you can [support us via Patreon](http://patreon.com/qdot) or
[Github Sponsors](http://github.com/sponsors/qdot)! Every donation helps us afford more hardware to
reverse, document, and write code for!

## Documentation

Library and API Documentation for buttplug-py is available at

https://buttplug-py.docs.buttplug.io

Other recommended reading includes

- [The Buttplug Protocol Spec](https://buttplug-spec.docs.buttplug.io)
- [The Buttplug Developer Guide](https://buttplug-developer-guide.docs.buttplug.io)

## Examples

Example code is available in the examples/ directory. Examples are heavily commented to hopefully
make usage of the library clearer.

## License

Buttplug is BSD 3-Clause licensed. More information is available in the LICENSE file.
