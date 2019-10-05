import unittest
from test_block import TestBlock
from blockchain import *

class TestBlockchain(unittest.TestCase):
    def setUp(self):
        pass

    def test_create_genesis_block(self):
        bk = Blockchain()
        bk.create_genesis_block()

    def test_new_transaction(self):
        bk = Blockchain()
        bk.create_genesis_block()
        data = {'company_name': 'Test', 'company_data': 'New Transaction'}
        bk.new_transaction(data)

    def test_proof_of_work(self):
        bk = Blockchain()
        bk.create_genesis_block()
        block = bk.last_block
        bk.proof_of_work(block)

    def test_add_block(self):
        tb = TestBlock()
        bk = Blockchain()
        bk.create_genesis_block()
        data = {'company_name': 'Test', 'company_data': 'Add Block'}
        bk.new_transaction(data)
        block = tb.test_create_block()
        proof = bk.proof_of_work(block)
        bk.add_block(block)

    def test_validate_proof(self):
        bk = Blockchain()
        b = Block()
        bk.create_genesis_block()
        block = bk.last_block
        proof = bk.proof_of_work(block)
        block['hash'] = b.compute_hash(block)
        bk.validate_proof(block, proof)

    def test_validate_previous_hash(self):
        b = Block()
        bk = Blockchain()
        tb = TestBlock()

        # First block
        bk.create_genesis_block()
        last_block = bk.last_block
        last_block['hash'] = b.compute_hash(last_block)

        # Second block
        new_block = tb.test_create_block()
        new_block['previous_hash'] = last_block['hash']
        bk.validate_previous_hash(new_block)

    def test_mine(self):
        bk = Blockchain()
        bk.create_genesis_block()
        data = {'company_name': 'Test', 'company_data': 'Mine'}
        bk.new_transaction(data)
        bk.mine()

if __name__ == '__main__':
    unittest.main()
