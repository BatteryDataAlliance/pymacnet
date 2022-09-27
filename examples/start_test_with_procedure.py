'''
Example how to start a test with a test procedure using the Maccor interface.
'''

import pymacnet
import json
import time

config_path = 'example_config_1.json'
with open(config_path, 'r') as file:
    config_dict = json.load(file)

maccor_interface = pymacnet.MaccorInterface(config_dict)
if not maccor_interface.create_connection():
    print("failed to create connection!")

print(maccor_interface.read_status())
maccor_interface.start_test_with_procedure()
#print(maccor_interface.read_status())