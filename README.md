# Python-ALUP
A python implementation of the ALUP v.0.2

## Properties
- Supported versions:
  - 0.2

- Supported connections:
  - UDP
  - Serial (USB)


## Installing
For now: copy-paste the src folder to your project
```python
# import the main library
from src.Device import Device
# import command definitions
from src.Frame import Command
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
  #@return: a bytes object containing the read bytes
  def Read(self, size):
    pass

```
