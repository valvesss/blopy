import time

from pprint import pprint
from server import Server

bob = Server('localhost', 5000, 20)
bob.start()

bob.bc.forge_genesis_block('IM BOB')
data = {'company_user': 'Papa', 'company_name': 'Fatec!', 'company_data': 'Bloco do Papa'}
bob.bc.new_tx(data)
bob.connect_with_peer('localhost', 6000)
# bob.bc.new_tx(data)
# time.sleep(5)
# time.sleep(8)
# bob.bc.new_tx(data)
# time.sleep(5)
bob.join()
pprint(bob.shared_ledger)
