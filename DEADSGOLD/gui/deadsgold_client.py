import requests
import threading
import time
from DEADSGOLD.wallet.wallet import Wallet
from DEADSGOLD.blockchain.transaction import Transaction

class DeadsgoldClient:
    def __init__(self, api_url="http://127.0.0.1:5000"):
        self.api_url = api_url
        self.wallet = Wallet()
        self.is_mining = False
        self.mining_thread = None
        self.mining_callback = None

    def get_blockchain_status(self):
        response = requests.get(f"{self.api_url}/chain")
        if response.status_code == 200:
            chain_data = response.json()
            return {
                "block_height": chain_data['length'],
                "last_block_hash": chain_data['chain'][-1]['hash'],
                "difficulty": chain_data['difficulty'], # Assuming API returns difficulty
            }
        return None

    def get_wallet_address(self):
        return self.wallet.address

    def get_wallet_balance(self):
        address = self.get_wallet_address()
        response = requests.get(f"{self.api_url}/balance/{address}")
        if response.status_code == 200:
            return response.json()['balance']
        return None

    def get_private_key_hex(self):
        try:
            return self.wallet.private_key_hex
        except ValueError:
            return "Private key not loaded or decrypted."

    def create_new_wallet(self):
        self.wallet = Wallet()
        return self.wallet.address, self.wallet.private_key_hex

    def load_wallet_from_private_key(self, private_key_hex: str):
        try:
            self.wallet = Wallet.from_private_key_hex(private_key_hex)
            return True
        except Exception as e:
            print(f"Error loading wallet from private key: {e}")
            return False

    def send_transaction(self, recipient, amount):
        transaction = self.wallet.create_transaction(recipient, amount)
        payload = {
            "sender": transaction.sender,
            "recipient": transaction.recipient,
            "amount": transaction.amount,
            "signature": transaction.signature.hex() if transaction.signature else None # Assuming signature is bytes
        }
        response = requests.post(f"{self.api_url}/transactions/new", json=payload)
        return response.status_code == 201

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
            print("Miner: Requesting to mine a new block via API...")
            response = requests.get(f"{self.api_url}/mine")
            if response.status_code == 200:
                mining_data = response.json()
                print(f"Miner: New block {mining_data['index']} mined: {mining_data['previous_hash']}")
                if self.mining_callback:
                    # We need to get the difficulty from the blockchain status
                    blockchain_status = self.get_blockchain_status()
                    difficulty = blockchain_status['difficulty'] if blockchain_status else None
                    self.mining_callback(mining_data['index'], mining_data['previous_hash'], difficulty)
            else:
                print(f"Miner: Failed to mine block. Status code: {response.status_code}, Response: {response.text}")

            time.sleep(0.1) # Small delay to prevent busy-waiting

    def get_dqn_status(self):
        response = requests.get(f"{self.api_url}/dqn_status")
        if response.status_code == 200:
            return response.json()['status']
        return None
