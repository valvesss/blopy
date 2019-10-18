import json
import logging

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
        if not isinstance(data,dict):
            return False
        data_keys = [k for k in data.keys()]
        base_keys = [k for k in base_dict.keys()]
        if sorted(data_keys) != sorted(base_keys):
            logging.error('Server Transaction: Transaction #{} keys are not valid!'.format(data['index']))
            return False
        return True

    def validate_dict_values(self, data, base_dict):
        if not isinstance(data,dict):
            return False
        keys = [k for k in data.keys()]
        for i in range(len(keys)):
            if type(data[keys[i]]) != base_dict[keys[i]]:
                logging.error('Server Transaction: Transaction #{} values are not valid!'.format(data['index']))
                return False
        return True
