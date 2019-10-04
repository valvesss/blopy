import json
import socket
import logging
import threading

class Node(threading.Thread):
    def __init__(self, serverHost, sock, addr, index, type, timeout):
        super(Node, self).__init__()
        self._serverHost_ = serverHost
        self._sock_ = sock
        self._host_ = addr[0]
        self._port_ = addr[1]
        self.index = index
        self.type = type
        self._buffer_ = []
        self._stop_flag_ = threading.Event()
        self.timeout = timeout
        self._sock_.settimeout(self.timeout)

    def stop(self):
        if not self._stop_flag_.is_set():
            self._stop_flag_.set()

    def run(self):
        while not self._stop_flag_.is_set():
            data = ""
            try:
                data = self._sock_.recv(1024)
            except socket.timeout:
                self.close_connection('timeout')
            except Exception as err:
                pass
            if data:
                message_decoded = self.decode_data(data)
                if not message_decoded:
                    break
                self._buffer_.append(message_decoded)
                logging.info('Node: Server received a message from {0}Peer #{1}'.format(self.type,self.index))
                # In use to debug
                logging.info('Content received: {0}'.format(message_decoded))
                self.send(message_decoded)
                self.stop()
        self.close_connection('finished run')

    def decode_data(self, data):
        try:
            data = data.decode('ascii')
        except:
            logging.info('{0}Peer #{1}: Error decoding message'.format(self.type,self.index))
            data = ""
            return False
        if len(data) > 20:
            data = json.loads(data)
        return data

    def encode_data(self,data):
        if isinstance(data, str):
            data = self.ascii_encode(data)
        elif isinstance(data, dict):
            try:
                data = json.dumps(data, sort_keys=True)
            except:
                logging.info('{0}Peer #{1}: Error dumping json!'.format(self.type,self.index))
                return False
            data = self.ascii_encode(data)
        else:
            logging.critical('{0}Peer #{1}: Data type not allowed ! Try again.'.format(self.type,self.index))
            return False
        return data

    def ascii_encode(self, data):
        try:
            data = data.encode('ascii')
        except Exception as error:
            logging.info('{0}Peer #{1}: Error encoding data!'.format(self.type,self.index))
            return False
        return data

    def send(self, data):
        if not self._stop_flag_.is_set():
            data = self.encode_data(data)
            if not data:
                return False
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
            logging.info('{0}Peer #{1}: has been disconnected due to {2}.'.format(self.type,self.index,msg))
            self._sock_.close()
