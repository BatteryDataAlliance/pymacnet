import pymacnet
import pymacnet.maccorspoofer
import pymacnet.messages

# Create Maccor Spoofer server
MACCOR_SPOOFER_CONFIG = { "server_ip": "127.0.0.1", "json_port": 5555, "tcp_port": 5556 }

# Create the interface we will use for testing.
MACCORINTERFACE_CONFIG = { 
    'channel':5,
    'test_name':'pymacnet_procedure_control',
    'test_procedure':'test_procedure_1',
    'c_rate_ah':1,
    'v_max_safety_limit_v':4.2,
    'v_min_safety_limit_v':2.9,
    'i_max_safety_limit_a':2.0,
    'i_min_safety_limit_a':-2.0,
    'server_ip':'127.0.0.1',
    'json_server_port':5555,
    'tcp_server_port':5556
}

def test_messages_basic():
    '''
    Send basic messages to the MaccorSpoofer and make sure we get the correct results.
    '''

    maccor_spoofer = pymacnet.maccorspoofer.MaccorSpoofer(MACCOR_SPOOFER_CONFIG)
    maccor_interfrace = pymacnet.MaccorInterface(MACCORINTERFACE_CONFIG)

    maccor_spoofer.start()
    maccor_interfrace.create_connection()
    
    # Read Status
    response = maccor_interfrace.read_status()
    key = pymacnet.messages.rx_read_status_msg
    key['result']['Chan'] = MACCORINTERFACE_CONFIG['channel']
    assert(response == key['result'])

    # Read Aux
    response = maccor_interfrace.read_aux()
    key = pymacnet.messages.rx_read_aux_msg
    key['result']['Chan'] = MACCORINTERFACE_CONFIG['channel']
    assert(response == key['result']['AuxValues'])

    # Read reset channel message
    response = maccor_interfrace._reset_channel()
    assert(response)

    # Set channel safety limits
    response = maccor_interfrace._set_channel_safety_limits()
    assert(response)

    # Set channel variable
    response = maccor_interfrace.set_channel_variable()
    assert(response)

    maccor_spoofer.stop()
    