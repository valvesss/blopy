import os
import sys
import json
import socket
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s :: %(levelname)s :: %(message)s')

class PeerServer():
    def __init__(self):
        self.__host__ = get_ip()
        self.__port__ = 5000
        self.__close_flag__ = False
        self.start()

    def start(self):
        self.__sock__ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__sock__.bind(('', self.__port__))
        self.__sock__.listen()
        self.__sock__.settimeout(10.0)
        logging.info('PeerServer is waiting for new connections.')

    def run(self):
        while not self.__close_flag__:
            try:
                peer_socket, peer_addr = self.__sock__.accept()
                with peer_socket:
                    new_peer = PeerNode(self.__host__, peer_socket, peer_addr)
                    data = peer_socket.recv(1024)
                    new_peer.send(data)
                    new_peer.close_connection()
            except socket.timeout:
                self.close_server_connection('timeout')

        self.close_server_connection('finished run.')

    def close_server_connection(self, msg):
        self.__close_flag__ = True
        self.__sock__.close()
        logging.info('Server closed his connection due to ' + msg)
        sys.exit(0)

class PeerNode():
    def __init__(self, serverHost, sock, addr):
        self.__serverHost__ = serverHost
        self.__sock__ = sock
        self.__host__ = addr[0]
        self.__port__ = addr[1]

        logging.info('Server connected to: {0}:{1}.'.format(self.__host__, self.__port__))

    def send(self, data):
        self.__sock__.sendall(data)
        logging.info('Server sent a message to: {0}:{1}.'.format(self.__host__, self.__port__))

    def close_connection(self):
        self.__sock__.close()
        logging.info('Peer {0}:{1} has been disconnected.'.format(self.__host__, self.__port__))

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
