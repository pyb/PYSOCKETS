import socket
from collections import deque
# CLIENT
MAX_BUFFER_SIZE = 1024
DELIMITER = "\n"

class Client:
    '''
    a client socket
    protocol: 
    client initiates conversation
    client can send multiple messages before receiving a response
    messages do not have fixed length
    1st message: number of messages to send
    each message is delimited by new line
    on recv: client calls recv() until it receives all messages

    '''

    def __init__(self, server_addr, msgs):
        '''creates a client socket'''
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print "client about to connect"
        self.N = len(msgs)
        self.total = 0
        print "number of messages to send: {}".format(self.N)
        self.sock.connect(server_addr)
        self.sendQ = deque()
        self.sendQ.append(str(self.N) + DELIMITER) # initialize msgs with number of messages
        for msg in msgs:
            self.sendQ.append(msg)
        self.recvL = []     # each element is a complete message
        self.buffer = ""         # holds part of a msg; complete msg is appended to recvQ
        self.sock.setblocking(False) # make socket non-blocking

    def send(self):
        """send message"""
        nextMSG = self.sendQ.popleft() 
        if nextMSG != '':
            sent = self.sock.send(nextMSG)
            print "client sent ",  sent
            print "sendQ is {}".format(len(self.sendQ))
            if sent == 0:
                raise RuntimeError("send: socket connection broken")
            self.sendQ.appendleft(nextMSG[sent:]) # add part of msg not sent to front of deque
        return len(self.sendQ) == 0

    
    def receive(self):
        """read characters; store complete msgs in recvL"""
#        print 'Client: in receive()'
        if DELIMITER in self.buffer:
            next_msg, sep, msgs_rest = self.buffer.partition(DELIMITER)
            self.recvL.append(next_msg)
            self.buffer = msgs_rest
            print "A : Received {} messages, Last len {}".format(len(self.recvL), len(self.recvL[-1]))
            return len(self.recvL) == (self.N + 1)
        else:
            chunk = self.sock.recv(MAX_BUFFER_SIZE)
            self.total += len(chunk)
            print "total : {} / {}", self.total, self.total + len(self.buffer) # grand total 204088
            # check for msg delimiter
            next_msg, sep, msgs_rest = chunk.partition(DELIMITER)
            if sep  == DELIMITER:
                # delimiter found
                msg = self.buffer + next_msg
                self.recvL.append(msg)
                self.buffer = msgs_rest # could contain 0 or more DELIMITERS
            else:
                # delimiter not found
                if len(chunk) == 0:
                    raise RuntimeError("receive: socket connection broken")
                    
                self.buffer += next_msg
        print "B : Received {} messages".format(len(self.recvL))
        print "total : {} / {}", self.total, self.total + len(self.buffer) # grand total 204088
        print "Buf len : {}".format(len(self.buffer))
        return len(self.recvL) == (self.N + 1)
