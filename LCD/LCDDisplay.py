# LCDDisplay.py
#
from serial import Serial

class LCDDisplay:

	def __init__(self, port):
		self.ser = Serial(port)
		
	def write(self, message):
		if "\n" in message:
			line1,line2 = message.split("\n")
			if len(line1) > 16 or len(line2) > 16:
				print "Message too long - max 16 chars per line, max 2 lines"
				return
			else:
				paddedline1 = line1.ljust(16)
				paddedline2 = line2.ljust(16)
				self.ser.write(paddedline1 + paddedline2)
		elif len(message) > 16:
			print "Message too long - max 16 characters"
			return
		else:
			paddedmessage = message.ljust(16)
			blankline = " " * 16
			self.ser.write(paddedmessage + blankline)
