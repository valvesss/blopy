from blockchain import *
from server import Server

alice = Server('localhost', 6000, 10)
alice.start()
