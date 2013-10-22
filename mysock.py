#!/usr/bin/python
# Echo client program
import socket, sys

if len(sys.argv)<=1:
	print "need a url as input"
	exit(1)
#HOST = 'ix.cs.uoregon.edu'    # The remote host
HOST = ''    # The remote host
PORT = 28088              # The same port as used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
s.send('GET %s HTTP/1.1\r\n'%sys.argv[1])
s.send('Host: %s\r\n'%sys.argv[1])
s.send('Accept: */*\r\n')
s.send('\r\n')
"""
s.send('GET / HTTP/1.1\r\n')
s.send('Host: ix.cs.uoregon.edu\r\n')
s.send('Accept: */*\r\n')
s.send('\r\n')
"""

data = s.recv(1024)
s.close()
print 'Received', repr(data)