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
    pow_difficulty = 2

    def __init__(self):
        self.unconfirmed_transactions = []
        self.chain = []

    def create_genesis_block(self):
        genesis_block = Block(0, [], str(datetime.datetime.now()), "0")
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)
        logging.info('Blockchain: genesis block created.')

    @property
    def last_block(self):
        return self.chain[-1]

    def add_block(self, block, proof):
        if not validate_block_fields(block):
            logging.info('Blockchain: Block #{} is not valid!.'.format(block.index))
            return False
        previous_hash = self.last_block.hash

        if previous_hash != block.previous_hash:
            return False

        if not Blockchain.is_valid_proof(block, proof):
            return False

        block.hash = proof
        logging.info('Blockchain: Block #{} was inserted in the chain.'.format(block.index))
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
            logging.info('Blockchain: There are no transactions to mine!')
            return False

        last_block = self.last_block

        new_block = Block(index=last_block.index + 1,
                          transactions=self.unconfirmed_transactions,
                          timestamp=str(datetime.datetime.now()),
                          previous_hash=last_block.hash)

        proof = self.proof_of_work(new_block)
        if not self.add_block(new_block, proof):
            return False
        self.unconfirmed_transactions = []
        logging.info('Blockchain: Unconfirmed transactions list set empty.')
        return new_block.index

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
