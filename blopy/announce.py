import logging

from message import Message

class Announce(object):
    def __init__(self, node, data):
        self.node = node
        self.data = data
        self.selector()

    def selector(self):
        if self.data['flag'] == 1:
            self.new_block()

    def new_block(self):
        block_number = self.data['content'][0]
