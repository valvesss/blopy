import os
import sys
import json
import time
import socket
import logging
import threading

logging.basicConfig(level=logging.INFO, format='%(asctime)s :: %(levelname)s :: %(message)s')

class PeerServer():
    def __init__(self):
        self.__host__ = get_ip()
        self.__port__ = 5000
        self.__close_flag__ = False
        self.__nodesIn__ = []
        self.timeout = 20
        self.start()

    def start(self):
        self.__sock__ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__sock__.bind(('', self.__port__))
        self.__sock__.listen()
        self.__sock__.settimeout(self.timeout)
        logging.info('PeerServer is waiting for income connections.')

    def run(self):
        while not self.__close_flag__:
            try:
                peer_socket, peer_addr = self.__sock__.accept()
                with peer_socket:
                    new_inbound_peer = PeerNode(self.__host__, peer_socket, peer_addr)
                    new_inbound_peer.start()
                    self.__nodesIn__.append(new_inbound_peer)
                    self.close_server_connection('test close inbounds')
            except socket.timeout:
                self.close_server_connection('timeout')

        self.close_server_connection('finished run.')

    def close_server_connection(self, msg):
        self.__close_flag__ = True
        self.__sock__.close()
        logging.info('Server closed his connection due to ' + msg)
        sys.exit(0)

    def close_connected_nodes(self):
        for nodes in self.__nodesIn__:
            nodes.close_connection('PeerServer request')

class PeerNode(threading.Thread):
    def __init__(self, serverHost, sock, addr):
        super(PeerNode, self).__init__()
        self.__serverHost__ = serverHost
        self.__sock__ = sock
        self.__host__ = addr[0]
        self.__port__ = addr[1]
        self.__buffer__ = ""
        self.__close_flag__ = False
        self.timeout = 20

        logging.info('Server connected to PeerNode: {0}:{1}.'.format(self.__host__, self.__port__))

    def run(self):
        while not self.__close_flag__:
            try:
                packets = self.__sock__.recv(1024)
                self.send(packets)
                time.sleep(2)
            except socket.timeout:
                self.close_connection('timeout')
        #     packets = ""
        #     try:
        #         packets = self.__sock__.recv(1024)
        #         packets = packets.encode('utf-8')

        #
        #     if packets != "":
        #         try:
        #             self.__buffer__ += packets
        self.close_connection('finished run')

    def send(self, data):
        self.__sock__.sendall(data)
        logging.info('Server sent a message to: {0}:{1}.'.format(self.__host__, self.__port__))

    def close_connection(self, msg):
        self.__close_flag__ = True
        self.__sock__.close()
        logging.info('PeerNode {0}:{1} has been disconnected due to {2}.'.format(self.__host__, self.__port__,msg))

def get_ip():
    if os.name == 'nt':
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
    elif os.name == 'posix':
        netifaces.ifaddresses('enp0s3')
        ip = netifaces.ifaddresses('enp0s3')[netifaces.AF_INET][0]['addr']
    return ip

if __name__ == '__main__':
    peer = PeerServer()
    try:
        peer.run()
    except KeyboardInterrupt:
        peer.close_server_connection('KeyboardInterrupt')

main()
