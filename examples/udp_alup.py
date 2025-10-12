from pyalup.Device import Device
from pyalup.Frame import Command
import time

# connect
dev = Device()
dev.UdpConnect('192.168.178.105', 5012)

#send a frame with some colors
dev.SetColors([0xffffff, 0x00ff00])
dev.Send()
# send a frame with colors and a command
dev.SetCommand(Command.CLEAR)
dev.SetColors([0xffffff,0x1252ff, 0x824347])
dev.Send()

# send a command
dev.SetCommand(Command.LED_BUILTIN);
dev.Send()

time.sleep(1);
dev.SetCommand(Command.LED_BUILTIN);
dev.Send()
# disconnect
dev.Disconnect()
