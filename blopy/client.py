import time

from pprint import pprint
from server import Server

bob = Server('localhost', 5000, 20)
bob.start()

bob.bc.forge_genesis_block('IM BOB')
bob.connect_with_peer('localhost', 6000)
data = {'company_user': 'Papa', 'company_name': 'Fatec!', 'company_data': 'Bloco do Papa'}
# bob.bc.new_tx(data)
time.sleep(5)
bob.bc.new_tx(data)
time.sleep(5)
# bob.bc.new_tx(data)
time.sleep(5)
bob.join()
pprint(bob.shared_ledger)
