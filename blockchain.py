import json
import logging
import datetime

from pprint import pprint
from hashlib import sha256

logging.basicConfig(level=logging.INFO, format='%(asctime)s :: %(levelname)s :: %(message)s')

class Block:
    def __init__(self, index, transactions, timestamp, previous_hash, nonce=0):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce

    def compute_hash(self):
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_string.encode()).hexdigest()

class Blockchain:
    pow_difficulty = 2

    def __init__(self):
        self.unconfirmed_transactions = []
        self.chain = []

    def create_genesis_block(self):
        genesis_block = Block(0, [], str(datetime.datetime.now()), "0")
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)
        logging.info('Genesis block created')

    @property
    def last_block(self):
        return self.chain[-1]

    def add_block(self, block, proof):
        previous_hash = self.last_block.hash

        if previous_hash != block.previous_hash:
            return False

        if not Blockchain.is_valid_proof(block, proof):
            return False

        block.hash = proof
        logging.info('Block #{} was inserted in the chain'.format(block.index))
        self.chain.append(block)
        return True

    def proof_of_work(self, block):
        block.nonce = 0

        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0' * Blockchain.pow_difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()
        return computed_hash

    def add_new_transaction(self, transaction):
        self.unconfirmed_transactions.append(transaction)

    @classmethod
    def is_valid_proof(cls, block, block_hash):
        return (block_hash.startswith('0' * Blockchain.pow_difficulty) and
                block_hash == block.compute_hash())

    def mine(self):
        if not self.unconfirmed_transactions:
            logging.fatal('There are no transactions to mine!')
            return False

        last_block = self.last_block

        new_block = Block(index=last_block.index + 1,
                          transactions=self.unconfirmed_transactions,
                          timestamp=time.time(),
                          previous_hash=last_block.hash)

        proof = self.proof_of_work(new_block)
        self.add_block(new_block, proof)
        self.unconfirmed_transactions = []
        logging.info('Unconfirmed transactions list set empty')
        return new_block.index

def new_transaction():
    tx_data = {'author': 'author_test', 'content': 'content_test'}
    required_fields = ["author", "content"]

    for field in required_fields:
        if not tx_data.get(field):
            logging.error('The transaction data is invalid')
            return False

    tx_data["timestamp"] = str(datetime.datetime.now())

    blockchain.add_new_transaction(tx_data)
    logging.info('A new transaction was made')

blockchain = Blockchain()
blockchain.create_genesis_block()
new_transaction()
blockchain.mine()
[pprint(block.__dict__) for block in blockchain.chain]
