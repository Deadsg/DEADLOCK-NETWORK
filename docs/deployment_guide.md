# Deployment Guide

This guide provides instructions on how to deploy and run the DQN-based minable Solana coin system.

## Prerequisites

-   [Rust](https://www.rust-lang.org/tools/install)
-   [Solana CLI](https://docs.solana.com/cli/install-solana-cli-tools)
-   [Anchor](https://www.anchor-lang.com/docs/installation)
-   [Python 3.8+](https://www.python.org/downloads/)
-   [PyTorch](https://pytorch.org/get-started/locally/)

## 1. Clone the Repository

```bash
git clone <repository-url>
cd <repository-name>
```

## 2. Install Dependencies

### Rust Dependencies

The Rust dependencies are managed by Cargo and are defined in `Cargo.toml`. They will be automatically installed when building the program.

### Python Dependencies

Install the required Python packages:

```bash
pip install torch numpy
```

## 3. Configure the Environment

The main configuration is done in `solana/config/network.json`.

-   `network`: The Solana network to use (`devnet`, `testnet`, or `mainnet-beta`).
-   `program_id`: The on-chain program ID (this will be updated automatically after deployment).
-   `mint_address`: The address of the SPL token (this will be updated automatically after token creation).

## 4. Build and Deploy

The system can be built and deployed using the provided CLI.

### Step 1: Build the Token

This command will create the SPL token on the configured Solana network.

```bash
python3 cli/gemini-cli.py build-token
```

This will create the token and update `solana/config/token.json` with the mint address.

### Step 2: Deploy the Program

This command will build and deploy the Anchor program.

```bash
python3 cli/gemini-cli.py deploy-program
```

This will deploy the program and update `solana/config/program.json` with the program ID.

## 5. Run the Miner

To start the mining process, run the following command:

```bash
python3 cli/gemini-cli.py init-mining
```

This will start the off-chain miner, which will begin to interact with the on-chain program.

## 6. Validate Proofs

The `validate-proof` command can be used to manually validate a mining proof.

```bash
python3 cli/gemini-cli.py validate-proof <proof> <miner_pubkey> <block_hash> <q_value>
```
