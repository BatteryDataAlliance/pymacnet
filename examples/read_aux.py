'''
Example of how to read channel aux readings
'''
import json
import pymacnet 
import time
import sys


config_path = 'example_config_1.json'
with open(config_path, 'r') as file:
    config_dict = json.load(file)
    
maccor_interface = pymacnet.MaccorInterface(config_dict)
if not maccor_interface.create_connection():
    sys.exit("failed to create connection!")

for i in range(0,5):
    print(maccor_interface.read_aux()[0])
    time.sleep(0.5)