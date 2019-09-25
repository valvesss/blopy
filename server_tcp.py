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
                    new_inbound_peer = PeerNode(self.__host__, peer_socket, peer_addr, len(self.__nodesIn__))
                    # new_inbound_peer.start()
                    self.__nodesIn__.append(new_inbound_peer)
            except socket.timeout:
                self.close_server_connection('timeout')

        self.close_server_connection('finished run.')

    def send_to_nodes(self):
        for node in self.__nodesIn__:
            node.send()

    def close_server_connection(self, msg):
        if not self.__close_flag__:
            self.close_connected_nodes()
            self.stop()
            self.__sock__.close()
            logging.info('Server closed his connection due to {}.'.format(msg))
            sys.exit(0)

    def close_connected_nodes(self):
        for nodes in self.__nodesIn__:
            nodes.close_connection('PeerServer being shut down')

    def stop(self):
        if not self.__close_flag__:
            self.__close_flag__ = True

class PeerNode(threading.Thread):
    def __init__(self, serverHost, sock, addr, index):
        super(PeerNode, self).__init__()
        self.__serverHost__ = serverHost
        self.__sock__ = sock
        self.__host__ = addr[0]
        self.__port__ = addr[1]
        self.index = index
        self.__buffer__ = ""
        self.__close_flag__ = False
        self.timeout = 10

        logging.info('Server connected to InPeerNode: #{0} {1}:{2}.'.format(self.index,self.__host__, self.__port__))
        self.run()

    def run(self):
        self.__sock__.settimeout(self.timeout)
        while not self.__close_flag__:
            packets = ""
            try:
                packets = self.__sock__.recv(1024)
                packets = packets.decode('ascii')
            except socket.timeout:
                self.close_connection('timeout')
            except Exception as err:
                pass
            if packets != "":
                try:
                    self.__buffer__ += packets
                except:
                    logging.info('InPeerNode #{0}: Error decoding message: {1}{2}'.format(self.index,packets,type(packets)))
                    self.stop()
                self.send()

        self.close_connection('finished run')

    def send(self):
        data = self.__buffer__
        data = data.encode('ascii')
        self.__sock__.sendall(data)
        logging.info('Server sent a message to InPeerNode: #{0}.'.format(self.index))

    def close_connection(self, msg):
        if not self.__close_flag__:
            self.stop()
            self.__sock__.close()
            logging.info('InPeerNode #{0} has been disconnected due to {1}.'.format(self.index,msg))

    def stop(self):
        if not self.__close_flag__:
            self.__close_flag__ = True

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
        # peer.send_to_nodes()
    except KeyboardInterrupt:
        peer.close_server_connection('KeyboardInterrupt')

main()
