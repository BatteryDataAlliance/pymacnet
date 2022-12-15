'''
Example of how to read Maccor status
'''
import pymacnet 
import time
import sys
import pymacnet.maccorspoofer

# Create Maccor Spoofer server
CONFIG_DICT = { "server_ip": "127.0.0.1", "server_port": 5556 } # IP and Port

# Create the interface we will use for testing.
MACCORINTERFACE_CONFIG = { 
    'channel':1,
    'test_name':'pymacnet_procedure_control',
    'test_procedure':'test_procedure_1',
    'c_rate_ah':1,
    'v_max_safety_limit_v':4.2,
    'v_min_safety_limit_v':3.0,
    'i_max_safety_limit_a':2.0,
    'i_min_safety_limit_a':-2.0,
    'server_ip':'127.0.0.1',
    'json_server_port':5556,
    'tcp_server_port':5556
}

spoofer_server = pymacnet.maccorspoofer.MaccorSpoofer(CONFIG_DICT)
spoofer_server.start()

time.sleep(4)

maccor_interfrace = pymacnet.MaccorInterface(MACCORINTERFACE_CONFIG)
if not maccor_interfrace.create_connection():
    sys.exit("failed to create connection!")

time.sleep(2)

for i in range(0,1):
    print(i)
    maccor_interfrace.read_status()
    print(i)
    time.sleep(0.5)

spoofer_server.stop()