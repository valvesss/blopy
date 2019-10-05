import unittest
from pprint import pprint
from blockchain import Block, Blockchain

class TestBlock(unittest.TestCase):
    def setUp(self):
        pass

    def test_create_block(self):
        index = 0
        nonce = 0
        previous_hash = 'New York'
        timestamp = '1944-03-16'
        transactions = ['Andrew Tanenbaum']

        b = Block()
        block_dummy = b.create_new(index,previous_hash,timestamp,transactions)
        return block_dummy

    def test_compute_hash(self):
        block = self.test_create_block()

        b = Block()
        b.compute_hash(block)

    def test_dict_to_json(self):
        block = self.test_create_block()

        b = Block()
        b.dict_to_json(block)

    def test_json_to_dict(self):
        block = self.test_create_block()

        b = Block()
        json_block = b.dict_to_json(block)
        b.json_to_dict(json_block)

    def test_validate_keys(self):
        block = self.test_create_block()

        b = Block()
        b.validate_keys(block)

    def test_validate_values(self):
        block = self.test_create_block()

        b = Block()
        b.validate_values(block)

if __name__ == '__main__':
    unittest.main()
