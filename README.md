# Python-ALUP
A python implementation of the ALUP v.0.3

## Properties
- Supported versions:
  - 0.3

- Supported connections:
  - TCP
  - Serial (USB)


## Installing

1. Clone the repository into any folder:
```sh
git clone git@github.com:Skyfighter64/Python-ALUP.git
```
2. Do development install (for now)
```sh
pip install -e ./Python-Alup/
```

```python
# import the main library
from pyalup.Device import Device
# import command definitions
from pyalup.Frame import Command
```
## Examples:
For examples, see ` ./examples ` directory

-----------
## Adding connection types:

A connection needs to implement the following functions:
```python
class Connection:
  #Establishes the connection; Blocks until finished
  def Connect(self):
    pass

  #function terminating the connection
  def Disconnect(self):
    pass  
  #function sending the given data over the connection
  #@param data: a bytes object containing the data to send
  def Send(self, data):
    pass

  #Function reading in the given size of data from the connection
  #Blocks until the requested number of bytes was received
  #@param size: an integer specifying the amount of bytes to read
  # @param timeout: timeout in ms. If there is no data received within the timeout, a TimeoutError is raised.
    #                 0 for non-blocking mode, None for full blocking mode. For more info, see socket docs.
    #                 Default: 0
  #@return: a bytes object containing the read bytes
  #@raises: TimeoutError if the given timeout is exceeded
  def Read(self, size, timeout):
    pass

```
