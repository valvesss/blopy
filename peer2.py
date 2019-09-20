import sys
import time
import json
import uuid
import socket
import logging
import threading

from pprint import pprint

logging.basicConfig(level=logging.INFO, format='%(asctime)s :: %(levelname)s :: %(message)s')

class Peer():

    def __init__(self):

        # The IP of this node
        self.host = '192.168.0.40'

        # The port this node is up
        self.port = 5000

        # The Universal Unique Identifier of this node
        self.id = uuid.uuid1()

        # Number of messages this node has sent
        self.message_count_send = 0

        # Number of messages this node received
        self.message_count_recv = 0

        # The chain of this node
        self.chain = []

        # Nodes the are connected with this node
        self.nodesIn = []

        # Nodes the this node is connected to
        self.nodesOut = []

        # Iniciate server listening
        self.init_server()

        # Set stop flag
        self.stop_flag = False

    def init_server(self):
        logging.info("Inicializating peer at: {0}:{1} with ID: {2}".format(self.host,self.port,self.id))

        # Defines the socket connection
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Binds the socket with the IP and port
        self.sock.bind(('', self.port))

        # Set socket timeout
        self.sock.settimeout(10.0)

        # Enables the server to accept connections | With only 1 to refuse before disconnect
        self.sock.listen(1)

    def run(self):
        while self.stop_flag is False:
            try:
                logging.info('Peer {0} is set up, waiting for new connections.'.format(self.id))
                connection, client_address = self.sock.accept()
                inbound_peer = PeerConnection(self.sock, client_address[0], client_address[1])
                self.nodesIn.append(inbound_peer)
                inbound_peer.receive()
            except socket.timeout:
                logging.info('Peer {0} has closed his connection due to timeout'.format(self.id))
                self.stop_flag = True
                self.sock.close()
                return False

            time.sleep(0.01)

        # If flag is set true, close all conecctions and itself
        for nodesIn in self.nodesIn:
            nodesIn.stop()

        self.sock.close()

    def get_message_count_send(self):
        return self.message_count_send

    def get_message_count_recv(self):
        return self.message_count_recv

    def validate_node_chain(self):
        if not self.chain:
            pass # REQUEST CHAIN

    def close_socket_connection(self):
        self.sock.close()
        logging.info('Peer {0} has closed the connection.'.format(self.id))

    def connect_with_peer(self, host, port):
        self.validate_new_peer_connection(host)
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((host, port))
            outbound_peer = PeerConnection(sock, host, port)
            self.nodesOut.append(outbound_peer)

        except Exception as e:
            logging.critical("Could not connect with node!")
            sys.exit(0)

    def validate_new_peer_connection(self, host):
        if host == self.host:
            logging.critical('Cannot stablish connection with this own peer! Aborting.')
            sys.exit(0)

        for node in self.nodesOut:
            if node.get_host() == host:
                logging.critical('Already connected with this peer! Aborting.')
                sys.exit(0)

class PeerConnection():

    def __init__(self, sock, host, port):

        self.host = host
        self.port = port
        # self.peerServer = peerServer
        self.sock = sock
        self.buffer = ""
        self.id = uuid.uuid1()
        self.stop_flag = False

        logging.info('Peer is now connected to peer {0}'.format(self.host))

    def send(self, data):
        try:
            self.sock.sendall(data.encode('utf-8'))
        except Exception as err:
            logging.error('An error ocurred on peer {0}: \n{1}'.format(self.id, err))
            sys.exit(0)

    def receive(self):
        self.sock.settimeout(10.0)
        while self.stop_flag is False:
            logging.info('Peer {0} is ready to receive packets'.format(self.host))
            packets = ""
            try:
                packets = self.sock.recv(4096)
                packets = packets.encode('utf-8')

            except socket.timeout:
                logging.info('Peer {0} has closed his connection due to timeout'.format(self.id))
                self.sock.close()

            print('pppackets:', packets)
            if packets != "":
                print('packets:', packets)
                self.buffer += str(packets.decode('utf-8'))
                # data = json.loads(self.buffer)
                print('data:',data)
                self.sock.close()
                logging.info('Peer {0} has closed his connection due to received packets'.format(self.id))
                self.stop_flag = True

        self.sock.close()

def get_ip():
    hostname = socket.gethostname()
    return socket.gethostbyname(hostname)

peer = Peer()
peer.run()
time.sleep(15)
peer.stop_flag = True
