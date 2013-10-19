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
	if not host=='':
		c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			c.connect((host, 80))
		except:
			print "connection to %s failed."%host
			conn.send( "connection to %s failed."%host)
			conn.close()
			return
		c.send(request)
		cdata = ""
		FIRST=True
		content_size=-1
		CONTENT=False
		while 1:
			try:
				line = c.recv(4096)
				if FIRST:
					strlist=(line.split("\r\n\r\n"))
					header=strlist[0].split("\r\n")
					for h in header:
						if h.startswith("Content-Length"):
							content_size=int(h.split(" ")[1])
					if content_size>=0:
						content_size-=len(strlist[1])
						CONTENT=True
				else:
					if CONTENT:
						content_size -= len(line)
				cdata += str(line)
				if CONTENT and content_size<=0:
					break
				elif re.search("</HTML>",line,re.IGNORECASE):
						break

				'''
				if re.search("</HTML>",line,re.IGNORECASE):
					#print "RECV: END OF HTML"
					break
				if len(line)==0:
					#print "RECV: EMPTY"
					break
				'''
			except Exception,e:
				print e
				break
		c.close()
		conn.send(cdata)
	conn.close()
	print "finish"


if __name__=="__main__":
	HOST = ''                 # Symbolic name meaning the local host
	PORT = 28088             # Arbitrary non-privileged port
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((HOST, PORT))
	s.listen(1)
	print s.gettimeout()
	while 1:
		print "start" 	# tested, multi-thread is correct.
		conn, addr = s.accept()
		thread.start_new_thread(processConn,(conn,addr))