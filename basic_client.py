#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import socket
import fileinput

# ip = "52.53.187.155"
# port = 2016
ip = sys.argv[1]
port = int(sys.argv[2])


client_sck = socket.socket()
client_sck.connect((ip, port))


while True:
	
	# print("dsad")
	line = sys.stdin.readline()
	client_sck.send(line)
	