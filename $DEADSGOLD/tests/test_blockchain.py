
import sys
import os
import unittest
import hashlib

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from blockchain.chain import Blockchain
from blockchain.block import Block
from blockchain.transaction import Transaction

class TestBlockchain(unittest.TestCase):

    def setUp(self):
        """Set up a new blockchain for each test."""
        self.blockchain = Blockchain()

    def test_genesis_block(self):
        """Test the creation of the genesis block."""
        genesis_block = self.blockchain.chain[0]
        self.assertEqual(genesis_block.index, 0)
        self.assertEqual(genesis_block.previous_hash, "0")
        self.assertEqual(genesis_block.transactions, [])

    def test_new_block(self):
        """Test the creation of a new block."""
        last_block = self.blockchain.last_block
        proof = 12345
        new_block = self.blockchain.new_block(proof)

        self.assertEqual(new_block.index, last_block.index + 1)
        self.assertEqual(new_block.previous_hash, last_block.hash)
        self.assertIsNotNone(new_block.hash)

    def test_new_transaction(self):
        """Test the creation of a new transaction."""
        self.blockchain.new_transaction(Transaction("sender1", "recipient1", 10))
        self.assertEqual(len(self.blockchain.pending_transactions), 1)
        self.assertEqual(self.blockchain.pending_transactions[0].sender, "sender1")

    def test_proof_of_work(self):
        """Test the proof of work algorithm."""
        last_proof = self.blockchain.last_block.nonce
        proof = self.blockchain.proof_of_work(last_proof)
        
        self.assertTrue(self.blockchain.valid_proof(last_proof, proof))
        
        # Test with an invalid proof
        invalid_proof = 999999
        self.assertFalse(self.blockchain.valid_proof(last_proof, invalid_proof))

    def test_chain_validity(self):
        """Test the validity of the blockchain."""
        # Add a new block
        last_proof = self.blockchain.last_block.nonce
        proof = self.blockchain.proof_of_work(last_proof)
        self.blockchain.new_block(proof)

        # Add another block
        last_proof = self.blockchain.last_block.nonce
        proof = self.blockchain.proof_of_work(last_proof)
        self.blockchain.new_block(proof)

        # The chain should be valid
        self.assertTrue(self.is_chain_valid(self.blockchain.chain))

        # Tamper with a block
        self.blockchain.chain[1].transactions = [Transaction("a", "b", 100)]
        
        # The chain should now be invalid
        self.assertFalse(self.is_chain_valid(self.blockchain.chain))

    def is_chain_valid(self, chain):
        """
        Helper function to determine if a given blockchain is valid.
        """
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            
            # Check that the hash of the block is correct
            if block.previous_hash != last_block.compute_hash():
                return False

            # Check that the Proof of Work is correct
            if not self.blockchain.valid_proof(last_block.nonce, block.nonce):
                 return False
            
            last_block = block
            current_index += 1

        return True

if __name__ == '__main__':
    unittest.main()
