import time

from blockchain import *
from server import Server

alice = Server('localhost', 6000, 15)
alice.start()

time.sleep(3)

alice.send_to_nodes('FLAG_01')
