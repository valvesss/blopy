import json
import socket
import logging
import threading

from blockchain.Block import json_to_dict, dict_to_json

class Node(threading.Thread):
    def __init__(self, server, sock, addr, index, type):
        super(Node, self).__init__()
        self._server_ = server
        self._server_host_ = server._host_
        self._sock_ = sock
        self._host_ = addr[0]
        self._port_ = addr[1]
        self.index = index
        self.type = type
        self._buffer_ = []
        self._stop_flag_ = threading.Event()
        self.timeout = server.timeout
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
                message_decoded = json_to_dict(data)
                self.handle_content_received(message_decoded):
        self.close_connection('finished run')

    def handle_content_received(self, data):
        logging.info('{0}Peer #{1}: received a message!'.format(self.type,self.index))
        if data['msg_type'] is 'block':
            if not self.handle_block(data):
                return False
        elif data['msg_type'] is 'request':
            self.handle_request(data)
        elif data['msg_type'] is 'response':
            self.handle_response(data)
        else:
            logging.error('{0}Peer #{1}: received a message not valid!'.format(self.type,self.index))
            return False

    def handle_block(self, data):
        logging.info('{0}Peer #{1}: received a block!'.format(self.type,self.index))
        block = data['content']
        if not self._server_.bc.chain:
            logging.critical('{0}Peer #{1}: I cannot validate blocks! I have no chain!'.format(self.type,self.index))
            return False
        if self._server_.bc.validate_block(block, block['hash']):
            self._server_.bc.chain.append(block)

    def handle_request(self, data):
        logging.info('{0}Peer #{1}: received a request!'.format(self.type,self.index))
        self.validate_received_request(data)

    def handle_response(self, data):
        logging.info('{0}Peer #{1}: received a response!'.format(self.type,self.index))
        self.validate_received_response(data)

    def validate_received_request(self, data):
        if data['flag'] == 1:
            self.request_chain_sync()
        elif data['flag'] == 2:
            self.request_chain_blocks()

    def validate_received_response(self, data):
        if data['flag'] == 1:
            self.response_chain_sync(data)
        elif data['flag'] == 2:
            self.response_chain_blocks(data)
        logging.info('{0}Peer #{1}: response'.format(self.type,self.index)) # TODO

    def request_chain_blocks(self):
        logging.info('{0}Peer #{1}: received a chain blocks request'.format(self.type,self.index))
        for block in self._server_.bc.chain:
            block = self._server_.bc.block.dict_to_json(block)
            self.send('RES_02{0}'.format(block))

    def response_chain_blocks(self, data):
        logging.info('{0}Peer #{1}: received a chain blocks response'.format(self.type,self.index))
        block = self._server_.bc.block.json_to_dict(data[6:])
        self._server_.bc.chain.append(block)
        logging.info('{0}Peer #{1}: \nMy chain: {2}'.format(self.type,self.index,self._server_.bc.chain))

    def request_chain_sync(self):
        logging.info('{0}Peer #{1}: received a chain sync request'.format(self.type,self.index))
        logging.info('{0}Peer #{1}: thats my chain size: {2} !'.format(self.type,self.index, len(self._server_.bc.chain)))
        node_chain_size = str(len(self._server_.bc.chain))
        self.send('RES_01{0}'.format(node_chain_size))

    def response_chain_sync(self, msg):
        logging.info('{0}Peer #{1}: received a chain sync response'.format(self.type,self.index))
        received_chain_size = int(msg[6:])
        logging.info('{0}Peer #{1}: chain size received: {2}!'.format(self.type,self.index,received_chain_size))
        self.validate_server_chain(received_chain_size)

    def validate_server_chain(self, size):
        if size > len(self._server_.bc.chain):
            logging.info('{0}Peer #{1}: my chain is smaller!'.format(self.type,self.index))
            self._server_.bc.chain = []
            self.request_node_chain()
        else:
            logging.info('{0}Peer #{1}: my chain is bigger!'.format(self.type,self.index))
        return True

    def request_node_chain(self):
        self.send('REQ_02')

    def encode_data(self,data):
        if isinstance(data, dict):
            try:
                data = json.dumps(data, sort_keys=True)
            except:
                logging.info('{0}Peer #{1}: Error dumping dict!'.format(self.type,self.index))
                return False
            data = self.ascii_encode(data)
        else:
            logging.critical('{0}Peer #{1}: Data type not allowed to be sent!'.format(self.type,self.index))
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
                logging.info('Server: failed to sent a message to {0}Peer: #{1}. \nError: {2}'.format(self.type,self.index,err))
                return False
        else:
            logging.error('{0}Peer #{1}: Could not sent message! I\'m already shut down!'.format(self.type,self.index))
        logging.info('Server: sent a message to {0}Peer: #{1}.'.format(self.type,self.index))

    def close_connection(self, msg):
        if not self._stop_flag_.is_set():
            self.stop()
            logging.info('{0}Peer #{1}: has been disconnected due to {2}.'.format(self.type,self.index,msg))
            self._sock_.close()
