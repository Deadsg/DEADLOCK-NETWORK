
from flask import Flask, jsonify, request
from uuid import uuid4

from DEADSGOLD.blockchain.chain import Blockchain
from DEADSGOLD.blockchain.transaction import Transaction

# Instantiate the Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()


@app.route('/mine', methods=['GET'])
def mine():
    # We run the proof of work algorithm to get the next proof...
    last_block = blockchain.last_block
    last_proof = last_block.nonce
    proof = blockchain.proof_of_work(last_proof)

    # We must receive a reward for finding the proof.
    # The sender is "0" to signify that this node has mined a new coin.
    blockchain.new_transaction(
        Transaction(sender="0", recipient=node_identifier, amount=1)
    )

    # Forge the new Block by adding it to the chain
    previous_hash = blockchain.last_block.hash
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "New Block Forged",
        'index': block.index,
        'transactions': [tx.__dict__ for tx in block.transactions],
        'proof': block.nonce,
        'previous_hash': block.previous_hash,
    }
    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    # Check that the required fields are in the POST'ed data
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new Transaction
    transaction = Transaction(sender=values['sender'], recipient=values['recipient'], amount=values['amount'])
    blockchain.new_transaction(transaction)

    response = {'message': f'Transaction will be added to Block {blockchain.last_block.index + 1}'}
    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': [block.__dict__ for block in blockchain.chain],
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
