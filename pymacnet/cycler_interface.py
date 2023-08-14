import logging
import copy
import socket
import logging
import json
import struct
import pymacnet.messages

logger = logging.getLogger(__name__)


class CyclerInterface():
    """
    Class for interfacing with Maccor Cycler using MacNet.
    """

    def __init__(self, config: dict):
        """
        Creates a CyclerInterface class instance. 

        Parameters
        ----------
        config : dict
            A configuration dictionary. Must contain the following keys:
            - `server_ip` - The IP address of the Maccor server. Use 127.0.0.1 if running on the same machine as the server.
            - `json_msg_port` - The port to communicate through with JSON messages. Default set to 57570.
            - `bin_msg_port` - The port to communicate through with binary messages. Default set to 57560.
            - `msg_buffer_size_bytes` - How big of a message buffer to use for sending/receiving messages. A minimum of 1024 bytes is recommended.
        """
        self.__msg_buffer_size_bytes = config['msg_buffer_size_bytes']

        assert (self.__create_connection(
            ip=config['server_ip'], json_msg_port=config['json_msg_port'], bin_msg_port=config['bin_msg_port']))

        self.__num_channels = self.read_general_info()['TestChannels']

    def get_num_channels(self) -> int:
        '''
        Returns the number of channels associated with the cycler
        '''
        return self.__num_channels

    def read_system_info(self) -> dict:
        """
        Reads the system info from the cycler.  MacNet message (1,1)

        Returns
        -------
        system_info : dict
            The system information for the cycler.
        """
        msg_outgoing_dict = copy.deepcopy(pymacnet.messages.tx_system_info_msg)

        rx_msg = self._send_receive_json_msg(msg_outgoing_dict)
        if rx_msg:
            return rx_msg['result']
        else:
            logger.error("Failed to read system info!")
            return None

    def read_general_info(self) -> dict:
        """
        Reads the general system info from the cycler.  MacNet message (1,2)

        Returns
        -------
        general_info : dict
            The general information for the cycler.
        """
        msg_outgoing_dict = copy.deepcopy(
            pymacnet.messages.tx_general_info_msg)

        rx_msg = self._send_receive_json_msg(msg_outgoing_dict)
        if rx_msg:
            return rx_msg['result']
        else:
            logger.error("Failed to read system info!")
            return None

    def read_channel_status(self, channel: int) -> dict:
        """
        Reads channel status for the specified `channel`.

        Returns
        -------
        status : dict
            A dictionary detailing the status of the channel. Returns None if there is an issue.
        """
        if not (channel > 0) and not (channel < self.__num_channels):
            logger.warning("Invalid channel number!")
            return None

        msg_outgoing_dict = copy.deepcopy(pymacnet.messages.tx_read_status_msg)
        msg_outgoing_dict['params']['Chan'] = channel
        status = self._send_receive_json_msg(msg_outgoing_dict)

        if status:
            return status['result']
        else:
            logger.error("Failed to read channel status")
            return None

    def read_all_channel_statuses(self) -> list:
        """
        Reads the channel status for all channels on the cycler.

        Returns
        -------
        statuses : list
            A list of channel statues where the index corresponds to the channel number (zero indexed.)
        """
        msg_outgoing_dict = copy.deepcopy(
            pymacnet.messages.tx_channel_status_multiple_channels)

        msg_outgoing_dict['params']['Len'] = self.__num_channels

        rx_msg = self._send_receive_json_msg(msg_outgoing_dict)
        if rx_msg:
            return rx_msg['result']['Status']
        else:
            logger.error("Failed to read channel status")
            return None

    def _send_receive_json_msg(self, outgoing_msg_dict) -> dict:
        """
        Sends and receives a JSON message to/from the Maccor server.

        Parameters
        ----------
        msg_outgoing_dict : dict
            A dictionary containing the message to be sent.

        Returns
        ----------
        msg_incoming_dict : dict
            A dictionary containing the message response. Returns None if there is an issue.
        """

        if self.__json_msg_socket:
            pass
        else:
            logger.error(
                "__json_msg_socket connection does not exist!", exc_info=True)
            return None

        # Take care of channel zero indexing on outgoing messages
        if 'params' in outgoing_msg_dict and 'Chan' in outgoing_msg_dict['params']:
            outgoing_msg_dict['params']['Chan'] -= 1

        try:
            msg_outgoing_packed = json.dumps(outgoing_msg_dict, indent=4)
            msg_outgoing_packed = msg_outgoing_packed.encode()
        except:
            logger.error("Error packing outgoing message!", exc_info=True)
            return None

        try:
            self.__json_msg_socket.send(msg_outgoing_packed)
        except:
            logger.error("Error sending message!", exc_info=True)
            return None

        try:
            msg_incoming_packed = b''
            while msg_incoming_packed[-2:] != b'\r\n':
                msg_incoming_packed += self.__json_msg_socket.recv(
                    self.__msg_buffer_size_bytes)
        except socket.timeout:
            logger.error(
                "Timeout on receiving message from Maccor server!", exc_info=True)
            return False
        except:
            logger.error("Error receiving message!", exc_info=True)
            return None

        try:
            msg_incoming_dict = json.loads(msg_incoming_packed.decode('utf-8'))
        except:
            logger.error("Error unpacking incoming message!", exc_info=True)
            logger.error("Message: " + str(msg_incoming_packed))
            return None

        # Take care of channel zero indexing on incoming messages
        if 'result' in msg_incoming_dict and 'Chan' in msg_incoming_dict['result']:
            msg_incoming_dict['result']['Chan'] += 1

        return msg_incoming_dict

    def _send_direct_output_rest_bin_msg(self, direct_out_msg_dict: dict) -> bool:
        """
        Sends a direct output binary message to set the channel to rest.
        Note this is necessary because there is a bug where direct output 
        JSON messages cannot set rest.

        Parameters
        ----------
        direct_out_msg_dict : dict
            A direct output message dictionary

        Returns
        -------
        success : bool
            True of False based on whether or not rest was set.
        """

        # Take care of channel zero indexing
        direct_out_msg_dict["params"]['Chan'] += 1

        msg_outgoing_bytes = struct.pack('<HHHHffffBB',
                                         direct_out_msg_dict["params"]['FClass'],
                                         direct_out_msg_dict["params"]['FNum'],
                                         direct_out_msg_dict["params"]['Chan'],
                                         18,
                                         direct_out_msg_dict["params"]['Current'],
                                         direct_out_msg_dict["params"]['Voltage'],
                                         direct_out_msg_dict["params"]['Power'],
                                         direct_out_msg_dict["params"]['Resistance'],
                                         direct_out_msg_dict["params"]['CurrentRange'],
                                         ord('R'))
        try:
            self.__bin_msg_socket.send(msg_outgoing_bytes)
        except:
            logger.error("Error sending binary rest message!", exc_info=True)
            return False
        try:
            response = self.__bin_msg_socket.recv(self.__msg_buffer_size_bytes)
        except socket.timeout:
            logger.error(
                "Timeout on receiving message from Maccor server!", exc_info=True)
            return False
        except:
            logger.error(
                "Error receiving rest message response!", exc_info=True)
            return False
        if response:
            # TODO: Should check something related to the response.
            return True
        else:
            logger.error("No response for setting rest!")
            return False

    def __create_connection(self, ip: str, json_msg_port: int, bin_msg_port: int) -> bool:
        """
        Creates a connection with Maccor server to send/receive JSON and binary messages.

        Parameters
        ----------
        ip : str
            The IP address of the Maccor server.
        json_msg_port : int
            The TCP port use for JSON message communication.
        bin_msg_port : 
            The TCP port used for binary message communication

        Returns
        ----------
        success : bool
            True or False based on whether the connection was created successfully
        """
        try:
            self.__json_msg_socket = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
            self.__json_msg_socket.settimeout(2)
            self.__json_msg_socket.connect(
                (ip, json_msg_port)
            )
        except:
            logger.error(
                "Failed to create JSON message socket!", exc_info=True)
            return False
        try:
            self.__bin_msg_socket = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
            self.__bin_msg_socket.settimeout(2)
            self.__bin_msg_socket.connect(
                (ip, bin_msg_port)
            )
        except:
            logger.error(
                "Failed to create binary message socket!", exc_info=True)
            return False

        return True
