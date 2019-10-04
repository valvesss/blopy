import json
import logging
import datetime

from pprint import pprint
from hashlib import sha256

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
    def __init__(self):
        self.unconfirmed_transactions = []
        self.chain = []
        self.pow_difficulty = 2

    def create_genesis_block(self):
        genesis_block = Block(0, [], str(datetime.datetime.now()), "Yo I'm Rupert")
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)
        logging.info('Blockchain: genesis block created.')

    @property
    def last_block(self):
        return self.chain[-1]

    def add_block(self, block, proof):
        if not validate_block_fields(block):
            return False

        if not self.is_valid_proof(block, proof):
            return False

        if not self.validate_previous_hash(block):
            return False

        block.hash = proof
        self.chain.append(block)
        self.unconfirmed_transactions = []
        logging.info('Blockchain: Block #{} was inserted in the chain.'.format(block.index))
        return True

    def is_valid_proof(self, block, block_hash):
        if (block_hash.startswith('0' * self.pow_difficulty) and
                block_hash == block.compute_hash()):
            return True
        else:
            logging.error('Blockchain: Block #{} has no valid proof!.'.format(block.index))
            return False

    def validate_previous_hash(self, block):
        previous_hash = self.last_block.hash
        if not previous_hash == block.previous_hash:
            return False
        return True

    def proof_of_work(self, block):
        block.nonce = 0
        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0' * self.pow_difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()
        return computed_hash

    def add_new_transaction(self, transaction):
        self.unconfirmed_transactions.append(transaction)

    def mine(self):
        if not self.unconfirmed_transactions:
            logging.info('Blockchain: There are no transactions to mine!')
            return False

        new_block = self.create_new_block()
        proof = self.proof_of_work(new_block)
        if not self.add_block(new_block, proof):
            return False

    def create_new_block(self):
        last_block = self.last_block
        return Block(last_block.index + 1,
                     self.unconfirmed_transactions,
                     str(datetime.datetime.now()),
                     last_block.hash)

    def new_transaction(self, data):
        required_fields = ["company_name", "company_data"]

        for field in required_fields:
            if not data.get(field):
                logging.error('Blockchain: The transaction data is invalid.')
                return False

        data["timestamp"] = str(datetime.datetime.now())

        self.add_new_transaction(data)
        logging.info('Blockchain: a new transaction was validated')

def validate_block_fields(block):
    if not (block.index and isinstance(block.index, int)):
        logging.info('Blockchain: Block #{0} index is Integer!.'.format(block.index))
        return False

    if not (block.transactions and isinstance(block.transactions, list)):
        logging.info('Blockchain: Block #{0} transactions is not a List!.'.format(block.index))
        return False

    if not (block.timestamp and isinstance(block.timestamp, str)):
        logging.info('Blockchain: Block #{0} timestamp is not a String!.'.format(block.index))
        return False

    if not (block.previous_hash and isinstance(block.previous_hash, str)):
        logging.info('Blockchain: Block #{0} previous hash is not equal to the previous block hash!'.format(block.index))
        return False

    if not (block.nonce and isinstance(block.nonce, int)):
        logging.info('Blockchain: Block #{0} nonce is not an Integer!.'.format(block.index))
        return False
    return True
