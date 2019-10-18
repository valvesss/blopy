import logging

from utils import Utils
from block import Block
from message import Message
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

    def chain_sync(self):
        u = Utils()
        blocks = [u.dict_to_json(block) for block in self.node.get_server_ledger()]
        self.return_response(2, blocks)

    def new_block(self):
        b = Block()
        block = self.data['content'][0]
        if not self.node.get_server_ledger():
            # Server has no chain, cannot validate previous hash
            logging.error('{0}Peer #{1}: cannot validate blocks! Authorizing!'.format(self.node.type,self.node.index))
            self.return_response(3, block)
        else:
            if b.validate(block):
                self.node.add_block(block)
                self.return_response(3, block)
                self.node.server.annouce_new_block(block['index'])
            else:
                self.return_response(3)

    def new_transaction(self):
        t = Transaction()
        logging.info('{0}Peer #{1}: Response: received a new transaction!'.format(self.node.type,self.node.index))
        tx = self.data['content'][0][0]
        if t.validate(tx):
            logging.info('{0}Peer #{1}: Response: transaction #{2} is valid!'.format(self.node.type,self.node.index,tx['index']))
            self.node.server.shared_tx.append(tx)
            self.return_response(4, tx)

    def return_response(self, flag, content=None):
        m = Message()
        response = m.create('response', flag, [content])
        self.node.send(response)
