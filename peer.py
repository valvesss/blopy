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
        self._host_ = host
        self._port_ = port
        self._stop_flag_ = threading.Event()
        self._nodesIn_ = []
        self._nodesOut_ = []
        self.timeout = 20
        self.scale_up()

    def scale_up(self):
        self._sock_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock_.bind(('', self._port_))
        self._sock_.listen()
        self._sock_.settimeout(self.timeout)
        logging.info('PeerServer is waiting for income connections.')

    def send_to_nodes(self, data=None):
        if self._nodesIn_:
            for node in self._nodesIn_:
                node.send(data)

        if self._nodesOut_:
            for node in self._nodesOut_:
                node.send(data)

    def connect_with_peer(self, host, port):
        if self.validate_new_peer_connection(host, port):
            index = len(self._nodesOut_)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                sock.connect((host, port))
            except socket.timeout:
                self.close_server_connection('timeout')
            except Exception as error:
                logging.error("Server could not connect to OutPeer: {0} \nError: {1}".format(host,error))
            outbound_peer = PeerNode(self._host_, sock, (host, port), index, 'Out')
            outbound_peer.start()
            self._nodesOut_.append(outbound_peer)
            logging.info('Server connected to OutPeer: #{0} {1}:{2}.'.format(index,host,port))

    def validate_new_peer_connection(self, host, port):
        if host == self._host_ and port == self._port_:
            logging.error('Server cannot connect to own host!')
            return False

        for node in self._nodesOut_:
            if node._host_ == host and node._port_ == port:
                logging.critical('Already connected with this Outpeer!')
                return False

        for node in self._nodesIn_:
            if node._host_ == host and node._port_ == port:
                logging.critical('Already connected with this Inpeer!')
                return False
        return True

    def close_server_connection(self, msg):
        if not self._stop_flag_.is_set():
            self.stop()
            self.close_connected_nodes()
            self._sock_.close()
            logging.info('Server closed his connection due to {}.'.format(msg))
            sys.exit(0)

    def close_connected_nodes(self):
        for node in self._nodesIn_:
            if not node._stop_flag_.is_set():
                node.close_connection('PeerServer being shut down')
                node.join()

        for node in self._nodesOut_:
            if not node._stop_flag_.is_set():
                node.close_connection('PeerServer being shut down')
                node.join()

    def stop(self):
        if not self._stop_flag_.is_set():
            self._stop_flag_.set()

    def run(self):
        while not self._stop_flag_.is_set():
            try:
                peer_socket, peer_addr = self._sock_.accept()
                index = len(self._nodesIn_)
                inbound_peer = PeerNode(self._host_, peer_socket, peer_addr, index, 'In')
                inbound_peer.start()
                logging.info('Server connected to InPeer: #{0} {1}:{2}.'.format(index,peer_addr[0],peer_addr[1]))
                self._nodesIn_.append(inbound_peer)
            except socket.timeout:
                self.close_server_connection('timeout')

        self.close_server_connection('finished run.')

class PeerNode(threading.Thread):
    def __init__(self, serverHost, sock, addr, index,type):
        super(PeerNode, self).__init__()
        self._serverHost_ = serverHost
        self._sock_ = sock
        self._host_ = addr[0]
        self._port_ = addr[1]
        self.index = index
        self.type = type
        self._buffer_ = ""
        self._stop_flag_ = threading.Event()
        self.timeout = 20
        self._sock_.settimeout(self.timeout)

    def stop(self):
        if not self._stop_flag_.is_set():
            self._stop_flag_.set()

    def run(self):
        while not self._stop_flag_.is_set():
            packets = ""
            try:
                packets = self._sock_.recv(1024)
            except socket.timeout:
                self.close_connection('timeout')
            except Exception as err:
                pass
            if packets:
                message_decoded = self.decode_packets(packets)
                self._buffer_ += message_decoded
                logging.info('Server received a message from {0}Peer #{1}'.format(self.type,self.index))
                logging.info('Content received: {0}'.format(message_decoded))
        self.close_connection('finished run')

    def decode_packets(self, packets):
        try:
            packets = packets.decode('ascii')
        except Exception as err:
            logging.info('{0}Peer #{1}: Error decoding message'.format(self.type,self.index))
            packets = ""
        return packets

    def send(self, data=None):
        if not self._stop_flag_.is_set():
            if not data:
                if self._buffer_:
                    data = self._buffer_
                else:
                    logging.error('Server has no buffer nor data to sent! Send message to {0}Peer #{1} failed.'.format(self.type,self.index))
                    return False
            if isinstance(data, str):
                data = data.encode('ascii')
            try:
                self._sock_.sendall(data)
            except Exception as err:
                logging.info('Server failed to sent a message to {0}Peer: #{1}. \nError: {2}'.format(self.type,self.index,err))
                return False
        else:
            logging.error('Could not sent message! {0}Peer #{1} already shut down!'.format(self.type,self.index))
        logging.info('Server sent a message to {0}Peer: #{1}.'.format(self.type,self.index))

    def close_connection(self, msg):
        if not self._stop_flag_.is_set():
            self.stop()
            logging.info('{0}Peer #{1} has been disconnected due to {2}.'.format(self.type,self.index,msg))
            self._sock_.close()
