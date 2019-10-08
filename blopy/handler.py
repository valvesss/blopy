import logging

from message import Message

class Handler(object):
    def __init__(self, node, data):
        self.node = node
        self.data_type = data['msg_type']
        self.message = Message()
        self.request = Request(self, data)
        self.response = Response(self, data)

    def validate(self):
        try:
            if self.message.validate(self.data):
                self.treat(data)

    def treat(self):
        if self.data_type is 'request':
            self.request.selector()
        elif self.data_type is 'response':
            self.response.selector()
        else:
            logging.error('{0}Peer #{1}: received a message not valid!'.format(self.node.type,self.node.index))
            return False

class Response:
    def __init__(self, node, data):
        self.node = node
        self.data = data

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
            logging.error('{0}Peer #{1}: response flag not valid!'.format(self.node.node_index,self.index))
            return False

    def chain_size(self, message):
        logging.info('{0}Peer #{1}: Response: received a chain size request'.format(self.node.node_index,self.index))
        if self.node.wait_response == 1:
            chain_size = self.data['content'][0]
            self.validate_chain_size(chain_size)
            self.node.wait_response = 0
        else:
            server_chain_size = str(len(self.node._server_.bc.chain))
            message = self.message.create('response', 1, [server_chain_size])
            self.node.send(message)

    def chain_sync(self, data):
        logging.info('{0}Peer #{1}: Response: received a chain sync request'.format(self.node.node_index,self.index))
        blocks = data['content']
        for block in blocks:
            if self.node._server_.bc.validate_block(block):
                self.node._server_.bc.add_block(block)

    def new_block(self):
        logging.info('{0}Peer #{1}: Response: received a new block!'.format(self.node.type,self.node.index))
        block = data['content'][0]
        if not self.node._server_.bc.chain:
            logging.error('{0}Peer #{1}: Response: I cannot validate blocks! Server has no chain!'.format(self.node.type,self.node.index))
        else:
            if self.node._server_.bc.validate_block(block):
                self.node._server_.bc.add_block(block)
                self.return_response(3, block)
            else:
                self.return_response(3)

    def append_new_block(self):
        if self.data['content']:
            self.node._server_.bc.add_block(self.data['content'])

    def validate_chain_size(self, size):
        if size > len(self.node._server_.bc.chain):
            logging.info('{0}Peer #{1}: my chain is smaller!'.format(self.node.node_index,self.index))
            self.node._server_.bc.chain = []
            self.request_node_chain()

    def return_response(self, flag, cotent=None):
        response = create('response', 3, [cotent])
        self.node.send(response)

class Request:
    def __init__(self, handler, data):
        self.node = handler.node
        self.message = handler.message
        self.data = data

    def selector(self):
        if self.data['flag'] == 1:
            self.chain_size()
        elif self.data['flag'] == 2:
            self.chain_sync()
        else:
            logging.error('{0}Peer #{1}: Request: flag not valid!'.format(self.node.type,self.node.index))
            return False

    def chain_size(self):
        message = self.message.create('request', 1, [])
        if self.node.send(message):
            self.node.wait_response = 1
        logging.info('{0}Peer #{1}: Request: sent chain size message'.format(self.node.type,self.node.index))

    def chain_sync(self):
        blocks = [dict_to_json(block) for block in self.node._server_.bc.chain]
        message = create('request', 2, blocks)
        if self.node.send(message):
            self.node.wait_response = 1
        logging.info('{0}Peer #{1}: Request: sent a chain sync message'.format(self.node.type,self.node.index))
