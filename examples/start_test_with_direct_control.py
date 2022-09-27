import pymacnet
import json
import time
import sys

config_path = 'example_config_1.json'
with open(config_path, 'r') as file:
    config_dict = json.load(file)

maccor_interface = pymacnet.MaccorInterface(config_dict)
if not maccor_interface.create_connection():
    sys.exit("failed to create connection!")

if maccor_interface.start_test_with_direct_control():
    print("Test started!")
else:
    sys.exit("Failed to start test!")

time.sleep(5) # Must wait at least 100 ms between trying to set control

i = 1.0
for i in range(0,5):
    maccor_interface.set_direct_mode_output(current_a = (i*0.1))
    time.sleep(5)
    i = i + 1

maccor_interface.set_direct_mode_output(current_a = 0.0)