from pyalup.Device import Device
from pyalup.Frame import Command
import time

# create a new device object
dev = Device()
# connect to a device in the network with the specified IP address and port
dev.TcpConnect("127.0.0.1", 5012)

# Send a color frame changing the first two leds
print("--- Color Test ---")
dev.SetColors([0xffffff, 0xabff15])
dev.Send()

time.sleep(1)

# Send a color frame only setting the 2nd LED to white
print("--- Clear Color Test ---")
dev.SetCommand(Command.CLEAR)
dev.offset = 1
dev.SetColors([0xffffff])
dev.Send()

time.sleep(1)

# Blink the builtin LED
# NOTE: this example needs Command ID 4 assigned to toggle the LED
print("--- Builtin LED blink ---")
dev.SetCommand(Command.LED_BUILTIN)
dev.Send()
time.sleep(1)
dev.SetCommand(Command.LED_BUILTIN)
dev.Send()

dev.Clear()
dev.Disconnect()
