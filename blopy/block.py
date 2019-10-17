import logging

from utils import Utils
from pprint import pprint
from datetime import datetime

class Block(object):
    utils = Utils()
    def forge(self,index,previous_hash,transactions):
        block = {'index': index,
                 'nonce': 0,
                 'previous_hash': previous_hash,
                 'timestamp': str(datetime.now()),
                 'transactions': transactions}
        if self.validate(block):
            return block
        return False

    def validate(self, block):
        if block['index'] == 0:
            return True

        validate = self.Validate(block)
        if validate.keys() and validate.values() and validate.proof():
            block['hash'] = validate.block_hash
            return True
        return False

    class Validate(object):
        utils = Utils()
        block_required_items = {'index': int,
                                 'nonce': int,
                                 'previous_hash': str,
                                 'timestamp': str,
                                 'transactions': list}

        def __init__(self, block):
            self.block = block
            self.block_hash = self.block_hash()
            self.remove_hash()

        def remove_hash(self):
            if 'hash' in self.block:
                self.block_hash = self.block['hash']
                del self.block['hash']

        def block_hash(self):
            if 'hash' in self.block:
                return self.block['hash']

        def keys(self):
            if self.utils.validate_dict_keys(self.block, self.block_required_items):
                return True
            return False

        def values(self):
            if self.utils.validate_dict_values(self.block, self.block_required_items):
                return True
            return False

        def proof(self):
            block_hash = self.utils.compute_hash(self.block)
            if (not (block_hash.startswith('0' * 2) or
                    block_hash != self.block_hash)):
                logging.error('Server Blockchain: Block #{} has no valid proof!'.format(self.block['index']))
                return False
            return True
