# System Architecture

This document describes the architecture of the DQN-based minable Solana coin system.

## Overview

The system is composed of three main components:
1.  **Solana On-chain Program:** An Anchor-based Solana program that handles the core logic of the token, including minting, transferring, and verifying mining proofs.
2.  **DQN Off-chain Miner:** A Python-based application that uses a Deep Q-Learning agent to find optimal mining solutions.
3.  **CLI:** A command-line interface for interacting with the system, including building the token, deploying the program, and initiating the mining process.

## On-chain Program

The on-chain program is built using the Anchor framework and is responsible for:
-   **Token Management:** Creating and managing the SPL token.
-   **Mining Proof Verification:** Verifying the proofs submitted by the off-chain miners. The `verify_mine` function is the entry point for this.
-   **Reward Distribution:** Distributing rewards to the miners based on the verified proofs.
-   **State Management:** Storing the state of the mining process on-chain, including difficulty and other parameters.

## Off-chain Miner

The off-chain miner is a Python application that performs the following tasks:
-   **DQN Agent:** Implements a DQN agent to learn the optimal mining strategy.
-   **Interaction with Solana:** Communicates with the Solana blockchain to get the current state of the mining process and to submit mining proofs.
-   **Q-value Calculation:** Calculates the Q-values for different mining actions and selects the best action.

The DQN miner consists of:
-   `network.py`: The neural network model.
-   `memory_buffer.py`: The replay memory for training the DQN.
-   `reward_engine.py`: The logic for calculating rewards and adjusting emission rates.

## CLI

The `gemini-cli.py` script provides a command-line interface for managing the system. It includes the following commands:
-   `build-token`: Creates the SPL token.
-   `deploy-program`: Deploys the Anchor program to the Solana blockchain.
-   `init-mining`: Initializes the mining process.
-   `validate-proof`: Validates a mining proof.

## Workflow

1.  The administrator uses the CLI to create the token and deploy the program.
2.  The administrator initializes the mining process using the CLI.
3.  Miners run the off-chain miner application to find mining solutions.
4.  The off-chain miner submits the mining proofs to the on-chain program.
5.  The on-chain program verifies the proofs and distributes rewards to the miners.
