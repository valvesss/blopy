import unittest
from blockchain import *

class TesteBlockchain(unittest.TestCase):
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

    def test_create_new_block(self):
        bk = Blockchain()
        bk.create_genesis_block()
        data = {'company_name': 'Test', 'company_data': 'Create Genesis Block'}
        bk.new_transaction(data)
        bk.create_new_block()

    def test_proof_of_work(self):
        bk = Blockchain()
        bk.create_genesis_block()
        data = {'company_name': 'Test', 'company_data': 'Proof of Work'}
        bk.new_transaction(data)
        block = bk.create_new_block()
        bk.proof_of_work(block)

    def test_add_block(self):
        bk = Blockchain()
        bk.create_genesis_block()
        data = {'company_name': 'Test', 'company_data': 'Add Block'}
        bk.new_transaction(data)
        block = bk.create_new_block()
        proof = bk.proof_of_work(block)
        bk.add_block(block, proof)

    def test_validate_block_fields(self):
        bk = Blockchain()
        bk.create_genesis_block()
        data = {'company_name': 'Test', 'company_data': 'Validate Block Fields'}
        bk.new_transaction(data)
        block = bk.create_new_block()
        validate_block_fields(block)

    def test_validate_previous_hash(self):
        bk = Blockchain()
        bk.create_genesis_block()
        data = {'company_name': 'Test', 'company_data': 'Validate Previous Hash'}
        bk.new_transaction(data)
        block = bk.create_new_block()
        bk.validate_previous_hash(block)

    def test_is_valid_proof(self):
        bk = Blockchain()
        bk.create_genesis_block()
        data = {'company_name': 'Test', 'company_data': 'Is Valid Proof?'}
        bk.new_transaction(data)
        block = bk.create_new_block()
        proof = bk.proof_of_work(block)
        bk.is_valid_proof(block, proof)

    def test_mine(self):
        bk = Blockchain()
        bk.create_genesis_block()
        data = {'company_name': 'Test', 'company_data': 'Mine'}
        bk.new_transaction(data)
        bk.mine()

if __name__ == '__main__':
    unittest.main()
