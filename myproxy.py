#!/usr/bin/python
import socket,re,thread,sys,os

#
# Thread-run function:
#	For each client connection, the proxy will create a new thread.
#	The thread will send and receive actual server's response and send back to client
# Input:
#	conn -- socket connected to the proxy client
#	addr -- client's IP address
#
def processConn(conn,addr):
	# Get HTTP request from client and initialize variables
	request = conn.recv(8092)
	host = ''
	get=''
	redirect=''

	if not request: 
		conn.close()
		return
	lst = request.split("\r\n")
	lst2 = []

	# Extract Host and GET information from the request
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
		# Connect to the host server
		c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			c.connect((host, 80))
		except:
			print "[1] connection to %s failed."%host
			conn.send( "connection to %s failed."%host)
			conn.close()
			return
		#c.settimeout(3)
		
		# Send request to the server
		num_sent = c.send(request)
		cdata = ""
		FIRST=True
		content_size=-1
		CONTENT=False
		HTML=False
		CHUNKED=False

		# Process response in loop
		while 1:
			try:
				line = c.recv(8092)
				# Send whatever content received from server to the client.
				# The proxy does not need to process the client.
				conn.send(line)
				if line=="":
					return
				
				# First segment should contain HTTP response header
				# Extract Content-Length or Encoding type from the header.
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
				# If Content-Length is set in header, will count the received size of content until it reaches the threshold
				if CONTENT:
					content_size-=len(content)
					if content_size<=0:
						break
				# If reach the end of HTML tag, also quit loop
				elif re.search("</HTML>",line,re.IGNORECASE):
					break
				# If received a chunked data and reach its end, quit loop
				elif CHUNKED:
					if re.search("\r\n0\r\n\r\n",line):
						break

			# Process socket time-out error.
			except socket.timeout:
				c.close()
				#conn.send(cdata)
				print "TIMEOUT ! ERROR !"
				break

			# Process other errors
			except Exception as e:
				exc_type, exc_obj, exc_tb = sys.exc_info()
				fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
				print(exc_type, fname, exc_tb.tb_lineno)
				print e
				break
		# Close socket connection to the server
		c.close()
	
	conn.close()


if __name__=="__main__":
	# Accept port number as inputs.
	if len(sys.argv)!=2:
		print "USAGE: python myproxy.py PORT"
		print "  e.g. python myproxy.py 28088"
		print ""
		exit(1)
	HOST = ''                 # Symbolic name meaning the local host
	PORT = -1
	try:
		PORT = int(sys.argv[1])             # Arbitrary non-privileged port
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.bind((HOST, PORT))
		s.listen(1)
	except Exception,e:
		print "Cannot bind the port on %d"%PORT
		print e
		exit(1)

	while 1:
		conn, addr = s.accept()
		thread.start_new_thread(processConn,(conn,addr))