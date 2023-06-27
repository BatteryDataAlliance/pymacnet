import logging
import copy
import pymacnet.messages
from datetime import datetime
from .cycler_interface import CyclerInterface

logger = logging.getLogger(__name__)


class ChannelInterface(CyclerInterface):
    """
    Class for controlling Maccor Cycler using MacNet.
    """

    def __init__(self, config: dict):
        """
        Creates a ChannelInterface class instance.

        Parameters
        ----------
        config : dict
            A configuration dictionary. Must contain the following keys:
            - `server_ip` - The IP address of the Maccor server. Use 127.0.0.1 if running on the same machine as the server.
            - `json_msg_port` - The port to communicate through with JSON messages. Default set to 57570.
            - `bin_msg_port` - The port to communicate through with binary messages. Default set to 57560.
            - `msg_buffer_size_bytes` - How big of a message buffer to use for sending/receiving messages. A minimum of 1024 bytes is recommended. 
            - `channel` - The channel to be targeted for all operations.
            - `test_name` - The test name to be used for any tests started. If left blank, Maccor will generate a unique random name for any started tests. Note that Maccor requires unique test names for each test.
            - `test_procedure` - The test procedure to be used, if starting a test with a procedure. Not needed with direct control.
            - `c_rate_ah` - The capacity value to be referenced when setting "C" values within the Maccor schedule. Units of amp-hours. Ignored if not used anywhere in the test.
            - `v_max_safety_limit_v` - Upper voltage safety limit for the channel. Units of volts.
            - `v_min_safety_limit_v` - Lower voltage safety limit for the channel. Units of volts.
            - `i_max_safety_limit_a` - Upper current safety limit for the channel. Units of amps.
            - `i_min_safety_limit_a` - Lower current safety limit for the channel. Units of amps.
            - `v_max_v` - Upper voltage limit used for charge/CV limits. Units of volts. Only used with direct control.
            - `v_min_v` - Lower voltage limit used for discharge limit. Units of volts. Only used with direct control.
            - `data_record_time_s` - How often data points are taken during direct control tests. Zero turns off. Used only for direct control.
            - `data_record_voltage_delta_vbys` - The dV/dt at which data points are taken during direct control tests. Zero disables. Used only for direct control.
            - `data_record_current_delta_abys` - The dI/dt at which data points are taken during direct control tests. Zero disables. Used only for direct control.
        """

        # Channels are zero indexed within MacNet so we must subtract one here.
        self.__channel = config['channel'] - 1
        self.__config = config

        assert (self.__verify_config())
        super().__init__(config=config)

    def get_channel_number(self):
        '''
        Returns the channel number for the class instance.
        '''
        return self.__channel

    def read_channel_status(self) -> dict:
        """
        Method to read the status of the channel defined in the config.

        Returns
        -------
        status : dict
            A dictionary detailing the status of the channel. Returns None if there is an issue.
        """
        
        # Add 1 to channel index since 1 is subtracted as part of init.
        return super().read_channel_status(channel=(self.__channel+1))

    def read_aux(self) -> list:
        """
        Reads the auxiliary readings for the channel specified in the config.

        Returns
        -------
        aux_readings : list
            A list of the auxiliary readings.
        """

        msg_outgoing_dict = copy.deepcopy(pymacnet.messages.tx_read_aux_msg)
        msg_outgoing_dict['params']['Chan'] = self.__channel

        aux_readings = self._send_receive_json_msg(msg_outgoing_dict)
        if aux_readings:
            return aux_readings['result']['AuxValues']
        else:
            logger.error("Failed to read channel aux values!")
            return None

    def reset_channel(self) -> bool:
        """
        Resets the channel. Note this will stop any actively running test on the target channel.

        Returns
        -------
        success : bool
            True of False based on whether the test was started or not.
        """
        msg_outgoing_dict = copy.deepcopy(
            pymacnet.messages.tx_reset_channel_msg
        )
        msg_outgoing_dict['params']['Chan'] = self.__channel

        reply = self._send_receive_json_msg(msg_outgoing_dict)
        if reply:
            if reply['result']['Result'] == 'OK':
                success = True
            else:
                logger.error("Failed reset channel! Channel did not reset!")
                success = False
        else:
            logger.error("Failed reset channel! Did not receive reply!")
            success = False

        return success

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
        msg_outgoing_dict = copy.deepcopy(
            pymacnet.messages.tx_set_variable_msg)
        msg_outgoing_dict['params']['Chan'] = self.__channel
        msg_outgoing_dict['params']['VarNum'] = var_num
        msg_outgoing_dict['params']['Value'] = var_value

        # Check to make variable was set
        reply = self._send_receive_json_msg(msg_outgoing_dict)
        if reply:
            try:
                assert ((reply['result']['Chan']) == self.__config['channel'])
                assert (reply['result']['Result'] == 'OK')
            except:
                logger.error("Variable not set!")
                return False
        else:
            logger.error(
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
        msg_outgoing_dict = copy.deepcopy(
            pymacnet.messages.tx_start_test_with_procedure_msg)
        msg_outgoing_dict['params']['Chan'] = self.__channel
        msg_outgoing_dict['params']['ProcName'] = self.__config['test_procedure']
        msg_outgoing_dict['params']['Crate'] = self.__config['c_rate_ah']
        msg_outgoing_dict['params']['Comment'] = "Started with pymacnet at " + \
            str(datetime.timestamp(datetime.now()))

        # If test name is not specified then start test with a random test
        if not self.__config['test_name']:
            msg_outgoing_dict['params']['TestName'] = 'Random'
        else:
            msg_outgoing_dict['params']['TestName'] = self.__config['test_name']

        # Check the status of the channel before we try to start the test.]
        status = self.read_channel_status()
        if status:
            if pymacnet.messages.status_dictionary[status['Stat']] == 'Completed':
                self.reset_channel()
        else:
            logger.error("Cannot read channel status!")
            return False

        # Set the safety limits.
        if not self.__set_channel_safety_limits():
            logger.error("Failed to set channel safety limits!")
            return False

        # Start the test.
        response = self._send_receive_json_msg(msg_outgoing_dict)
        if response:
            if response['result']['Result'] != 'OK':
                logger.error("Error starting test! Comment from Maccor: " +
                             response['result']['Result'])
                return False
            else:
                return True
        else:
            logger.error(
                "Failed to get message response when trying to start test!")
            return False

    def start_test_with_direct_control(self) -> bool:
        """
        Starts a test to be manually controlled with direct output on the channel specified in the config.

        Returns
        -------
        success : bool
            True of False based on whether the test was started or not.
        """

        msg_outgoing_dict = copy.deepcopy(
            pymacnet.messages.tx_start_test_with_direct_control_msg)
        msg_outgoing_dict['params']['Chan'] = self.__channel
        msg_outgoing_dict['params']['DataTime'] = self.__config['data_record_time_s']
        msg_outgoing_dict['params']['DataV'] = self.__config['data_record_voltage_delta_vbys']
        msg_outgoing_dict['params']['DataI'] = self.__config['data_record_current_delta_abys']
        # Make sure the start current is always zero.
        msg_outgoing_dict['params']['Current'] = 0
        # Set to something within range so it's not disabled.
        msg_outgoing_dict['params']['Voltage'] = self.__config['v_max_v']
        # TODO: FIX having a weird issue where I can't set the mode to rest.
        msg_outgoing_dict['params']['ChMode'] = "C"

        # If test name is not specified then start test with a random test
        if not self.__config['test_name']:
            msg_outgoing_dict['params']['TestName'] = "Random"
        else:
            msg_outgoing_dict['params']['TestName'] = self.__config['test_name']

        # Check the status of the channel before we try to start the test.
        status = self.read_channel_status()
        if status:
            if pymacnet.messages.status_dictionary[status['Stat']] == 'Completed':
                self.reset_channel()
        else:
            logger.error("Cannot read channel status!")
            return False

        # Set the safety limits.
        if not self.__set_channel_safety_limits():
            logger.error("Failed to set channel safety limits!")
            return False

        # Start the test
        response = self._send_receive_json_msg(msg_outgoing_dict)
        if response:
            if response['result']['Result'] != 'OK':
                logger.error("Error starting test! Comment from Maccor: " +
                             response['result']['Result'])
                return False
            else:
                return True
        else:
            logger.error(
                "Failed to get message response when trying to start test!")
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
            set_voltage_v = self.__config['v_min_v']
            mode = "D"
        else:
            logger.error("Undefined state is set direct control output!")
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

        msg_outgoing_dict = copy.deepcopy(
            pymacnet.messages.tx_set_direct_output_msg)
        msg_outgoing_dict['params']['Chan'] = self.__channel
        msg_outgoing_dict['params']['Current'] = set_current_a
        msg_outgoing_dict['params']['Voltage'] = set_voltage_v
        msg_outgoing_dict['params']['ChMode'] = mode
        msg_outgoing_dict['params']['CurrentRange'] = current_range

        # Send the rest command using the caveman method as JSON cannot set rest currently (10/4/2022)
        if mode == "R":
            return self._send_direct_output_rest_bin_msg(msg_outgoing_dict)
        else:
            # Send message and make sure response indicates values were accepted.
            response = self._send_receive_json_msg(msg_outgoing_dict)
            if response:
                if response['result']['Result'] == "OK":
                    return True
                else:
                    logger.error(
                        "Error Setting output! Message : " + str(response))
                    return False
            else:
                logger.error(
                    "Failed to get message response when trying to set output!")
                return False

    def __set_channel_safety_limits(self) -> bool:
        """
        Sets channel safety limits on the channel specified in the config. 

        Returns
        -------
        success : bool
            Returns True/False based on whether the safety limits were set correctly.
        """
        msg_outgoing_dict = copy.deepcopy(
            pymacnet.messages.tx_set_safety_limits_msg
        )
        msg_outgoing_dict['params']['Chan'] = self.__channel
        msg_outgoing_dict['params']['VSafeMax'] = self.__config['v_max_safety_limit_v']
        msg_outgoing_dict['params']['VSafeMin'] = self.__config['v_min_safety_limit_v']
        msg_outgoing_dict['params']['ISafeChg'] = self.__config['i_max_safety_limit_a']
        msg_outgoing_dict['params']['ISafeDis'] = self.__config['i_min_safety_limit_a']

        # Check to make sure all safety limits were set correctly
        reply = self._send_receive_json_msg(msg_outgoing_dict)
        if reply:
            try:
                assert ((reply['result']['Chan']) == self.__config['channel'])
                assert (abs(reply['result']['VSafeMax'] -
                        self.__config['v_max_safety_limit_v']) < 0.001)
                assert (abs(reply['result']['VSafeMin'] -
                        self.__config['v_min_safety_limit_v']) < 0.001)
                assert (abs(reply['result']['ISafeChg'] -
                        self.__config['i_max_safety_limit_a']) < 0.001)
                assert (abs(reply['result']['ISafeDis'] -
                        self.__config['i_min_safety_limit_a']) < 0.001)
            except:
                logger.error(
                    "Set safety limits to not match sent safety limits! Message response: " + str(reply))
                return False
        else:
            logger.error(
                "Failed to receive reply message when trying to set safety limits!")
            return False

        return True

    def __verify_config(self) -> bool:
        """
        Verifies that the config passed on construction is valid.

        Returns
        --------------------------
        success : bool
            True or False based on whether the config passed at construction is valid.
        """
        success = False

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
                                'json_msg_port',
                                'bin_msg_port']

        missing_keyes = False
        for key in required_config_keys:
            if key not in self.__config:
                logger.error("Missing key from config! Missing : " + key)
                missing_keyes = True

        if not missing_keyes:
            success = True

        return success
