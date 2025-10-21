import pytest
import hashlib
import json
from time import time

from DEADSGOLD.blockchain.block import Block
from DEADSGOLD.blockchain.chain import Blockchain
from DEADSGOLD.blockchain.transaction import Transaction
from DEADSGOLD.miner.miner import Miner

@pytest.fixture
def sample_blockchain():
    blockchain = Blockchain()
    # Add a genesis block for a valid blockchain state
    blockchain.chain = [blockchain.create_genesis_block()]
    return blockchain

@pytest.fixture
def sample_transactions():
    tx1 = Transaction("sender1", "recipient1", 10)
    tx2 = Transaction("sender2", "recipient2", 20)
    return [tx1, tx2]

def test_miner_cpu_mining(sample_blockchain, sample_transactions):
    miner = Miner(sample_blockchain)
    difficulty = 2  # Use a low difficulty for testing

    last_block = sample_blockchain.last_block
    pending_transactions = sample_transactions

    print(f"Starting mining test with difficulty {difficulty}...")
    nonce, timestamp = miner.mine_cpu(last_block, pending_transactions, difficulty)
    print(f"Mining test completed. Found nonce: {nonce}")

    assert nonce is not None
    assert isinstance(nonce, int)

    # Verify the found nonce with valid_proof_hash
    is_valid = miner.valid_proof_hash(last_block, pending_transactions, nonce, difficulty, timestamp)
    assert is_valid, "The found nonce should produce a valid hash"

def test_valid_proof_hash_function(sample_blockchain, sample_transactions):
    miner = Miner(sample_blockchain)
    difficulty = 2

    last_block = sample_blockchain.last_block
    pending_transactions = sample_transactions

    # Test with a known valid nonce (this might need to be adjusted if the hash calculation changes)
    # For simplicity, let's assume a nonce that would work for difficulty 2
    # In a real scenario, you might pre-calculate a valid nonce for a fixed block data
    # For now, we'll rely on mine_cpu to find one and then test valid_proof_hash with it.
    
    # First, find a valid nonce using the miner
    nonce, timestamp = miner.mine_cpu(last_block, pending_transactions, difficulty)
    assert nonce is not None

    # Now, use this nonce to test valid_proof_hash
    is_valid = miner.valid_proof_hash(last_block, pending_transactions, nonce, difficulty, timestamp)
    assert is_valid, "valid_proof_hash should return True for a correctly found nonce"

    # Test with an invalid nonce
    invalid_nonce = nonce + 1 # A slightly different nonce should be invalid
    is_invalid = miner.valid_proof_hash(last_block, pending_transactions, invalid_nonce, difficulty, timestamp)
    assert not is_invalid, "valid_proof_hash should return False for an incorrect nonce"
