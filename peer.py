import os
import sys
import json
import time
import socket
import logging
import threading

logging.basicConfig(level=logging.INFO, format='%(asctime)s :: %(levelname)s :: %(message)s')

class PeerServer(threading.Thread):
    def __init__(self, host, port):
        super(PeerServer, self).__init__()
        # self.__host__ = get_ip()
        self.__host__ = host
        self.__port__ = port
        self.__stop_flag__ = threading.Event()
        self.__nodesIn__ = []
        self.__nodesOut__ = []
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

    def connect_with_peer(self, host, port):
        if self.validate_new_peer_connection(host, port):
            index = len(self.__nodesOut__)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                try:
                        sock.connect((host, port))
                        outbound_peer = PeerNode(self.__host__, sock, (host, port), index, 'Out')
                except socket.timeout:
                    self.close_server_connection('timeout')

                except Exception as error:
                    logging.critical("Server could not connect to OutPeer: {0} \nError: {1}".format(host,error))
            outbound_peer.start()
            self.__nodesOut__.append(outbound_peer)
            logging.info('Server connected to OutPeer: #{0} {1}:{2}.'.format(index,host,port))

    def validate_new_peer_connection(self, host, port):
        if host == self.__host__ and port == self.__port__:
            logging.error('Server cannot connect to own host!')

        for node in self.__nodesOut__:
            if node.__host__ == host and node.__port__ == port:
                logging.critical('Already connected with this Outpeer!')

        for node in self.__nodesIn__:
            if node.__host__ == host and node.__port__ == port:
                logging.critical('Already connected with this Inpeer!')

    def close_server_connection(self, msg):
        if not self.__stop_flag__.is_set():
            self.stop()
            self.close_connected_nodes()
            self.__sock__.close()
            logging.info('Server closed his connection due to {}.'.format(msg))
            sys.exit(0)

    def close_connected_nodes(self):
        for node in self.__nodesIn__:
            if not node.__stop_flag__.is_set():
                node.close_connection('PeerServer being shut down')
                node.join()

        for node in self.__nodesOut__:
            if not node.__stop_flag__.is_set():
                node.close_connection('PeerServer being shut down')
                node.join()

    def stop(self):
        if not self.__stop_flag__.is_set():
            self.__stop_flag__.set()

    def run(self):
        while not self.__stop_flag__.is_set():
            try:
                peer_socket, peer_addr = self.__sock__.accept()
                with peer_socket:
                    index = len(self.__nodesIn__)
                    inbound_peer = PeerNode(self.__host__, peer_socket, peer_addr, index, 'In')
                    inbound_peer.start()
                    logging.info('Server connected to InPeer: #{0} {1}:{2}.'.format(index,peer_addr[0],peer_addr[1]))
                    self.__nodesIn__.append(inbound_peer)
            except socket.timeout:
                self.close_server_connection('timeout')

        self.close_server_connection('finished run.')

class PeerNode(threading.Thread):
    def __init__(self, serverHost, sock, addr, index,type):
        super(PeerNode, self).__init__()
        self.__serverHost__ = serverHost
        self.__sock__ = sock
        self.__host__ = addr[0]
        self.__port__ = addr[1]
        self.index = index
        self.type = type
        self.__buffer__ = ""
        self.__stop_flag__ = threading.Event()
        self.timeout = 20
        self.__sock__.settimeout(self.timeout)

    def stop(self):
        if not self.__stop_flag__.is_set():
            self.__stop_flag__.set()

    def run(self):
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
                    logging.info('Server received a message from {0}Peer #{1}.'.format(self.type,self.index))
                except:
                    logging.info('{0}Peer #{1}: Error decoding message: {2}{3}'.format(self.type,self.index,packets,type(packets)))
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
                        logging.info('Server failed to sent a message to {0}Peer: #{1}. \nError: {1}'.format(self.type,self.index,err))
                    logging.info('Server sent a message to {0}Peer: #{1}.'.format(self.type,self.index))
                    self.close_connection('message sent')
                    return False
                else:
                    logging.error('Server has no buffer! Send message to {0}Peer #{1} failed. Try: {2}'.format(self.type,self.index,i+1))
                    time.sleep(1)
            else:
                logging.error('Could not sent message! {0}Peer #{1} already shut down!'.format(self.type,self.index))

    def close_connection(self, msg):
        if not self.__stop_flag__.is_set():
            self.stop()
            logging.info('{0}Peer #{1} has been disconnected due to {2}.'.format(self.type,self.index,msg))
            self.__sock__.close()


# def get_ip():
#     if os.name == 'nt':
#         hostname = socket.gethostname()
#         ip = socket.gethostbyname(hostname)
#     elif os.name == 'posix':
#         netifaces.ifaddresses('enp0s3')
#         ip = netifaces.ifaddresses('enp0s3')[netifaces.AF_INET][0]['addr']
#     return ip
#
# if __name__ == '__main__':
#     peer = PeerServer()
#     try:
#         peer.start()
#     except KeyboardInterrupt:
#         peer.close_server_connection('KeyboardInterrupt')
