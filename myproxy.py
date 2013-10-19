#!/usr/bin/python
import socket
import re
import thread

def processConn(conn,addr):
	request = conn.recv(1024)
	host = ''
	if not request: 
		conn.close()
		return
	lst = request.split("\r\n")
	for d in lst:
		if re.search("^Host",d):
			host = d.split(' ')[1]
	#print "host",host
	if not host=='':
		c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			c.connect((host, 80))
		except:
			print "connection to %s failed."%h
			conn.send( "connection to %s failed."%h)
			conn.close()
			return
		c.send(request)
		cdata = ""
		while 1:
			try:
				line = c.recv(1024)
				cdata += str(line)
				if re.search("</HTML>",line,re.IGNORECASE):
					#					print "FOUND /HTML"
					break
				if len(line)==0:
					break
				#print line
			except :
				break
		c.close()
		conn.send(cdata)
	conn.close()


if __name__=="__main__":
	HOST = ''                 # Symbolic name meaning the local host
	PORT = 28088             # Arbitrary non-privileged port
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((HOST, PORT))
	s.listen(1)
	while 1:
		conn, addr = s.accept()
		thread.start_new_thread(processConn,(conn,addr))