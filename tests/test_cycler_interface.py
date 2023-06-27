import copy
import pytest
import pymacnet
import pymacnet.maccorspoofer
import pymacnet.messages

# Create Maccor Spoofer server
MACCOR_SPOOFER_CONFIG = {"server_ip": "127.0.0.1",
                         "json_port": 7889, "tcp_port": 7890, "num_channels": 128}

# Create the interface we will use for testing.
CYCLER_INTERFACE_CONFIG = {
    'server_ip': MACCOR_SPOOFER_CONFIG['server_ip'],
    'json_msg_port': MACCOR_SPOOFER_CONFIG['json_port'],
    'bin_msg_port': MACCOR_SPOOFER_CONFIG['tcp_port'],
    'msg_buffer_size_bytes': 4096
}


def test_cycler_interface_messages():
    '''
    Test creating class instance
    '''
    maccor_spoofer = pymacnet.maccorspoofer.MaccorSpoofer(
        MACCOR_SPOOFER_CONFIG)
    maccor_spoofer.start()

    cycler_interface = pymacnet.CyclerInterface(CYCLER_INTERFACE_CONFIG)

    system_info = cycler_interface.read_system_info()
    assert (system_info == pymacnet.messages.rx_system_info_msg['result'])

    general_info = cycler_interface.read_general_info()
    assert (general_info == pymacnet.messages.rx_general_info_msg['result'])

    channel_statues = cycler_interface.read_all_channel_statuses()
    assert (channel_statues ==
            pymacnet.messages.rx_channel_status_multiple_channels['result']['Status'])

    maccor_spoofer.stop()