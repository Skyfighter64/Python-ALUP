from pyalup.Device import Device
from pyalup.Frame import Command
import time

# create a new device object
dev = Device()
# establish the serial connection to the ALUP device
dev.SerialConnect("COM6", 115200)
print("Connected")

# Blink all LEDs every second
try:
    while(True):
        # set all LEDs to red
        dev.SetColors([0xff0000] * dev.configuration.ledCount)
        dev.Send()
        print("--- Blink ---")

        time.sleep(1)
        # set all LEDs to black
        dev.Clear()
        time.sleep(1)
        
except KeyboardInterrupt:
    print(" CTL + C pressed. Stopping...")

# clear all LEDs and disconnect device
dev.Clear()
dev.Disconnect()
