
from solders.keypair import Keypair
from solana.rpc.api import Client
from solders.pubkey import Pubkey
from solders.transaction import Transaction
from solders.system_program import TransferParams, transfer
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

    def get_balance(self, public_key: Pubkey) -> float:
        """
        Gets the SOL balance of a given public key.
        """
        response = self.client.get_balance(public_key)
        return response.value / LAMPORTS_PER_SOL

    def request_airdrop(self, public_key: Pubkey, amount: float) -> str:
        """
        Requests an airdrop of SOL to the given public key (only on devnet/testnet).
        """
        lamports = int(amount * LAMPORTS_PER_SOL)
        return response.value

    def transfer_sol(self, sender_keypair: Keypair, recipient_public_key: Pubkey, amount: float) -> str:
        """
        Transfers SOL from sender to recipient.
        """
        lamports = int(amount * LAMPORTS_PER_SOL)
        transaction = Transaction().add(
            transfer(
                TransferParams(
                    from_pubkey=sender_keypair.pubkey(),
                    to_pubkey=recipient_public_key,
                    lamports=lamports,
                )
            )
        )
        response = self.client.send_transaction(transaction, sender_keypair)
        return response.value

    def get_transactions(self, public_key: Pubkey, limit: int = 10) -> list:
        """
        Gets recent transaction history for a given public key.
        """
        signatures_response = self.client.get_signatures_for_address(public_key, limit=limit)
        transactions = []
        for signature_info in signatures_response.value:
            transaction_response = self.client.get_transaction(signature_info.signature)
            if transaction_response.value:
                transactions.append(transaction_response.value)
        return transactions

    def get_token_accounts_by_owner(self, public_key: Pubkey) -> dict:
        """
        Gets SPL token accounts and their balances for a given public key.
        """
        response = self.client.get_token_accounts_by_owner(public_key, {'programId': Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")})
        token_accounts = {}
        for account in response.value:
            pubkey = account.pubkey
            info = account.account.data.parsed['info']
            token_accounts[str(pubkey)] = {
                'mint': info['mint'],
                'owner': info['owner'],
                'amount': info['tokenAmount']['uiAmountString']
            }
        return token_accounts

    def transfer_token(self, sender_keypair: Keypair, mint_address: Pubkey, recipient_public_key: Pubkey, amount: float) -> str:
        """
        Transfers SPL tokens from sender to recipient.
        """
        from spl.token.instructions import transfer, TransferParams
        from spl.token.associated_token_account import get_associated_token_address

        sender_token_account = get_associated_token_address(sender_keypair.pubkey(), mint_address)
        recipient_token_account = get_associated_token_address(recipient_public_key, mint_address)

        # Check if recipient's token account exists, if not, create instruction to create it
        # For simplicity, we'll assume it exists or handle creation outside this function for now.
        # In a real app, you'd add logic to create if not exists.

        transaction = Transaction().add(
            transfer(
                TransferParams(
                    program_id=Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"),
                    source=sender_token_account,
                    dest=recipient_token_account,
                    owner=sender_keypair.pubkey(),
                    amount=int(amount) # Assuming integer amount for SPL tokens for simplicity
                )
            )
        )
        response = self.client.send_transaction(transaction, sender_keypair)
        return response.value

