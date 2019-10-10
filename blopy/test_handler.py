import unittest

from pprint import pprint
from server import Server
from handler import Handler

class TestHandler(unittest.TestCase):
    def setUp(self):
        pass

    data = {'type': 'request',
                'flag': 1,
                'content': 'any content',
                'timestamp': '2019-10-07'}

    class NodeMock():
        def __init__(self):
            self.type = 'Out'
            self.index = 1
            self._server_ = Server('localhost', 5000, 10)

    node = NodeMock()
    h = Handler(node, data)

    def test_request_validate(self):
        self.h.request.selector()


if __name__ == '__main__':
    unittest.main()
