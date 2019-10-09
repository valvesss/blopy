import logging

from message import Message
from blockchain import Block

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
        else:
            logging.error('{0}Peer #{1}: response flag not valid!'.format(self.node.type,self.node.index))
            return False

    def chain_size(self):
        server_chain_size = len(self.node._server_.bc.chain)
        message = self.message.create('response', 1, [server_chain_size])
        self.node.send(message)
        logging.info('{0}Peer #{1}: Response: sent a chain size request'.format(self.node.type,self.node.index))

    def chain_sync(self):
        blocks = [self.handler.block.dict_to_json(block) for block in self.node._server_.bc.chain]
        message = self.handler.message.create('response', 2, blocks)
        self.node.send(message)
        logging.info('{0}Peer #{1}: Response: sent a chain sync message'.format(self.node.type,self.node.index))

    def new_block(self):
        logging.info('{0}Peer #{1}: Response: received a new block!'.format(self.node.type,self.node.index))
        block = self.data['content'][0]
        if not self.node._server_.bc.chain:
            logging.error('{0}Peer #{1}: Response: I cannot validate blocks! Server has no chain!'.format(self.node.type,self.node.index))
        else:
            if self.node._server_.bc.validate_block(block):
                self.node._server_.bc.add_block(block)
                self.return_response(3, block)
            else:
                self.return_response(3)

    def return_response(self, flag, cotent=None):
        response = create('response', 3, [cotent])
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
        else:
            logging.error('{0}Peer #{1}: response flag not valid!'.format(self.node.type,self.node.index))
            return False

    def chain_size(self):
        chain_size = self.data['content'][0]
        self.validate_chain_size(chain_size)

    def chain_sync(self):
        self.node._server_.bc.chain = []
        for json_block in self.data['content']:
            block = self.handler.block.json_to_dict(json_block)
            if self.node._server_.bc.validate_block(block, block['hash']):
                self.node._server_.bc.add_block(block)

    def new_block(self):
        if self.data['content'][0]:
            self.node._server_.bc.add_block(block)
            logging.info('{0}Peer #{1}: Response: received a block confirmation. Appending!'.format(self.node.type,self.node.index))

    def validate_chain_size(self, size):
        if size > len(self.node._server_.bc.chain):
            logging.info('{0}Peer #{1}: my chain is smaller!'.format(self.node.type,self.node.index))
            self.node._server_.bc.chain = []
            self.request_node_chain()
