'''
Example of how to start a test with direct control and control charge/discharge current.
'''
import pymacnet
import json
import time
import sys

config_path = 'example_config_1.json'
with open(config_path, 'r') as file:
    config_dict = json.load(file)

maccor_interface = pymacnet.MaccorInterface(config_dict)
if not maccor_interface.start():
    sys.exit("failed to create connection!")

if maccor_interface.start_test_with_direct_control():
    print("Test started!")
else:
    sys.exit("Failed to start test!")

time.sleep(5) # Must wait at least 100 ms between trying to set control

# Set the starting current
start_current_a = 0.02
dwell_time_s = 0.25
num_steps = 100

# Discharge for 100 Steps
for i in range(1,num_steps+1):
    maccor_interface.set_direct_mode_output(current_a = (0 - start_current_a*i))
    time.sleep(dwell_time_s)

# Must wait at least 100 ms between trying to set control
maccor_interface.set_direct_mode_output(current_a = 0)
time.sleep(5) 

# Charge for 100 Steps
for i in range(1,num_steps+1):
    maccor_interface.set_direct_mode_output(current_a = (0 + start_current_a*i))
    time.sleep(dwell_time_s)

maccor_interface.set_direct_mode_output(current_a = 0.0)
print("Test Complete!")