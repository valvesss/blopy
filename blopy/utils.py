import json
import logging

from pprint import pprint
from hashlib import sha256

class Utils(object):
    def compute_hash(self, block):
        json_block = self.dict_to_json(block)
        return sha256(json_block.encode()).hexdigest()

    def json_to_dict(self, data):
        try:
            dict_data = json.loads(data)
        except Exception as error:
            logging.error('Block: error converting json to dict!')
            return False
        return dict_data

    def dict_to_json(self, data):
        try:
            json_data = json.dumps(data, sort_keys=True)
        except Exception as error:
            logging.error('Block: error converting dict to json!')
            return False
        return json_data

    def validate_dict_keys(self, data, base_dict):
        data_keys = [k for k in data.keys()]
        base_keys = [k for k in base_dict.keys()]
        if sorted(data_keys) != sorted(base_keys):
            logging.error('Server Transaction: Transaction #{} keys are not valid!'.format(data['index']))
            return False
        return True

    def validate_dict_values(self, data, base_dict):
        keys = [k for k in data.keys()]
        for i in range(len(keys)):
            if type(data[keys[i]]) != base_dict[keys[i]]:
                logging.error('Server Transaction: Transaction #{} values are not valid!'.format(data['index']))
                return False
        return True

    def validate_proof(self, block):
        block_hash = self.compute_hash(block)
        if (not (block_hash.startswith('0' * 2) or
                block_hash != block['hash'])):
            logging.error('Server Blockchain: Block #{} has no valid proof!'.format(self.block['index']))
            return False
        return True
