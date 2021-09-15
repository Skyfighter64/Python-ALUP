from src.Device import Device
from src.Frame import Command


dev = Device()
dev.UdpConnect('192.168.178.105', 5012)
dev.SetColors([0xffffff, 0x00ff00])
dev.Send()
dev.SetCommand(Command.CLEAR)
dev.SetColors([0xffffff,0x1252ff, 0x824347])
dev.Send()
dev.Disconnect()