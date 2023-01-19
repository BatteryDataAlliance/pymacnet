# pymacnet

`pymacnet` provides a channel level interface for communication and control of Maccor cyclers via MacNet. MacNet is an interface provided by Maccor that allows for control of their cyclers via UDP/IP and TCP/IP. `pymacnet` provides a way to utilize MacNet with simple python class. Details on Macnet can be found in `docs/macnet_from_maccor_help.pdf`.

For an overview of `pymacnet` functionality see the `demo.ipynb` notebook. For detailed function descriptions see the `docs/` directory.

## Installation

To install `pymacnet` clone this repo and within it type the following commands:

```
pip install requirements.txt
pip install . 
```

## How to use

`pymacnet` interfacts with the Maccor cycler through instances of individual `MaccorInterface` classes that target specific cycler channels. Each class instance requires a configuration dictionary on initiation  where the fields are as follows:

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

## Dev

### Docs 

To re-generate the documentation:

```
pdoc --html .
```

### Testing

From within the test directory: 

```
pytest .
```
