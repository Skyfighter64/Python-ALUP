from src.UdpConnection import UdpConnection


dev = UdpConnection("127.0.0.1", 1025)
dev.server_port = 1027
dev.Connect()
while True:
    dev.Send("Hello there".encode("ascii"))