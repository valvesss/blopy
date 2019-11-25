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
        elif self.data['flag'] == 4:
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
            if b.validate(block):
                self.node.server.shared_ledger.append(block)
        logging.info('{0}Peer #{1}: chain renewed!'.format(self.node.type,self.node.index))

    def new_block(self):
        block = self.data['content'][0]
        if block:
                self.node.add_block(block)

    def new_tx(self):
        tx = self.data['content'][0]
        self.node.is_tx_valid(tx)

    def validate_chain_size(self, size):
        if size > self.node.get_ledger_size():
            self.node.clear_ledger()
            self.request_node_chain()

    def request_node_chain(self):
        m = Message()
        msg = m.create('request', 2)
        self.node.buffer_sent.append(msg)
