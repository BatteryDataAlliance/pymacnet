import json
import pymacnet
import pymacnet.maccorspoofer

# Create Maccor Spoofer
spoofer_config_path = 'test_configs/server_config.json'
spoofer = maccorspoofer.MaccorSpoofer(spoofer_config_path)
spoofer.start()


def test_read_status():
    config_path = 'test_configs/test_config_1.json'
    with open(config_path, 'r') as file:
        config_dict = json.load(file)

    maccor_interface = pymacnet.MaccorInterface(config_dict)
    assert (maccor_interface.create_connection())

    expected_status_response = {'jsonrpc': '2.0',
                                'result': {'FClass': 4,
                                           'FNum': 7,
                                           'Chan': 93,
                                           'RF1': 0,
                                           'RF2': 192,
                                           'Stat': 0,
                                           'LastRecNum': 4225,
                                           'Cycle': 0,
                                           'Step': 5,
                                           'TestTime': 212.199996948242,
                                           'StepTime': 209.889999389648,
                                           'Capacity': 0,
                                           'Energy': 0,
                                           'Current': 0,
                                           'Voltage': 3.85938811302185,
                                           'TesterTime':
                                           '2022-10-13T12:32:56'},
                                'id': 1987}
    status_recevied = maccor_interface.read_status()
    assert (status_recevied == expected_status_response)


def test_read_aux():
    config_path = 'test_configs/test_config_1.json'
    with open(config_path, 'r') as file:
        config_dict = json.load(file)

    maccor_interface = pymacnet.MaccorInterface(config_dict)
    assert (maccor_interface.create_connection())

    expected_aux_response = {'jsonrpc': '2.0', 'result': {'FClass': 4, 'FNum': 4, 'Chan': 93, 'Len': 1, 'AuxValues': [24.7545490264893]}, 'id': 1987}
    aux_recevied = maccor_interface.read_aux()
    assert (aux_recevied == expected_aux_response)


def test_set_channel_variables():
    config_path = 'test_configs/test_config_1.json'
    with open(config_path, 'r') as file:
        config_dict = json.load(file)

    maccor_interface = pymacnet.MaccorInterface(config_dict)
    assert (maccor_interface.create_connection())

    expected_channel_variables_response = {'jsonrpc': '2.0', 'result': {'FClass': 6, 'FNum': 9, 'Chan': 93, 'Result': 'OK'}, 'id': 1987}
    channel_variables_recevied = maccor_interface.set_channel_variables()
    assert (channel_variables_recevied == expected_channel_variables_response)


def test_start_test_with_procedure():
    config_path = 'test_configs/test_config_1.json'
    with open(config_path, 'r') as file:
        config_dict = json.load(file)

    maccor_interface = pymacnet.MaccorInterface(config_dict)
    assert (maccor_interface.create_connection())

    expected_start_test_with_procedure_response = {'jsonrpc': '2.0', 'result': {'FClass': 6, 'FNum': 2, 'Chan': 93, 'Result': 'OK'}, 'id': 1987}
    start_test_with_procedure_recevied = maccor_interface.start_test_with_procedure()
    assert (start_test_with_procedure_recevied == expected_start_test_with_procedure_response)


def test_start_test_with_direct_control():
    config_path = 'test_configs/test_config_1.json'
    with open(config_path, 'r') as file:
        config_dict = json.load(file)

    maccor_interface = pymacnet.MaccorInterface(config_dict)
    assert (maccor_interface.create_connection())

    expected_direct_control_response = {'jsonrpc': '2.0', 'result': {'FClass': 6, 'FNum': 7, 'Chan': 93, 'Result': 'OK'}, 'id': 1987}
    direct_control_recevied = maccor_interface.start_test_with_direct_control()
    assert (direct_control_recevied == expected_direct_control_response)


def test_set_direct_mode_output():
    config_path = 'test_configs/test_config_1.json'
    with open(config_path, 'r') as file:
        config_dict = json.load(file)

    maccor_interface = pymacnet.MaccorInterface(config_dict)
    assert (maccor_interface.create_connection())

    expected_set_direct_mode_output_response = {'jsonrpc': '2.0', 'result': {'FClass': 6, 'FNum': 8, 'Chan': 93, 'Result': 'OK'}, 'id': 1987}
    set_direct_mode_output_recevied = maccor_interface.set_direct_mode_output()
    assert (set_direct_mode_output_recevied == expected_set_direct_mode_output_response)


test_read_status()
test_read_aux()
test_set_channel_variables()
test_start_test_with_procedure()
test_start_test_with_direct_control()
test_set_direct_mode_output()

spoofer.kill()
