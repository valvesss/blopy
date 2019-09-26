import os
import sys
import json
import time
import socket
import logging
import threading

logging.basicConfig(level=logging.INFO, format='%(asctime)s :: %(levelname)s :: %(message)s')

class PeerServer(threading.Thread):
    def __init__(self):
        super(PeerServer, self).__init__()
        self.__host__ = get_ip()
        self.__port__ = 5000
        self.__stop_flag__ = threading.Event()
        self.__nodesIn__ = []
        self.timeout = 20
        self.scale_up()

    def scale_up(self):
        self.__sock__ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__sock__.bind(('', self.__port__))
        self.__sock__.listen()
        self.__sock__.settimeout(self.timeout)
        logging.info('PeerServer is waiting for income connections.')

    def send_to_nodes(self):
        if self.__nodesIn__:
            for node in self.__nodesIn__:
                node.send()
        else:
            logging.info('There are no InboundNodes! Sending message to nodes failed.')

    def close_server_connection(self, msg):
        if not self.__stop_flag__.is_set():
            self.close_connected_nodes()
            self.stop()
            self.__sock__.close()
            logging.info('Server closed his connection due to {}.'.format(msg))
            sys.exit(0)

    def close_connected_nodes(self):
        for nodes in self.__nodesIn__:
            if not nodes.__stop_flag__.is_set():
                nodes.close_connection('PeerServer being shut down')
                nodes.join()

    def stop(self):
        if not self.__stop_flag__.is_set():
            self.__stop_flag__.set()

    def run(self):
        while not self.__stop_flag__.is_set():
            try:
                peer_socket, peer_addr = self.__sock__.accept()
                with peer_socket:
                    new_inbound_peer = PeerNode(self.__host__, peer_socket, peer_addr, len(self.__nodesIn__))
                    new_inbound_peer.start()
                    self.__nodesIn__.append(new_inbound_peer)
                    logging.info('New node appended to InboundNodes.')
                    # time.sleep(5)
                    new_inbound_peer.send()
            except socket.timeout:
                self.close_server_connection('timeout')

        self.close_server_connection('finished run.')

class PeerNode(threading.Thread):
    def __init__(self, serverHost, sock, addr, index):
        super(PeerNode, self).__init__()
        self.__serverHost__ = serverHost
        self.__sock__ = sock
        self.__host__ = addr[0]
        self.__port__ = addr[1]
        self.index = index
        self.__buffer__ = ""
        self.__stop_flag__ = threading.Event()
        self.timeout = 20
        logging.info('Server connected to InPeerNode: #{0} {1}:{2}.'.format(self.index,self.__host__, self.__port__))

    def stop(self):
        if not self.__stop_flag__.is_set():
            self.__stop_flag__.set()

    def run(self):
        self.__sock__.settimeout(self.timeout)
        while not self.__stop_flag__.is_set():
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
                    logging.info('Server received a message from InPeerNode #{0}.'.format(self.index))
                except:
                    logging.info('InPeerNode #{0}: Error decoding message: {1}{2}'.format(self.index,packets,type(packets)))
                    self.stop()

        self.close_connection('finished run')

    def send(self):
        for i in range(5):
            if not self.__stop_flag__.is_set():
                if self.__buffer__:
                    data = self.__buffer__
                    data = data.encode('ascii')
                    try:
                        self.__sock__.sendall(data)
                    except Exception as err:
                        logging.info('Server failed to sent a message to InPeerNode: #{0}. \nError: {1}'.format(self.index,err))
                    logging.info('Server sent a message to InPeerNode: #{0}.'.format(self.index))
                    self.close_connection('message sent')
                    return False
                else:
                    logging.error('Server has no buffer! Send message to InPeerNode #{0} failed. Try: {1}'.format(self.index,i+1))
                    time.sleep(1)
            else:
                logging.error('Could not sent message! InPeerNode #{0} already shut down!'.format(self.index))

    def close_connection(self, msg):
        if not self.__stop_flag__.is_set():
            self.stop()
            self.__sock__.close()
            logging.info('InPeerNode #{0} has been disconnected due to {1}.'.format(self.index,msg))

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
        peer.start()
    except KeyboardInterrupt:
        peer.close_server_connection('KeyboardInterrupt')
