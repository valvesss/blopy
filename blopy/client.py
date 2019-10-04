from blockchain import *
from server import Server
import time

bob = Server('localhost', 5000, 10)
bob.start()

bob.connect_with_peer('localhost', 6000)

bk = Blockchain()
bk.create_genesis_block()
data = {'company_name': 'Test', 'company_data': 'New Transaction'}
bk.new_transaction(data)
bk.mine()
last_block = bk.last_block.__dict__

bob.send_to_nodes('FLAG_01')
time.sleep(2)
bob.send_to_nodes(last_block)
time.sleep(2)
bob.send_to_nodes('FLAG_01')
