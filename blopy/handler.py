import logging

from message import Message
from block import Block

class Handler(object):
    def __init__(self, node, data):
        self.node = node
        self.data = data
        self.message = Message()
        self.request = Request(self, data)
        self.response = Response(self, data)
        self.block = Block()

    def validate(self):
        if self.message.validate(self.data):
            self.treat()

    def treat(self):
        if self.data['msg_type'] == 'request':
            self.response.selector()
        elif self.data['msg_type'] == 'response':
            self.request.selector()
        else:
            logging.error('{0}Peer #{1}: received a message not valid!'.format(self.node.type,self.node.index))
            return False

class Response:
    def __init__(self, handler, data):
        self.node = handler.node
        self.data = data
        self.message = handler.message
        self.handler = handler

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
        elif self.data['flag'] == 4:
            self.new_transaction()
        else:
            logging.error('{0}Peer #{1}: response flag not valid!'.format(self.node.type,self.node.index))
            return False

    def chain_size(self):
        server_chain_size = len(self.node._server_.bc.shared_ledger)
        self.return_response(1, server_chain_size)
        logging.info('{0}Peer #{1}: Response: sent a chain size response'.format(self.node.type,self.node.index))

    def chain_sync(self):
        blocks = [self.handler.block.dict_to_json(block) for block in self.node._server_.bc.shared_ledger]
        self.return_response(2, blocks)
        logging.info('{0}Peer #{1}: Response: sent a chain sync response'.format(self.node.type,self.node.index))

    def new_block(self):
        logging.info('{0}Peer #{1}: Response: received a new block!'.format(self.node.type,self.node.index))
        block = self.data['content'][0]
        if not self.node._server_.bc.shared_ledger:
            logging.error('{0}Peer #{1}: Response: I cannot validate blocks! Server has no chain!'.format(self.node.type,self.node.index))
        else:
            if self.node._server_.bc.validate_block(block, block['hash']):
                self.node._server_.bc.add_block(block)
                self.return_response(3, block)
            else:
                self.return_response(3)

    def new_transaction(self):
        logging.info('{0}Peer #{1}: Response: received a new transaction!'.format(self.node.type,self.node.index))
        tx = self.data['content'][0]
        if self.node._server_.bc.validate_tx_data(tx):
            self.node._server_.bc.local_tx.append(tx)
            self.node._server_.bc.add_tx()
            self.return_response(4, True)

    def return_response(self, flag, content=None):
        response = self.message.create('response', flag, [content])
        self.node.send(response)

class Request:
    def __init__(self, handler, data):
        self.node = handler.node
        self.data = data
        self.message = handler.message
        self.handler = handler

    def selector(self):
        if self.data['flag'] == 1:
            self.chain_size()
        elif self.data['flag'] == 2:
            self.chain_sync()
        elif self.data['flag'] == 3:
            self.new_block()
        elif self.data['flag'] == 4:
            self.new_tx()
        else:
            logging.error('{0}Peer #{1}: response flag not valid!'.format(self.node.type,self.node.index))
            return False

    def chain_size(self):
        chain_size = self.data['content'][0]
        self.validate_chain_size(chain_size)

    def chain_sync(self):
        self.node._server_.bc.shared_ledger = []
        for json_block in self.data['content'][0]:
            block = self.handler.block.json_to_dict(json_block)
            if self.node._server_.bc.validate_block(block, block['hash']):
                self.node._server_.bc.add_block(block)
        logging.info('{0}Peer #{1}: Response: received a new chain. Refreshing!'.format(self.node.type,self.node.index))

    def new_block(self):
        block = self.data['content'][0]
        if block:
            self.node._server_.bc.add_block(block)
            logging.info('{0}Peer #{1}: Response: received a block confirmation. Appending!'.format(self.node.type,self.node.index))

    def new_tx(self):
        tx = self.data['content'][0]
        if tx:
            self.node._server_.bc.add_tx()

    def validate_chain_size(self, size):
        if size > len(self.node._server_.bc.shared_ledger):
            logging.info('{0}Peer #{1}: my chain is smaller. Requesting synchronization!'.format(self.node.type,self.node.index))
            self.node._server_.bc.shared_ledger = []
            self.request_node_chain()

    def request_node_chain(self):
        msg = self.message.create('request', 2)
        self.node.send(msg)
