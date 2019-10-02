import unittest
from blockchain import *
from server import Server

class TestServer(unittest.TestCase):
    def setUp(self):
        pass

    def test_scale_up(self):
        server = Server('localhost', 3000, 1)

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

    def test_send_to_nodes(self):
        server = Server('localhost', 3000, 3)
        server.start()
        server2 = Server('localhost', 4000, 3)
        server2.start()
        server.connect_with_peer('localhost', 4000)
        bk = Blockchain()
        bk.create_genesis_block()
        data = {'company_name': 'Test', 'company_data': 'Brand new block!'}
        bk.new_transaction(data)
        block = bk.create_new_block()
        block_dict = block.__dict__
        server.send_to_nodes(block_dict)
        server.join()
        server2.join()

    def test_validate_new_peer_connection(self):
        server = Server('localhost', 3000, 2)
        server.start()
        server2 = Server('localhost', 4000, 2)
        server2.start()
        server.validate_new_peer_connection('localhost', 4000)
        server.join()
        server2.join()

    def test_close_server_connection(self):
        server = Server('localhost', 3000, 1)
        server.start()
        server.close_server_connection('unit test')
        server.join()

    def test_close_connected_nodes(self):
        server = Server('localhost', 3000, 3)
        server.start()
        server2 = Server('localhost', 4000, 3)
        server2.start()
        server.connect_with_peer('localhost', 4000)
        server.close_connected_nodes()
        server.join()

    def test_stop(self):
        server = Server('localhost', 3000, 3)
        server.start()
        server.stop()
        server.join()

if __name__ == '__main__':
    unittest.main()
