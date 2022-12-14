import socket
import json
import threading
import pymacnet.messages

class MaccorSpoofer:
    """
    Class to mimic behavior of Maccor cycler. 
    """
    
    server_thread:threading.Thread
    receive_msg_wait_time_ms = 1000
    msg_buffer_size_bytes = 1024
    stop_server = False

    def __init__(self, config: dict):
        """
        Init function.
        -------
        Parameters
        ----------
        config : dict
            A configuration dictionary containing the target server ip address and port.
        """
        self.config = config
        self.server_thread = threading.Thread(target=self.__server_loop, 
                                                args=(),daemon=True)

    def start(self):
        """
        Starts the send/receive forever loop
        """
        self.server_thread.start()                                               

    def __server_loop(self):
        """
        Starts a forver zmq server.
        """

        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.config["server_ip"], self.config["server_port"]))
        sock.settimeout(1)
        sock.listen()
        
        stop = lambda : self.stop_server
        
        while True:
            try:
                connection, client_address = sock.accept()
                with connection:            
                    rx_msg = connection.recv(self.msg_buffer_size_bytes)
                    rx_msg = json.loads(rx_msg)

                    # Determine the type of received message and give appropriate response.
                    if rx_msg:
                        if (pymacnet.messages.tx_read_status_msg['params']['FClass'] == rx_msg['params']['FClass'] and 
                                pymacnet.messages.tx_read_status_msg['params']['FNum'] == rx_msg['params']['FNum']):
                            tx_msg = pymacnet.messages.rx_read_status_msg
                            tx_msg['result']['Chan'] = rx_msg['params']['Chan']
                        else:
                            tx_msg = {'err':1}

                    # Send the resposne message
                    if tx_msg:
                        tx_msg_packed = json.dumps( tx_msg, indent = 4)
                        tx_msg_packed = tx_msg_packed.encode('utf-8')
                        connection.send(tx_msg_packed) # maybe use send here instead?

            # In event of timeout see if we should break.       
            except socket.timeout:
               if stop():
                sock.close()
                break

    def stop(self):
        """
        Stop the send/receive forever loop
        """
        self.stop_server = True
        self.server_thread.join()

    def read_aux(self):
        expected_aux_response = {'jsonrpc': '2.0', 'result': {'FClass': 4, 'FNum': 4, 'Chan': 93, 'Len': 1, 'AuxValues': [24.7545490264893]}, 'id': 1987}
        return expected_aux_response

    def set_channel_variables(var_num, var_value):
        expected_channel_variables_response = {'jsonrpc': '2.0', 'result': {'FClass': 6, 'FNum': 9, 'Chan': 93, 'Result': 'OK'}, 'id': 1987}
        return expected_channel_variables_response

    def start_test_with_procedure(self):
        expected_start_test_with_procedure_response = {'jsonrpc': '2.0', 'result': {'FClass': 6, 'FNum': 2, 'Chan': 93, 'Result': 'OK'}, 'id': 1987}
        return expected_start_test_with_procedure_response

    def start_test_with_direct_control(self):
        expected_direct_control_response = {'jsonrpc': '2.0', 'result': {'FClass': 6, 'FNum': 7, 'Chan': 93, 'Result': 'OK'}, 'id': 1987}
        return expected_direct_control_response

    def set_direct_mode_output(self):
        expected_set_direct_mode_output_response = {'jsonrpc': '2.0', 'result': {'FClass': 6, 'FNum': 8, 'Chan': 93, 'Result': 'OK'}, 'id': 1987}
        return expected_set_direct_mode_output_response