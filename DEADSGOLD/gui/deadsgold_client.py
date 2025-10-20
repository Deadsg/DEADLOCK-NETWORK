import threading
import time
from DEADSGOLD.blockchain.chain import Blockchain
from DEADSGOLD.wallet.wallet import Wallet
from DEADSGOLD.dqn.validator import DQNValidator
from DEADSGOLD.miner.miner import Miner
from DEADSGOLD.blockchain.transaction import Transaction

class DeadsgoldClient:
    def __init__(self):
        self.blockchain = Blockchain()
        self.wallet = Wallet()
        self.miner = Miner(self.blockchain)
        self.dqn_validator = DQNValidator() # Assuming DQNValidator is initialized here
        self.is_mining = False
        self.mining_thread = None
        self.mining_callback = None

    def get_blockchain_status(self):
        return {
            "block_height": len(self.blockchain.chain),
            "last_block_hash": self.blockchain.last_block.hash,
            "difficulty": self.blockchain.difficulty,
        }

    def get_wallet_address(self):
        return self.wallet.public_key

    def get_wallet_balance(self):
        return self.blockchain.get_balance(self.wallet.public_key)

    def create_new_wallet(self):
        self.wallet = Wallet()
        return self.wallet.public_key

    def send_transaction(self, recipient, amount):
        transaction = self.wallet.create_transaction(recipient, amount)
        if self.blockchain.new_transaction(transaction):
            return True
        return False

    def start_mining(self, callback=None):
        if not self.is_mining:
            self.is_mining = True
            self.mining_callback = callback
            self.mining_thread = threading.Thread(target=self._mining_loop)
            self.mining_thread.daemon = True
            self.mining_thread.start()
            return True
        return False

    def stop_mining(self):
        if self.is_mining:
            self.is_mining = False
            if self.mining_thread:
                self.mining_thread.join(timeout=1) # Wait for the thread to finish
            return True
        return False

    def _mining_loop(self):
        while self.is_mining:
            last_block = self.blockchain.last_block
            pending_transactions = self.blockchain.pending_transactions.copy()
            difficulty = self.blockchain.difficulty

            # Add a reward transaction for the miner
            reward_transaction = Transaction("0", self.wallet.address, 1.0) # Assuming 1.0 unit reward
            pending_transactions.append(reward_transaction)

            print(f"Miner: Starting to mine block {last_block.index + 1}...")
            proof = self.miner.mine(last_block, pending_transactions, difficulty)

            if proof is not None:
                new_block = self.blockchain.new_block(proof)
                print(f"Miner: New block {new_block.index} mined: {new_block.hash}")
                if self.mining_callback:
                    self.mining_callback(new_block.index, new_block.hash, difficulty)
            else:
                print("Miner: No proof found (should not happen in current implementation)")

            time.sleep(0.1) # Small delay to prevent busy-waiting

    def get_dqn_status(self):
        # Placeholder for DQN status
        return {
            "status": "Active",
            "last_decision": "Transaction validated",
            "model_version": "1.0",
        }
