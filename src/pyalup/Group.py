from .Device import Device
from .Frame import Command
import threading

class Group:
    """
    A group of ALUP devices which are updated synchronously

    The colors of each device can be set to the device directly
    and then synchronously sent with its group
    
    """

    def __init__(self):
        # the ALUP devices in this group
        self.devices = []
    
    def Add(self, device: Device):
        """
        Add the given device to this group
        """
        self.devices.append(device)

    def Remove(self, device: Device):
        """
        Remove the first occurence of the given device from the group
        """
        self.devices.remove(device)

    def Send(self):
        """
        Send to all devices in the group at the same time,
        using multithreading
        """
        threads = []
        # configure one thread for each device
        for device in self.devices:
            thread = threading.Thread(target=device.Send)
            threads.append(thread)

        # start all threads
        for thread in threads:
            thread.start()

        # wait for all threads to finish
        for thread in threads:
            thread.join()

    def SetColors(self, colors):
        """
        Set the colors of all grouped devices, overriding their current color.
        If a device has less LEDs than color values given, the colors given are cut to size for this device.
        """
        for device in self.devices:
            device.SetColors(colors[:device.configuration.ledCount])

    def SetCommand(self, command):
        """
        Set the given command for all grouped devices. 
        """
        for device in self.devices:
            device.SetCommand(command)


    def Clear(self):
        self.SetCommand(Command.CLEAR)
        self.Send()



    def __str__(self):
        out = f"Group of {len(self.devices)} ALUP Devices\n"
        for device in self.devices:
            out += f"\t{device.configuration.name} ({device.configuration.ledCount} LEDs)\n" 
        return out
    
