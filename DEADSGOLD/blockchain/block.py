
import hashlib
import json
from time import time

class Block:
    def __init__(self, index, transactions, previous_hash, nonce=0, timestamp=None):
        self.index = index
        self.timestamp = timestamp or time()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.compute_hash()

    def compute_hash(self):
        """
        Computes the hash of the block.
        """
        block_data = {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": [t.__dict__ for t in self.transactions],
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }
        block_string = json.dumps(block_data, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
