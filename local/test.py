from src.UdpConnection import UdpConnection


dev = UdpConnection("127.0.0.1", 1026)
dev.server_port = 1025
dev.Connect()
while True:
    #dev.Send("Hello there".encode("ascii"))
    print(str(dev.Read(4).decode("ascii")))