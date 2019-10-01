import unittest
from server import Server

class TestServer(unittest.TestCase):
    def setUp(self):
        pass

    def test_start(self):
        server = Server('localhost', 3000, 1)
        server.start()
        server.join()

    def test_connect_with_peer(self):
        server = Server('localhost', 3000, 2)
        server.start()
        server2 = Server('localhost', 4000, 2)
        server2.start()
        server.connect_with_peer('localhost', 4000)
        server.join()
        server2.join()

if __name__ == '__main__':
    unittest.main()
