# OpenSoundControl.py
#

import OSC
import warnings
from OSC import OSCClientError

class Client:
  def __init__(self, port=9000):
    with warnings.catch_warnings():
      warnings.simplefilter("ignore")      
      self._client = OSC.OSCClient()
      self._address = '127.0.0.1', port
      self._client.connect(self._address)

  def send(self, address, data):
    with warnings.catch_warnings():
      warnings.simplefilter("ignore")
      m = OSC.OSCMessage()
      m.setAddress(address)
      if isinstance(data, list) :
        for d in data:
          m.append(d)
      else:
        m.append(data)
      try:
        self._client.send(m)
      except OSCClientError, e:
        pass
        #print "!!! Pure Data client not connected\n\n"
        #print 'e: %s' % e
        #print repr(e)
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