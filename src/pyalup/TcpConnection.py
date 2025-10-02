import socket


class TcpConnection:
    # default constructor
    # @param ip: a string containing the ip address of the remote device
    # @param port: the port number of the remote socket
    def __init__(self, ip, port):
        # ip and port of the ALUP client device
        self.remote_ip = ip
        self.remote_port = port
        self.socket = None
        # a buffer for incoming bytes. recv() only seems to be able to read whole packages,
        # docs are unclear, so this seems to be needed
        self._rxBuffer = bytearray()

    # function establishing the TCP connection to the specified device
    def Connect(self):
        # create a TCP socket for the given credentials
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.socket.settimeout(15)
        self.socket.connect((self.remote_ip, self.remote_port))

    # function disconnecting the TCP connection
    def Disconnect(self):
        self.socket.close()

    # function sending the given data over the Socket connection
    # @param data: a bytes object containing the binary data to send
    def Send(self, data):
        self.socket.send(data)

    # function reading in data from the socket and returning the requested number
    # of bytes.
    # @param size: the number of bytes to read from the rx buffer
    # @param timeout: timeout in ms. If there is no data received within the timeout, a TimeoutError is raised.
    #                 0 for non-blocking mode, None for full blocking mode. For more info, see socket docs.
    #                 Default: 0
    #                 NOTE: the timeout is per-packet, each packet has its own timeout when reading multiple packets
    # @return the binary data received from the socket
    # @raises: TimeoutError if the given timeout is exceeded
    def Read(self, size, timeout=0):
        self.socket.settimeout((timeout / 1_000) if timeout is not None else None)
        while (len(self._rxBuffer) < size):
            # not enough data in buffer
            # read in a new packet
            (data, address) = self.socket.recvfrom(4096)

            # add the read data to the buffer
            self._rxBuffer += data

        # get the requested amount of bytes from the buffer
        result = self._rxBuffer[:size]
        #delete the requested bytes from the buffer
        del self._rxBuffer[:size]

        return result
