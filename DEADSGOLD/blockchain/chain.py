
import hashlib
from blockchain.block import Block
from blockchain.transaction import Transaction
from wallet.wallet import Wallet
from dqn.validator import DQNValidator
from miner.miner import Miner
import time

class Blockchain:
    TARGET_BLOCK_TIME = 10 # seconds
    DIFFICULTY_ADJUSTMENT_INTERVAL = 10 # blocks

    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.pending_transactions = []
        self.difficulty = 4 # Proof of work difficulty
        self.validator = DQNValidator()
        self.miner = Miner(self)

    def create_genesis_block(self):
        """
        Creates the very first block in the chain.
        """
        return Block(0, [], "0", timestamp=time.time())

    @property
    def last_block(self):
        """
        Returns the last block in the chain.
        """
        return self.chain[-1]

    def new_transaction(self, transaction: Transaction) -> bool:
        """
        Adds a new transaction to the list of pending transactions after verification.
        Returns True if the transaction is valid and added, False otherwise.
        """
        if transaction.sender == "0":  # Reward transaction
            self.pending_transactions.append(transaction)
            return True

        if not Wallet.verify(transaction.sender, transaction.signature, transaction.to_bytes()):
            print(f"Invalid transaction signature from {transaction.sender}")
            return False

        if not self.validator.validate_transaction(transaction):
            print(f"Transaction from {transaction.sender} failed DQN validation.")
            return False

        self.pending_transactions.append(transaction)
        return True

    def new_block(self, proof, previous_hash=None):
        """
        Creates a new block and adds it to the chain.
        """
        block = Block(
            index=len(self.chain),
            transactions=self.pending_transactions,
            previous_hash=previous_hash or self.last_block.hash,
            nonce=proof,
            timestamp=time.time()
        )

        # Reset the list of pending transactions
        self.pending_transactions = []

        self.chain.append(block)

        # Adjust difficulty if needed
        if block.index % self.DIFFICULTY_ADJUSTMENT_INTERVAL == 0 and block.index > 0:
            self.adjust_difficulty()

        return block

    def adjust_difficulty(self):
        """
        Adjusts the mining difficulty based on the time taken to mine recent blocks.
        """
        if len(self.chain) < self.DIFFICULTY_ADJUSTMENT_INTERVAL + 1:
            return

        # Get the last N blocks for adjustment
        recent_blocks = self.chain[-(self.DIFFICULTY_ADJUSTMENT_INTERVAL + 1):]
        time_taken = recent_blocks[-1].timestamp - recent_blocks[0].timestamp
        expected_time = self.TARGET_BLOCK_TIME * self.DIFFICULTY_ADJUSTMENT_INTERVAL

        if time_taken < expected_time / 2: # Too fast, increase difficulty significantly
            self.difficulty += 2
        elif time_taken < expected_time: # A bit fast, increase difficulty slightly
            self.difficulty += 1
        elif time_taken > expected_time * 2: # Too slow, decrease difficulty significantly
            self.difficulty = max(1, self.difficulty - 2)
        elif time_taken > expected_time: # A bit slow, decrease difficulty slightly
            self.difficulty = max(1, self.difficulty - 1)

        print(f"Difficulty adjusted to: {self.difficulty}")

    def get_balance(self, address: str) -> float:
        """
        Calculates the balance of a given address.
        """
        balance = 0
        for block in self.chain:
            for tx in block.transactions:
                if tx.recipient == address:
                    balance += tx.amount
                if tx.sender == address:
                    balance -= tx.amount
        return balance

    def valid_proof(self, block: Block) -> bool:
        """
        Validates the proof: Does the hash of the block contain <difficulty> leading zeros?
        """
        return self.miner.valid_proof_hash(self.last_block, block.transactions, block.nonce, self.difficulty)

    def mine_local(self):
        """
        Mines a new block using a local proof-of-work mechanism.
        """
        last_block = self.last_block
        last_proof = last_block.nonce
        
        proof = 0
        while not self.valid_proof_local(last_proof, proof, self.difficulty):
            proof += 1

        # Create the new block
        block = self.new_block(proof)
        return block

    def valid_proof_local(self, last_proof, proof, difficulty):
        """
        Validates the proof: Does the hash of the proof contain <difficulty> leading zeros?
        """
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:difficulty] == '0' * difficulty
