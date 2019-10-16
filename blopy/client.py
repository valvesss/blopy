import time

from pprint import pprint
from server import Server

bob = Server('localhost', 5000, 5)
bob.start()

bob.bc.forge_genesis_block('IM BOB')
# bob.connect_with_peer('localhost', 6000)
data = {'company_user': 'Papa', 'company_name': 'Fatec!', 'company_data': 'Bloco do Papa'}
bob.bc.new_tx(data)
bob.bc.new_tx(data)
bob.bc.new_tx(data)
time.sleep(3)
bob.bc.mine()
bob.join()
pprint(bob.bc.shared_ledger)
