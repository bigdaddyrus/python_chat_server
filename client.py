import sys
import socket
import select
import re
from utils import *

RECV_BUFFER = MESSAGE_LENGTH


class Client(object):

    def __init__(self, chatname, server_host, server_port):
        self.server_host = server_host
        self.server_port = server_port
        self.socket_list = []

        # current channel name
        self.in_channel = ''
        self.channel_lst = []
        self.chatname = chatname

    def serve(self):
        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
         
        # connect to remote host
        try :
            s.connect((host, port))
        except :
            print CLIENT_CANNOT_CONNECT.format(host, port)
            sys.exit()
        
        # to be removed
        print 'Connected to remote host. You can start sending messages'


        sys.stdout.write('[Me] '); sys.stdout.flush()
        first_msg = True

        while 1:

            socket_list = [sys.stdin, s]
             
            # Get the list sockets which are readable
            ready_to_read,ready_to_write,in_error = select.select(socket_list , [], [])
             
            for sock in ready_to_read:             

                if sock == s:
                    # incoming message from remote server, s
                    data = sock.recv(RECV_BUFFER)
                    if not data :
                        print CLIENT_SERVER_DISCONNECTED.format(host, port)
                        sys.exit()
                    else :
                        #print data
                        sys.stdout.write(CLIENT_WIPE_ME)
                        sys.stdout.write("\r"+data.rstrip(' '))
                        sys.stdout.write(CLIENT_MESSAGE_PREFIX); sys.stdout.flush()     
                
                else :
                    if first_msg:
                        msg = "/chatname {}".format(self.chatname)
                        s.send(pad_msg(msg))
                    
                    # user entered a message
                    msg = sys.stdin.readline()

                    # See if msg is a command
                    if re.search('^/', msg):
                        self.handle_cmd(msg)
                    
                    # send msg if not a command
                    else:
                        if not self.in_channel:
                            print SERVER_CLIENT_NOT_IN_CHANNEL
                        else:
                            
                            s.send(pad_msg(msg))
                    sys.stdout.write('[Me] '); sys.stdout.flush()



    # command handler
    def handle_cmd(self, cmd):
        if re.search('^/join', cmd):
            if re.search( '^/join .+', cmd):
                channel = cmd.split()[1]
                self.join_channel(channel)
            else:
                print SERVER_JOIN_REQUIRES_ARGUMENT
        elif re.search('^/create', cmd):
            if re.search( '^/create .+', cmd):
                channel = cmd.split()[1]
                self.create_channel(channel)
            else:
                print SERVER_CREATE_REQUIRES_ARGUMENT
        elif re.search('^/list *', cmd):
            self.list_channels()
        else:
            print SERVER_INVALID_CONTROL_MESSAGE.format(cmd)

    # joining channel
    def join_channel(self, channel):
        if channel not in self.channel_lst:
            print SERVER_NO_CHANNEL_EXISTS.format(channel)
        else:

            self.in_channel = channel


    #  create channel
    def create_channel(self, channel):
        if channel in self.channel_lst:
            print SERVER_CHANNEL_EXISTS.format(channel)
        else:
            self.in_channel = channel
            self.channel_lst.append(channel)

    def list_channels(self):
        for c in self.channel_lst:
            print "{}\n".format(c)


# helper functions
def pad_msg(msg):
    if (len(msg) < MESSAGE_LENGTH):
        msg = msg.ljust(MESSAGE_LENGTH)
    return msg




if __name__ == "__main__":
    if(len(sys.argv) < 4) :
        print 'Usage : python client.py chatname hostname port'
        sys.exit()
    name = sys.argv[1]
    host = sys.argv[2]
    port = int(sys.argv[3])
    client_server = Client(name, host, port)
    sys.exit(client_server.serve())