from src.Device import Device
from src.Frame import Command
import time

# create a new device object
dev = Device()
#establish the serial connection at port "COM9" with a BAUD of 115200
dev.SerialConnect("COM9", 115200)

# Send a color frame changing the first two leds
print("--- Color Test ---")
dev.SetColors([0xffffff, 0xabff15])
dev.Send()

# Send a color frame only setting the 2nd LED to white
print("--- Clear Color Test ---")
dev.SetCommand(Command.CLEAR)
dev.offset = 1
dev.SetColors([0xffffff])
dev.Send()

# Blink the builtin LED
# NOTE: this example needs Command ID 4 assigned to toggle the LED
print("--- Builtin LED blink ---")
dev.SetCommand(Command.LED_BUILTIN);
dev.Send()
sleep(1)
dev.SetCommand(Command.LED_BUILTIN);
dev.Send()

dev.Disconnect()
