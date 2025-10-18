
import hashlib
from .block import Block
from .transaction import Transaction
from wallet.wallet import Wallet
from dqn.validator import DQNValidator
import time

class Blockchain:
    def __init__(self, use_gpu: bool = False):
        self.chain = [self.create_genesis_block()]
        self.pending_transactions = []
        self.difficulty = 2 # Proof of work difficulty
        self.validator = DQNValidator()
        self.use_gpu = use_gpu # Flag to enable GPU mining placeholder

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

    def gpu_mine(self, last_proof: int) -> int:
        """
        Placeholder for GPU-accelerated Proof of Work.
        In a real implementation, this would call a CUDA/OpenCL kernel.
        For now, it simulates GPU work by calling the CPU PoW.
        """
        print("Simulating GPU mining...")
        # In a real scenario, you'd pass last_proof, difficulty, etc., to a GPU kernel
        # and get the proof back. For this placeholder, we'll just use the CPU PoW.
        return self.proof_of_work_cpu(last_proof)

    def proof_of_work_cpu(self, last_proof: int) -> int:
        """
        Original CPU-bound Proof of Work Algorithm.
        """
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof

    def proof_of_work(self, last_proof: int) -> int:
        """
        Dispatches to CPU or GPU PoW based on configuration.
        """
        if self.use_gpu:
            return self.gpu_mine(last_proof)
        else:
            return self.proof_of_work_cpu(last_proof)

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

    def valid_proof(self, last_proof: int, proof: int) -> bool:
        """
        Validates the proof: Does hash(last_proof, proof) contain <difficulty> leading zeros?
        """
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:self.difficulty] == "0" * self.difficulty
