import time

from pprint import pprint
from server import Server
from message import Message

alice = Server('localhost', 6000, 20)
alice.start()
m = Message()

# alice.bc.create_genesis_block('IM ALICE')
time.sleep(5)
msg = m.create('request', 1)
alice.send_to_nodes(msg)
# time.sleep(15)
alice.join()
pprint(alice.shared_ledger)
