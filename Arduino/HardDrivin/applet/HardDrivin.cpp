#include <Servo.h> 

// Create a Servo object for each servo
#include "WProgram.h"
void setup();
void loop();
void resetServoPositions();
Servo servo1;
Servo servo2;
Servo servo3;
Servo servo4;

// Common servo setup values
int minPulse = 600;   // minimum servo position, us (microseconds)
int maxPulse = 2400;  // maximum servo position, us

// User input for servo and position
int userInput[3];    // raw input from serial buffer, 3 bytes
int startbyte;       // start byte, begin reading input
int servo;           // which servo to pulse?
int pos;             // servo angle 0-180
int i;               // iterator
int counter;

int ledPin = 13;
 
void setup() {

  // Attach each Servo object to a digital pin
  servo1.attach(3, minPulse, maxPulse);
  servo2.attach(5, minPulse, maxPulse);
  servo3.attach(6, minPulse, maxPulse);
  servo4.attach(9, minPulse, maxPulse);
  
  pinMode(ledPin, OUTPUT);

  Serial.begin(115200);
  counter = 0;
  resetServoPositions();
} 
 
void loop() { 
  // Wait for serial input (min 3 bytes in buffer)
  if (Serial.available() > 2) {
    // Read the first byte
    startbyte = Serial.read();
    // If it's really the startbyte (255) ...
    if (startbyte == 255) {
      // ... then get the next two bytes
      for (i=0;i<2;i++) {
        userInput[i] = Serial.read();
      }
      // First byte = servo to move?
      servo = userInput[0];
      // Second byte = which position?
      pos = userInput[1];
      // Packet error checking and recovery
      if (pos == 255) { servo = 255; }

      // Assign new position to appropriate servo
      switch (servo) {
        case 1:
          servo1.write(pos);
          break;
        case 2:
          servo2.write(pos);
          break;
        case 3:
          servo3.write(pos);
          break;
        case 4:
          servo4.write(pos);
          break;
      }
    }
  } else {
    delay(10);
    counter++;
    if (counter >= 90) {
      resetServoPositions();
      counter = 0;
    }
  }
}

void resetServoPositions() {
  servo1.write(90);
  servo2.write(90);
  servo3.write(90);
  servo4.write(90);
}

int main(void)
{
	init();

	setup();
    
	for (;;)
		loop();
        
	return 0;
}

