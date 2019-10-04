from blockchain import *
from server import Server
import time

bob = Server('localhost', 5000, 15)
bob.start()

bob.connect_with_peer('localhost', 6000)

bob.bc.create_genesis_block()
data = {'company_name': 'Test', 'company_data': 'New Transaction'}
bob.bc.new_transaction(data)
bob.bc.mine()
last_block = bob.bc.last_block.__dict__

bob.send_to_nodes('FLAG_01')
# time.sleep(3)
# bob.send_to_nodes(last_block)
# time.sleep(3)
# bob.send_to_nodes('FLAG_01')
