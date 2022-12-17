import pymacnet
import pymacnet.maccorspoofer
import pymacnet.messages

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

def test_read_status():
    '''
    Test to make sure the interface can read the status.
    '''
    maccor_spoofer = pymacnet.maccorspoofer.MaccorSpoofer(MACCOR_SPOOFER_CONFIG)
    maccor_interfrace = pymacnet.MaccorInterface(MACCORINTERFACE_CONFIG)

    maccor_spoofer.start()
    maccor_interfrace.create_connection()
    
    response = maccor_interfrace.read_status()

    key = pymacnet.messages.rx_read_status_msg
    key['result']['Chan'] = MACCORINTERFACE_CONFIG['channel']
    assert(response == key['result'])

    response = maccor_interfrace.read_status()

    #del maccor_interfrace
    maccor_spoofer.stop()