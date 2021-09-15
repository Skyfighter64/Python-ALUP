# Python-ALUP
A python implementation of the ALUP v.0.2



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
