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
    'v_max_v':4.2,
    'v_min_v':3.0,
    'data_record_time_s':1,
    'data_record_voltage_delta_vbys':1,
    'data_record_current_delta_abys':1,
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
    start_success = maccor_interfrace.start()
    assert(start_success)
    
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
    response = maccor_interfrace.reset_channel()
    assert(response)

    # Set channel safety limits
    response = maccor_interfrace._set_channel_safety_limits()
    assert(response)

    # Set channel variable
    response = maccor_interfrace.set_channel_variable()
    assert(response)

    # Start test with procedure
    response = maccor_interfrace.start_test_with_procedure
    assert(response)

    # Start test with direct control
    response = maccor_interfrace.start_test_with_direct_control
    assert(response)

    # Set direct control output. Rest
    response = maccor_interfrace.set_direct_mode_output( current_a = 0, voltage_v = 4.2)
    assert(response)

    # Set direct control output. Charge CCCV
    response = maccor_interfrace.set_direct_mode_output( current_a = 0.5, voltage_v = 4.2)
    assert(response)

    # Set direct control output. Charge CC
    response = maccor_interfrace.set_direct_mode_output( current_a = 0.5)
    assert(response)

    # Set direct control output. Discharge
    response = maccor_interfrace.set_direct_mode_output( current_a = -2.0)
    assert(response)

    maccor_spoofer.stop()

def test_no_server():
    '''
    Try to start MaccorInterface without a server running.
    '''
    maccor_interfrace = pymacnet.MaccorInterface(MACCORINTERFACE_CONFIG)
    start_success = maccor_interfrace.start()
    assert(not start_success)

def test_bad_config():
    '''
    Try to run with an incomplete config.
    '''
    
    bad_config = {'channel':1}
    maccor_spoofer = pymacnet.maccorspoofer.MaccorSpoofer(MACCOR_SPOOFER_CONFIG)
    maccor_interfrace = pymacnet.MaccorInterface(bad_config)

    maccor_spoofer.start()
    start_success = maccor_interfrace.start()
    assert(not start_success)

def test_illegal_sends():
    '''
    Try to send messages without existing server connections
    '''
    
    maccor_interfrace = pymacnet.MaccorInterface(MACCORINTERFACE_CONFIG)

    response = maccor_interfrace.read_status()
    assert(not response)

    response = maccor_interfrace.read_aux()
    assert(not response)

    response = maccor_interfrace.reset_channel()
    assert(not response)

    response = maccor_interfrace._set_channel_safety_limits()
    assert(not response)

    response = maccor_interfrace.set_channel_variable()
    assert(not response)

    response = maccor_interfrace.start_test_with_procedure()
    assert(not response)

    response = maccor_interfrace.start_test_with_direct_control()
    assert(not response)

    response = maccor_interfrace.set_direct_mode_output( current_a = 0.5, voltage_v = 4.2)
    assert(not response)

    # Try rest.
    response = maccor_interfrace.set_direct_mode_output( current_a = 0)
    assert(not response)