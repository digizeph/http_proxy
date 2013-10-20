#!/usr/bin/python
import socket
import re
import thread
import sys, os

def processConn(conn,addr):
	request = conn.recv(1024)
	new_request_list = []
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
		elif re.search("Accept-Encoding",d):
			continue
		new_request_list.append(d)
	new_request="\r\n".join(new_request_list)

	print "request content from ",host,get
	print new_request_list
	if not host=='':
		c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			c.connect((host, 80))
		except:
			print "[1] connection to %s failed."%host
			conn.send( "connection to %s failed."%host)
			conn.close()
			return
		c.send(new_request)
		cdata = ""
		FIRST=True
		content_size=-1
		CONTENT=False
		while 1:
			try:
				line = c.recv(4096)
				if line=="":
					print "   EMPTY LINE"
					return

				if FIRST:
					strlist=(line.split("\r\n\r\n"))
					header=strlist[0].split("\r\n")
					print header
					for h in header:
						if h.startswith("Content-Length"):
							content_size=int(h.split(" ")[1])
						# REDIRECTION
						if re.search("Location",h):
							redirect = h.split(" ")[1].lower()
							rhost=redirect.lstrip("http://")
							resource="/"+"/".join(rhost.split("/")[1:])
							rhost=rhost.split("/")[0]
							c.close()
							try:
								c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
								c.connect((rhost, 80))
								new_request_lst=[]
								for d in lst:
									ld=d.lower()
									new=''
									if re.search("^host",ld):
										new = "Host: %s"%rhost
									elif re.search("^get",ld):
										new = "%s %s %s"%(d.split(" ")[0],resource,d.split(" ")[2])
									elif re.search("encoding"):
										print "disable encoding",d
										continue
									else:
										new = d
									new_request_lst.append(new)
								new_request="\r\n".join(new_request_lst)
								c.send(new_request)
								cdata = ""
								FIRST=True
								content_size=-1
								CONTENT=False
							except Exception as e:
								exc_type, exc_obj, exc_tb = sys.exc_info()
								fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
								print(exc_type, fname, exc_tb.tb_lineno)
								print "[2] connection to %s failed."%rhost
								conn.send( "connection to %s failed."%rhost)
								conn.close()
								return
							continue
							
					if content_size>0:
						try:
							content_size-=len(strlist[1])
							CONTENT=True
						except:
							pass
				else:
					if CONTENT:
						content_size -= len(line)
				FIRST=False
				cdata += str(line)
				if CONTENT and content_size<=0:
					break
				elif re.search("</HTML>",line,re.IGNORECASE):
						break

			except Exception as e:
				exc_type, exc_obj, exc_tb = sys.exc_info()
				fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
				print(exc_type, fname, exc_tb.tb_lineno)
				#print e
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
	print s.gettimeout()
	while 1:
		conn, addr = s.accept()
		thread.start_new_thread(processConn,(conn,addr))