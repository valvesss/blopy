# blopy

Blopy is a python library that provides a full self blockchain node. It
handles P2P connections, immutable-ledger, cryptography, consensus protocol and
mining functions.

Each node runs independently until find other nodes in the network. As the
premise says: "if the node found has a large chain, it adapts to it".

The application was made to run by third part, so use it with a client.

- Client example:

> from blockchain import *

> from server import Server

> from message import Message

> m = Message()

1) Starting a node (In one terminal)

> bob = Server('localhost', 5000, 10)

> bob.start()

2) Starting other node (In other terminal)

> alice = Server('localhost', 6000, 10)

> alice.start()

3) Connecting to other nodes:

> bob.connect_with_peer('localhost', 6000)

4) Sending string-like messages:

> bob.send_to_nodes('Hello World')

5) Sending JSON-like messages (now using blockchain functions):

> bk = Blockchain()

> bk.create_genesis_block()

> bk.new_transaction()

> bk.mine()

> block = bk.forge_block()

> proof = bk.proof_of_work(block)

> validated_block = bk.validate_block(block, proof)

> bob.send_to_nodes(validated_block)

6) Request node chain size:

> req = m.create('request', 1)

> bob.send_to_nodes(req)

7) Request other's node chain blocks:

> req = m.create('request', 2)

> bob.send_to_nodes(req)

8) Request a new block validation:

> req = m.create('request', 3)

> bob.send_to_nodes(req)

- Tests:

To test the application, simple execute:

> python -m unittest -v test_server


# TO-DO LIST

- Integrated Consensus (Actual moving)
- More...

# Contribute

- Help with documentation!
- Help forking!
- Help pulling requests!

Enjoy!
