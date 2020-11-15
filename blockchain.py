import datetime
import hashlib
import json
from flask import Flask, jsonify
from typing import Dict, List, Tuple, Union

class Blockchain:

    @classmethod
    def satisfies_constraint(self, candidate_hash) -> bool:
        return candidate_hash[:4] == '0000'


    @classmethod
    def hash_proofs(self, proof_candidate, previous_proof) -> str:
        return hashlib.sha256(str(proof_candidate**2 - previous_proof**2).encode()).hexdigest()


    @classmethod
    def hash_block(self, block) -> str:
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()


    @classmethod
    def proof_of_work(self, previous_proof) -> int:
        proof_candidate = 1
        check_proof = False
        while check_proof is False:
            candidate_hash = Blockchain.hash_proofs(proof_candidate, previous_proof)
            if Blockchain.satisfies_constraint(candidate_hash):
                check_proof = True
            else:
                proof_candidate += 1
        return proof_candidate


    @classmethod
    def is_chain_valid(self, chain) -> bool:
        previous_block = chain[0]
        current_block_index = 1
        while current_block_index < len(chain):
            current_block = chain[current_block_index]
            if current_block['previous_hash'] != Blockchain.hash_block(previous_block):
                return False
            previous_proof = previous_block['proof']
            current_proof = current_block['proof']
            current_hash = Blockchain.hash_proofs(current_proof, previous_proof)
            if Blockchain.satisfies_constraint(current_hash) is False:
                return False
            previous_block = current_block
            current_block_index += 1
        return True


    def __init__(self) -> None:
        self.chain: List[Dict[str, Union[int, str]]] = []
        self.create_block(proof=1, previous_hash='0')


    def create_block(self, proof, previous_hash) -> Dict[str, Union[int, str]]:
        block = {'index': len(self.chain),
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash}
        self.chain.append(block)
        return block


    def get_last_block(self) -> Dict[str, Union[int, str]]:
        return self.chain[-1]


app = Flask(__name__)
blockchain = Blockchain()


@app.route('/mine_block', methods=['GET'])
def mine_block() -> Tuple[str, int]:
    previous_block = blockchain.get_last_block()
    previous_proof = previous_block['proof']
    proof = Blockchain.proof_of_work(previous_proof)
    previous_hash = Blockchain.hash_block(previous_block)
    block = blockchain.create_block(proof, previous_hash)
    response = block
    return jsonify(response), 200


@app.route('/get_chain', methods=['GET'])
def get_chain() -> Tuple[str, int]:
    chain = blockchain.chain
    response = {'chain': chain, 'length': len(chain)}
    return jsonify(response), 200


@app.route('/is_valid', methods=['GET'])
def is_valid() -> Tuple[str, int]:
    chain = blockchain.chain
    response = Blockchain.is_chain_valid(chain)
    return jsonify(response), 200


app.run(port=5000)
