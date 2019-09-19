import sys
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
        logging.info('Peer {0} is listening.'.format(self.id))
        #self.close_socket_connection()

    def run(self):
        while True:
            try:
                logging.info('Peer {0} is set up, waiting for new connections.'.format(self.id))
                connection, client_address = self.sock.accept()
                inbound_peer = PeerConnection(self.__init__, self.sock, client_address)
                data = 'Hello! This is a test :)'
                inbound_peer.send(data)
                if connection:
                    self.sock.close()
                    logging.info('Original peer closed')
            except socket.timeout:
                pass

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
            outbound_peer = PeerConnection(self.__init__, sock, host)
            # outbound_peer.run()
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

    def __init__(self, peerServer, sock, host):

        self.host = host
        self.port = 5000
        self.peerServer = peerServer
        self.sock = sock
        self.buffer = ""
        self.id = uuid.uuid1()

        logging.info('Peer is now connected to peer {0}'.format(self.host))

    def send(self, data):
        try:
            # message = json.dumps(data)
            # pprint(message)
            print('data:',data)
            self.sock.sendall(data.encode('utf-8'))
        except Exception as err:
            logging.error('An error ocurred on peer {0}: \n{1}'.format(self.id, err))
            sys.exit(0)

    def receive(self):
        self.sock.settimeout(10.0)
        while True:
            packets = ""
            try:
                packets = self.sock.recv(4096)
                packets = packets.encode('utf-8')

            except socket.timeout:
                pass

            if packets != "":
                self.buffer += str(packets.decode('utf-8'))
                data = json.loads(self.buffer)
                pprint(data)

            self.sock.settimeout(None)
            self.sock.close()
            logging.info('Peer {0} has closed his connection'.format(self.id))

def get_ip():
    hostname = socket.gethostname()
    return socket.gethostbyname(hostname)

peer = Peer()
peer.init_server()
peer.run()
