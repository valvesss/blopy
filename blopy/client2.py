import time

from pprint import pprint
from blockchain import *
from server import Server

alice = Server('localhost', 6000, 20)
alice.start()

alice.bc.create_genesis_block('IM ALICE')
alice.send_to_nodes('REQ_01')
time.sleep(5)
msg = alice.create_message('request', 1, '')
alice.send_to_nodes(msg)
