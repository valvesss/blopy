import unittest
from content import Content, Validate

from pprint import pprint

class TestContent(unittest.TestCase):
    def setUp(self):
        pass

    v = Validate()
    c = Content()

    def test_create_message(self):
        msg_type = 'response'
        flag = 1
        content = ['44']
        self.c.create_message(msg_type, flag, content)

    def test_message_raw(self):
        msg_type = 'response'
        flag = 1
        content = ['44']
        msg = self.v.message_raw(msg_type,flag,content)

if __name__ == '__main__':
    unittest.main()
