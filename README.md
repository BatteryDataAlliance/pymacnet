`pymacnet` is a Python module that provides a channel level interface for communication and control of [Maccor cyclers](http://www.maccor.com/) via MacNet. MacNet is an interface provided by Maccor that allows for control of their cyclers via UDP/IP and TCP/IP. `pymacnet` provides hassle-free way to utilize MacNet with a simple python class.

Details on Macnet can be found in `docs/macnet_from_maccor_help.pdf`.

### Overview

- [Motivation](#Motivation)
- [Installation](#Installation)
    - [Requirements](#Requirements)
    - [Base Installation](#BaseInstall)
    - [Source Installation](#SourceInstall)
- [Examples](#Examples)
  - [Getting Started](#GettingStarted)
    - [Configuration](#Config)
  - [Getting Channel Readings](#Readings) 
  - [Starting a Test](#StartingTest)
  - [Setting Variables](#Impedance)
  - [Direct Control](#SingleCycle)
- [Development](#Characterization)
  - [MaccorSpoofer](#Spoofer)
  - [Expanding functionality](#Expanding)
  - [Testing](#Testing)
  - [Updating Docs](#Docs)
- [License](#License)

# <a name="Motivation"></a>Motivation

Why bother using `pymacnet`? The package enables an wide variety of applications such as:

- Real-time data logging and reporting

`pymacnet` can be used to passively monitor running tests and log readings directly to a database, bypassing the need for manually exporting data. Moreover, it's possible to create automated alerts based on incoming real-time data if, for example, a test were to fault or temperature were to exceed a set threshold. While Maccor already has a built-in notification system with MacNotify `pymacnet` provides a more flexible and customizable solution without having to directly modify the test procedure. 

- Automated test management

The GUI provided by Maccor for test management is straight forward and easy to use, but requires significant manual work. With `pymacnet` it's possible to write programs to automatically start tests simultaneously across many channels (or even many cyclers) at once.

- Testing of next generation closed-loop charging methods

While conventional constant-current followed by constant-voltage (CCCV) charging has been the industry for many years and is well supported by cyclers, there is movement towards advanced [closed-loop control charging techniques that provide improved battery life and decreased charge times](https://battgenie.life/technology/). `pymacnet` enables testing of closed-loop battery charging methods by providing an interface between software hosting battery charging algorithms and active Maccor tests, where the charge current can be set dynamically by setting test variables with `pymacnet`

- Well tested, easy to use, community supported interface in the most popular programming language. 

It is entirely possible to write one's own code for a MacNet interface, but `pymacnet` provides a well tested ready to use package that takes care of lower level communication, providing a simple yet powerful interface in the most popular programming language. 

# <a name="Installation"></a>Installation

## <a name="Requirements"></a>Requirements

`pymacnet` requires only Python 3.X+ packages from the standard library. It has been tested on on Windows, Mac, and Debian operating systems.

## <a name="BaseInstall"></a>Base Installation

To install directly from the Python Package Index (PyPI) simply open a command line interface and enter the following:

```
pip install pymacnet
```

## <a name="SourceInstall"></a>Source Installation


To install from source clone [the repository](https://github.com/BattGenie/pymacnet), navigate into the directory, and type type the following into the command line:

```
pip install .
```

# <a name="Examples"></a>Examples

Below are a series of examples of how to use `pymacnet`

## <a name="GettingStarted"></a>Getting Started

`pymacnet` provides a class `MaccorInterface` that communicates with the Maccor cycler via MacNet. Each instance of `MaccorInterface` interacts with a single channel of the target Maccor cycler as defined in the that instances configuration dictionary passed at instantiation. The configuration is a python dictionary containing various fields defined in the follow section: 

### <a name="Configuration"></a>Configuration

Each class instance requires a configuration dictionary on initiation  where the fields are as follows:

- `channel` -> The channel to be targeted for all operations.
- `test_name` -> The test name to be used for any tests started. If left blank, Maccor will generate a unique random name for any started tests. Note that Maccor requires unique test names for each test.
- `test_procedure` -> The test procedure to be used, if starting a test with a procedure. Not needed with direct control.
- `c_rate_ah` -> The capacity value to be referenced when setting "C" values within the Maccor schedule. Units of amp-hours. Ignored if not used anywhere in the test.
- `v_max_safety_limit_v` -> Upper voltage safety limit for the channel. Units of volts.
- `v_min_safety_limit_v` -> Lower voltage safety limit for the channel. Units of volts.
- `i_max_safety_limit_a` -> Upper current safety limit for the channel. Units of amps.
- `i_min_safety_limit_a` -> Lower current safety limit for the channel. Units of amps.
- `v_max_v` -> Upper voltage limit used for charge/CV limits. Units of volts. Only used with direct control.
- `v_min_v` -> Lower votage limit used for discharge limit. Units of volts. Only used with direct control.
- `data_record_time_s` -> How often data points are taken during direct control tests. Zero turns off. Used only for direct control.
- `data_record_voltage_delta_vbys` -> The dV/dt at which data points are taken during direct control tests. Zero disables. Used only for direct control.
- `data_record_current_delta_abys` -> The dI/dt at which data points are taken during direct control tests. Zero disables. Used only for direct control.
- `server_ip` -> The IP address of the Maccor server. Use 127.0.0.1 if running on the same machine as the server.
- `json_server_port` -> The port to communicate through with JSON commands. Default set to 57570.
- `tcp_server_port` -> The port to communicate through with TCP commands. Default set to 57560.

For examples of the `MaccorInterface` class in use see the `demo.ipynb` notebook. For detailed method documentation see the `docs` directory.

### <a name="CyclingCapacity"></a>Cycling Capacity Plots

## Installation

To install `pymacnet` clone this repo and within it type the following commands:

```
pip install -r requirements.txt
pip install . 
```


## Dev

### Docs 

To re-generate the documentation:

```
pdoc --html .
```

### Testing

From within the test directory: 

```
pytest . License
```

## <a name="License"></a>License

MIT License

Copyright (c) 2023 BattGenie Inc. 

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE
