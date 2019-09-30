from blockchain import *
from server import Server
from node import Node
import logging

node01 = Server('localhost', 3400)
node02 = Server('localhost', 3600)


def test_client_start():
    try:
        # node01 = Server('localhost', 3400)
        node01.start()
    except:
        logging.info('The connection was closed due to some unknown error')


def test_server_start():
    try:
        # node02 = Server('localhost', 3600)
        node02.start()
    except:
        logging.info('The connection was closed due to some unknown error')


def test_connect_peer():
    try:
        node02.connect_with_peer('localhost', 3400)
        node02.send_to_nodes('opa')
    except:
        logging.info('The connection between the server and the client could not happen')


# def call_blockchain():
#     bk = Blockchain()
#     bk.create_genesis_block()
