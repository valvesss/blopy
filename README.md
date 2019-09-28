# BlockchainPython

BlockchainPython is an library that provides a full self blockchain node. It
handles P2P connections, immutable-ledger, cryptography, consensus protocol and
mining functions.

Each node runs indenpendently until find other nodes in the network. As the
premise says: "if the node found has a large chain, it adapts to it".

The application was made to run by third part, so use it with a client.

- Client example:

> from peer import *

1) Starting a node (In one terminal)

> node1 = PeerServer('localhost', 5000)

> node1.start()

2) Starting other node (In other terminal)

> node2 = PeerServer('localhost', 6000)

> node2.start()

3) Connecting to other nodes:

> node1.connect_with_peer('localhost', 6000)

4) Sending messages:

> node1.send_to_nodes('Jhonny')

# TODO LIST

- Consensus
- Integrate blockchain with peer
- Send blocks to other nodes (json-like)
- Validate blocks in all nodes
- More...

Enjoy!
