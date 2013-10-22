#!/usr/bin/python
import socket
import re
import thread
import sys, os

def processConn(conn,addr):
	request = conn.recv(8092)
	print "######## REQUEST ########"
	print request
	print "######## END OF REQUEST ########"
	print ""
	host = ''
	get=''
	redirect=''
	if not request: 
		conn.close()
		return
	lst = request.split("\r\n")
	for d in lst:
		if re.search("^Host",d):
			host = d.split(' ')[1]
		elif re.search("^GET",d):
			get = d.split(' ')[1]

	#print "request content from ",host,get
	if not host=='':
		c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			c.connect((host, 80))
		except:
			print "[1] connection to %s failed."%host
			conn.send( "connection to %s failed."%host)
			conn.close()
			return
		#c.settimeout(3)
		num_sent = c.send(request)
		print "******** REQUEST SENT TO SERVER %s of %d bytes ********"%(host,num_sent)
		print ""
		cdata = ""
		FIRST=True
		content_size=-1
		CONTENT=False
		HTML=False
		CHUNKED=False
		while 1:
			try:
				line = c.recv(8092)
				conn.send(line)
				if line=="":
					print "   EMPTY LINE"
					return

				if FIRST:
					strlist=(line.split("\r\n\r\n"))
					header=strlist[0].split("\r\n")
					content=""
					print "######## RESPONSE from %s ########"%host
					print line
					print "######## END OF RESPONSE ########"
					print ""
					for h in header:
						if h.startswith("Content-Length"):
							content_size=int(h.split(" ")[1])
							content=strlist[1]
							CONTENT=True
						if h.startswith("Content-Type: text/html"):
							HTML=True
						if h.startswith("Transfer-Encoding: chunked"):
							CHUNKED=True
					FIRST=False
				else:
					content=line

				#cdata += str(line)

				if CONTENT:
					content_size-=len(content)
					if content_size<=0:
						print "BREAK: NO CONTENT LEFT %d"%content_size
						print ""
						break
				elif re.search("</HTML>",line,re.IGNORECASE):
					print "BREAK: END OF HTML"
					print ""
					break
				elif CHUNKED:
					if re.search("\r\n0\r\n\r\n",line):
						print "BREAK: END OF CHUNKED MESSAGE"
						print ""
						break

			except socket.timeout:
				c.close()
				#conn.send(cdata)
				print "TIMEOUT ! ERROR !"
				break

			except Exception as e:
				exc_type, exc_obj, exc_tb = sys.exc_info()
				fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
				print(exc_type, fname, exc_tb.tb_lineno)
				print e
				break
		c.close()
		#print "######## SEND BACK CLIENT ########"
		#print "######## END OF CLIENT ########"
		#conn.send(cdata)
	conn.close()


if __name__=="__main__":
	HOST = ''                 # Symbolic name meaning the local host
	PORT = 28088             # Arbitrary non-privileged port
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((HOST, PORT))
	s.listen(1)
	print s.gettimeout()
	while 1:
		conn, addr = s.accept()
		thread.start_new_thread(processConn,(conn,addr))