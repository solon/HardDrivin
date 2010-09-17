# CarControl.py
#
from serial import Serial
from threading import Timer

class CarControl:

    def __init__(self, comport):
        
        self.comport = comport
        self.cars = {
            1: {'x-servo':1, 'y-servo':2},
            2: {'x-servo':3, 'y-servo':4},
            3: {'x-servo':5, 'y-servo':6}
        }
        self.directions = {
            'S':  {'x-servo-val':90, 'y-servo-val':90},
            'F':  {'x-servo-val':120, 'y-servo-val':90},
            'B':  {'x-servo-val':60, 'y-servo-val':90},
            'FL': {'x-servo-val':120, 'y-servo-val':70},
            'FR': {'x-servo-val':120, 'y-servo-val':100},
            'BL': {'x-servo-val':60, 'y-servo-val':100},
            'BR': {'x-servo-val':60, 'y-servo-val':70}
        }
        
        self.arduino = Serial(self.comport, 115200, timeout=1)
        
    def move(self, car, direction, duration=500):
        xservo = self.cars[car]['x-servo']
        yservo = self.cars[car]['y-servo']
        xval = self.directions[direction]['x-servo-val']
        yval = self.directions[direction]['y-servo-val']
        
        # steer first...
        #print "xservo %d %d" % (xservo, xval)
        self.moveServo(xservo, xval)
        
        # then hit the gas!
        #print "yservo %d %d" % (yservo, yval)
        self.moveServo(yservo, yval)
        
        # stop the car after given duration
        print "stopping after %d" % (duration)
        t = Timer(10 + float(duration)/1000, self.stop, [car])
        t.start()
        
    def stop(self, car):
        print "stopping car %d" % car
        xservo = self.cars[car]['x-servo']
        yservo = self.cars[car]['y-servo']
        xcentre = self.directions['S']['x-servo-val']
        ycentre = self.directions['S']['y-servo-val']
        self.moveServo(yservo, ycentre)
        self.moveServo(xservo, xcentre)

    def moveServo(self, servo, angle):
        '''
        Moves the specified servo to the supplied angle.
        Arguments:
            servo
              the servo number to command, an integer from 1-6
            angle
              the desired servo angle, an integer from 0 to 180

        (e.g.) >>> servo.move(2, 90)
               ... # "move servo #2 to 90 degrees"
        '''
        
        if (0 <= angle <= 180):
            self.arduino.write(chr(255))
            self.arduino.write(chr(servo))
            self.arduino.write(chr(angle))
            print "servo %d: %d" % (servo,angle)
        else:
            print "Servo angle must be an integer between 0 and 180.\n"
        
