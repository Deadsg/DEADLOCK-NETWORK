#!/bin/bash

# This script creates a new SPL token on the Solana devnet.

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration ---

# The Solana cluster to use. Options: mainnet-beta, testnet, devnet
CLUSTER="devnet"

# The number of decimals for the token.
DECIMALS=9

# The initial supply of the token to mint.
INITIAL_SUPPLY=1000000000

# The keypair for the mint authority.
MINT_AUTHORITY_KEYPAIR="solana/mint_authority.json"

# --- Script ---

echo "Setting up Solana CLI..."
solana config set --url https://rpc.ankr.com/solana_devnet
solana config set --keypair $MINT_AUTHORITY_KEYPAIR

# Check if mint authority keypair exists, if not create it.
if [ ! -f "$MINT_AUTHORITY_KEYPAIR" ]; then
    echo "Generating new mint authority keypair..."
    solana-keygen new --no-bip39-passphrase --outfile $MINT_AUTHORITY_KEYPAIR
fi

echo "Airdropping SOL to mint authority..."
solana airdrop 2

echo "Creating new SPL token..."
TOKEN_MINT_ADDRESS=$(spl-token create-token --decimals $DECIMALS | awk '/Creating token/ {print $3}')
echo "Token Mint Address: $TOKEN_MINT_ADDRESS"

echo "Creating token account..."
TOKEN_ACCOUNT=$(spl-token create-account $TOKEN_MINT_ADDRESS | awk '/Creating account/ {print $3}')
echo "Token Account Address: $TOKEN_ACCOUNT"

echo "Minting $INITIAL_SUPPLY tokens..."
spl-token mint $TOKEN_MINT_ADDRESS $INITIAL_SUPPLY $TOKEN_ACCOUNT

echo "Token minting process complete."
echo "Mint Address: $TOKEN_MINT_ADDRESS"
echo "Account Address: $TOKEN_ACCOUNT"

# Save the mint address for later use
echo "{"token_mint_address": "$TOKEN_MINT_ADDRESS"}" > solana/config/token.json
