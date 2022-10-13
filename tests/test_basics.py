import pymacnet
import json
import maccor_spoofer

# Create Maccor Spoofer
spoofer_config_path = 'test_configs/maccor_spoofer_config.json'
spoofer = maccor_spoofer.MaccorSpoofer(spoofer_config_path)
spoofer.start()

def basic_test():
    config_path = 'test_configs/test_config_1.json'
    with open(config_path, 'r') as file:
        config_dict = json.load(file)
    
    maccor_interface = pymacnet.MaccorInterface(config_dict)
    assert(maccor_interface.create_connection())

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
    assert(status_recevied==expected_status_response)

spoofer.kill()