import logging

from message import Message

class Request(object):
    def __init__(self, node, data):
        self.node = node
        self.data = data

    def selector(self):
        if self.data['flag'] == 20:
            self.new_block()

    def new_block(self):
        block_number = self.data['content'][0]
        logging.info('Announcement: block #{0} was declared valid!'.format(block_number))
        self.node.server.write_message('request',1)
