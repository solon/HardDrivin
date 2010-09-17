# HardDrivin.py
#

import time, threading, yaml
from threading import Timer

from CarControl import CarControl
from OSC import OSCServer

class HardDrivin:
        
    def __init__(self):
        
        try:
            f = open('settings.yaml')
            self.settings = yaml.load(f)
        except Exception, e:
            print 'e: %s' % e
            print repr(e)
            exit(1)
    
        # Receive commands from Pure Data via OSC
        self.oscRecvAddress = self.settings['car_control']['osc_recv_addr'], self.settings['car_control']['osc_recv_port']
        
        self.cars = CarControl(self.settings['serial_port'])
        
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
    
    print ""
    print "    __ __             __  ___      _       _      _ "
    print "   / // /___ ________/ / / _ \____(_)_  __(_)___ ( )"
    print "  / _  // _ `/ __/ _  / / // / __/ /| |/ / // _ \|/ "
    print " /_//_/ \_,_/_/  \_,_/ /____/_/ /_/ |___/_//_//_/   "
    print ""
    print "  __        __   __   __       ___  __   __       "
    print " /  `  /\  |__) /  ` /  \ |\ |  |  |__) /  \ |    "
    print " \__, /~~\ |  \ \__, \__/ | \|  |  |  \ \__/ |___ "
    print ""                                    

    hd = HardDrivin()
    hd.startOSCServer()
    