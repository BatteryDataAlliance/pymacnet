import socket
import json
import threading
import pymacnet.messages

class MaccorSpoofer:
    """
    Class to mimic behavior of Maccor cycler MacNet control server. 
    """
    
    __json_server_thread:threading.Thread
    __receive_msg_timeout_s = 1
    __msg_buffer_size_bytes = 1024
    __stop_servers_lock = threading.Lock()
    __stop_servers = False

    def __init__(self, config: dict):
        """
        Init function.
        -------
        Parameters
        ----------
        config : dict
            A configuration dictionary containing the server ip address and ports to use.
        """
        self.config = config

        self.__json_server_thread = threading.Thread(target=self.__json_server_loop, 
                                                args=(),daemon=True)
        self.__tcp_server_thread = threading.Thread(target=self.__tcp_server_loop, 
                                                args=(),daemon=True)

    def start(self):
        """
        Starts the send/receive forever loop
        """
        self.__json_server_thread.start()       
        self.__tcp_server_thread.start()                                         

    def __json_server_loop(self):
        """
        Starts a the JSON server in a forever loop. Breaks when stop method is called.
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.config["server_ip"], self.config["json_port"]))
        sock.settimeout(self.__receive_msg_timeout_s)
        sock.listen()
        
        while True:
            try:
                connection, client_address = sock.accept()
                with connection:    
                    rx_msg = connection.recv(self.__msg_buffer_size_bytes)
                    rx_msg = json.loads(rx_msg)

                    # Determine the type of received message and give appropriate response.
                    if rx_msg:
                        if (pymacnet.messages.tx_read_status_msg['params']['FClass'] == rx_msg['params']['FClass'] and 
                                pymacnet.messages.tx_read_status_msg['params']['FNum'] == rx_msg['params']['FNum']):
                            tx_msg = pymacnet.messages.rx_read_status_msg
                            tx_msg['result']['Chan'] = rx_msg['params']['Chan']
                        elif (pymacnet.messages.tx_read_aux_msg['params']['FClass'] == rx_msg['params']['FClass'] and 
                                pymacnet.messages.tx_read_aux_msg['params']['FNum'] == rx_msg['params']['FNum']):
                            tx_msg = pymacnet.messages.rx_read_aux_msg
                            tx_msg['result']['Chan'] = rx_msg['params']['Chan']
                        elif (pymacnet.messages.tx_start_test_with_procedure_msg['params']['FClass'] == rx_msg['params']['FClass'] and 
                                pymacnet.messages.tx_start_test_with_procedure_msg['params']['FNum'] == rx_msg['params']['FNum']):
                            tx_msg = pymacnet.messages.rx_start_test_with_procedure_msg
                            tx_msg['result']['Chan'] = rx_msg['params']['Chan']
                        elif (pymacnet.messages.tx_set_variable_msg['params']['FClass'] == rx_msg['params']['FClass'] and 
                                pymacnet.messages.tx_set_variable_msg['params']['FNum'] == rx_msg['params']['FNum']):
                            tx_msg = pymacnet.messages.rx_set_variable_msg
                            tx_msg['result']['Chan'] = rx_msg['params']['Chan']
                        elif (pymacnet.messages.tx_start_test_with_direct_control_msg['params']['FClass'] == rx_msg['params']['FClass'] and 
                                pymacnet.messages.tx_start_test_with_direct_control_msg['params']['FNum'] == rx_msg['params']['FNum']):
                            tx_msg = pymacnet.messages.rx_start_test_with_direct_control_msg
                            tx_msg['result']['Chan'] = rx_msg['params']['Chan']
                        elif (pymacnet.messages.tx_set_direct_output_msg['params']['FClass'] == rx_msg['params']['FClass'] and 
                                pymacnet.messages.tx_set_direct_output_msg['params']['FNum'] == rx_msg['params']['FNum']):
                            tx_msg = pymacnet.messages.rx_set_direct_output_msg
                            tx_msg['result']['Chan'] = rx_msg['params']['Chan']
                        elif (pymacnet.messages.tx_reset_channel_msg['params']['FClass'] == rx_msg['params']['FClass'] and 
                                pymacnet.messages.tx_reset_channel_msg['params']['FNum'] == rx_msg['params']['FNum']):
                            tx_msg = pymacnet.messages.rx_reset_channel_msg
                            tx_msg['result']['Chan'] = rx_msg['params']['Chan']
                        elif (pymacnet.messages.tx_set_safety_limits_msg['params']['FClass'] == rx_msg['params']['FClass'] and 
                                pymacnet.messages.tx_set_safety_limits_msg['params']['FNum'] == rx_msg['params']['FNum']):
                            tx_msg = pymacnet.messages.rx_set_safety_limits_msg
                            tx_msg['result']['Chan'] = rx_msg['params']['Chan']
                        else:
                            tx_msg = {'err':1}
                    if tx_msg:
                        tx_msg_packed = json.dumps( tx_msg, indent = 4)
                        tx_msg_packed = tx_msg_packed.encode('utf-8')
                        connection.send(tx_msg_packed)
            except socket.timeout:
                with self.__stop_servers_lock:
                    if self.__stop_servers:
                        sock.close()
                        break

    def __tcp_server_loop(self):
        """
        Starts a the TCP server in a forever loop. Breaks when stop method is called.

        TODO: Currently just setup as an echo server. Add functionality later.
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.config["server_ip"], self.config["tcp_port"]))
        sock.settimeout(self.__receive_msg_timeout_s)
        sock.listen()
        
        while True:
            try:
                connection, client_address = sock.accept()
                with connection:    
                    rx_msg = connection.recv(self.__msg_buffer_size_bytes)
                    if rx_msg:
                        tx_msg = rx_msg
                    if tx_msg:
                        connection.send(tx_msg)
            except socket.timeout:
                with self.__stop_servers_lock:
                    if self.__stop_servers:
                        sock.close()
                        break

    def stop(self):
        """
        Stop the server loops
        """
        with self.__stop_servers_lock:
            self.__stop_servers = True
        self.__json_server_thread.join()
        self.__tcp_server_thread.join()

    def __del__(self):
        self.stop()