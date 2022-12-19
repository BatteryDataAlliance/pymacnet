import socket
import json
import threading
import pymacnet.messages

class MaccorSpoofer:
    """
    Class to mimic behavior of Maccor cycler MacNet control server.

    Currently dumb and just sends back basic response messages without 
    any notion of channel status or readings. Could be expanded in future. 
    """
    
    __client_connect_timeout_s = 1
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

        json_server_config = {'ip':config['server_ip'],'port':config['json_port']}
        self.__json_server_thread = threading.Thread( target=self.__server_loop, 
                                                        args=( json_server_config, JsonWorker,), 
                                                        daemon=True)

        tcp_server_config = {'ip':config['server_ip'],'port':config['tcp_port']}
        self.__tcp_server_thread = threading.Thread( target=self.__server_loop,
                                                         args=( tcp_server_config, TcpWorker,), 
                                                        daemon=True)

    def start(self):
        """
        Starts the server loops

        Note: 
        """
        self.__json_server_thread.start()       
        self.__tcp_server_thread.start()

    def __server_loop( self, sock_config : dict, Worker):  
        """
        Creates a server and forever loop to service client socket requests.
        ----------
        sock_cofig : dict
            A configuration for the socket containing the IP and port number.
        Worker : SocketWorker
            A reference to the worker class that will service individual client connections.
        """       
        # List that will hold all the workers to service client connections.
        client_workers = [] 

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((sock_config["ip"], sock_config["port"]))
        sock.settimeout(self.__client_connect_timeout_s)
        sock.listen()
        
        while True:
            try: 
                client_connection, client_address = sock.accept()
                client_workers.append(Worker(client_connection))
            except socket.timeout:
                with self.__stop_servers_lock:
                    # If stop commmand is issued then kill all workers.
                    if self.__stop_servers:
                        for worker in client_workers:
                            if worker.is_alive():
                                worker.kill_worker()
                        break
                # Remove any workers that made have died from disconnecting clients.
                client_workers[:] = [worker for worker in client_workers if worker.is_alive()]                         

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

class SocketWorker:
    '''
    Generic worker class that will respond to client socket requests. 
    Default setup as an echo server. Child classes should overwrite the 
    the `_process_client_msg()` method with their own responses.
    '''
    __receive_msg_timeout_s = 1
    __msg_buffer_size_bytes = 1024
    __stop_lock = threading.Lock()
    __stop = False

    def __init__(self, s: socket.socket):
        """
        Creates the thread to service client requests.
        ----------
        s : socket.socket
            Socket connection to client.
        """
        self.stop = False
        self.__client_thread = threading.Thread( target=self.___service_loop, args=(s,), daemon=True)
        self.__client_thread.start()
    
    def ___service_loop(self, s: socket.socket):
        """
        Forever loop to service client requests. Wait to receive a message. If no messages is 
        received before the timeout then check to see if stop command has been issued. Loop is 
        also broken if client breaks conenction by sending b''. 
        ----------
        s : socket.socket
            Socket connection to client.
        """
        s.settimeout(self.__receive_msg_timeout_s)

        while True:
            try:
                rx_msg = s.recv(self.__msg_buffer_size_bytes)
                if not rx_msg:
                    break
                tx_msg = self._process_client_msg(rx_msg)
                s.sendall(tx_msg)
            except socket.timeout:
                with self.__stop_lock:
                    if self.__stop:    
                        break
        s.close()

    def _process_client_msg(self, rx_msg):
        """
        Takes the incoming client message and generates a response. 
        ----------
        rx_msg : PyBytesObject
            The client message received.
        Returns
        -------
        tx_msg : PyBytesObject
            The client response.
        """
        return rx_msg

    def is_alive(self):
        """
        Method to call to see if the client service thread is still running.
        Returns
        -------
        running : bool
            True of False based on whether or not the client thread is running.
        """
        return self.__client_thread.is_alive()

    def kill_worker(self):
        '''
        Method to stop client service loop.
        '''
        if self.__client_thread.is_alive():
            with self.__stop_lock:
                self.__stop = True
            self.__client_thread.join()

class JsonWorker(SocketWorker):
    '''
    Class to handle requests from MacNet JSON socket clients.
    '''

    def _process_client_msg(self, rx_msg):
        """
        Takes the incoming JSON client message and generates a response. 
        ----------
        rx_msg : PyBytesObject
            The client message received.
        Returns
        -------
        tx_msg : PyBytesObject
            The client response.
        """

        rx_msg = json.loads(rx_msg)
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
            tx_msg['result']['VSafeMax'] = rx_msg['params']['VSafeMax']
            tx_msg['result']['VSafeMin'] = rx_msg['params']['VSafeMin']
            tx_msg['result']['ISafeChg'] = rx_msg['params']['ISafeChg']
            tx_msg['result']['ISafeDis'] = rx_msg['params']['ISafeDis']
            tx_msg['result']['PBatSafeChg'] = rx_msg['params']['PBatSafeChg']
            tx_msg['result']['PBatSafeDis'] = rx_msg['params']['PBatSafeDis']
        else:
            tx_msg = {'err':1}

        tx_msg = json.dumps( tx_msg, indent = 4)
        tx_msg = tx_msg.encode('utf-8')

        return tx_msg

class TcpWorker(SocketWorker):
    '''
    Class to handle requests from TCP socket clients.
    Currently just implemented as an echo server.
    '''
    pass