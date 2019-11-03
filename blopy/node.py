import json
import socket
import logging
import threading

from time import sleep
from block import Block
from pprint import pprint
from message import Message
from request import Request
from response import Response
from announce import Announce
from transaction import Transaction

class Node(threading.Thread):
    def __init__(self, server, sock, addr, index, type):
        super(Node, self).__init__()
        self.server = server
        self.serverhost_ = server._host_
        self._sock_ = sock
        self._host_ = addr[0]
        self._port_ = addr[1]
        self.index = index
        self.type = type
        self._buffer_ = []
        self._stop_flag_ = threading.Event()
        self.timeout = server.timeout
        self._sock_.settimeout(self.timeout)
        self.wait_response = 0
        self.start_thread_funcs()
        self.chain_sync()

    def chain_sync(self):
        m = Message()
        msg = m.create('request', 1)
        self.send(msg)

    def start_thread_funcs(self):
        h = threading.Thread(target=self.handle_message)
        h.start()

    def get_server_ledger(self):
        if self.server.shared_ledger:
            return self.server.shared_ledger
        return False

    def get_ledger_size(self):
        return len(self.server.shared_ledger)

    def clear_ledger(self):
        self.server.shared_ledger = []

    def stop(self):
        if not self._stop_flag_.is_set():
            self._stop_flag_.set()

    def run(self):
        while not self._stop_flag_.is_set():
            data = ""
            try:
                data = self._sock_.recv(2048)
            except socket.timeout:
                self.close_connection('timeout')
            except Exception as err:
                pass
            if data:
                message = self.decode_data(data)
                if message:
                    self._buffer_.append(message)
        self.close_connection('finished run')

    def add_block(self, block):
        self.server.shared_ledger.append(block)
        logging.info('{0}Peer #{1}: block #{2} added to shared_ledger'.format(self.type,self.index,block['index']))
        self.server.bc.clear_shared_tx(block)

    def is_tx_valid(self, tx):
        t = Transaction()
        stored_txs_indexes = [stored_tx['index'] for stored_tx in self.server.shared_tx]
        if t.validate(tx) and tx['index'] not in stored_txs_indexes:
            self.add_tx(tx)
            return True

    def add_tx(self, tx):
        self.server.shared_tx.append(tx)
        logging.info('{0}Peer #{1}: tx #{2} added to shared_tx'.format(self.type,self.index,tx['index']))

    def handle_message(self):
        while not self._stop_flag_.is_set():
            if self._buffer_:
                local_buffer = self._buffer_
                self._buffer_ = []
                for message in local_buffer:
                    if message['msg_type'] == 'request':
                        Response(self, message)
                    elif message['msg_type'] == 'response':
                        Request(self, message)
                    elif message['msg_type'] == 'announce':
                        Announce(self, message)
                    else:
                        logging.error('{0}Peer #{1}: received a message not valid!'.format(self.type,self.index))
            sleep(1)

    def decode_data(self, data):
        try:
            data = data.decode('ascii')
            data = json.loads(data)
        except Exception as error:
            logging.error('{0}Peer #{1}: Could not decode data!'.format(self.type,self.index))
            return False
        return data

    def encode_data(self,data):
        if isinstance(data, dict):
            try:
                data = json.dumps(data, sort_keys=True)
            except:
                logging.info('{0}Peer #{1}: Error dumping dict!'.format(self.type,self.index))
                return False
            data = self.ascii_encode(data)
        else:
            logging.error('{0}Peer #{1}: Message invalid! Encode failed!'.format(self.type,self.index))
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

    def close_connection(self, msg):
        if not self._stop_flag_.is_set():
            self.stop()
            logging.info('{0}Peer #{1}: has been disconnected due to {2}.'.format(self.type,self.index,msg))
            self._sock_.close()
