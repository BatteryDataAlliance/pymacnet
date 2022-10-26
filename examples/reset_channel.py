'''
Example of how set vaiable on a channel.

MAKE SURE A TEST WITH A VARIABLE IS SET ON CHA
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


print(maccor_interface._reset_channel(var_num = 1, var_value = set_current))
