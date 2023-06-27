import socket
import json
import pymacnet.maccorspoofer
import pymacnet.messages
import copy

"""
Various parameters we will use accross all the tests.
"""
MSG_BUFFER_SIZE_BYTES = 1024
CONFIG_DICT = {"server_ip": "127.0.0.1", "json_port": 1234,
               "tcp_port": 5678, "num_channels": 128}
CHANNEL = 1  # The channel we will use to associated tests messages.


def __send_recv_msg(s: socket.socket, tx_msg: dict):
    """
    Helper function for sending and receiving messages.

    Parameters
    ----------
    s : socket.socket
        Socket to send and receive with.
    tx_msg : dict
        The message to send.

    Returns
    -------
    rx_msg : dict
        The response msg.
    """
    tx_msg_packed = json.dumps(tx_msg, indent=4).encode()
    s.send(tx_msg_packed)
    rx_msg_packed = s.recv(MSG_BUFFER_SIZE_BYTES)
    rx_msg = json.loads(rx_msg_packed.decode())
    return rx_msg

def test_messages():
    """
    Test that the spoofer replies correctly to all messages.
    """
    spoofer_server = pymacnet.maccorspoofer.MaccorSpoofer(CONFIG_DICT)
    spoofer_server.start()

    # Send all messages and make sure we get the correct responses.
    messages = [(pymacnet.messages.tx_read_status_msg, pymacnet.messages.rx_read_status_msg),
                (pymacnet.messages.tx_read_aux_msg,
                 pymacnet.messages.rx_read_aux_msg),
                (pymacnet.messages.tx_start_test_with_procedure_msg,
                 pymacnet.messages.rx_start_test_with_procedure_msg),
                (pymacnet.messages.tx_set_variable_msg,
                 pymacnet.messages.rx_set_variable_msg),
                (pymacnet.messages.tx_start_test_with_direct_control_msg,
                 pymacnet.messages.rx_start_test_with_direct_control_msg),
                (pymacnet.messages.tx_set_direct_output_msg,
                 pymacnet.messages.rx_set_direct_output_msg),
                (pymacnet.messages.tx_reset_channel_msg,
                 pymacnet.messages.rx_reset_channel_msg),
                (pymacnet.messages.tx_set_safety_limits_msg,
                 pymacnet.messages.rx_set_safety_limits_msg),
                ]

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((CONFIG_DICT["server_ip"], CONFIG_DICT["json_port"]))

    for tx_msg, ans_key in messages:
        tx_msg['params']['Chan'] = CHANNEL
        ans_key['result']['Chan'] = CHANNEL
        rx_msg = __send_recv_msg(s, tx_msg)
        assert (rx_msg == ans_key)

    s.close()
    spoofer_server.stop()

def test_update_status():
    """
    Check that updating channel status works and does not effect other channel.
    """

    spoofer_server = pymacnet.maccorspoofer.MaccorSpoofer(CONFIG_DICT)
    spoofer_server.start()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((CONFIG_DICT["server_ip"], CONFIG_DICT["json_port"]))

    tx_msg = copy.deepcopy(pymacnet.messages.tx_read_status_msg)
    ans_key = copy.deepcopy(pymacnet.messages.rx_read_status_msg)
    tx_msg['params']['Chan'] = CHANNEL
    ans_key['result']['Chan'] = CHANNEL

    # Check default setting.
    rx_msg = __send_recv_msg(s, tx_msg)
    assert (rx_msg == ans_key)

    # Try updating voltage and test time.
    updated_voltage = 4.20
    updated_test_time = 7.69
    ans_key['result']['Voltage'] = updated_voltage
    ans_key['result']['TestTime'] = updated_test_time
    assert (spoofer_server.update_channel_status(
        CHANNEL, {'Voltage': updated_voltage, 'TestTime': updated_test_time}))
    rx_msg = __send_recv_msg(s, tx_msg)
    assert (rx_msg == ans_key)

    # Try to apply status update with invalid key
    assert (not spoofer_server.update_channel_status(
        CHANNEL, {'Voltage': 2.1, 'Fake_Key': updated_test_time}))
    # Make sure values were not updated
    rx_msg = __send_recv_msg(s, tx_msg)
    assert (rx_msg == ans_key)

    # Make updating only changed values for the specified channel
    ans_key = copy.deepcopy(pymacnet.messages.rx_read_status_msg)
    tx_msg = copy.deepcopy(pymacnet.messages.tx_read_status_msg)
    tx_msg['params']['Chan'] = CHANNEL+1
    ans_key['result']['Chan'] = CHANNEL + 1
    rx_msg = __send_recv_msg(s, tx_msg)
    assert (rx_msg == ans_key)

    s.close()
    spoofer_server.stop()