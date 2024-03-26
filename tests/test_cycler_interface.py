import time

import pymacnet
import pymacnet.messages
import pymacnet.maccorspoofer


# Create Maccor Spoofer server
MACCOR_SPOOFER_CONFIG = {"server_ip": "127.0.0.1",
                         "json_port": 5620,
                         "tcp_port": 5720,
                         "num_channels": 128}

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
    spoofer_config = MACCOR_SPOOFER_CONFIG.copy()
    spoofer_config['json_port'] += 1
    spoofer_config['tcp_port'] += 1
    maccor_spoofer = pymacnet.maccorspoofer.MaccorSpoofer(
        spoofer_config)
    maccor_spoofer.start()
    # Give time for the spoofer to start.
    time.sleep(5)

    config = CYCLER_INTERFACE_CONFIG.copy()
    config['json_msg_port'] += 1
    config['bin_msg_port'] += 1
    cycler_interface = pymacnet.CyclerInterface(config)

    system_info = cycler_interface.read_system_info()
    assert (system_info == pymacnet.messages.rx_system_info_msg['result'])

    general_info = cycler_interface.read_general_info()
    assert (general_info == pymacnet.messages.rx_general_info_msg['result'])

    channel_statues = cycler_interface.read_all_channel_statuses()
    assert (channel_statues ==
            pymacnet.messages.rx_channel_status_multiple_channels['result']['Status'])

    maccor_spoofer.stop()
