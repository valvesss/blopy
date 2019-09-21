import os
import sys
import time
import json
import uuid
import socket
import logging
import netifaces
import threading

from pprint import pprint

logging.basicConfig(level=logging.INFO, format='%(asctime)s :: %(levelname)s :: %(message)s')

class Peer(threading.Thread):

    def __init__(self):
        super(Peer, self).__init__()
        # The IP of this node
        self.host = get_ip()

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
        while not self.stop_flag:
            try:
                logging.info('Peer {0} is set up, waiting for new connections.'.format(self.id))
                connection, client_address = self.sock.accept()
                inbound_peer = PeerConnection(self.sock, client_address[0], client_address[1])
                inbound_peer.start()
                self.nodesIn.append(inbound_peer)
            except socket.timeout:
                logging.info('Peer {0} has closed his connection due to timeout'.format(self.id))
                self.stop()

            time.sleep(0.01)

        # If flag is set true, close all conecctions and itself
        for nodesIn in self.nodesIn:
            nodesIn.stop()
            nodesIn.join()

        self.stop()

    def get_message_count_send(self):
        return self.message_count_send

    def get_message_count_recv(self):
        return self.message_count_recv

    def validate_node_chain(self):
        if not self.chain:
            pass # REQUEST CHAIN

    def connect_with_peer(self, host, port):
        self.validate_new_peer_connection(host)
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((host, port))
            outbound_peer = PeerConnection(sock, host, port)
            self.nodesOut.append(outbound_peer)

        except Exception as e:
            logging.critical("Could not connect with node! Error: {}".format(e))
            self.stop()
            sys.exit(0)
        return outbound_peer

    def validate_new_peer_connection(self, host):
        if host == self.host:
            logging.critical('Cannot stablish connection with this own peer! Aborting.')
            self.stop()
            sys.exit(0)

        for node in self.nodesOut:
            if node.get_host() == host:
                logging.critical('Already connected with this peer! Aborting.')
                self.stop()
                sys.exit(0)

    def stop(self):
        logging.info('Peer {0} has closed the connection.'.format(self.id))
        self.stop_flag = True
        self.sock.close()

class PeerConnection(threading.Thread):

    def __init__(self, sock, host, port):
        super(PeerConnection, self).__init__()
        
        self.host = host
        self.port = port
        self.sock = sock
        self.buffer = ""
        self.id = uuid.uuid1()
        self.stop_flag = False

        logging.info('Peer is now connected to peer {0}'.format(self.host))

    def send(self):
        message = 'Hello! This is a test :)'

        try:
            self.sock.sendall(message.encode('utf-8'))
            logging.info('Peer {0} sent a message to all nodes!'.format(self.host))
        except Exception as err:
            logging.error('Peer {0} could not send message! \nError: {1}'.format(self.host, err))
            self.sock.close()
            sys.exit(0)

    def run(self):
        self.sock.settimeout(10.0)
        logging.info('Peer {0} is ready to receive packets'.format(self.host))
        while not self.stop_flag:
            packets = ""
            try:
                packets = self.sock.recv(4096)
                print('pppackets (befor encode):', packets)
                packets = packets.encode('utf-8')
                print('pppackets (after encode):', packets)
            except socket.timeout:
                logging.info('Peer {0} has closed his connection due to timeout'.format(self.id))
                self.stop()

            if packets != "":
                try:
                    self.buffer += str(packets.decode('utf-8'))
                    print('peer1 buffer:',self.buffer)
                except:
                    logging.info('Error in decode message!')
                    self.stop()
                logging.info('Peer {0} has closed his connection due to received packets'.format(self.id))
                self.stop()

    def stop(self):
        self.stop_flag = True
        self.sock.close()

def get_ip():
    if os.name == 'nt':
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
    elif os.name == 'posix':
        netifaces.ifaddresses('enp0s3')
        ip = netifaces.ifaddresses('enp0s3')[netifaces.AF_INET][0]['addr']
    return ip

def main():
    peer = Peer()
    if len(sys.argv) > 1:
        peer.start()
        node1 = peer.connect_with_peer('192.168.0.40', 5000)
        time.sleep(3)
        node1.send()
        node1.stop()
    else:
        peer.start()
        node1 = peer.connect_with_peer('192.168.0.25', 5000)
        time.sleep(15)
        peer.stop()

main()
