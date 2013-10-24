HTTP Proxy Server
====

Author: Mingwei Zhang <mingwei@cs.uoregon.edu>

Proxy logic:
1. Receive HTTP request from client (browser).
2. Parse HTTP packet, get host and file requested.
3. Send proper request to the actual web server.
4. Get response from the web server and send it back to client.

To run the proxy, just simply run: 
	python myproxy.py 28088
Or just:
	python myproxy.py
The number in which can be any random number from 1025 to 65535, which is used as proxy port.
If you do not specify a port number, the program will use 28088 as a default port.

The output of the program is reduced to simply the request's destination and the reply's source.
The proxy has been tested on ix.cs.uoregon.edu with Firefox web browsing tasks, works just fine. 

Internally it applies socket.accept and multi-thread programming to allow multiple sockets connecting at the same time.
The detail implementation can refer to the code. 