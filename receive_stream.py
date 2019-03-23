import numpy as np
import socket
import struct
from display import LEDdisplay


UDP_IP = "192.168.1.247"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))


disp = LEDdisplay()

while True:
	data, addr = sock.recvfrom(2700) # buffer size is 2700 bytes
	linear_array = np.zeros(2700, dtype=np.int)
	s = ""
	for i in range(2700):
		s+="B"
	linear_array = struct.unpack(s,data)
#	print "received message:", linear_array
	disp.set_from_array(linear_array)
