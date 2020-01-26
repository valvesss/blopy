import time

from pprint import pprint
from server import Server

### SERVIDOR ###
alice = Server('localhost', 6000, 20)
alice.start()

time.sleep(5)

### MESSAGES / TRANSACTIONS ###
for i in range(4):
    data = {'company_user': 'Alice', 'company_name': 'Fatec!', 'company_data': '{0}'.format(i)}
    alice.bc.new_tx(data)
    time.sleep(3)
alice.join()

### IMMUTABLE-LEDGER ###
print('### Blocos ###')
pprint(alice.shared_ledger)
