import time

from blockchain import *
from server import Server
from message import Message

bob = Server('localhost', 5000, 20)
bob.start()
m = Message()
bob.connect_with_peer('localhost', 6000)

bob.bc.create_genesis_block('IM BOB')
data = {'company_name': 'It works!', 'company_data': 'Bloco do Bob'}
bob.bc.new_transaction(data)
bob.bc.mine()
time.sleep(8)
block = bob.bc.forge_block()
bob.bc.request_add_block()
time.sleep(12)
pprint(bob.bc.chain)
