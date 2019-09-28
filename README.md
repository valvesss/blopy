# BlockchainPython

BlockchainPython is an library that provides a full self blockchain node. It
handles P2P connections, immutable-ledger, cryptography, consensus protocol and
mining functions.

Each node runs indenpendently until find other nodes in the network. As the
premise says: "if the node found has a large chain, it adapts to it".

The application was made to run by third part, so use it with a client.

Client example:

1) Starting the server

> from peer import *
> node1 = PeerServer('localhost', 5000)
> node1.start()

2) Connecting to other nodes:

> node1.connect_with_peer('localhost', 6000)

3) Sending messages:

> node1.send_to_nodes('Jhonny')

Enjoy!
