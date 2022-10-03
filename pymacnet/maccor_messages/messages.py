read_status_msg = {
    'jsonrpc': '2.0', 
    'method': 'MacNet', 
    'params':
    {
        'FClass': 4, 
        'FNum': 7,
        'Chan': -1
    },
    'id': 1987 
}
'''
(4, 7) All status and readings of one channel
The status and readings of “Chan” channel will be returned.
'''

start_test_with_procedure_msg = {
    "jsonrpc": "2.0",
    "method": "MacNet", 
    "params":
    {
        "FClass": 6,
        "FNum": 2,
        "Chan": 3,
        "TestName": "Random", 
        "ProcName": "Procedure Name", 
        "Comment": "Test comment", 
        "Crate": 1,
        "ChamberNum": 0, 
        "StartCycle": 0, 
        "TotCycles": 0, 
        "Mass": 1, 
        "VGain": 0, 
        "AbsTRepAlign": 0, 
        "ParallelR": 0, 
        "VDivHiR": 0, 
        "VDivLoR": 0, 
        "CANpos": -1, 
        "CANprof": "", 
        "RegimeName": ""
    },
    "id": 1987
}
'''
(6, 2) Start test with direct control

Selects the test channel to be started. The test name and procedure name can be up to 250 characters long.
Also, do not select the channel in advance of starting the test. The JSON Start test command will both select and 
start the channel. If, however, multiple channels should be started with the same test, do first select the channels,
then start the test using 65535, meaning "all selected".

Paramters as follows:

TestName
    Up to 25 ascii characters for the data file name. “Random” will generate a pseudo-random name. 
    The field is fixed in length, so remaining characters should be space characters.
ProcName
    Up to 25 ascii characters for the test procedure name. The test procedure must exist in the 
    C:\Maccor\Procedur folder and the “.000” should not be part of the name. The field is fixed in length, 
    so remaining characters should be space characters.
Comment
    Up to 80 characters for the test comment. The field is fixed in length, so remaining characters should be space characters.
Crate
    C-rate. If C-rate is not used, enter 1
ChamberNum
    Environmental chamber number. If the environmental chamber is not used, enter 0.
StartCycle
    Default: 0; See Start Test Setup for further details
TotCycles
    Default: 0; See Start Test Setup for further details
Mass
    Default: 1; See Start Test Setup for further details
VGain
    Default: 0; Used to change the gain of the constant voltage feedback loop. Only use it after consulting Customer Service.
        0: Gain x1 1: Gain x2 2: Gain x4 3: Gain x8 4: Gain /1 5: Gain /2 6: Gain /4 7: Gain /8
AbsTRepAlign
    Default: 0; 1: Use absolute time report alignment. See Start Test Setup for further details
ParallelR
    See Start Test Setup for further details
VDivHiR
    See Start Test Setup for further details
VDivLoR
    See Start Test Setup for further details
'''

start_test_with_direct_control_msg = {
    "jsonrpc": "2.0", 
    "method": "MacNet", 
    "params":
    {
        "FClass": 6,
        "FNum": 7,
        "Chan": 3,
        "TestName": "Random", 
        "Current": 0.0,
        "Voltage": 5.0, 
        "Power": 50, 
        "Resistance": 0, 
        "CurrentRange": 1, 
        "ChMode": 'D', 
        "DataTime": 1.0, 
        "DataV": 0, 
        "DataI": 0
    },
    "id": 1987 
}
'''
(6, 7) Start direct mode

Start direct mode. Initializes direct remote control of the test channel with the 
following data in the “Data” area. The channel will output this current, voltage 
and power - mutually limiting as standard - until the values are changed with the 
“(6, 8) Set direct output” command described below or stopped.

A watchdog timer can be activated in the Misc_Options section of the System.ini file. Setting the 
MacNetDirectModeWD to a value higher than 0 will cause a channel under direct mode to suspend if it 
has not been updated within the specified number of seconds.

Parameters are a follows

testName
    Up to 25 ascii characters for the data file name. “Random” (Case sensitive) will 
    generate a pseudo-random name. The field is fixed in length, so remaining characters should be space characters.
Current
    Amps. Mutually limiting. Set outside range to ignore. 0 is within range. 
    Must be active to function in (6, 8) Set direct mode output.
Voltage
    Voltage. Mutually limiting. Set outside range to ignore. 0 is within range. 
    Must be active to function in (6, 8) Set direct mode output.
Power   
    Watts. Mutually limiting. Set outside range to ignore. 0 is within range. 
    Must be active to function in (6, 8) Set direct mode output.
Resistance 
    Ohms. Mutually limiting. Set to 0 to ignore. 
    Must be active to function in (6, 8) Set direct mode output.
Current range
    The desired current range: 1, 2, 3, 4
Charge mode
    67 i.e. 'C' for charge, 68 i.e. 'D' for discharge and 82 i.e. 'R' for rest
Data record time
    Time increment between data records in the data file. Enter 0 for no data.
Data record voltage
    Voltage increment to generate a data record in the data file. Enter 0 to disable.
Data record current
    Current increment to generate a data record in the data file. Enter 0 to disable.
'''

set_direct_output_msg = {
    "jsonrpc": "2.0", 
    "method": "MacNet", 
    "params":
    {
        "FClass": 6, 
        "FNum": 8, 
        "Chan": 3, 
        "Current": 0.0, 
        "Voltage": 65536, 
        "Power": 65536, 
        "Resistance": 0, 
        "CurrentRange": 4, 
        "ChMode": "C"
    },
    "id": 1987 
}
'''
(6, 8) Set direct mode output

Set direct output. When a channel has been started in direct mode, the output can be set with this 
command and these arguments:

Parameters as follows:
    Current
        Amps. Mutually limiting. Set outside range to ignore. 0 is within range. 
        Must be active to function in (6, 8) Set direct mode output.
    Voltage
        Voltage. Mutually limiting. Set outside range to ignore. 0 is within range. 
        Must be active to function in (6, 8) Set direct mode output.
    Power   
        Watts. Mutually limiting. Set outside range to ignore. 0 is within range. 
        Must be active to function in (6, 8) Set direct mode output.
    Resistance 
        Ohms. Mutually limiting. Set to 0 to ignore. 
        Must be active to function in (6, 8) Set direct mode output.
    Current range
        The desired current range: 1, 2, 3, 4
    Charge mode
        67 i.e. 'C' for charge, 68 i.e. 'D' for discharge and 82 i.e. 'R' for rest

Response back results decode as follows:
    0: OK
    1: Illegal system type. This feature only works for type 0
    2: The channel is not active
    3: Command sent too fast. There must be at least 100 ms (10 ticks) between commands.
    4: Direct mode is not active.
    5: Direct mode is not ready yet.
'''

reset_channel_msg = {
    "jsonrpc": "2.0", 
    "method": "MacNet",
    "params":
    {
        "FClass": 6, 
        "FNum": 5, 
        "Chan": -1
    },
    "id": 1987 
}
'''
Reset “Chan” test channel.
'''

read_aux_msg = {
    "jsonrpc": "2.0", 
    "method": "MacNet", 
    "params":
    {
        "FClass": 4, 
        "FNum": 4, 
        "Chan": 1
    },
    "id": 1987 
}
'''
The the auxiliary values.
'''

set_safety_limits_msg = {
    "jsonrpc": "2.0", 
    "method": "MacNet", 
    "params":
    {
        "FClass": 6, 
        "FNum": 10, 
        "Chan": 3, 
        "VSafeMax": 4.5,
        "VSafeMin": 2.5,
        "ISafeChg": 4.3, 
        "ISafeDis": 2.5,
        "PBatSafeChg": 20,
        "PBatSafeDis": 20
    },
    "id": 1987
}
'''
Sets safety limits on a channel
'''