
from solana.keypair import Keypair
from solana.rpc.api import Client
from solana.publickey import PublicKey
from solana.transaction import Transaction
from solana.system_program import TransferParams, transfer
from solana.constants import LAMPORTS_PER_SOL

SOLANA_CLUSTER_URL = "https://api.devnet.solana.com"

class SolanaClient:
    def __init__(self):
        self.client = Client(SOLANA_CLUSTER_URL)

    def generate_keypair(self) -> Keypair:
        """
        Generates a new Solana keypair.
        """
        return Keypair()

    def get_balance(self, public_key: PublicKey) -> float:
        """
        Gets the SOL balance of a given public key.
        """
        response = self.client.get_balance(public_key)
        return response['result']['value'] / LAMPORTS_PER_SOL

    def request_airdrop(self, public_key: PublicKey, amount: float) -> str:
        """
        Requests an airdrop of SOL to the given public key (only on devnet/testnet).
        """
        lamports = int(amount * LAMPORTS_PER_SOL)
        response = self.client.request_airdrop(public_key, lamports)
        return response['result']

    def transfer_sol(self, sender_keypair: Keypair, recipient_public_key: PublicKey, amount: float) -> str:
        """
        Transfers SOL from sender to recipient.
        """
        lamports = int(amount * LAMPORTS_PER_SOL)
        transaction = Transaction().add(
            transfer(
                TransferParams(
                    from_pubkey=sender_keypair.public_key,
                    to_pubkey=recipient_public_key,
                    lamports=lamports,
                )
            )
        )
        response = self.client.send_transaction(transaction, sender_keypair)
        return response['result']
