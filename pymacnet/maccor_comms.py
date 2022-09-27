import socket
import logging
import json
import pymacnet.maccor_messages
from datetime import datetime

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
        self.config = config
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
            self.sock.connect((self.config['server_ip'], self.config['server_port']))
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
            msg_incoming_packed = self.sock.recv(self.config['msg_buffer_size'])
        except:
            log.error("Error receiving message!")
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
        
    def _reset_channel(self):
        """
        Resets the channel
        ----------
        Returns
        -------
        success : bool
            True of False based on whether the test was started or not.
        """
        msg_outging_dict = pymacnet.maccor_messages.reset_channel_msg.copy()
        msg_outging_dict['params']['Chan'] = self.channel

        reply = self._send_receive_msg(msg_outging_dict)
        if reply:
            if reply['result']['Result'] == 'OK':
                success = True
            else:
                log.error("Failed reset channel! Channel did not reset!")
                success = False
        else:
            log.error("Failed reset channel! Did not receive reply!")
            success = False

        return success 

    def start_test_with_procedure(self):
        """
        Starts the test on the channel and with the procedure specified in the passed config.
        Will not start a test if the channel is current running a test.
        Will reset a channel if there is a completed test on that channel.
        ----------
        Returns
        -------
        success : bool
            True of False based on whether the test was started or not
        """

        msg_outging_dict = pymacnet.maccor_messages.start_test_with_procedure_msg.copy()
        msg_outging_dict['params']['Chan'] = self.channel
        msg_outging_dict['params']['ProcName'] = self.config['test_procedure']
        msg_outging_dict['params']['Comment'] = "Started with pymacnet at " + str(datetime.timestamp(datetime.now()))

        # If test name is not specified then start test with a random test
        if not self.config['test_name']:
            msg_outging_dict['params']['TestName'] = 'Random'
        else:
            msg_outging_dict['params']['TestName'] = self.config['test_name']

        # Check the status of the channel before we try to start the test.
        status = self.read_status()
        if status:
            if pymacnet.maccor_messages.stat_dict[status['Stat']] == 'Completed':
                self._reset_channel()
        else:
            log.error("Cannot read channel status!")
            return False

        reponse = self._send_receive_msg(msg_outging_dict)
        if reponse['result']['Result'] != 'OK':
            log.error("Error starting test! " + reponse['result']['Result'])
            return False
        else:
            return True

    def start_test_direct_control(self):
        """
        Starts a test to be manually controled with on the channel specified in the config.
        ----------
        Returns
        -------
        status : dict
            A dictionary detailing the status of the channel. Returns None if there is an issue.
        """
        # TODO: WRITE THIS
        pass

    def set_direct_mode_output( self, voltage_v, current_a):
        """
        Sets the voltage/current output on the channel specified on in the config. Note that the
        test must have been started with the start_test_direct_control method.
        ----------
        Returns
        -------
        status : dict
            A dictionary detailing the status of the channel. Returns None if there is an issue.
        """
        # TODO: WRITE THIS
        pass

    def __del__(self):
        """
        Kills cycler connections on death.
        """
        if self.sock:
            self.sock.close()




   

