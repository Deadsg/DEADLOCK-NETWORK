
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
        block_data = self.to_dict(include_hash=False) # Use to_dict for consistent serialization, but exclude hash
        block_string = json.dumps(block_data, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def to_dict(self, include_hash: bool = True):
        """
        Returns a dictionary representation of the block.
        """
        block_dict = {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": [tx.to_dict() for tx in self.transactions], # Assuming Transaction has to_dict
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
        }
        if include_hash:
            block_dict["hash"] = self.hash
        return block_dict
