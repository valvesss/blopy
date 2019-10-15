import time

# import block
# from blockchain import Blockchain
from pprint import pprint
from server import Server
from message import Message

bob = Server('localhost', 5000, 5)
bob.start()

bob.bc.forge_genesis_block('IM BOB')
# m = Message()
# bob.connect_with_peer('localhost', 6000)

# bob.bc.create_genesis_block('IM BOB')
data = {'company_user': 'Papa',
        'company_name': 'Fatec!',
        'company_data': 'Bloco do Papa'}
bob.bc.new_tx(data)
bob.bc.mine()
bob.join()
pprint(bob.bc.shared_ledger)
# time.sleep(8)
# time.sleep(12)
