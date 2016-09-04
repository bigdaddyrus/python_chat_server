import sys
import socket
import select
from utils import *
import re

RECV_BUFFER = MESSAGE_LENGTH
HOST = "localhost"

class Server(object):
	def __init__(self, port):
		self.host = HOST
		self.port = port
		# list of socket object
		self.socket_list = []
		# each socket fileno key corresponds to [name, channel]
		self.socket_dict = {}
		# each channel key corresponds to an array of client sockets objects
		self.channel_dict = {"split_messages":[]}

		self.server_socket = ''

		# for handling split messages
		self.buffering = False
		self.split_buffer = ''

	def serve(self):

		server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		server_socket.bind((self.host, self.port ))
		server_socket.listen(10)
		
		# add server socket object to the list of readable connections
		self.socket_list.append(server_socket)
		self.server_socket = server_socket

		print "Chat server started on port " + str(self.port )
	 
		while 1:

			# get the list sockets which are ready to be read through select
			# 4th arg, time_out  = 0 : poll and never block
			ready_to_read,ready_to_write,in_error = select.select(self.socket_list,[],[])
		  	
			for sock in ready_to_read:
				# a new connection request recieved
				if sock == server_socket: 
					sockfd, addr = server_socket.accept()
					self.socket_list.append(sockfd)
					self.socket_dict[sockfd.fileno()] = ['','']

					print "Client (%s, %s) connected" % addr
					 
					# self.broadcast(server_socket, sockfd, "[%s:%s] entered our chatting room\n" % addr)
				 
				# a message from a client, not a new connection
				else:
					# process data recieved from client, 

					# try:
					# receiving data from the socket.

					# TODO: split msg: if buffer < 200, wait for a while for the full message
					data = sock.recv(RECV_BUFFER)

					# print sock
					# print sock.fileno()
					# print self.socket_list
					if data:


						# there is something in the socket

						data = data.rstrip(' ')
						# print data

						# see if first message
						if not self.getname(sock):
							self.socket_dict[sock.fileno()][0] = data
							continue

						# See if data is a command
						if re.search('^/', data):
							self.handle_cmd(data, sock)

						# if not command broadcast this message to channel
						else:
							channel = self.getchan(sock)

							if not channel:
								sock.send(pad_msg(SERVER_CLIENT_NOT_IN_CHANNEL+'\n'))
							else:
								self.broadcast_to(channel, server_socket, sock, "\r" + '[' + self.getname(sock) + '] ' + data)  
					
					else:
						# at this stage, no data means probably the connection has been broken
						self.broadcast_to(self.getchan(sock), server_socket, sock, SERVER_CLIENT_LEFT_CHANNEL.format(self.getname(sock)) + '\n') 

						# remove the socket that's broken    
						if sock in self.socket_list:
							self.remove_socket(sock)


					# add exception handler last fckkk
					# except:
					# 	self.broadcast(server_socket, sock, "Client (%s, %s) is offline\n" % addr)
					# 	continue

		self.server_socket.close()

	def getname(self, sock):
		return self.socket_dict[sock.fileno()][0]

	def getchan(self, sock):
		return self.socket_dict[sock.fileno()][1]

	def is_in_channel(self, sock):
		# print sock
		return (self.socket_dict[sock.fileno()][1] != '')

	# remove disconnected socket
	def remove_socket(self, sock):
		
		if self.is_in_channel(sock):
			channel = self.getchan(sock)
			self.channel_dict[channel].remove(sock)
		self.socket_list.remove(sock)
		self.socket_dict.pop(sock.fileno(), None)

	def remove_from_channel(self, sock):
		if self.is_in_channel(sock):
			channel = self.getchan(sock)
			self.channel_dict[channel].remove(sock)

		self.socket_dict[sock.fileno()][1] = ''


	# TODO: 
	# handle commands sent by users
	def handle_cmd(self, cmd, sock):

		if re.search('^/join', cmd):
			channel = cmd.split()[1]

			# if doesn't exit, send error message
			if channel not in self.channel_dict.keys():
				sock.send(pad_msg(SERVER_NO_CHANNEL_EXISTS.format(channel)+'\n'))
			else:
				# has joined channel
				self.broadcast_to(channel, self.server_socket, sock, SERVER_CLIENT_JOINED_CHANNEL.format(self.getname(sock))+'\n')

				# XXX has left channel
				if self.is_in_channel(sock):
					self.broadcast_to(self.getchan(sock), self.server_socket, sock, SERVER_CLIENT_LEFT_CHANNEL.format(self.getname(sock))+'\n')


				# remove from channel
				self.remove_from_channel(sock)

				# join new channel
				self.socket_dict[sock.fileno()][1] = channel
				# print self.channel_dict
				self.channel_dict[channel] += [sock]
				

				
		elif re.search('^/create', cmd):
			channel = cmd.split()[1]

			# if exits, send error message
			if channel in self.channel_dict.keys():
				sock.send(pad_msg(SERVER_CHANNEL_EXISTS.format(channel)+'\n'))
			else:


				# XXX has left channel
				if self.is_in_channel(sock):
					self.broadcast_to(self.getchan(sock), self.server_socket, sock, SERVER_CLIENT_LEFT_CHANNEL.format(self.getname(sock))+'\n')

				self.remove_from_channel(sock)
				self.channel_dict[channel] = [sock]

				self.socket_dict[sock.fileno()][1] = channel
				# print self.channel_dict
				# self.broadcast_to(channel, self.server_socket, sock, SERVER_CLIENT_LEFT_CHANNEL.format(self.getname(sock))) 

		# send to user only
		elif re.search('^/list', cmd):

			res = '\n'.join([str(c) for c in self.channel_dict.keys()])
			res = pad_msg(res+'\n')
			sock.send(res)

		# change chatname
		elif re.search('^/chatname', cmd):
			# print "handling chat name"
			chatname = cmd.split()[1]
			self.socket_dict[sock.fileno()][0] = chatname 

		# debug purpose
		# else:
		# 	print SERVER_INVALID_CONTROL_MESSAGE.format(cmd)



	# broadcast chat messages to all connected clients
	def broadcast (self, server_socket, sock, message):
		message = pad_msg(message)
		for socket in self.socket_list:
			# send the message only to peer
			if socket != server_socket and socket != sock :
				try :

					socket.send(message)
				except :
					print "Could not send message to socket {}".format(socket)
					# broken socket connection
					socket.close()
					# broken socket, remove it
					if socket in self.socket_list:
						self.remove_socket(socket)


	# padding the message, broadcast chat messages to all connected clients in a channel
	def broadcast_to (self, channel, server_socket, sock, message):
		message = pad_msg(message)
		chan_socket_list = self.channel_dict[channel]
		for socket in chan_socket_list:
			# send the message only to peer
			if socket != server_socket and socket != sock :
				try :
					socket.send(message)
				except :
					# broken socket connection
					socket.close()

					# broken socket, remove it from data structures
					if socket in chan_socket_list:
						self.remove_socket(socket)

# helper functions
def pad_msg(msg):
	if (len(msg) < MESSAGE_LENGTH):
		msg = msg.ljust(MESSAGE_LENGTH)
	return msg


if __name__ == "__main__":

	if(len(sys.argv) < 2) :
		print 'Usage : python server.py port'
		sys.exit()

	port = int(sys.argv[1])

	chat_server = Server(port)
	chat_server.serve()
	sys.exit(chat_server.serve()) 