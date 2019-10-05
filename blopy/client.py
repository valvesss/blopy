from blockchain import *
from server import Server
import time

bob = Server('localhost', 5000, 20)
bob.start()

bob.connect_with_peer('localhost', 6000)

bob.bc.create_genesis_block('IM BOB')
data = {'company_name': 'Test', 'company_data': 'New Transaction'}
bob.bc.new_transaction(data)
bob.bc.mine()
time.sleep(10)
block = bob.bc.forge_block()
proof = bob.bc.proof_of_work(block)
validated_block = bob.bc.validate_block(block, proof)
time.sleep(3)
bob.send_to_nodes(validated_block)
