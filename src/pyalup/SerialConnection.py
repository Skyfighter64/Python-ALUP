import serial

#
#   This class requires pySerial to be installed
#   Install using "pip3 install pySerial"
#
class SerialConnection:

    # default constructor
    # @param port: a string containing the Serial port to connect to
    # @param baud: an integer defining the communication speed
    def __init__(self, port, baud):
        self.port = port
        self.baud = baud
        self.connection = None

    # Establishes the connection; Blocks until finished
    def Connect(self):
        self.connection = serial.Serial(self.port, self.baud)

    # function terminating the connection
    def Disconnect(self):
        self.connection.close()

    # function sending the given data over the connection
    # @param data: a bytes object containing the data to send
    def Send(self, data):
        self.connection.write(data)

    # Function reading in the given size of data from the connection
    # Blocks until the requested number of bytes was received
    # @param size: an integer specifying the amount of bytes to read
    # @return: a bytes object containing the read bytes
    def Read(self, size):
        return self.connection.read(size)
