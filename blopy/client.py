import time

from blockchain import *
from server import Server
from message import Message

bob = Server('localhost', 5000, 10)
bob.start()
m = Message()
bob.connect_with_peer('localhost', 6000)

bob.bc.create_genesis_block('IM BOB')
data = {'company_name': 'It works!', 'company_data': 'Bloco do Bob'}
bob.bc.new_transaction(data)
bob.bc.mine()
time.sleep(3)
block = bob.bc.forge_block()
proof = bob.bc.proof_of_work(block)
validated_block = bob.bc.validate_block(block, proof)
