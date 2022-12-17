'''
Example of how to read Maccor status
'''
import pymacnet 
import time
import sys
import pymacnet.maccorspoofer

# Create Maccor Spoofer server
MACCOR_SPOOFER_CONFIG = { "server_ip": "127.0.0.1", "json_port": 5555, "tcp_port": 5556 }

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
    'json_server_port':5555,
    'tcp_server_port':5556
}

maccor_spoofer = pymacnet.maccorspoofer.MaccorSpoofer(MACCOR_SPOOFER_CONFIG)
maccor_spoofer.start()

maccor_interfrace = pymacnet.MaccorInterface(MACCORINTERFACE_CONFIG)
if not maccor_interfrace.create_connection():
    sys.exit("failed to create connection!")

for i in range(0,5):
    print(i)
    print(maccor_interfrace.read_status())
    print(i)
    time.sleep(0.5)

response = maccor_interfrace.read_status()
print(response)

#del maccor_interfrace
maccor_spoofer.stop()