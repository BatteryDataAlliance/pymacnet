# PyMacNet

A class based python interface for communication and control of Maccor cyclers over Macnet.

## Running

See `examples/` to see instances of how to use the code for various tasks. Note that the MaccorInterface class instance must receive a config dictionary on initialization. In the example code these are read from a JSON file:

The fields are as follows:

- `channel` -> The channel to be targeted for all operations.
- `test` -> The test name to be used for any tests started. If left blank, Maccor will generate a unique random name for any started tests. Note that Maccor requires unique test names for each test.
- `v_max_v` -> Upper voltage limit used for charge/CV limits. Units of volts. Only used with direct control.
- `v_min_v` -> Lower votage limit used for discharge limit. Units of volts. Only used with direct control.
- `v_max_safety_limit_v` -> Upper voltage safety limit for the channel. Units of volts.
- `v_min_safety_limit_v` -> Lower voltage safety limit for the channel. Units of volts.
- `i_max_safety_limit_v` -> Upper current safety limit for the channel. Units of amps.
- `i_min_safety_limit_v` -> Lower current safety limit for the channel. Units of amps.
- `data_record_time_s` -> How often data points are taken during direct control tests. Zero turns off.
- `data_record_voltage_delta` -> The dV/dt at which data points are taken during direct control tests. Zero disables.
- `data_record_current_delta` -> The dI/dt at which data points are taken during direct control tests. Zero disables.
- `test_procedure` -> The test procedure to be used, if starting a test with a procedure. Not needed with direct control.
- `server_ip` -> The IP address of the Maccor server.
- `server_port` -> The port to communicate through. Note this must be set to 57570 for JSON TCP/IP communication.
- `msg_buffer_size` -> Max buffer size for reading data back from Maccor server.

## Install

Navigate to the repo directory and run the following command:

```
pip install .
```

