from .Device import Device
from .Frame import Command

import threading
import time
from timeit import default_timer as timer

class Group:
    """
    A group of ALUP devices which are updated synchronously

    The colors of each device can be set to the device directly
    and then synchronously sent with its group
    
    """

    def __init__(self):
        # the ALUP devices in this group
        self.devices = []
        # the round-trip latency of the last frame sent
        # equivalent to the maximum latency of any device in practice 
        self.latency = 0
    
    def Add(self, device: Device):
        """
        Add the given device to this group
        """
        self.devices.append(device)

    def Remove(self, device: Device):
        """
        Remove the first occurrence of the given device from this group
        """
        self.devices.remove(device)

    def Send(self, delayTarget=None):
        """
        Send to all devices in the group at the same time,
        using multithreading

        @param delayTarget: Synchronously update all devices after the given delay target (in ms) passed.
                            Set to None to deactivate (default).
                            NOTE: This overrides time stamps of all group devices' frames
                            NOTE: If a device's connection is slower than the specified delay target, it will
                                    instead update ASAP.
        """

        # synchronize all group members to update after reaching the delay target
        if (delayTarget not None):
            now = time.time_ns() // 1_000_000
            for device in self.devices:
                device.frame.timestamp = now + delayTarget

        # send frame and wait for response while measuring time
        start = timer()

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

        # measure the total latency of the group
        self.latency = (timer() - start)* 1000


    def SetColors(self, colors):
        """
        Set the colors of all grouped devices, overriding their current color.
        If a device has less LEDs than color values given, the colors given are cut to size for this device.

        @param colors: A list with integer color values.
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
        """
        Clear the LEDs for all grouped devices
        """
        self.SetCommand(Command.CLEAR)
        self.Send()


    def Disconnect(self):
        for device in self.devices:
            device.Disconnect()


    def __str__(self):
        out = f"Group of {len(self.devices)} ALUP Devices\n"
        for device in self.devices:
            out += f"\t{device.configuration.deviceName} ({device.configuration.ledCount} LEDs)\n" 
        return out
    
