from src.UdpConnection import UdpConnection
from src.Frame import *
from src.Configuration import Configuration
import time




class Device:

    # protocol constants
    _CONNECTION_REQUEST_BYTE = b'\xff'
    _CONNECTION_ACKNOWLEDGEMENT_BYTE = b'\xfe'
    _CONFIGURATION_START_BYTE = b'\xfd'
    _CONFIGURATION_ACKNOWLEDGEMENT_BYTE = b'\xfc'
    _CONFIGURATION_ERROR_BYTE = b'\xfb'
    _FRAME_ACKNOWLEDGEMENT_BYTE = b'\xfa'
    _FRAME_ERROR_BYTE = b'\xf9'

    def __init__(self):
        self.connection = None
        self.frame = Frame()
        self.configuration = None


    # function starting an ALUP/UDP connectionthe connection to the given device
    def UdpConnect(self, ip, port):
        self.connection = UdpConnection(ip,port)
        self.connection.Connect()
        self._WaitForConnectionRequest()
        self._SendByte(self._CONNECTION_ACKNOWLEDGEMENT_BYTE)
        self.configuration = self._ReadConfiguration()
        print("- connection established")

    # function terminating the connection
    def Disconnect(self):
        print("Disconnecting...")
        #self.SetColors([0xffffff])
        self.SetCommand(Command.DISCONNECT)
        self.Send()
        self.connection.Disconnect()
        print("Disconnected")


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
        pingStart = round(time.time() * 1000)
        self.SendFrame()
        self._WaitForFrameAcknowledgement()
        print("Ping: " + str((round(time.time() * 1000) - pingStart)) + "ms")

    # function sending the current frame without waiting for an acknowledgement
    # Inproper usage may result in connection freeze
    def SendFrame(self):
        frameBytes = self.frame.ToBytes()
        self.connection.Send(frameBytes)
        # clear the frame
        self.frame = Frame()


    # function reading in the configuration
    # @return: The configuration object read
    # @throws: ConfigurationException if the protocol version of the devices are incompatible
    def _ReadConfiguration(self):
        # wait for the configuration start byte
        while(self.connection.Read(1) != self._CONFIGURATION_START_BYTE):
            print("- Waiting for Configuration Start")

        config = Configuration()
        #read in the protocol version
        config.protocolVersion = self._ReadString()
        # check if the protcol version is compatible
        if (not self._CheckProtocolVersion(config.protocolVersion)):
            raise ConfigurationException("Incompatible protocol versions: Version 0.2 (this) and " + config.protocolVersion)
        
        # read the configuration values
        config.deviceName = self._ReadString()
        config.ledCount = self._ReadInt()
        config.dataPin = self._ReadInt()
        config.clockPin = self._ReadInt()
        config.extraValues = self._ReadString()

        print("Received config:" + str(config))
        self._SendByte(self._CONFIGURATION_ACKNOWLEDGEMENT_BYTE)

        return config




    # function checking the protocol versions of both devices for compatibility
    # @param protocolVersion: a string representing the protocol version
    # @return: True if versions are compatible, else False
    def _CheckProtocolVersion(self, protocolVersion):
        print("Checking protcol version...")
        if (protocolVersion != "0.2"):
            print("Incompatible protocol version " + protocolVersion + ". Version 0.2 needed")
            # send a configuration error indicating that the versions are incompatible 
            self._SendByte(self._CONFIGURATION_ERROR_BYTE)
            return False
        print("Compatible!")
        return True


    # function waiting for a connection request
    def _WaitForConnectionRequest(self):
        # wait for the connection request
        while(True):
            if (self.connection.Read(1) == self._CONNECTION_REQUEST_BYTE):
                print("- Received connection request")
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
        print("Waiting for acknowledgement...")
        while(True):
            r = self.connection.Read(1)
            print("Received: " + str(r))
            if(r == self._FRAME_ACKNOWLEDGEMENT_BYTE):
                print("Received frame acknowledgement")
                return
            elif (r == self._FRAME_ERROR_BYTE):
                print("Received frame error")
                return


class ConfigurationException(Exception):
    pass