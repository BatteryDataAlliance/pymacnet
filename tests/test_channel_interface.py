import copy
import pytest
import pymacnet
import pymacnet.maccorspoofer
import pymacnet.messages

# Create Maccor Spoofer server
MACCOR_SPOOFER_CONFIG = {"server_ip": "127.0.0.1",
                         "json_port": 5690, 
                         "tcp_port": 5691, 
                         "num_channels": 128}

# Create the interface we will use for testing.
CHANNEL_INTERFACE_CONIFG = {
    'server_ip': MACCOR_SPOOFER_CONFIG['server_ip'],
    'json_msg_port': MACCOR_SPOOFER_CONFIG['json_port'],
    'bin_msg_port': MACCOR_SPOOFER_CONFIG['tcp_port'],
    'msg_buffer_size_bytes': 4096,
    'channel': 5,
    'test_name': 'pymacnet_procedure_control',
    'test_procedure': 'test_procedure_1',
    'c_rate_ah': 1,
    'v_max_safety_limit_v': 4.2,
    'v_min_safety_limit_v': 2.9,
    'i_max_safety_limit_a': 2.0,
    'i_min_safety_limit_a': -2.0,
    'v_max_v': 4.2,
    'v_min_v': 3.0,
    'data_record_time_s': 1,
    'data_record_voltage_delta_vbys': 1,
    'data_record_current_delta_abys': 1,
}


def test_messages_basic():
    """
    Send basic messages to the MaccorSpoofer and make sure we get the correct results.
    """
    maccor_spoofer = pymacnet.maccorspoofer.MaccorSpoofer(
        MACCOR_SPOOFER_CONFIG)
    maccor_spoofer.start()

    channel_interface = pymacnet.ChannelInterface(CHANNEL_INTERFACE_CONIFG)

    # Read Status
    response = channel_interface.read_channel_status()
    ans_key = copy.deepcopy(pymacnet.messages.rx_read_status_msg)
    ans_key['result']['Chan'] = CHANNEL_INTERFACE_CONIFG['channel']
    assert (response == ans_key['result'])

    # Read Aux
    response = channel_interface.read_aux()
    ans_key = copy.deepcopy(pymacnet.messages.rx_read_aux_msg)
    ans_key['result']['Chan'] = CHANNEL_INTERFACE_CONIFG['channel']
    assert (response == ans_key['result']['AuxValues'])

    # Read reset channel message
    response = channel_interface.reset_channel()
    assert (response)

    # Set channel variable
    response = channel_interface.set_channel_variable()
    assert (response)

    # Start test with procedure
    response = channel_interface.start_test_with_procedure()
    assert (response)

    # Start test with direct control
    response = channel_interface.start_test_with_direct_control()
    assert (response)

    # Set direct control output. Rest
    response = channel_interface.set_direct_mode_output(
        current_a=0, voltage_v=4.2)
    assert (response)

    # Set direct control output. Charge CCCV
    response = channel_interface.set_direct_mode_output(
        current_a=0.5, voltage_v=4.2)
    assert (response)

    # Set direct control output. Charge CC
    response = channel_interface.set_direct_mode_output(current_a=0.5)
    assert (response)

    # Set direct control output. Discharge
    response = channel_interface.set_direct_mode_output(current_a=-2.0)
    assert (response)

    maccor_spoofer.stop()


def test_no_server():
    """
    Test that failing to connect rasies an assertion error
    """
    with pytest.raises(AssertionError):
        pymacnet.ChannelInterface(CHANNEL_INTERFACE_CONIFG)


def test_bad_config():
    """
    Test that passing an invalid config raises an assertion error
    """
    bad_config = {'channel': 1}
    with pytest.raises(AssertionError):
        pymacnet.ChannelInterface(bad_config)
