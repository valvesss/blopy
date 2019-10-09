import time

from blockchain import *
from pprint import pprint
from server import Server
from message import Message

alice = Server('localhost', 6000, 10)
alice.start()
m = Message()

# alice.bc.create_genesis_block('IM ALICE')
time.sleep(3)
msg = m.create('request', 2)
alice.send_to_nodes(msg)
