from src.Device import Device
from src.Frame import Command
import time


# NOTE: this file was only used for testing purposes and is now deprecated, TODO: remove


# create a new device object
dev = Device()
# establish the serial connection at port "COM9" with a BAUD of 115200
dev.SerialConnect("COM5", 115200)

# Send a color frame changing the first two leds
print("--- Color Test ---")
dev.SetColors([0xffffff, 0xabff15,0xabff15,0xabff15])
dev.Send()
time.sleep(1)
# Send a color frame only setting the first LED to white
print("--- Clear Color Test ---")
dev.SetCommand(Command.CLEAR)
dev.SetColors([0xffffff])
dev.Send()

# shift through leds using offset
for i in range(dev.configuration.ledCount):
    # set all leds to black
    dev.SetCommand(Command.CLEAR)
    # set the offset
    dev.frame.offset = i
    # set i'th led to white
    time.sleep(0.5)
    dev.SetColors([0xffffff])
    dev.Send()
    
# Error Tests
# todo
print("--- Invalid Offset Test ---")
dev.frame.offset = dev.configuration.ledCount
dev.SetColors([0xffffff])
dev.Send()


# Blink the builtin LED
# NOTE: this example needs Command ID 4 assigned to toggle the LED
print("--- Builtin LED blink ---")
dev.SetCommand(Command.LED_BUILTIN);
dev.Send()
time.sleep(1)
dev.SetCommand(Command.LED_BUILTIN);
dev.Send()

dev.Disconnect()
