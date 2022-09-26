import socket
import logging
import json
import pymacnet.maccor_messages

import struct

log = logging.getLogger(__name__)

class MaccorInterface:
    """
    Class for establishing a connection with the Maccor server.
    """

    def __init__(self, config: dict):
        """
        Init function.
        -------
        Parameters
        ----------
        config : dict
            A configuration dictionary containing the following: 
            channel : int
                The channel we want to control / read from.
            server_ip : str
                The IP of the Maccor machine to communicate with.
            server_port : str
                The port on the Maccor machine to communicate through.
        """

        self.channel = config['channel'] - 1 # Note that channels are zero indexed within Macnet so we must subract one here.
        self.ip = config['server_ip']
        self.port = config['server_port']
        self.msg_buffer_size = config['msg_buffer_size']
        self.sock = None

    def create_connection(self):
        """
        Attempts to create a connection with Maccor server.
        ----------
        Returns
        -------
        success : bool
            True or False based on whether the connection was created successfully
        """
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.ip, self.port))
            success = True
        except:
            log.error("Failed to create TCP connection with Maccor server!")
            success = False

        return success

    def _send_receive_msg( self, outgoing_msg_dict):
        """
        Takes in a message dictionary, packs it, sends to Maccor server, and unpacks the response.
        ----------
        msg_outgoing_dict : dict
            A dictionary containing the message to be sent.
        Returns
        -------
        msg_incoming_dict : dict
            A dictionary containing the message response. Returns None if there is an issue.
        """

        # Pack message
        try:
            msg_outgoing_packed = json.dumps( outgoing_msg_dict, indent = 4)
            msg_outgoing_packed = msg_outgoing_packed.encode()
        except:
            log.error("Error packing outgoing message!")
            return None

        # Send message
        try:
            self.sock.send(msg_outgoing_packed)
        except:
            log.error("Error sending message!")
            return None

        # Receive response
        try:
            msg_incoming_packed = self.sock.recv(self.msg_buffer_size)
        except:
            log.error("Error receiving incoming message!")
            return None

        # Unpack response
        try:
            msg_incoming_dict = json.loads(msg_incoming_packed.decode('utf-8'))
        except:
            log.error("Error unpacking incoming message!")
            return None

        return msg_incoming_dict

    def read_status(self):
        """
        Method to read the status of the channel defined in the config.
        ----------
        Returns
        -------
        status : dict
            A dictionary detailing the status of the channel. Returns None if there is an issue.
        """

        msg_outging_dict = pymacnet.maccor_messages.read_status_msg.copy()
        msg_outging_dict['params']['Chan'] = self.channel

        status = self._send_receive_msg(msg_outging_dict)

        if status:
            return status['result']
        else:
            log.error("Failed to read channel status")
            return None
        

    def __del__(self):
        """
        Kills cycler connections on death.
        """
        if self.sock:
            self.sock.close()




   

