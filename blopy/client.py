import time

from pprint import pprint
from server import Server

bob = Server('localhost', 5000, 20)
bob.start()

bob.bc.forge_genesis_block('IM BOB')
bob.connect_with_peer('localhost', 6000)
time.sleep(5)

for i in range(4):
    data = {'company_user': 'Papa', 'company_name': 'Fatec!', 'company_data': '{0}'.format(i)}
    bob.bc.new_tx(data)
    time.sleep(3)

bob.join()
print('### Transacoes NÃO Inseridas ###')
pprint(bob.shared_tx)
print('### Blocos ###')
# pprint(bob.shared_ledger)
