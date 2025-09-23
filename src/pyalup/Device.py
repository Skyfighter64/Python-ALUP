from .UdpConnection import UdpConnection
from .TcpConnection import TcpConnection
from .SerialConnection import SerialConnection
from .Frame import *
from .Configuration import Configuration

import time
import logging
import collections
import statistics
from timeit import default_timer as timer



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

    # default constructor
    # @param _time_delta_buffer_size: The number of time measurements for the median used to calculate the time_delta.
    # This parameter does not need to be changed except if a device has a lot of time drift and packets are sent very sparsely (reduce to 10 or 1)
    def __init__(self, _time_delta_buffer_size=100):
        self.connection = None
        self.connected = False
        self.frame = Frame()
        self.configuration = None
        self.logger = logging.getLogger(__name__)
        self.latency = 0

        # time stamps for the current packet in ms
        self._t_frame_out = 0 # time when frame was sent out
        self._t_receiver_in = 0 # time when receiver got the frame
        self._t_receiver_out = 0 # time when receiver sent out acknowledgement
        self._t_response_in = 0 # time when acknowledgement was received

        self._time_deltas_ms_raw = collections.deque(maxlen=_time_delta_buffer_size)
        self.time_delta_ms = 0 # the time offset from the system time to the receiver's system time in ms
        self._time_delta_ms_raw = 0
        
    # function starting an ALUP/TCP connection
    # @param ip: a string containing the ip address for the device to connect to
    # @param port: an int containing the TCP port of the device to use
    def TcpConnect(self, ip, port):
        self.connection = TcpConnection(ip,port)
        self.connection.Connect()
        self._AlupConnect()
        self.logger.info("TCP Connection to %s:%d established successfully." % (ip, port))

    # function starting an ALUP/UDP connection
    # @param ip: a string containing the ip address for the device to connect to
    # @param port: an int containing the UDP port of the device to use
    def UdpConnect(self, ip, port):
        self.connection = UdpConnection(ip,port)
        self.connection.Connect()
        self._AlupConnect()
        self.logger.info("UDP Connection to %s:%d established successfully." % (ip, port))

    # function starting an ALUP/Serial connection
    # @param port: a string containing the serial port to connect to
    # @param baud: an integer defining the serial communication speed
    def SerialConnect(self, port, baud):
        self.connection = SerialConnection(port, baud)
        self.connection.Connect()
        self._AlupConnect()
        self.logger.info("Serial Connection to %s:%d established successfully." % (port, baud))


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
        # send frame and wait for response while measuring time
        start = timer()
        self.SendFrame()
        self._WaitForFrameAcknowledgement()
        self._SynchronizeDeviceTime()

        # reset the command to default
        self.frame.command = Command.NONE

        # measure round-trip time in ms
        self.latency = (timer() - start)* 1000

    # function sending the current frame without waiting for an acknowledgement
    # Improper usage may result in connection freeze
    def SendFrame(self):
        self.logger.info("Sending frame:")
        self.logger.debug(f"Converting timestamp: local time stamp {self.frame.timestamp} + offset {self.time_delta_ms} = receiver time stamp {self.frame._LocalTimeToReceiverTime(self.time_delta_ms)}")
        frameBytes = self.frame.ToBytes(self.time_delta_ms)
        self.logger.info("\n" + str(self.frame))
        self.logger.info("Total Frame size: %d" % (len(frameBytes)))
        self.logger.debug("Hex Data:\n %s" % (frameBytes.hex()))

        # save timestamp when frame was sent
        self._t_frame_out = time.time_ns() // 1000000
        
        self.connection.Send(frameBytes)

    # Set all LEDs to black by sending a clear command
    def Clear(self):
        self.SetCommand(Command.CLEAR)
        self.Send()


    # function reading in the configuration
    # @return: The configuration object read
    # @throws: ConfigurationException if the protocol version of the devices are incompatible
    def _ReadConfiguration(self):
        self.logger.debug("Waiting for configuration start")
        # wait for the configuration start byte
        while(self.connection.Read(1) != self._CONFIGURATION_START_BYTE):
            #print("- Waiting for Configuration Start")
            pass

        config = Configuration()
        #read in the protocol version
        config.protocolVersion = self._ReadString()
        # check if the protocol version is compatible
        if (not self._CheckProtocolVersion(config.protocolVersion)):
            raise ConfigurationException("Incompatible protocol versions: Supported versions: " + str(self.PROTOCOL_VERSIONS)+ " but device has: " + config.protocolVersion)

        # read the configuration values
        config.deviceName = self._ReadString()
        config.ledCount = self._ReadInt()
        config.dataPin = self._ReadInt()
        config.clockPin = self._ReadInt()
        config.extraValues = self._ReadString()

        self.logger.info("Received device configuration: " + str(config))
        self._SendByte(self._CONFIGURATION_ACKNOWLEDGEMENT_BYTE)
        self.logger.debug("Configuration acknowledgement sent.")
        return config




    # function checking the protocol versions of both devices for compatibility
    # @param protocolVersion: a string representing the protocol version
    # @return: True if versions are compatible, else False
    def _CheckProtocolVersion(self, protocolVersion):
        self.logger.debug("Checking Protocol versions:\n\tDevice: %s\n\tCompatible Versions: %s" % (protocolVersion, str(self.PROTOCOL_VERSIONS)))
        if (protocolVersion not in self.PROTOCOL_VERSIONS):
            self.logger.error("Protocol Version Check: Device Protocol version is not supported: " + "Supported versions: " + str(self.PROTOCOL_VERSIONS)+ " but device has: " + protocolVersion)
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

    # function reading a 2s complement integer value from the connection
    # @param bytes: the number of bytes the integer has (eg. 4 Bytes for 32bit Integer)
    # @return: the received number
    def _ReadInt(self, bytes=4):
        b = self.connection.Read(bytes)
        return int.from_bytes(b, byteorder='big', signed=True)
    
    # function reading an unsigned integer value from the connection
    # @param bytes: the number of bytes the integer has (eg. 4 Bytes for 32bit Integer)
    # @return: the received number
    def _ReadUInt(self, bytes=4):
        b = self.connection.Read(bytes)
        return int.from_bytes(b, byteorder='big', signed=False)

    # function sending a single byte over the connection
    def _SendByte(self, b):
        self.connection.Send(b)

    # function waiting for a frame acknowledgement or frame error
    # TODO: the timeout should be handled by the connection and not here
    def _WaitForFrameAcknowledgement(self):
        startTime = time.time_ns() / 1000000
        elapsedTime = 0

        # timeout for this function in ms
        timeout = 1000 
        
        self.logger.info("Waiting for frame acknowledgement from device")
        while(elapsedTime <= timeout):
            # update timeout
            elapsedTime = (time.time_ns()/ 1000000) - startTime

            r = self.connection.Read(1)
            self.logger.debug("Received %s (%s)" % (str(r), r.hex()))

            if(r == self._FRAME_ACKNOWLEDGEMENT_BYTE):
                # save response timestamp in ms
                self._t_response_in = time.time_ns() // 1000000
                
                self.logger.info("Received frame acknowledgement from device")
                # read in timestamps from receiver
                self._t_receiver_in = self._ReadUInt()
                self._t_receiver_out = self._ReadUInt()
                return
            
            elif (r == self._FRAME_ERROR_BYTE):
                self.logger.warning("Received ALUP Frame Error from device. Frame data could not be applied")
                return
            # If the received data is neither a frame error or acknowledgement it gets ignored
               
        # timeout was reached
        raise TimeoutError("No Frame Acknowledgement or Frame Error received from receiver within a time of %d ms" % (timeout))

    # function calculating the offset from the sender's time
    # to the time on the receiver
    def _SynchronizeDeviceTime(self):
        # calculate the time delta based on the saved timestamps
        # This combines the following steps:
        # 1. Retrieve system time from receiver
        # 2. Adjust receiver system time for transmission delay
        # 3. Calculate difference to sender's system time  
        # With: 
        # time_delta_ms = time_receiver -  time_sender
        self._time_delta_ms_raw = (-self._t_frame_out + self._t_receiver_in + self._t_receiver_out - self._t_response_in)/ 2
        # we collect multiple measurements and take the median to smooth out inconsistencies
        self._time_deltas_ms_raw.append(self._time_delta_ms_raw)
        self.time_delta_ms = statistics.median(self._time_deltas_ms_raw) # TODO: is is better here to use median or mean?



class ConfigurationException(Exception):
    pass
