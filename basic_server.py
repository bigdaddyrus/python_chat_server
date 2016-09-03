#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import socket

port = int(sys.argv[1])


server_sck = socket.socket()
server_sck.bind(("localhost", port))

server_sck.listen(3)

while True:
	#accept connections from outside
	(clientsocket, address) = server_sck.accept()
	#now do something with the clientsocket
	msg = clientsocket.recv(1024)
	# print("before {}".format(msg))
	print(msg)



