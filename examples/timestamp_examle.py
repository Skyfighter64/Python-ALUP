from pyalup.Device import Device
from pyalup.Frame import Command
import time


"""
Time stamps use synchronized time between the sender and receiver to 
specify the time in ms at which the LEDs should change.
"""

# create a new device object
dev = Device()
# establish the serial connection to the ALUP device
dev.SerialConnect("COM6", 115200)
print("--- Connected ---")

# calibrate the time synchronization
dev.Calibrate()
print("--- Calibrated ---")


# Blink all LEDs every second
try:
    while(True):
        # set all LEDs to red
        dev.SetColors([0xff0000] * dev.configuration.ledCount)

        # set the timestamp to one second from now
        dev.frame.timestamp = (time.time_ns() // 1_000_000) + 1000 
        dev.Send()
        print("--- Blink ---")

        # set all LEDs to black after 1 second from now
        dev.Clear(timestamp=(time.time_ns() // 1_000_000) + 1000)
        time.sleep(1)

except KeyboardInterrupt:
    print(" CTL + C pressed. Stopping...")


# clear all LEDs and disconnect device
dev.Clear()
dev.Disconnect()
