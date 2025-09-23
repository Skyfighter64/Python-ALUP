
class Configuration:
    def __init__(self):
        self.protocolVersion = ''
        self.deviceName = ''
        self.ledCount = 0
        self.frameBufferSize = 0
        self.dataPin = 0
        self.clockPin = 0
        self.extraValues = ''

    def __str__(self):

        result =  "Configuration:\n"
        result += "\tVersion:" + self.protocolVersion + "\n"
        result += "\tName: \'" + self.deviceName+ "\'\n"
        result += "\tLEDs: " + str(self.ledCount) + "\n"
        result += "\tBuffer Size: " + str(self.frameBufferSize) + "\n"
        result += "\tData pin: " + str(self.dataPin)+ "\n"
        result += "\tClock pin: " + str(self.clockPin) + "\n"
        result += "\tExtras: \'" + self.extraValues + "\'"
        return result