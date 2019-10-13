import logging

from utils import Utils
from hashlib import sha256
from datetime import datetime
# from Utils import dict_to_json

class Block(object):
    def forge(self,index,previous_hash,transactions):
        block = {'index': index,
                 'nonce': 0,
                 'previous_hash': previous_hash,
                 'timestamp': str(datetime.now()),
                 'transactions': transactions}
        if self.validate(block):
            return block
        return False

    def compute_hash(self, block):
        convert = Utils()
        json_block = convert.dict_to_json(block)
        return sha256(json_block.encode()).hexdigest()

    def validate(self, block):
        if block['index'] == 0:
            return True
        validate = self.Validate(block)
        if (not validate.keys() or
            not validate.values() or
            not validate.proof()):
                return False
        return True

    class Validate(object):
        block_required_items = {'index': int,
                                 'nonce': int,
                                 'previous_hash': str,
                                 'timestamp': str,
                                 'transactions': list}

        def __init__(self, block):
            self.block = block

        def remove_hash(self):
            if 'hash' in block:
                del self.block['hash']

        def keys(self):
            self.remove_hash()
            if not all (k in self.block for k in self.block_required_items.keys()):
                logging.error('Server Blockchain: Block #{} keys are not valid!'.format(self.block['index']))
                return False
            return True

        def values(self):
            self.remove_hash()
            keys = [k for k in self.block.keys()]
            for i in range(len(self.block)):
                if type(self.block[keys[i]]) != self.block_required_items[keys[i]]:
                    logging.error('Server Blockchain: Block #{} values are not valid!'.format(self.block['index']))
                    return False
            return True

        def validate_proof(self):
            if self.block['index'] == 0:
                logging.error('Server Blockchain: Block #{} has no valid proof! He\'s genesis!'.format(self.block['index']))
                return True
            block_hash = self.compute_hash(self.block)
            if (not (block_hash.startswith('0' * self.pow_difficulty) or
                    block_hash != self.block['hash'])):
                logging.error('Server Blockchain: Block #{} has no valid proof!'.format(self.block['index']))
                return False
            return True
