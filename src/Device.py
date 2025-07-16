from src.UdpConnection import UdpConnection
from src.SerialConnection import SerialConnection
from src.Frame import *
from src.Configuration import Configuration
import time
import logging




class Device:

    # protocol constants
    _CONNECTION_REQUEST_BYTE = b'\xff'
    _CONNECTION_ACKNOWLEDGEMENT_BYTE = b'\xfe'
    _CONFIGURATION_START_BYTE = b'\xfd'
    _CONFIGURATION_ACKNOWLEDGEMENT_BYTE = b'\xfc'
    _CONFIGURATION_ERROR_BYTE = b'\xfb'
    _FRAME_ACKNOWLEDGEMENT_BYTE = b'\xfa'
    _FRAME_ERROR_BYTE = b'\xf9'

    # a list of all supported protocol versions
    PROTOCOL_VERSIONS = ["0.2"]

    def __init__(self):
        self.connection = None
        self.connected = False
        self.frame = Frame()
        self.configuration = None
        self.logger = logging.getLogger(__name__)
        


    # function starting an ALUP/UDP connection
    # @param ip: a string containing the ip address od the device to connect to
    # @param port: an int containing the UDP port of the device to use
    def UdpConnect(self, ip, port):
        self.connection = UdpConnection(ip,port)
        self.connection.Connect()
        self._AlupConnect()
        self.logger.info("UDP Connection to %s:%d established." % (ip, port))

    # function starting an ALUP/Serial connection
    # @param port: a string containing the serial port to connect to
    # @param baud: an integer defining the serial communication speed
    def SerialConnect(self, port, baud):
        self.connection = SerialConnection(port, baud)
        self.connection.Connect()
        self._AlupConnect()
        self.logger.info("Serial Connection to %s:%d established." % (port, baud))


    # function establishing the ALUP connection
    # Note: the communication has to be established first
    def _AlupConnect(self):
        self._WaitForConnectionRequest()
        self._SendByte(self._CONNECTION_ACKNOWLEDGEMENT_BYTE)
        self.configuration = self._ReadConfiguration()
        self.connected = True

    # function terminating the connection
    def Disconnect(self):
        #self.SetColors([0xffffff])
        self.SetCommand(Command.DISCONNECT)
        self.Send()
        self.connected = False
        self.connection.Disconnect()
        self.logger.info("Disconnected.")


    # function setting the color values for the next frame
    # @param colors: an array of RGB values in hexadecimal representation eg: [0xffffff, 0x00ff00]
    def SetColors(self, colors):
        self.frame.colors = colors

    # function setting the command for the next frame
    # @param command: a Frame.Command value
    def SetCommand(self, command):
        self.frame.command = command

    # function sending the current frame to the device and waiting for an acknowledgement
    def Send(self):
        #pingStart = round(time.time() * 1000)
        self.SendFrame()
        self._WaitForFrameAcknowledgement()
        #print("Ping: " + str((round(time.time() * 1000) - pingStart)) + "ms")

    # function sending the current frame without waiting for an acknowledgement
    # Improper usage may result in connection freeze
    def SendFrame(self):
        self.logger.debug("Sending frame:")
        frameBytes = self.frame.ToBytes()
        self.logger.debug("\n" + str(self.frame))
        self.logger.debug("Total Frame size: %d" % (len(frameBytes)))
        self.logger.debug("Hex Data:\n %s" % (frameBytes.hex()))
        self.connection.Send(frameBytes)
        # clear the frame
        self.frame = Frame()

    # Set all LEDs to black by sending a clear command
    def Clear(self):
        self.SetCommand(Command.CLEAR)
        self.Send()

    # function reading in the configuration
    # @return: The configuration object read
    # @throws: ConfigurationException if the protocol version of the devices are incompatible
    def _ReadConfiguration(self):
        # wait for the configuration start byte
        while(self.connection.Read(1) != self._CONFIGURATION_START_BYTE):
            #print("- Waiting for Configuration Start")
            pass

        config = Configuration()
        #read in the protocol version
        config.protocolVersion = self._ReadString()
        # check if the protocol version is compatible
        if (not self._CheckProtocolVersion(config.protocolVersion)):
            raise ConfigurationException("Incompatible protocol versions: Version 0.2 (this) and " + config.protocolVersion)

        # read the configuration values
        config.deviceName = self._ReadString()
        config.ledCount = self._ReadInt()
        config.dataPin = self._ReadInt()
        config.clockPin = self._ReadInt()
        config.extraValues = self._ReadString()

        #print("Received config:" + str(config))
        self._SendByte(self._CONFIGURATION_ACKNOWLEDGEMENT_BYTE)

        return config




    # function checking the protocol versions of both devices for compatibility
    # @param protocolVersion: a string representing the protocol version
    # @return: True if versions are compatible, else False
    def _CheckProtocolVersion(self, protocolVersion):
        self.logger.debug("Checking Protocol versions:\n\tDevice: %s\n\tCompatible Versions: %s" % (protocolVersion, str(self.PROTOCOL_VERSIONS)))
        if (protocolVersion not in self.PROTOCOL_VERSIONS):
            self.logger.error("Protocol Version Check: Device Protocol version %s is not supported." % (protocolVersion))
            # send a configuration error indicating that the versions are incompatible
            self._SendByte(self._CONFIGURATION_ERROR_BYTE)
            return False
        self.logger.info("Protocol Version Check: Device Protocol version %s is compatible." % (protocolVersion))
        return True


    # function waiting for a connection request
    def _WaitForConnectionRequest(self):
        self.logger.info("Waiting for connection request from device")
        # wait for the connection request
        while(True):
            if (self.connection.Read(1) == self._CONNECTION_REQUEST_BYTE):
                self.logger.info("Received connection request from device")
                return



    # function reading a null-terminated string from the connection
    # @return: the received utf-8 string
    def _ReadString(self):
        receivedBytes = b''
        # read in all bytes until a null terminator is read
        b = self.connection.Read(1)
        while(b != b'\x00'):
            receivedBytes += b
            b = self.connection.Read(1)

        return receivedBytes.decode('utf-8')

    # function reading a 32bit 2s complement integer value from the connection
    def _ReadInt(self):
        b = self.connection.Read(4)
        return int.from_bytes(b, byteorder='big', signed=True)

    # function sending a single byte over the connection
    def _SendByte(self, b):
        self.connection.Send(b)

    # function waiting for a frame acknowledgement or frame error
    def _WaitForFrameAcknowledgement(self):
        startTime = time.time_ns() / 1000000
        elapsedTime = 0

        # timeout for this function in ms
        timeout = 1000 
        
        self.logger.debug("Waiting for frame acknowledgement from device")
        while(elapsedTime <= timeout):
            # update timeout
            elapsedTime = (time.time_ns()/ 1000000) - startTime

            r = self.connection.Read(1) # todo this should be non-blocking
            self.logger.debug("Received %s (%s)" % (str(r), r.hex()))

            if(r == self._FRAME_ACKNOWLEDGEMENT_BYTE):
                self.logger.debug("Received frame acknowledgement from device")
                return
            elif (r == self._FRAME_ERROR_BYTE):
                self.logger.warning("Received ALUP Frame Error from device. Frame data could not be applied")
                return
            # If the received data is neither a frame error or acknowledgement it gets ignored
               
        # timeout was reached
        raise TimeoutError("No Frame Acknowledgement or Frame Error received from receiver within a time of %d ms" % (timeout))


class ConfigurationException(Exception):
    pass
