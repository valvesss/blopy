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
