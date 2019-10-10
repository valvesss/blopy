import json
import logging
import datetime

from pprint import pprint
from hashlib import sha256
from message import Message

class Block:
    block_required_items = {'index': int,
                             'nonce': int,
                             'previous_hash': str,
                             'timestamp': str,
                             'transactions': list}

    def create_new(self,index,previous_hash,timestamp,transactions):
        return {'index': index,
                 'nonce': 0,
                 'previous_hash': previous_hash,
                 'timestamp': timestamp,
                 'transactions': transactions}

    def compute_hash(self, block):
        block_string = self.dict_to_json(block)
        return sha256(block_string.encode()).hexdigest()

    def json_to_dict(self, json_block):
        try:
            data = json.loads(json_block)
        except Exception as error:
            logging.error('Block: error converting json to dict!')
            return False
        return data

    def dict_to_json(self, block):
        try:
            data = json.dumps(block, sort_keys=True)
        except Exception as error:
            logging.error('Block: error converting dict to json!')
            return False
        return data

    def validate_keys(self, block):
        if 'hash' in block:
            del block['hash']
        if not all (k in block for k in self.block_required_items.keys()):
            logging.error('Server Blockchain: Block #{} keys are not valid!'.format(block['index']))
            return False
        return True

    def validate_values(self, block):
        if 'hash' in block:
            del block['hash']
        keys = [k for k in block.keys()]
        for i in range(len(block)):
            if type(block[keys[i]]) != self.block_required_items[keys[i]]:
                logging.error('Server Blockchain: Block #{} values are not valid!'.format(block['index']))
                return False
        return True

class Blockchain:
    m = Message()
    def __init__(self, server):
        self.server = server
        self.unconfirmed_blocks = []
        self.unconfirmed_transactions = []
        self.local_tx = []
        self.chain = []
        self.pow_difficulty = 2
        self.block = Block()

    def create_genesis_block(self, content=None):
        genesis_block = self.block.create_new(0, "Yo I'm Rupert (aka Genesis Blok) {0}".format(content), str(datetime.datetime.now()), [])
        genesis_block['hash'] = self.block.compute_hash(genesis_block)
        self.chain.append(genesis_block)
        logging.info('Server Blockchain: genesis block created.')

    @property
    def last_block(self):
        return self.chain[-1]

    def validate_block(self, block, proof):
        if block['index'] == 0:
            return True
        if (not self.block.validate_keys(block) or
            not self.block.validate_values(block) or
            not self.validate_proof(block, proof)):
                return False
        if not 'hash' in block:
            block['hash'] = proof
        return block

    def validate_new_block(self, block, proof):
        if self.validate_block(block, proof):
            if self.validate_previous_hash(block):
                return block
        return False

    def validate_proof(self, block, proof):
        if block['index'] == 0:
            logging.error('Server Blockchain: Block #{} has no valid proof! He\'s genesis!'.format(block['index']))
            return True
        block_hash = self.block.compute_hash(block)
        if (not (block_hash.startswith('0' * self.pow_difficulty) or
                block_hash != proof)):
            logging.error('Server Blockchain: Block #{} has no valid proof!'.format(block['index']))
            return False
        return True

    def validate_previous_hash(self, block):
        last_block = self.last_block
        if block['previous_hash'] != last_block['hash']:
            logging.error('Server Blockchain: Block #{} previous_hash is not valid!'.format(block['index']))
            return False
        return True

    def proof_of_work(self, block):
        computed_hash = self.block.compute_hash(block)
        while not computed_hash.startswith('0' * self.pow_difficulty):
            block['nonce'] += 1
            computed_hash = self.block.compute_hash(block)
        return computed_hash

    def mine(self):
        if not self.unconfirmed_transactions:
            logging.info('Server Blockchain: There are no transactions to mine!')
            return False

        block = self.forge_block()
        proof = self.proof_of_work(block)
        validated_block = self.validate_new_block(block, proof)
        if not validated_block:
            return False
        self.request_add_block(validated_block)
        self.unconfirmed_transactions = []
        logging.info('Server Blockchain: Block #{} was inserted in the chain.'.format(block['index']))

    def get_unconfirmed_blocks(self):
        blocks = self.unconfirmed_blocks
        self.unconfirmed_blocks = []
        return blocks

    def add_block(self, block):
        self.chain.append(block)

    def request_add_block(self):
        blocks = self.get_unconfirmed_blocks()
        message = self.m.create('request', 3, blocks)
        if self.server.is_any_node_alive():
            self.server.send_to_nodes(message)
            logging.info('Server Blockchain: Local blocks were sent to validation.')
        else:
            self.add_block(block)

    def forge_block(self):
        block = self.block.create_new(self.last_block['index'] + 1,
                                     self.last_block['hash'],
                                     str(datetime.datetime.now()),
                                     self.unconfirmed_transactions)
        proof = self.proof_of_work(block)
        if self.validate_block(block, proof):
            self.unconfirmed_blocks.append(block)

    def add_tx(self):
        tx = self.local_tx[-1]
        self.unconfirmed_transactions.append(tx)
        self.local_tx = []

    def new_transaction(self, data):
        if not self.validate_tx_data(data):
            return False

        self.local_tx.append(data)
        if self.server.is_any_node_alive():
            msg = self.m.create('request', 4, [data])
            self.server.send_to_nodes(msg)
            logging.info('Server Blockchain: a new transaction was sent to the network')
        else:
            self.add_tx()

    def validate_tx_data(self, data):
        required_fields = ["company_name", "company_data"]
        for field in required_fields:
            if not data.get(field):
                logging.error('Server Blockchain: The transaction data is invalid.')
                return False
        return True
        logging.info('Server Blockchain: a new transaction was validated')
