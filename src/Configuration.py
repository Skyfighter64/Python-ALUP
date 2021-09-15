
class Configuration:
    def __init__(self):
        self.protocolVersion = ''
        self.deviceName = ''
        self.ledCount = 0
        self.dataPin = 0
        self.clockPin = 0
        self.extraValues = ''

    def __str__(self):

        result =  "Configuration:"
        result += " Version:" + self.protocolVersion + ";"
        result += " name: " + self.deviceName+ ";"
        result += " data pin: " + str(self.dataPin)+ ";"
        result += " clock pin: " + str(self.clockPin) + ";"
        result += " leds: " + str(self.ledCount) + ";"
        result += " extra values: " + self.extraValues
        return result