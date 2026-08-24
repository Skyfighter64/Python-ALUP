from enum import IntEnum
import logging

class Frame:
    def __init__(self):
        # an array containing the color for each LED
        # each color is represented as hex integer (e.g. 0x00ff00)
        self.colors = []
        # the offset of the color values
        self.offset = 0
        # The time stamp in ms at which the frame will be applied to the LEDs on the receiver.
        # If the given time stamp is in the past, the frame will be applied instantly.
        # Has to be in the receiver's time domain, will be converted to the receiver's time domain
        # before sending 
        # If time stamp is set to 0, time stamps are disabled and frame is applied ASAP
        self.timestamp = 0
        # the command of this frame
        self.command = Command.NONE

        self._id = 0 # the ID of this frame for identifying the corresponding response; unsigned 8bit integer (0-255)

        # time stamps for the frame in ms
        self._t_frame_out = 0 # time when frame was sent out
        self._t_receiver_in = 0 # time when receiver got the frame
        self._t_receiver_out = 0 # time when receiver sent out acknowledgement
        self._t_response_in = 0 # time when acknowledgement was received

        self.logger = logging.getLogger(__name__)

    # function returning a binary representation of this frame according to
    # the ALUP protocol definition
    # @param time_delta_ms: the time offset for the device this frame is sent to
    # @return: a bytes object containing this frame
    def ToBytes(self, time_delta_ms):
        b = b''
        b += self._HeaderToBytes(time_delta_ms)
        b += self._BodyToBytes()
        return b

    # function returning a binary representation of this frame's header
    # @param time_delta_ms: the time offset for the device this frame is sent to
    # @return: a bytes object containing the header of this frame
    def _HeaderToBytes(self, time_delta_ms):
        #convert the header values into binary format
        b = self._id.to_bytes(1, byteorder='big', signed=False)
        b += self.command.value.to_bytes(1, byteorder='big', signed=False)
        b += (len(self.colors) * 3).to_bytes(4, byteorder='big', signed=True)
        b += self.offset.to_bytes(4, byteorder='big', signed=True)
        
        receiver_time_stamp = self._LocalTimeToReceiverTime(time_delta_ms)
        b += receiver_time_stamp.to_bytes(4, byteorder='big', signed=False)
        # return the parsed bytes
        return b
    
    # Convert the frame's time stamp in the receiver's time domain 
    # by using the time synchronization data
    # @param time_delta_ms: the time offset for the device this frame is sent to
    # @returns: The frame's time stamp in the receiver time domain
    def _LocalTimeToReceiverTime(self, time_delta_ms):
        if (self.timestamp == 0):
            # time stamps are disabled; apply frame asap
            # by also setting receiver time stamp to 0
            return 0
        # NOTE: Limit the timestamp to 32 bit unsigned integer values
        return int((self.timestamp + time_delta_ms) % 2**32)

    # function returning a binary representation of this frame's body
    # @return: a bytes object containing the body of this frame
    def _BodyToBytes(self):
        b = b''
        for color in self.colors:
            # convert each hex color into binary and append the result
            b += color.to_bytes(3, byteorder='big', signed = False)
        return b

    # function parsing the given binary data into this frame instance
    # @param bytes: a valid byte representation of an ALUP frame
    # @returns: 
    def FromBytes(self, frame_bytes):
        # split the bytes according to the protocol standard
        # and apply them to the fields of this frame

        # parse the frame header
        id_bytes = frame_bytes[0:1]
        command_bytes = frame_bytes[1:2]
        body_size_bytes = frame_bytes[2:6]
        body_offset_bytes = frame_bytes[6:10]
        timestamp_bytes = frame_bytes[10:14]

        self._id = int.from_bytes(id_bytes, byteorder='big', signed=False)
        self.command = Command(int.from_bytes(command_bytes, byteorder='big', signed=False))
        self.body_size = int.from_bytes(body_size_bytes, byteorder='big', signed=True)
        self.offset = int.from_bytes(body_offset_bytes, byteorder='big', signed=True)
        self.timestamp = int.from_bytes(timestamp_bytes, byteorder='big', signed=False)

        # check the frame body size
        if(self.body_size % 3 != 0):
            self.logger.warning(f"Frame body has invalid size: {self.body_size} is not divisible by 3")

        # parse the frame body
        self.colors = []
        frame_body_bytes = frame_bytes[14:]

        # check the length of the frame body size
        if(len(frame_body_bytes) != self.body_size):
            self.logger.warning(f"Frame Body contains more bytes ({len(frame_body_bytes)}) than specified in header ({self.body_size}).")

        # extract the individual colors
        for i in range(0, self.body_size, 3):
            color = int.from_bytes(frame_body_bytes[i:i+3], byteorder='big', signed=False)
            self.colors.append(color)

        # check if the sizes match
        assert len(self.colors) == self.body_size // 3


    def __str__(self):
        output = "Header:" \
        "\n\tID: " + str(self._id) + \
        "\tFrame Body Size: " + str(len(self.colors) * 3) + \
        "\n\tFrame Body Offset: " + str(self.offset) + \
        "\n\tTime Stamp: " + str(self.timestamp) + \
        "\n\tCommand: " + self.command.name  + " (" + str(self.command.value) + ")" + \
        "\nBody:\n\t" + str(self.colors)
        return output


# an enum containing all supported ALUP commands
class Command(IntEnum):
    NONE = 0
    CLEAR = 1
    DISCONNECT = 2
    LED_BUILTIN = 4
