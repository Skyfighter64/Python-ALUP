import serial
import logging

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
        self._rxBuffer = bytearray()
        self.logger = logging.getLogger(__name__)

    # Establishes the connection; Blocks until finished
    def Connect(self):
        self.connection = serial.Serial(self.port, self.baud)
        self.connection.reset_output_buffer()
        self.connection.reset_input_buffer()

    # function terminating the connection
    def Disconnect(self):
        self.connection.flush()
        self.connection.close()

    # function sending the given data over the connection
    # @param data: a bytes object containing the data to send
    def Send(self, data):
        self.logger.debug("[>>>]: " + str(data))
        self.connection.write(data)
        self.connection.flush()

    # Function reading in the given size of data from the connection
    # Blocks until the requested number of bytes was received or the timeout is exceeded
    # @param size: an integer specifying the amount of bytes to read
    # @param timeout: timeout in ms. If there is no data received within the timeout, a TimeoutError is raised.
    #                 0 for non-blocking mode, None for full blocking mode. For more info, see pySerial docs.
    #                 Default: 0
    # @return: a bytes object containing the read bytes
    def Read(self, size, timeout=0):
        # apply the timeout to the serial connection
        if (timeout != self.connection.timeout):
            self.connection.timeout = (timeout / 1_000) if timeout is not None else None

        # NOTE: we need to buffer the incoming bytes here in case of an exception.
        # The reason for this is the way pySerial handles read timeouts.
        # When reading the next time, we first check the buffer and then read in the 
        # remaining needed data 

        # check how many bytes are already buffered
        sizeToRead = size - len(self._rxBuffer)
        sizeToRead = max(0, sizeToRead)

        #NOTE: this will return all already read bytes even if the timeout is reached
        # Therefore, if it times out we would be loosing data if we wouldn't buffer.
        if(sizeToRead > 0):
            incomingBytes = self.connection.read(sizeToRead)
            self._rxBuffer += incomingBytes
            # check if the read call timed out or returned successfully
            if len(incomingBytes) < size:
                raise TimeoutError

        # get the requested amount of bytes from the buffer
        result = self._rxBuffer[:size]
        #delete the requested bytes from the buffer
        del self._rxBuffer[:size]

        self.logger.debug("[<<<]: " + str(result))
        return result

    def __str__(self):
        return f"SerialConnection({self.port}:{self.baud})"