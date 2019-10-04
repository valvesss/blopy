import unittest
from node import Node
from server import Server

class TestNode(unittest.TestCase):
    def setUp(self):
        pass

    def test_start(self):
        server = Server('localhost', 3000, 5)
        server.start()
        server2 = Server('localhost', 4000, 5)
        server2.start()
        server.connect_with_peer('localhost', 4000)
        sock = server.create_new_server_connection('localhost', 4000)
        node = Node(server._host_, sock, 'localhost', '4000', 'Out')
        node.start()
        server.join()
        server2.join()

if __name__ == '__main__':
    unittest.main()
