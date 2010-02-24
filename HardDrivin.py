# HardDrivin.py
#

import time, threading
from threading import Timer

from TwitterService import TwitterService
from CarControl import CarControl
from OSC import *

class HardDrivin:
    
    def __init__(self):
        
        self.oscSendAddress = '127.0.0.1', 9000
        self.oscRecvAddress = '127.0.0.1', 9001
        
        self.cars = CarControl('COM26')
        self.twitter = TwitterService()

        self.oscClient = OSCClient()
        self.oscClient.connect(self.oscSendAddress)
        
        self.oscServer = OSCServer(self.oscRecvAddress)
    
        # this registers a 'default' handler (for unmatched messages), 
        # an /'error' handler, an '/info' handler.
        # And, if the client supports it, a '/subscribe' & '/unsubscribe' handler
        self.oscServer.addDefaultHandlers()
        # user defined handlers
        self.oscServer.addMsgHandler("/print", self.printing_handler)
        self.oscServer.addMsgHandler("/movecar", self.movecar_handler) 
        self.oscServer.addMsgHandler("/stopcar", self.stopcar_handler) 

    def movecar_handler(self, addr, tags, stuff, source):
        car, direction, duration = stuff[0], stuff[1], stuff[2]
        print "---"
        print "Moving car %s %s for %s ms" % (car, direction, duration)
        self.cars.move(car, direction, duration);
        
    def stopcar_handler(self, addr, tags, stuff, source):
        car = stuff[0]
        print "---"
        print "Stopping car %s" % car
        self.cars.stop(car);

    # define a message-handler function for the server to call.
    def printing_handler(self, addr, tags, stuff, source):
        print "---"
        print "received new osc msg from %s" % OSC.getUrlStr(source)
        print "with addr : %s" % addr
        print "typetags %s" % tags
        print "data %s" % stuff
        print "---"
        
    def sendOSC(self, address, data):
        m = OSC.OSCMessage()
        m.setAddress(address)
        m.append(data)
        self.oscClient.send(m)
        
    def startOSCServer(self):
        # Start OSCServer
        print "\nStarting OSCServer. Use ctrl-C to quit."
        st = threading.Thread( target = self.oscServer.serve_forever )
        st.start()
        
        try :
            while 1 :
                time.sleep(5)

        except KeyboardInterrupt :
            print "\nClosing OSCServer."
            self.oscServer.close()
            print "Waiting for Server-thread to finish"
            st.join()
            print "Done"
                
if __name__ == "__main__":
    
    print "  ___ ___                   .___ ________        .__        .__      /\\"
    print " /   |   \_____  _______  __| _/ \______ \_______|__|___  __|__| ____)/"
    print "/    ~    \__  \ \_  __ \/ __ |   |    |  \_  __ \  |\  \/ /|  |/    \ "
    print "\    Y    // __ \_|  | \/ /_/ |   |    `   \  | \/  | \   / |  |   |  \\"
    print " \___|_  /(____  /|__|  \____ |  /_______  /__|  |__|  \_/  |__|___|  /"
    print "       \/      \/            \/          \/                         \/ "

    '''
    configfd = ConfigParser.RawConfigParser()
    configfd.read(configfile)
    print "Reading config: %s" % configfile

    username  = configfd.get('Connection', 'username')
    password  = configfd.get('Connection', 'password')
    recieveID = configfd.getint('Connection', 'recieveID')
    if configfd.has_option('Connection', 'timeout'):
    timeout = configfd.getint('Connection', 'timeout')
    else:
    timeout = 5    

    actions = {}
    for section in configfd.sections():
    if section == 'Connection':
      continue
    action = {}
    action['match']   = re.compile(configfd.get(section,'match'))
    action['command'] = configfd.get(section,'command')
    action['output']  = configfd.get(section,'output')
    actions.update({section:action})
    print "Loaded modules: %s"%", ".join(actions.keys())
    '''

    
    hd = HardDrivin()
    hd.startOSCServer()
    