'''
Example how to create a connection with the Maccor interface and read channel status
'''

import json
import pymacnet 
import time

config_path = 'example_config_1.json'
with open(config_path, 'r') as file:
    config_dict = json.load(file)

maccor_interface = pymacnet.MaccorInterface(config_dict)

if not maccor_interface.create_connection():
    print("failed to create connection!")

for i in range(0,5):
    status = maccor_interface.read_status()
    print(status)
    time.sleep(0.5)


