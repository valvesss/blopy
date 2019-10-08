import unittest
from message import Message

from pprint import pprint

class TestMessage(unittest.TestCase):
    def setUp(self):
        pass

    m = Message()

    def test_create(self):
        msg_type = 'response'
        flag = 1
        content = ['44']
        self.m.create(msg_type, flag, content)

    def test_message_raw(self):
        msg_type = 'response'
        flag = 1
        content = ['44']
        self.m.validate(msg_type, flag, content)

if __name__ == '__main__':
    unittest.main()
