# pycmanet

`pymacnet` is a Python module that provides a channel level interface for communication and control of [Maccor cyclers](http://www.maccor.com/) via MacNet. MacNet is an interface provided by Maccor that allows for controlling their cyclers via UDP/IP and TCP/IP. `pymacnet` provides a hassle-free way to utilize MacNet with a simple python class.

### Overview

- [Motivation](#Motivation)
- [Installation](#Installation)
    - [Requirements](#Requirements)
    - [Source Installation](#source-installation)
- [Examples](#Examples)
  - [Getting Started](#getting-started)
    - [Configuration](#Configuration)
  - [Getting Channel Readings](#getting-channel-readings) 
  - [Starting a Test](#starting-a-test)
  - [Setting Variables](#setting-variables)
  - [Direct Control](#direct-control)
- [Development](#Dev)
  - [Contributing](#Contributing)
  - [Testing](#Testing)
    - [MaccorSpoofer](#Spoofer)
  - [Documentation](#Documentation)
- [License](#License)

# <a name="Motivation"></a>Motivation

Why bother using `pymacnet`? This package enables a wide variety of applications such as:

- Real-time data logging and reporting

`pymacnet` can be used to passively monitor running tests and log readings directly to a database, bypassing the need to manually export data. Moreover, it's possible to create automated alerts based on incoming real-time data. For example, if a test were to fault or temperature were to exceed a set threshold. While Maccor already has a built-in notification system with MacNotify `pymacnet` provides a more flexible and customizable solution without having to directly modify test procedures. 

- Automated test management

The GUI provided by Maccor for test management is straight forward and easy to use, but requires significant manual work. With `pymacnet` it's possible to write programs to automatically start tests simultaneously across many channels (or even many cyclers) at once.

- Testing of next generation closed-loop charging methods

While conventional constant-current followed by constant-voltage (CCCV) charging has been the industry standard for many years and is well supported by cyclers, there is movement towards advanced [closed-loop control charging techniques that provide improved battery life and decreased charge times](https://battgenie.life/technology/). `pymacnet` enables testing of closed-loop battery charging methods by providing an interface between software hosting battery charging algorithms and active Maccor tests, allowing the charge current to be dynamically set.

- Well tested, easy to use, community supported interface in the most popular programming language. 

It is entirely possible to write one's own MacNet wrapper, but `pymacnet` provides a well-tested ready to use package that takes care of lower level communication, providing a simple yet powerful interface in the most popular programming language. 

# <a name="Installation"></a>Installation

## <a name="Requirements"></a>Requirements

`pymacnet` requires only Python 3 and packages from the standard library. It has been tested on on Windows, Mac, and Debian operating systems.

## <a name="Source Installation"></a>Source Installation

To install from source clone [this repository](https://github.com/BattGenie/pymacnet), navigate into the directory, and type the following into the command line:

```
pip install .
```

# <a name="Examples"></a>Examples

This section goes over various of examples of how to use `pymacnet` to do such tasks as getting channel readings, starting a test, and even controlling a channel directly without a test procedure. For interactive examples see the `demo.ipynb` notebook in the repository. 

## <a name="Getting Started"></a>Getting Started

`pymacnet` provides a class `MaccorInterface` that communicates with the Maccor cycler via MacNet. Each class instance targets a specific channel of the cycler and requires a configuration dictionary with the following fields:

### <a name="Configuration"></a>Configuration

- `channel` - The channel to be targeted for all operations.
- `test_name` - The test name to be used for any tests started. If left blank, Maccor will generate a unique random name for any started tests. Note that Maccor requires unique test names for each test.
- `test_procedure` - The test procedure to be used, if starting a test with a procedure. Not needed with direct control.
- `c_rate_ah` - The capacity value to be referenced when setting "C" values within the Maccor schedule. Units of amp-hours. Ignored if not used anywhere in the test.
- `v_max_safety_limit_v` - Upper voltage safety limit for the channel. Units of volts.
- `v_min_safety_limit_v` - Lower voltage safety limit for the channel. Units of volts.
- `i_max_safety_limit_a` - Upper current safety limit for the channel. Units of amps.
- `i_min_safety_limit_a` - Lower current safety limit for the channel. Units of amps.
- `v_max_v` - Upper voltage limit used for charge/CV limits. Units of volts. Only used with direct control.
- `v_min_v` - Lower voltage limit used for discharge limit. Units of volts. Only used with direct control.
- `data_record_time_s` - How often data points are taken during direct control tests. Zero turns off. Used only for direct control.
- `data_record_voltage_delta_vbys` - The dV/dt at which data points are taken during direct control tests. Zero disables. Used only for direct control.
- `data_record_current_delta_abys` - The dI/dt at which data points are taken during direct control tests. Zero disables. Used only for direct control.
- `server_ip` - The IP address of the Maccor server. Use 127.0.0.1 if running on the same machine as the server.
- `json_server_port` - The port to communicate through with JSON commands. Default set to 57570.
- `tcp_server_port` - The port to communicate through with TCP commands. Default set to 57560.

## <a name="Readings"></a>Getting Channel Readings

Below is example code for reading channel status (which includes voltage, current, etc.) from channel 75 on a Maccor cycler with IP address 3.3.31.83.

```python
import time
import sys
import pymacnet 

config = {
    "channel": 75,
    "test_name": "",
    "c_rate_ah": 1,
    "v_max_v": 4.2,
    "v_min_v": 3.0,
    "v_max_safety_limit_v": 4.25,
    "v_min_safety_limit_v": 2.9,
    "i_max_safety_limit_a": 3.0,
    "i_min_safety_limit_a": 3.0,
    "data_record_time_s": 0.05,
    "data_record_voltage_delta_vbys": 0.0,
    "data_record_current_delta_abys": 0.0,
    "test_procedure": "test_procedure_1",
    "server_ip": "3.3.31.83",
    "json_server_port": 57570,
    "tcp_server_port": 57560,
    "msg_buffer_size_bytes": 1024
}
    
maccor_interface = pymacnet.MaccorInterface(config)
if not maccor_interface.start():
    sys.exit("failed to create connection!")

status_reading = maccor_interface.read_status()
print(status_reading)
```

Example output:

```
{'FClass': 4, 'FNum': 7, 'Chan': 1, 'RF1': 0, 'RF2': 192, 'Stat': 0, 'LastRecNum': 4225, 'Cycle': 0, 'Step': 5, 'TestTime': 2.0, 'StepTime': 1.0, 'Capacity': 0, 'Energy': 0, 'Current': 0, 'Voltage': 3.85, 'TesterTime': '2022-10-13T12:32:56'}
```

## <a name="Test"></a>Starting a Test

Here is in example of how to start a test named "simple_test_1" on channel 75 with an existing test procedure named "test_procedure_1". Note the safety limits defined in the config will be set on the channel before starting the test. Also, test names must be unique. If a non-unique test name is provided then the test will not start. If no test name is provided then a unique random test name is generated. 

```python
import pymacnet
import sys

config = {
    "channel": 75,
    "test_name": "simple_test_1",
    "c_rate_ah": 1,
    "v_max_v": 4.2,
    "v_min_v": 3.0,
    "v_max_safety_limit_v": 4.25,
    "v_min_safety_limit_v": 2.9,
    "i_max_safety_limit_a": 3.0,
    "i_min_safety_limit_a": 3.0,
    "data_record_time_s": 0.05,
    "data_record_voltage_delta_vbys": 0.0,
    "data_record_current_delta_abys": 0.0,
    "test_procedure": "test_procedure_1",
    "server_ip": "3.3.31.83",
    "json_server_port": 57570,
    "tcp_server_port": 57560,
    "msg_buffer_size_bytes": 1024
}
maccor_interface = pymacnet.MaccorInterface(config_dict)
if not maccor_interface.start():
    sys.exit("failed to create connection!")

if maccor_interface.start_test_with_procedure():
    print("Test started!")
```

## <a name="Variables"></a>Setting Variables

Here is an example of how to set VAR1 to 0.01 on a test running on channel 75.

```python
import pymacnet
import sys

config = {
    "channel": 75,
    "test_name": "",
    "c_rate_ah": 1,
    "v_max_v": 4.2,
    "v_min_v": 3.0,
    "v_max_safety_limit_v": 4.25,
    "v_min_safety_limit_v": 2.9,
    "i_max_safety_limit_a": 3.0,
    "i_min_safety_limit_a": 3.0,
    "data_record_time_s": 0.05,
    "data_record_voltage_delta_vbys": 0.0,
    "data_record_current_delta_abys": 0.0,
    "test_procedure": "test_procedure_1",
    "server_ip": "3.3.31.83",
    "json_server_port": 57570,
    "tcp_server_port": 57560,
    "msg_buffer_size_bytes": 1024
}

maccor_interface = pymacnet.MaccorInterface(config_dict)
if not maccor_interface.start():
    sys.exit("failed to create connection!")

maccor_interface.set_channel_variable(var_num = 1, var_value = 0.01)
```

## <a name="Direct"></a>Direct Control

Here is an example of how to bypass using a test procedure all together and control the channel directly using direct control.  Note the channel safety limits will be set before the test is started. **WARNING DIRECT CONTROL IS POTENTIALLY DANGEROUS. BE CAREFUL AND MAKE SURE YOU UNDERSTAND EXACTLY WHAT YOUR CODE IS DOING.**

```python
import pymacnet
import sys

config = {
    "channel": 75,
    "test_name": "",
    "c_rate_ah": 1,
    "v_max_v": 4.2,
    "v_min_v": 3.0,
    "v_max_safety_limit_v": 4.25,
    "v_min_safety_limit_v": 2.9,
    "i_max_safety_limit_a": 3.0,
    "i_min_safety_limit_a": 3.0,
    "data_record_time_s": 0.05,
    "data_record_voltage_delta_vbys": 0.0,
    "data_record_current_delta_abys": 0.0,
    "test_procedure": "test_procedure_1",
    "server_ip": "3.3.31.83",
    "json_server_port": 57570,
    "tcp_server_port": 57560,
    "msg_buffer_size_bytes": 1024
}

maccor_interface = pymacnet.MaccorInterface(config_dict)
if not maccor_interface.start():
    sys.exit("failed to create connection!")

if maccor_interface.start_test_with_direct_control():
    print("Test started!")
else:
    sys.exit("Failed to start test!")

time.sleep(1) # Must wait at least 100 ms between trying to set contro

# Discharge at 200 mA for 5 seconds. 
maccor_interface.set_direct_mode_output(current_a = -0.200)
time.sleep(5)

# Rest for 5 seconds
maccor_interface.set_direct_mode_output(current_a = 0)
time.sleep(5) 

# Charge at 200 mA for 5 seconds
maccor_interface.set_direct_mode_output(current_a = 0.200)
time.sleep(5)

maccor_interface.set_direct_mode_output(current_a = 0.0)
time.sleep(1)
```

# <a name="Dev"></a>Development

This section contains various information to help developers further extend and test `pymacnet`

## <a name="Contributing"></a>Contributing

As it exists now, `pymacnet` only implements a fraction of the messages supported by MacNet. Further work can be done to expand `pymacnet` to include more of the messages detailed in the MacNet documentation `docs/macnet_from_maccor_help.pdf`.
s
We welcome your help in expanding `pymacnet`! Please see the CONTRIBUTING.md file in this repository for contribution guideliens. 

## <a name="Testing"></a>Testing

To run the tests navigate to the "tests" directory and type type the following:

```
pytest .
```

### <a name="Spoofer"></a>MaccorSpoofer

Testing software on a real cycler is dangerous so we've created a submodule `maccorspoofer` to emulate some of the behavior of the Maccor software with a class `MaccorSpoofer`. This class creates TCP and UDP servers and accepts connections from n number of clients. The `MaccorSpoofer` does not perfectly emulate a Maccor cycler (for example, it does not track if a test is already running on a channel) and merely checks that the message format is correct and responds with standard message. This could be expanded in the future as needed.

## <a name="Documentation"></a>Documentation

All documentation was generated with [pydoc](https://docs.python.org/3/library/pydoc.html). To re-generate the documentation type the following command from the top level directory of the repository:

```
pdoc --html .
```

# <a name="License"></a>License

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
