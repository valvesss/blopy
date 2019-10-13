import json
import logging
import datetime

from pprint import pprint
from block import Block
from message import Message

class Blockchain(object):
    m = Message()
    block = Block()
    def __init__(self, server):
        self.server = server
        self.unconfirmed_blocks = []
        self.unconfirmed_transactions = []
        self.local_tx = []
        self.chain = []
        self.pow_difficulty = 2

    @property
    def last_block(self):
        return self.chain[-1]

    def add_to_chain(self, block):
        self.chain.append(block)

    def forge_genesis_block(self, content=None):
        content = "Yo I'm Rupert (aka Genesis Blok) {0}".format(content)
        block = self.block.forge(0, content, [])
        block['hash'] = self.block.compute_hash(block)
        self.add_to_chain(block)
        logging.info('Server Blockchain: genesis block created.')

    def validate_previous_hash(self, block_raw):
        last_block = self.last_block
        if block_raw['previous_hash'] != last_block['hash']:
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

        block_raw = self.forge_block()
        proof = self.proof_of_work(block_raw)
        if not self.block.validate(block_raw, proof):
            return False
        if not self.validate_previous_hash(validated_block):
            return False
        self.request_add_block(validated_block)
        self.unconfirmed_transactions = []
        logging.info('Server Blockchain: Block #{} was inserted in the chain.'.format(block['index']))

    def get_unconfirmed_blocks(self):
        blocks = self.unconfirmed_blocks
        self.unconfirmed_blocks = []
        return blocks

    def add_block(self, block_raw):
        self.chain.append(block_raw)

    def request_add_block(self):
        blocks = self.get_unconfirmed_blocks()
        message = self.m.create('request', 3, blocks)
        if self.server.is_any_node_alive():
            self.server.send_to_nodes(message)
            logging.info('Server Blockchain: Local blocks were sent to validation.')
        else:
            self.add_block(block)

    def forge_block(self):
        block_raw = self.block.forge(self.last_block['index'] + 1,
                                     self.last_block['hash'],
                                     self.unconfirmed_transactions)
        proof = self.proof_of_work(block_raw)
        if self.block.validate(block_raw):
            self.unconfirmed_blocks.append(block_raw)

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
