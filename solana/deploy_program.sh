#!/bin/bash

# This script builds and deploys the Solana program.

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration ---

# The Solana cluster to use. Options: mainnet-beta, testnet, devnet
CLUSTER="devnet"

# The keypair for the deployer.
DEPLOYER_KEYPAIR="solana/mint_authority.json"

# --- Script ---

echo "Setting up Solana CLI..."
solana config set --url https://solana-devnet.drpc.org
solana config set --keypair $DEPLOYER_KEYPAIR

echo "Building the Solana program..."
cargo build-sbf --manifest-path=programs/dqn_mine/Cargo.toml --sbf-out-dir=target/deploy

echo "Deploying the Solana program..."
solana program deploy target/deploy/dqn_mine.so

PROGRAM_ID=$(solana-keygen pubkey target/deploy/dqn_mine-keypair.json)

echo "Program ID: $PROGRAM_ID"

# Save the program id for later use
echo "{"program_id": "$PROGRAM_ID"}" > solana/config/program.json