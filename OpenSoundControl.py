# OpenSoundControl.py
#

import OSC

class Client:
  def __init__(self, port=9000):
    self._client = OSC.OSCClient()
    self._address = '127.0.0.1', port
    self._client.connect(self._address)

  def send(self, address, data):
    m = OSC.OSCMessage()
    m.setAddress(address)
    if isinstance(data, list) :
      for d in data:
        m.append(d)
    else:
      m.append(data)
    self._client.send(m)

'''
class OSCServer:
  def __init(self)__:
    self.oscRecvAddress = '127.0.0.1', 9001
    self.oscServer = OSCServer(self.oscRecvAddress)

    # this registers a 'default' handler (for unmatched messages), 
    # an /'error' handler, an '/info' handler.
    # And, if the client supports it, a '/subscribe' & '/unsubscribe' handler
    self.oscServer.addDefaultHandlers()
    # user defined handlers
    self.oscServer.addMsgHandler("/print", self.printing_handler)
    self.oscServer.addMsgHandler("/movecar", self.movecar_handler) 
    self.oscServer.addMsgHandler("/stopcar", self.stopcar_handler) 
'''