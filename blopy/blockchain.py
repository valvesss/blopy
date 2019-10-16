import json
import logging
import datetime

from time import sleep
from block import Block
from utils import Utils
from transaction import Transaction

class Blockchain(object):
    block = Block()
    utils = Utils()
    def __init__(self, server):
        self.server = server
        self.local_tx = []
        self.count_tx = 0
        self.local_block = None
        self.pow_difficulty = 2

    @property
    def last_block(self):
        return self.server.shared_ledger[-1]

    def get_local_block(self):
        return self.local_block

    def set_local_block(self, block):
        self.local_block = block

    def checkserverstatus(self):
        while not self.server.alive:
            sleep(1)

    def get_tx_num(self):
        self.count_tx += 1
        return self.count_tx

    # Block
    def forge_genesis_block(self, content=None):
        self.checkserverstatus()
        content = "Yo I'm Rupert (aka Genesis Blok) {0}".format(content)
        self.local_block = self.block.forge(0, content, [])
        self.local_block['hash'] = self.utils.compute_hash(self.local_block)
        self.add_block()
        logging.info('Server Blockchain: genesis block created.')

    def validate_previous_hash(self, block_raw):
        last_block = self.last_block
        if block_raw['previous_hash'] != last_block['hash']:
            logging.error('Server Blockchain: Block #{} previous_hash is not valid!'.format(block['index']))
            return False
        return True

    def add_block(self):
        self.server.shared_ledger.append(self.local_block)
        logging.info('Server Blockchain: inserted block #{0}'.format(self.local_block['index']))
        self.clear_local_block()

    def request_add_block(self):
        if not self.local_block:
            logging.info('Server Blockchain: There is no block to mine!.')
            return False
        if self.server.is_any_node_alive():
            self.server.write_message('request', 3, [self.local_block])
            logging.info('Server Blockchain: Local blocks were sent to validation.')
        else:
            self.add_block()

    def forge_block(self):
        self.local_block = self.block.forge(self.last_block['index'] + 1,
                                            self.last_block['hash'],
                                            self.server.shared_tx)

    def clear_local_block(self):
        self.local_block = None

    # Mine
    def mine(self):
        self.forge_block()
        self.proof_of_work()
        self.request_add_block()

    def proof_of_work(self):
        block = self.local_block
        computed_hash = self.utils.compute_hash(block)
        while not computed_hash.startswith('0' * self.pow_difficulty):
            block['nonce'] += 1
            computed_hash = self.utils.compute_hash(block)
        self.local_block['hash'] = computed_hash

    # Transactions
    def new_tx(self, data):
        tx = Transaction()
        data['index'] = self.get_tx_num()
        tx_raw = tx.new(data)
        self.local_tx.append(tx_raw)
        self.send_tx_to_nodes()

    def send_tx_to_nodes(self):
        if self.server.is_any_node_alive():
            self.server.write_message('request', 4, self.local_tx)
            self.clear_local_tx()
            logging.info('Server Blockchain: a new tx was sent to the network')
        else:
            self.add_tx()

    def add_tx(self):
        for tx in self.local_tx:
            self.server.shared_tx.append(tx)
            logging.info('Server Blockchain: inserted tx #{0}'.format(tx['index']))
        self.clear_local_tx()

    def clear_local_tx(self):
        self.local_tx = []
