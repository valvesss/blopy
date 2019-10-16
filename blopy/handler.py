import logging

from utils import Utils
from block import Block
from message import Message
from pprint import pprint
from transaction import Transaction

class Response:
    def __init__(self, node, data):
        self.node = node
        self.data = data
        self.selector()

    def selector(self):
        if self.data['flag'] == 1:
            self.chain_size()
        elif self.data['flag'] == 2:
            self.chain_sync()
        elif self.data['flag'] == 3:
            if isinstance(self.data['content'], bool):
                self.append_new_block()
            else:
                self.new_block()
        else:
            self.new_transaction()

    def chain_size(self):
        server_chain_size = self.node.get_ledger_size()
        self.return_response(1, server_chain_size)
        logging.info('{0}Peer #{1}: Response: sent a chain size response'.format(self.node.type,self.node.index))

    def chain_sync(self):
        b = Block()
        blocks = [b.dict_to_json(block) for block in self.node.get_server_ledger()]
        self.return_response(2, blocks)
        logging.info('{0}Peer #{1}: Response: sent a chain sync response'.format(self.node.type,self.node.index))

    def new_block(self):
        b = Block()
        logging.info('{0}Peer #{1}: Response: received a new block!'.format(self.node.type,self.node.index))
        block = self.data['content'][0]
        if not self.node.get_server_ledger():
            logging.error('{0}Peer #{1}: Response: I cannot validate blocks! Server has no chain!'.format(self.node.type,self.node.index))
            self.return_response(3, True)
        else:
            if b.validate(block) and b.is_proof_valid(block):
                self.node.add_block(block)
                self.return_response(3, block)
            else:
                self.return_response(3)

    def new_transaction(self):
        t = Transaction()
        logging.info('{0}Peer #{1}: Response: received a new transaction!'.format(self.node.type,self.node.index))
        tx = self.data['content'][0]
        if t.validate(tx):
            self.node.server.shared_tx.append(tx)
            self.return_response(4, True)

    def return_response(self, flag, content=None):
        m = Message()
        response = m.create('response', flag, [content])
        pprint(response)
        self.node.send(response)

class Request:
    block = Block()
    def __init__(self, node, data):
        self.node = node
        self.data = data

    def selector(self):
        if self.data['flag'] == 1:
            self.chain_size()
        elif self.data['flag'] == 2:
            self.chain_sync()
        elif self.data['flag'] == 3:
            self.new_block()
        else:
            self.new_tx()

    def chain_size(self):
        chain_size = self.data['content'][0]
        self.validate_chain_size(chain_size)

    def chain_sync(self):
        b = Block()
        u = Utils()
        self.node.clear_ledger()
        for json_block in self.data['content'][0]:
            block = u.json_to_dict(json_block)
            if b.validate(block) and b.is_proof_valid(block):
                self.node.add_block(block)
        logging.info('{0}Peer #{1}: Response: received a new chain. Refreshing!'.format(self.node.type,self.node.index))

    def new_block(self):
        block = self.data['content'][0]
        if block:
            self.node.add_block(block)
            logging.info('{0}Peer #{1}: Response: received a block confirmation. Appending!'.format(self.node.type,self.node.index))

    def new_tx(self):
        tx = self.data['content'][0]
        if tx:
            self.node.server.shared_tx.append(tx)

    def validate_chain_size(self, size):
        if size > self.node.get_ledger_size():
            logging.info('{0}Peer #{1}: my chain is smaller. Requesting synchronization!'.format(self.node.type,self.node.index))
            self.node.clear_ledger()
            self.request_node_chain()
        else:
            logging.info('{0}Peer #{1}: my chain is bigger!'.format(self.node.type,self.node.index))

    def request_node_chain(self):
        m = Message()
        msg = m.create('request', 2)
        self.node.send(msg)
