'''
Example how to start a test with a test procedure.
'''
import pymacnet
import json
import sys

config_path = 'example_config_1.json'
with open(config_path, 'r') as file:
    config_dict = json.load(file)

maccor_interface = pymacnet.MaccorInterface(config_dict)
if not maccor_interface.start():
    sys.exit("failed to create connection!")

if maccor_interface.start_test_with_procedure():
    print("Test started!")