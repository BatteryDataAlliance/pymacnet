import socket
import logging
import json
import struct
import copy
import pymacnet.messages
from datetime import datetime

log = logging.getLogger(__name__)


class MaccorInterface:
    """
    Class for controlling Maccor Cycler using MacNet.
    """

    __msg_buffer_size_bytes = 1024

    def __init__(self, config: dict):
        """
        Creates a class instance. The `start()` method still needs to be run to create the connection.

        Parameters
        ----------
        config : dict
            A configuration dictionary. See the README.md for a detailed breakdown of all parameters 
            that must be included.
        """

        # Channels are zero indexed within Macnet so we must subtract one here.
        self.channel = config['channel'] - 1
        self.config = config
        self.__json_sock = None
        self.__tcp_sock = None

    def start(self) -> bool:
        """
        Verifies that the config passed during construction is valid and creates connections to 
        the Maccor server.

        Returns
        -------
        success : bool
            True or False based on whether the config passed at construction is valid.
        """
        if not self.__verify_config():
            return False
        elif not self.__create_connection():
            return False
        else:
            return True

    def __verify_config(self) -> bool:
        """
        Verifies that the config passed on construction is valid.

        Returns
        --------------------------
        success : bool
            True or False based on whether the config passed at construction is valid.
        """

        required_config_keys = ['channel',
                                'test_name',
                                'test_procedure',
                                'v_max_safety_limit_v',
                                'v_min_safety_limit_v',
                                'i_max_safety_limit_a',
                                'i_min_safety_limit_a',
                                'v_max_v',
                                'v_min_v',
                                'c_rate_ah',
                                'data_record_time_s',
                                'data_record_voltage_delta_vbys',
                                'data_record_current_delta_abys',
                                'server_ip',
                                'json_server_port',
                                'tcp_server_port']

        for key in required_config_keys:
            if key not in self.config:
                log.error("Missing key from config! Missing : " + key)
                return False
        return True

    def __create_connection(self) -> bool:
        """
        Creates a connection with Maccor server to send/receive JSON and binary messages.

        Returns
       ----------
        success : bool
            True or False based on whether the connection was created successfully
        """
        try:
            self.__json_sock = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM
            )
            self.__json_sock.connect(
                (self.config['server_ip'], self.config['json_server_port'])
            )
        except:
            log.error(
                "Failed to create JSON TCP connection with Maccor server!", exc_info=True)
            return False
        try:
            self.__tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__tcp_sock.connect(
                (self.config['server_ip'], self.config['tcp_server_port'])
            )
        except:
            log.error(
                "Failed to create TCP connection with Maccor server!", exc_info=True)
            return False

        return True

    def __send_receive_msg(self, outgoing_msg_dict) -> dict:
        """
        Takes in a message dictionary, packs it, sends it to the Maccor server, and unpacks the response.

        Parameters
        ----------
        msg_outgoing_dict : dict
            A dictionary containing the message to be sent.

        Returns
        ----------
        msg_incoming_dict : dict
            A dictionary containing the message response. Returns None if there is an issue.
        """

        # Make Sure this is json_socket connection exists first.
        if self.__json_sock:
            pass
        else:
            log.error("json_socket connection does not exist!", exc_info=True)
            return None
        # Pack message
        try:
            msg_outgoing_packed = json.dumps(outgoing_msg_dict, indent=4)
            msg_outgoing_packed = msg_outgoing_packed.encode()
        except:
            log.error("Error packing outgoing message!", exc_info=True)
            return None
        # Send message
        try:
            self.__json_sock.send(msg_outgoing_packed)
        except:
            log.error("Error sending message!", exc_info=True)
            return None
        # Receive response
        try:
            msg_incoming_packed = self.__json_sock.recv(
                self.__msg_buffer_size_bytes
            )
        except:
            log.error("Error receiving message!", exc_info=True)
            return None
        # Unpack response
        try:
            msg_incoming_dict = json.loads(msg_incoming_packed.decode('utf-8'))
        except:
            log.error("Error unpacking incoming message!", exc_info=True)
            log.error("Message: " + str(msg_incoming_packed))
            return None

        # If the response messages has the channel in it add 1 so things look correct to user.
        if 'result' in msg_incoming_dict.keys():
            if 'Chan' in msg_incoming_dict['result'].keys():
                msg_incoming_dict['result']['Chan'] += 1

        return msg_incoming_dict

    def read_status(self) -> dict:
        """
        Method to read the status of the channel defined in the config.

        Returns
        -------
        status : dict
            A dictionary detailing the status of the channel. Returns None if there is an issue.
        """

        msg_outging_dict = copy.deepcopy(pymacnet.messages.tx_read_status_msg)
        msg_outging_dict['params']['Chan'] = self.channel

        status = self.__send_receive_msg(msg_outging_dict)

        if status:
            return status['result']
        else:
            log.error("Failed to read channel status")
            return None

    def read_aux(self) -> list:
        """
        Reads the auxiliary readings for the channel specified in the config.

        Returns
        -------
        aux_readings : list
            A list of the auxiliary readings.
        """

        msg_outging_dict = copy.deepcopy(pymacnet.messages.tx_read_aux_msg)
        msg_outging_dict['params']['Chan'] = self.channel

        aux_readings = self.__send_receive_msg(msg_outging_dict)
        if aux_readings:
            return aux_readings['result']['AuxValues']
        else:
            log.error("Failed to read channel aux values!")
            return None

    def reset_channel(self) -> bool:
        """
        Resets the channel. Note this will stop any actively running test on the target channel.

        Returns
        -------
        success : bool
            True of False based on whether the test was started or not.
        """
        msg_outging_dict = copy.deepcopy(
            pymacnet.messages.tx_reset_channel_msg
        )
        msg_outging_dict['params']['Chan'] = self.channel

        reply = self.__send_receive_msg(msg_outging_dict)
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

    def __set_channel_safety_limits(self) -> bool:
        """
        Sets channel safety limits on the channel specified in the config. 

        Returns
        -------
        success : bool
            Returns True/False based on whether the safety limits were set correctly.
        """
        msg_outging_dict = copy.deepcopy(
            pymacnet.messages.tx_set_safety_limits_msg
        )
        msg_outging_dict['params']['Chan'] = self.channel
        msg_outging_dict['params']['VSafeMax'] = self.config['v_max_safety_limit_v']
        msg_outging_dict['params']['VSafeMin'] = self.config['v_min_safety_limit_v']
        msg_outging_dict['params']['ISafeChg'] = self.config['i_max_safety_limit_a']
        msg_outging_dict['params']['ISafeDis'] = self.config['i_min_safety_limit_a']

        # Check to make sure all safety limits were set correctly
        reply = self.__send_receive_msg(msg_outging_dict)
        if reply:
            try:
                assert ((reply['result']['Chan']) == self.config['channel'])
                assert (abs(reply['result']['VSafeMax'] -
                        self.config['v_max_safety_limit_v']) < 0.001)
                assert (abs(reply['result']['VSafeMin'] -
                        self.config['v_min_safety_limit_v']) < 0.001)
                assert (abs(reply['result']['ISafeChg'] -
                        self.config['i_max_safety_limit_a']) < 0.001)
                assert (abs(reply['result']['ISafeDis'] -
                        self.config['i_min_safety_limit_a']) < 0.001)
            except:
                log.error(
                    "Set safety limits to not match sent safety limits! Message response: " + str(reply))
                return False
        else:
            log.error(
                "Failed to receive reply message when trying to set safety limits!")
            return False

        return True

    def set_channel_variable(self, var_num=1, var_value=0) -> bool:
        """
        Sets test variables on the target channel. See the "Variables" section in the 
        Maccor manual for more details about how to use these in tests.

        Parameters
        ----------
        var_num : int
            Value between 1 and 16, depending on which variable to set.
        var_value : float
            Value to set the variable to.

        Returns
        -------
        success : bool
            True of False based on whether or not the variable value was set.
        """
        msg_outging_dict = copy.deepcopy(pymacnet.messages.tx_set_variable_msg)
        msg_outging_dict['params']['Chan'] = self.channel
        msg_outging_dict['params']['VarNum'] = var_num
        msg_outging_dict['params']['Value'] = var_value

        # Check to make variable was set
        reply = self.__send_receive_msg(msg_outging_dict)
        if reply:
            try:
                assert ((reply['result']['Chan']) == self.config['channel'])
                assert (reply['result']['Result'] == 'OK')
            except:
                log.error("Variable not set!")
                return False
        else:
            log.error(
                "Failed to receive reply message when trying to set variable!")
            return False

        return True

    def start_test_with_procedure(self) -> bool:
        """
        Starts the test on the channel and with the procedure specified in the passed config. 
        Note that it will not start a test if the channel is current running a test.

        Returns
        -------
        success : bool
            True of False based on whether the test was started or not
        """
        msg_outging_dict = copy.deepcopy(
            pymacnet.messages.tx_start_test_with_procedure_msg)
        msg_outging_dict['params']['Chan'] = self.channel
        msg_outging_dict['params']['ProcName'] = self.config['test_procedure']
        msg_outging_dict['params']['Crate'] = self.config['c_rate_ah']
        msg_outging_dict['params']['Comment'] = "Started with pymacnet at " + \
            str(datetime.timestamp(datetime.now()))

        # If test name is not specified then start test with a random test
        if not self.config['test_name']:
            msg_outging_dict['params']['TestName'] = 'Random'
        else:
            msg_outging_dict['params']['TestName'] = self.config['test_name']

        # Check the status of the channel before we try to start the test.]
        status = self.read_status()
        if status:
            if pymacnet.messages.status_dictionary[status['Stat']] == 'Completed':
                self.reset_channel()
        else:
            log.error("Cannot read channel status!")
            return False

        # Set the safety limits.
        if not self.__set_channel_safety_limits():
            log.error("Failed to set channel safety limits!")
            return False

        # Start the test.
        response = self.__send_receive_msg(msg_outging_dict)
        if response:
            if response['result']['Result'] != 'OK':
                log.error("Error starting test! Comment from Maccor: " +
                          response['result']['Result'])
                return False
            else:
                return True
        else:
            log.error("Failed to get message response when trying to start test!")
            return False

    def start_test_with_direct_control(self) -> bool:
        """
        Starts a test to be manually controlled with direct output on the channel specified in the config.

        Returns
        -------
        success : bool
            True of False based on whether the test was started or not.
        """

        msg_outging_dict = copy.deepcopy(
            pymacnet.messages.tx_start_test_with_direct_control_msg)
        msg_outging_dict['params']['Chan'] = self.channel
        msg_outging_dict['params']['DataTime'] = self.config['data_record_time_s']
        msg_outging_dict['params']['DataV'] = self.config['data_record_voltage_delta_vbys']
        msg_outging_dict['params']['DataI'] = self.config['data_record_current_delta_abys']
        # Make sure the start current is always zero.
        msg_outging_dict['params']['Current'] = 0
        # Set to something within range so it's not disabled.
        msg_outging_dict['params']['Voltage'] = self.config['v_max_v']
        # TODO: FIX having a weird issue where I can't set the mode to rest.
        msg_outging_dict['params']['ChMode'] = "C"

        # If test name is not specified then start test with a random test
        if not self.config['test_name']:
            msg_outging_dict['params']['TestName'] = "Random"
        else:
            msg_outging_dict['params']['TestName'] = self.config['test_name']

        # Check the status of the channel before we try to start the test.
        status = self.read_status()
        if status:
            if pymacnet.messages.status_dictionary[status['Stat']] == 'Completed':
                self.reset_channel()
        else:
            log.error("Cannot read channel status!")
            return False

        # Set the safety limits.
        if not self.__set_channel_safety_limits():
            log.error("Failed to set channel safety limits!")
            return False

        # Start the test
        response = self.__send_receive_msg(msg_outging_dict)
        if response:
            if response['result']['Result'] != 'OK':
                log.error("Error starting test! Comment from Maccor: " +
                          response['result']['Result'])
                return False
            else:
                return True
        else:
            log.error("Failed to get message response when trying to start test!")
            return False

    def set_direct_mode_output(self, current_a, voltage_v=4900) -> bool:
        """
        Sets the current/voltage output on the channel specified on in the config. Note that the
        test must have been started with the start_test_direct_control method for this to work.

        For discharging: Indicated with a negative sign on current. A lower voltage limit is set based on the
            `v_min_v` value set in the config.

        For charging: If only `current_a` is passed, the cycler will charge at the this current until commanded 
            otherwise or until the upper voltage safety limit is hit. If a `voltage_v` argument is passed in addition to `current_a`, then the cycler will do a CCCV 
            charge with the requested voltage.


        Returns
        -------
        success : bool
            True of False based on whether the values were set or not.
        """

        # Determine mode and voltage limits based on sign of passed current.
        if current_a == 0:
            set_current_a = 0
            set_voltage_v = 0
            mode = "R"
        elif current_a > 0:
            set_current_a = current_a
            set_voltage_v = voltage_v
            mode = "C"
        elif current_a < 0:
            set_current_a = abs(current_a)
            set_voltage_v = self.config['v_min_v']
            mode = "D"
        else:
            log.error("Undefined state is set direct control output!")
            return False

        # Determine range based on the magnitude of the current
        if set_current_a == 0:
            # Don't bother changing current range if we're just setting to zero.
            current_range = 4
        elif set_current_a < 0.000150:
            current_range = 1
        elif set_current_a < 0.005:
            current_range = 2
        elif set_current_a < 0.150:
            current_range = 3
        else:
            current_range = 4

        msg_outging_dict = copy.deepcopy(
            pymacnet.messages.tx_set_direct_output_msg)
        msg_outging_dict['params']['Chan'] = self.channel
        msg_outging_dict['params']['Current'] = set_current_a
        msg_outging_dict['params']['Voltage'] = set_voltage_v
        msg_outging_dict['params']['ChMode'] = mode
        msg_outging_dict['params']['CurrentRange'] = current_range

        # Send the rest command using the caveman method as JSON cannot set rest currently (10/4/2022)
        if mode == "R":
            return self.__send_rest_cmd_msg(msg_outging_dict)

        # Send message and make sure response indicates values were accepted.
        response = self.__send_receive_msg(msg_outging_dict)
        if response:
            if response['result']['Result'] == "OK":
                return True
            else:
                log.error("Error Setting output! Message : " + str(response))
                return False
        else:
            log.error("Failed to get message response when trying to set output!")
            return False

    def __send_rest_cmd_msg(self, msg_outging_dict) -> bool:
        """
        Commands rest step using caveman MacNet UDP/TCP method.

        Parameters
        ----------
        msg_outgoing_dict : dict
            A dictionary containing the message to be sent.

        Returns
        -------
        success : bool
            True of False based on whether or not rest was set
        """

        msg_outgoing_bytes = struct.pack('<HHHHffffBB',
                                         msg_outging_dict["params"]['FClass'],
                                         msg_outging_dict["params"]['FNum'],
                                         msg_outging_dict["params"]['Chan'],
                                         18,
                                         msg_outging_dict["params"]['Current'],
                                         msg_outging_dict["params"]['Voltage'],
                                         msg_outging_dict["params"]['Power'],
                                         msg_outging_dict["params"]['Resistance'],
                                         msg_outging_dict["params"]['CurrentRange'],
                                         ord('R'))

        try:
            self.__tcp_sock.send(msg_outgoing_bytes)
        except:
            log.error("Error sending rest message!", exc_info=True)
            return False
        try:
            response = self.__tcp_sock.recv(self.__msg_buffer_size_bytes)
        except:
            log.error("Error receiving rest message response!", exc_info=True)
            return False
        if response:
            # TODO: Should check something related to the response.
            pass
        else:
            log.error("No response for setting rest!")
            return False

        return True

    def __del__(self):
        """
        Kills cycler connections on death.
        """
        if self.__json_sock:
            self.__json_sock.close()

        if self.__tcp_sock:
            self.__tcp_sock.close()
