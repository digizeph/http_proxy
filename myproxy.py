#!/usr/bin/python
import socket
import re
import thread
import sys, os

def processConn(conn,addr):
	request = conn.recv(8092)
	host = ''
	get=''
	redirect=''
	if not request: 
		conn.close()
		return
	lst = request.split("\r\n")
	lst2 = []
	for d in lst:
		if re.search("^Host",d):
			host = d.split(' ')[1]
		elif re.search("^GET",d):
			getlst=d.split(' ')

			get = getlst[1]
			if re.search("http://",get):
				get= '/'.join(get.lstrip("http://").split('/')[1:])
			get='/'+get
			getlst[1]=get
			d=' '.join(getlst)
		lst2.append(d)
	request='\r\n'.join(lst2)

	print "HTTP request to ",host
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
					return

				if FIRST:
					print "HTTP reply from ",host
					strlist=(line.split("\r\n\r\n"))
					header=strlist[0].split("\r\n")
					content=""
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
						break
				elif re.search("</HTML>",line,re.IGNORECASE):
					break
				elif CHUNKED:
					if re.search("\r\n0\r\n\r\n",line):
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
	if len(sys.argv)!=2:
		print "USAGE: python myproxy.py PORT"
		print "  e.g. python myproxy.py 28088"
		print ""
		exit(1)
	HOST = ''                 # Symbolic name meaning the local host
	PORT = int(sys.argv[1])             # Arbitrary non-privileged port
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		s.bind((HOST, PORT))
		s.listen(1)
	except Exception,e:
		print "Cannot bind the port on %d"%PORT
		print e
		exit(1)
	while 1:
		conn, addr = s.accept()
		thread.start_new_thread(processConn,(conn,addr))