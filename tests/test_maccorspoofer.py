import socket
import json
import pymacnet.maccorspoofer
import pymacnet.messages

'''
Various parameters we will use accross all the tests.
'''
MSG_BUFFER_SIZE_BYTES = 1024
CONFIG_DICT = { "server_ip": "127.0.0.1", "json_port": 1234, "tcp_port": 5678 }
CHANNEL = 1 # The channel we will use to associated tests messages.

def test_messages():
    '''
    Test that the spoofer replies correectly to all messages.
    '''
    spoofer_server = pymacnet.maccorspoofer.MaccorSpoofer(CONFIG_DICT)
    spoofer_server.start()

    # Send all messages and make sure we get the correct responses.
    messages = [ (pymacnet.messages.tx_read_status_msg, pymacnet.messages.rx_read_status_msg),
                 (pymacnet.messages.tx_read_aux_msg, pymacnet.messages.rx_read_aux_msg),
                 (pymacnet.messages.tx_start_test_with_procedure_msg, pymacnet.messages.rx_start_test_with_procedure_msg),
                 (pymacnet.messages.tx_set_variable_msg, pymacnet.messages.rx_set_variable_msg),
                 (pymacnet.messages.tx_start_test_with_direct_control_msg, pymacnet.messages.rx_start_test_with_direct_control_msg),
                 (pymacnet.messages.tx_set_direct_output_msg, pymacnet.messages.rx_set_direct_output_msg),
                 (pymacnet.messages.tx_reset_channel_msg, pymacnet.messages.rx_reset_channel_msg),
                 (pymacnet.messages.tx_set_safety_limits_msg, pymacnet.messages.rx_set_safety_limits_msg),
                ] 

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((CONFIG_DICT["server_ip"], CONFIG_DICT["json_port"]))

    for tx_msg, key in messages:
        tx_msg['params']['Chan'] = CHANNEL
        key['result']['Chan'] = CHANNEL
        tx_msg_packed = json.dumps( tx_msg, indent = 4).encode()
        s.send(tx_msg_packed)
        rx_msg_packed = s.recv(MSG_BUFFER_SIZE_BYTES)
        rx_msg = json.loads(rx_msg_packed.decode())
        assert(rx_msg == key)

    s.close()
    spoofer_server.stop()