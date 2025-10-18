
import hashlib
from .block import Block
from .transaction import Transaction
from wallet.wallet import Wallet
from dqn.validator import DQNValidator
from miner.miner import Miner
import time

class Blockchain:
    def __init__(self, use_gpu: bool = False):
        self.chain = [self.create_genesis_block()]
        self.pending_transactions = []
        self.difficulty = 4 # Proof of work difficulty
        self.validator = DQNValidator()
        self.miner = Miner(self, use_gpu)

    def create_genesis_block(self):
        """
        Creates the very first block in the chain.
        """
        return Block(0, [], "0")

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
            nonce=proof
        )

        # Reset the list of pending transactions
        self.pending_transactions = []

        self.chain.append(block)
        return block

    def mine(self):
        """
        Mines a new block.
        """
        proof = self.miner.mine()
        return self.new_block(proof)

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
        return block.hash[:self.difficulty] == "0" * self.difficulty
