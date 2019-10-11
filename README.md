# blopy

Blopy is a python library that provides a full self blockchain node. It
handles P2P connections, immutable-ledger, cryptography, consensus protocol and
mining functions.

Each node runs independently until connect to other nodes in the network. As the
premise says: "if the node connected has a large chain, it adapts to it".

The application was made to run by third part, so use it with a client.

- Client example:

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

4) Create genesis block:

> bob.bc.create_genesis_block()

5) Send transactions to all peers-shared-tx-memory

> data = {'company_name': 'It works!', 'company_data': 'Bloco do Bob'}

> bob.bc.new_transaction(data)

6) Mining !!!

> bob.bc.mine()

7) Forge a new block

> bob.forge_block()

8) Requesting other nodes validation for new block

> bob.bc.request_add_block()

9) Request node chain size:

> req = m.create('request', 1)

> bob.send_to_nodes(req)

10) Request other's node chain blocks:

> req = m.create('request', 2)

> bob.send_to_nodes(req)

- Tests:

Please look to our [Wiki Running Tests](Running Tests)

# TO-DO LIST

- Validate for nodes running different chains (but in same network)
- Node search for other nodes over the network
- Smart consensus (51%)
- Improve out of memory immutable-ledger
- Integration with NGROK
- More...

# Contribute

- Help with documentation!!!!!!!!!!!
- Help writing tests!!!!!!!!!!!
- Help forking!
- Help pulling requests!

Enjoy!
