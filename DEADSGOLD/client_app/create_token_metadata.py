import json
import os
from solana.rpc.api import Client
from solana.keypair import Keypair
from solana.publickey import PublicKey
from solana.transaction import Transaction
from spl.token.constants import TOKEN_PROGRAM_ID
from spl.token.instructions import initialize_mint, MINT_LAYOUT, create_associated_token_account, get_associated_token_address
from spl.token.client import Token

# Configuration
RPC_URL = "https://api.mainnet-beta.solana.com"
TOKEN_JSON_PATH = "DEADSGOLD/token.json"
MINER_KEYPAIR_PATH = "DEADSGOLD/miner_keypair.json"

def create_token_metadata():
    print("Loading token information...")
    with open(TOKEN_JSON_PATH, 'r') as f:
        token_info = json.load(f)

    mint_address_str = token_info["mint_address"]
    token_name = token_info["name"]
    token_symbol = token_info["symbol"]
    token_decimals = token_info["decimals"]
    wallet_address_str = token_info["creators"][0]["address"]

    print("Loading miner keypair...")
    with open(MINER_KEYPAIR_PATH, 'r') as f:
        miner_keypair_bytes = json.load(f)
    miner_keypair = Keypair.from_secret_key(bytes(miner_keypair_bytes))
    wallet_address = PublicKey(wallet_address_str)

    print(f"Connecting to RPC: {RPC_URL}")
    client = Client(RPC_URL)

    # Check if the mint already exists (optional, but good practice)
    mint_pubkey = PublicKey(mint_address_str)
    try:
        mint_info = client.get_account_info(mint_pubkey)
        if mint_info.value:
            print(f"Mint account {mint_address_str} already exists. Skipping creation.")
            return
    except Exception as e:
        print(f"Could not fetch mint info (might not exist yet): {e}")

    print(f"Creating token mint with name: {token_name}, symbol: {token_symbol}, decimals: {token_decimals}")

    # Generate a new keypair for the mint account
    # In a real scenario, you might want to use a specific keypair for the mint authority
    # For simplicity, we'll use the miner_keypair as both payer and mint authority
    mint_authority = miner_keypair
    freeze_authority = None # No freeze authority for simplicity

    # Create the mint account
    # This is a simplified approach. The spl-token-py library has a Token.create_mint function
    # that handles many of these steps.
    # For direct instruction building, it's more complex.
    # Let's use the Token client for simplicity.
    token_client = Token(
        conn=client,
        pubkey=mint_pubkey,
        program_id=TOKEN_PROGRAM_ID,
        payer=miner_keypair
    )

    # Create the mint account and initialize it
    # This function handles creating the account, initializing the mint, and setting authorities.
    # It uses the payer to pay for the transaction and the mint_authority to sign the initialize_mint instruction.
    try:
        new_mint_pubkey = token_client.create_mint(
            payer=miner_keypair,
            mint_authority=mint_authority.pubkey(),
            freeze_authority=freeze_authority,
            decimals=token_decimals,
            skip_confirmation=False,
        )
        print(f"Successfully created token mint: {new_mint_pubkey}")

        # Create associated token account for the wallet address
        ata_pubkey = get_associated_token_address(wallet_address, new_mint_pubkey)
        print(f"Creating associated token account for {wallet_address} at {ata_pubkey}")
        create_ata_ix = create_associated_token_account(
            payer=miner_keypair.pubkey(),
            owner=wallet_address,
            mint=new_mint_pubkey,
        )
        txn = Transaction().add(create_ata_ix)
        client.send_transaction(txn, miner_keypair)
        print(f"Associated token account created: {ata_pubkey}")

    except Exception as e:
        print(f"Error creating token mint or ATA: {e}")

    print("\n--- Metaplex Metadata ---" )
    print("To create full Metaplex metadata (including URI, creators, etc.), you would typically:")
    print("1. Upload the content of your token.json (or a more detailed JSON) to a decentralized storage like Arweave or IPFS.")
    print("2. Get the URI of the uploaded content.")
    print("3. Interact with the Metaplex Token Metadata program to create/update the metadata account for your mint.")
    print("   This usually involves using a Metaplex SDK (e.g., @metaplex-foundation/js in JavaScript) or constructing raw transactions.")
    print("   The Python solana/spl-token libraries do not directly expose Metaplex metadata creation.")

if __name__ == '__main__':
    create_token_metadata()
