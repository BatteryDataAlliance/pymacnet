import socket
import json
import pymacnet.maccorspoofer
import pymacnet.messages

'''
Various parameters we will use accross all the tests.
'''
message_buffer_size_bytes = 1024
config_dict = { "server_ip": "127.0.0.1", "server_port": 5556 } # IP and Port
channel = 1 # The channel we will use to associated tests messages.

def test_basics():
    '''
    Test that we can create and kill the Maccor spoofer
    '''

    spoofer_server = pymacnet.maccorspoofer.MaccorSpoofer(config_dict)
    spoofer_server.start()

    # Messages to send
    outgoing_msg_dict = pymacnet.messages.tx_read_status_msg
    outgoing_msg_dict['params']['Chan'] = 1

    # Create the client to talk to the spooferls
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((config_dict["server_ip"], config_dict["server_port"]))
        msg_outgoing_packed = json.dumps( outgoing_msg_dict, indent = 4)
        msg_outgoing_packed = msg_outgoing_packed.encode()
        s.send(msg_outgoing_packed)
        msg_incoming_packed = s.recv(1024)

    msg_incoming_dict = json.loads(msg_incoming_packed.decode())
    print(msg_incoming_dict)

    spoofer_server.stop()

    assert(True)