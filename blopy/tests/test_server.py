import unittest
from blopy.blopy.server import Server

class TestServer(unittest.TestCase):
    def setUp(self):
        pass

    def test_server_start(self):
        server = Server('localhost', 3000)
        try:
            server.start()
        except Exception as err:
            print("Test server start error! Check this:\nError:{0}".format(error))

if __name__ == '__main__':
    unittest.main()
