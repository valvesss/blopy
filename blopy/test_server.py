import unittest
from server import Server

class TestServer(unittest.TestCase):
    def setUp(self):
        pass

    def test_server_start(self):
        server = Server('localhost', 3000, 1)
        try:
            server.start()
        except Exception as error:
            print("Test server start error! Check this:\nError:{0}".format(error))
        server.join()

    def test_server_connect_with_peer(self):
        server = Server('localhost', 3000, 2)
        server.start()
        server2 = Server('localhost', 4000, 2)
        server2.start()
        try:
            server.connect_with_peer('localhost', 4000)
        except Exception as error:
            print("Test server connect_with_peer error! Check this:\nError:{0}".format(error))
        server.join()
        server2.join()

if __name__ == '__main__':
    unittest.main()
