import datetime
import hashlib
import json
import requests
import sys
from flask import Flask, jsonify, request
from uuid import uuid4
from urllib.parse import urlparse
from typing import cast, List, Set,Tuple, TypedDict, Union

Transaction = TypedDict('Transaction', {'sender': str,
                                        'receiver': str,
                                        'amount': float})

Block = TypedDict('Block', {'index': int,
                            'timestamp': str,
                            'proof': int,
                            'previous_hash': str,
                            'transactions': List[Transaction]})

ChainAndLength = TypedDict('ChainAndLength', {'chain': List[Block],
                                              'length': int})


class MyCoin:

    @classmethod
    def satisfies_constraint(self, candidate_hash: str) -> bool:
        return candidate_hash[:4] == '0000'


    @classmethod
    def hash_proofs(self, proof_candidate: int, previous_proof: int) -> str:
        return hashlib.sha256(str(proof_candidate**2 - previous_proof**2).encode()).hexdigest()


    @classmethod
    def hash_block(self, block: Block) -> str:
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()


    @classmethod
    def proof_of_work(self, previous_proof: int) -> int:
        proof_candidate = 1
        check_proof = False
        while check_proof is False:
            candidate_hash = MyCoin.hash_proofs(proof_candidate, previous_proof)
            if MyCoin.satisfies_constraint(candidate_hash):
                check_proof = True
            else:
                proof_candidate += 1
        return proof_candidate


    @classmethod
    def is_chain_valid(self, chain: List[Block]) -> bool:
        previous_block = chain[0]
        current_block_index = 1
        while current_block_index < len(chain):
            current_block = chain[current_block_index]
            if current_block['previous_hash'] != MyCoin.hash_block(previous_block):
                return False
            previous_proof = previous_block['proof']
            current_proof = current_block['proof']
            current_hash = MyCoin.hash_proofs(current_proof, previous_proof)
            if MyCoin.satisfies_constraint(current_hash) is False:
                return False
            previous_block = current_block
            current_block_index += 1
        return True


    def __init__(self) -> None:
        self.chain: List[Block] = []
        self.transactions: List[Transaction] = []
        self.nodes: Set[str] = set()
        self.create_block(proof=1, previous_hash='0')


    def create_block(self, proof: int, previous_hash: str) -> Block:
        block: Block = {'index': len(self.chain),
                        'timestamp': str(datetime.datetime.now()),
                        'proof': proof,
                        'previous_hash': previous_hash,
                        'transactions': self.transactions}
        self.transactions = []
        self.chain.append(block)
        return block


    def get_last_block(self) -> Block:
        return self.chain[-1]


    def add_transaction(self, sender: str, receiver: str, amount: float) -> int:
        new_transaction: Transaction = {'sender': sender,
                                        'receiver': receiver,
                                        'amount': amount}
        self.transactions.append(new_transaction)
        previous_block = self.get_last_block()
        return previous_block['index'] + 1


    def add_node(self, address: str) -> None:
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)


    def replace_chain(self) -> bool:
        def node_to_chain_and_length(node: str) -> ChainAndLength:
            return cast(ChainAndLength, requests.get(f'http://{node}/get_chain').json())
        nodes_chain_and_length = map(node_to_chain_and_length, self.nodes)
        longest_chain_and_length: ChainAndLength = {'chain': self.chain, 'length': len(self.chain)}
        for node_chain_and_length in nodes_chain_and_length:
            if (node_chain_and_length['length'] > longest_chain_and_length['length']):
                longest_chain_and_length = node_chain_and_length
        new_chain = longest_chain_and_length['chain']
        is_chain_replaced = self.chain != new_chain
        self.chain = new_chain
        return is_chain_replaced


node_address = str(uuid4())
blockchain = MyCoin()
app = Flask(__name__)


@app.route('/mine_block', methods=['POST'])
def mine_block() -> Tuple[str, int]:
    receiver = request.get_json()['receiver']
    previous_block = blockchain.get_last_block()
    previous_proof = previous_block['proof']
    proof = MyCoin.proof_of_work(previous_proof)
    previous_hash = MyCoin.hash_block(previous_block)
    blockchain.add_transaction(sender = node_address, receiver = receiver, amount = 1.0)
    block = blockchain.create_block(proof, previous_hash)
    response = block
    return jsonify(response), 200


@app.route('/get_chain', methods=['GET'])
def get_chain() -> Tuple[str, int]:
    chain = blockchain.chain
    response: ChainAndLength = {'chain': chain, 'length': len(chain)}
    return jsonify(response), 200


@app.route('/is_valid', methods=['GET'])
def is_valid() -> Tuple[str, int]:
    chain = blockchain.chain
    response = MyCoin.is_chain_valid(chain)
    return jsonify(response), 200


@app.route('/add_transaction', methods=['POST'])
def add_transaction() -> Tuple[str, int]:
    transaction = cast(Transaction, request.get_json())
    index = blockchain.add_transaction(transaction['sender'], transaction['receiver'], transaction['amount'])
    response = {'message': f'Transaction will be added to block {index}'}
    return jsonify(response), 201


@app.route('/connect_node', methods=['POST'])
def connect_node() -> Tuple[str, int]:
    json = request.get_json()
    nodes = cast(List[str], json.get('nodes'))
    for node in nodes:
        blockchain.add_node(node)
    response = {'message': 'All nodes are now connected', 'nodes': list(blockchain.nodes)}
    return jsonify(response), 201


@app.route('/replace_chain', methods=['GET'])
def replace_chain() -> Tuple[str, int]:
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        message = 'The local chain has been replaced'
    else:
        message = 'The local chain was already up-to-date'
    response = {'message': message, 'chain': blockchain.chain}
    return jsonify(response), 200


if len(sys.argv) == 2:
    app.run(port=sys.argv[1])
else:
    print('One argument expected: the port number')
    sys.exit(1)
