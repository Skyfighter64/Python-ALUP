import socket
import logging

class UdpConnection:
    # default constructor
    # @param ip: a string containing the ip address of the remote device
    # @param port: the port number of the remote socket
    def __init__(self, ip, port):
        self.remote_ip = ip
        self.remote_port = port
        self.socket = None
        self.server_ip = '0.0.0.0'
        # use the same port as the remote per default
        self.server_port = port
        #note: the remote ip/port describe the sending ip/port and the server ip/port
        # ones used for listening
        # a buffer for incoming bytes. recv() only seems to be able to read whole packages,
        # docs are unclear, so this seems to be needed s
        self._rxBuffer = bytearray()

        self.logger = logging.getLogger(__name__)

    # function establishing the UDP connection to the specified device
    def Connect(self):
        # create an UDP socket for the given credentials
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # set the ip and port on this end of the connection
        self.socket.bind((self.server_ip, self.server_port))
        print("Listening to %s, %d:" %(self.server_ip, self.server_port))
        print("Sending to: %s, %d" %(self.remote_ip, self.remote_port))

    # function disconnecting the UDP connection
    def Disconnect(self):
        self.socket.close()

    # function sending the given data over the UDP connection
    # @param data: a bytes object containing the binary data to send
    def Send(self, data):
        print("Sending: " + str(data))
        self.socket.sendto(data, (self.remote_ip, self.remote_port))

    # function reading in data from the socket and returning the requested number
    # of bytes.
    # Note: This function is blocking until the requested number of bytes has been received
    # @param size: the number of bytes to read from the rx buffer
    # @return the binary data received from the socket
    def Read(self, size):
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
