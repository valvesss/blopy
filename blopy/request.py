import logging

from utils import Utils
from block import Block
from message import Message

class Request(object):
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
            logging.info('{0}Peer #{1}: Response: received block #{2} confirmation. Appending!'.format(self.node.type,self.node.index,block['index']))

    def new_tx(self):
        logging.info('{0}Peer #{1}: Response: tx receveid!'.format(self.node.type,self.node.index))
        tx = self.data['content'][0]
        if tx:
            self.node.server.shared_tx.append(tx)
            logging.info('{0}Peer #{1}: Response: tx #{2} was appended!'.format(self.node.type,self.node.index,tx['index']))

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
