import sys
import socket
import select
from utils import *


RECV_BUFFER = MESSAGE_LENGTH


class Server(object):
	def __init__(self, host, port):
		self.host = host
		self.port = port
		self.socket_list = []
		# each socket key corresponds to [name, channel]
		self.socket_dict = {}
		# each channel key corresponds to an array of client sockets
		self.channel_dict = {}
		self.server_socket


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
			ready_to_read,ready_to_write,in_error = select.select(self.socket_list,[],[],0)
		  
			for sock in ready_to_read:
				# a new connection request recieved
				if sock == server_socket: 
					sockfd, addr = server_socket.accept()
					self.socket_list.append(sockfd)
					

					print "Client (%s, %s) connected" % addr
					 
					self.broadcast(server_socket, sockfd, "[%s:%s] entered our chatting room\n" % addr)
				 
				# a message from a client, not a new connection
				else:
					# process data recieved from client, 
					try:
						# receiving data from the socket.
						data = sock.recv(RECV_BUFFER)
						if data:
							# there is something in the socket
							self.broadcast(server_socket, sock, "\r" + '[' + str(sock.getpeername()) + '] ' + data)  
						else:
							# remove the socket that's broken    
							if sock in self.socket_list:
								self.socket_list.remove(sock)

							# at this stage, no data means probably the connection has been broken
							self.broadcast(server_socket, sock, "Client (%s, %s) is offline\n" % addr) 

					# exception 
					except:
						self.broadcast(server_socket, sock, "Client (%s, %s) is offline\n" % addr)
						continue

		server_socket.close()


	# handle commands sent by users
	def handle_cmd(self, cmd, sock):
        if re.search('^/join', cmd):
        	channel = cmd.split()[1]

        elif re.search('^/create', cmd):
        	channel = cmd.split()[1]
        	self.channel_dict[channel] = [sock]

        
        # elif re.search('^/list', cmd):

        elif re.search('^/chatname', cmd):
        	chatname = cmd.split()[1]
        	self.socket_dict[sock][0] = chatname 

        else:
            print SERVER_INVALID_CONTROL_MESSAGE.format(cmd)



	# broadcast chat messages to all connected clients
	def broadcast (self, server_socket, sock, message):
		message = pad_msg(message)
		for socket in self.socket_list:
			# send the message only to peer
			if socket != server_socket and socket != sock :
				try :

					socket.send(message)
				except :
					# broken socket connection
					socket.close()
					# broken socket, remove it
					if socket in self.socket_list:
						self.socket_list.remove(socket)


	# broadcast chat messages to all connected clients in a channel
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
					# broken socket, remove it
					if socket in chan_socket_list:
						chan_socket_list.remove(socket)
						self.channel_dict[channel] = chan_socket_list

# helper functions
def pad_msg(msg):
    if (len(msg) < MESSAGE_LENGTH):
        msg = msg.ljust(MESSAGE_LENGTH)
    return msg


if __name__ == "__main__":

	if(len(sys.argv) < 3) :
		print 'Usage : python server.py hostname port'
		sys.exit()
	host = sys.argv[1]
	port = int(sys.argv[2])

	chat_server = Server(host, port)
	chat_server.serve()
	sys.exit(chat_server.serve()) 