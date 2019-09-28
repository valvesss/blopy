# BlockchainPython

Blockchain Python is a library that provides a full self blockchain node. It
handles P2P connections, immutable-ledger, cryptography, consensus protocol and
mining functions.

Each node runs independently until find other nodes in the network. As the
premise says: "if the node found has a large chain, it adapts to it".

The application was made to run by third part, so use it with a client.

- Client example:

> from peer import *

1) Starting a node (In one terminal)

> bob = PeerServer('localhost', 5000)

> bob.start()

2) Starting other node (In other terminal)

> alice = PeerServer('localhost', 6000)

> alice.start()

3) Connecting to other nodes:

> bob.connect_with_peer('localhost', 6000)

4) Sending string-like messages:

> bob.send_to_nodes('Hello World')

5) Sending JSON-like messages:

> block = {

>    'index': '0',

>    'timestamp': '20190928',

>    'transaction': 'Hello World',

>    'nonce': '0',

>    'previous_hash': 'IMAPREVIOUSHASH'

> }

> bob.send_to_nodes(block)

# TODO LIST

- Send blocks to other nodes (json-like) (Actual moving)
- Consensus
- Integrate blockchain with peer
- Validate blocks in all nodes
- More...

Enjoy!
