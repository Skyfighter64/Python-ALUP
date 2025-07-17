from enum import IntEnum


class Frame:
    def __init__(self):
        # an array containing the color for each LED
        # each color is represented as hex integer (e.g. 0x00ff00)
        self.colors = []
        # the offset of the color values
        self.offset = 0
        # the command of this frame
        self.command = Command.NONE

    # function returning a binary representation of this frame according to
    # ALUP v.0.2
    # @return: a bytes object containing this frame
    def ToBytes(self):
        b = b''
        b += self._HeaderToBytes()
        b += self._BodyToBytes()
        return b

    # function returning a binary representation of this frame's header
    # @return: a bytes object containing the header of this frame
    def _HeaderToBytes(self):
        #convert the header values into binary format
        b = (len(self.colors) * 3).to_bytes(4, byteorder='big', signed=True)
        b += self.offset.to_bytes(4, byteorder='big', signed=True)
        b += self.command.value.to_bytes(1, byteorder='big', signed=False)
        # add the unused bytes
        b += b'\x00'
        # return the parsed bytes
        return b

    # function returning a binary representation of this frame's body
    # @return: a bytes object containing the body of this frame
    def _BodyToBytes(self):
        b = b''
        for color in self.colors:
            # convert each hex color into binary and append the result
            b += color.to_bytes(3, byteorder='big', signed = False)
        return b
    
    def __str__(self):
        output = "Header:\n" \
        "\tFrame Body Size: " + str(len(self.colors) * 3) + \
        "\n\tFrame Body Offset: " + str(self.offset) + \
        "\nBody:\n\t" + str(self.colors)
        return output


# an enum containing all supported ALUP commands
class Command(IntEnum):
    NONE = 0
    CLEAR = 1
    DISCONNECT = 2
    LED_BUILTIN = 4
