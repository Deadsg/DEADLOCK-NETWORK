# $DEADSGOLD: An AI-Powered Blockchain Project

Welcome to $DEADSGOLD! This project is a unique blockchain implementation that uses Artificial Intelligence (AI) to validate transactions. It's a great way to learn about both blockchain technology and AI.

## Features

*   **Simple Blockchain:** A functional blockchain built from the ground up in Python.
*   **AI-Powered Transaction Validation:** A Deep Q-Network (DQN) is used to validate transactions, adding an intelligent layer to the blockchain.
*   **HTTP API:** A simple API built with Flask to interact with the blockchain.
*   **Wallet:** A basic wallet implementation for signing transactions.
*   **Solana Integration:** Includes examples for integrating with the Solana blockchain.

## Getting Started

Follow these instructions to get a copy of the project up and running on your local machine.

### Prerequisites

*   Python 3.8+
*   pip

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    ```
2.  **Navigate to the project directory:**
    ```bash
    cd $DEADSGOLD
    ```
3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Install additional dependencies:**
    Some dependencies are not listed in the `requirements.txt` file. Please install them manually:
    ```bash
    pip install flask torch
    ```

## Project Structure

Here's a brief overview of the project's structure:

*   `api/`: Contains the Flask API for interacting with the blockchain.
*   `blockchain/`: The core blockchain implementation, including blocks, the chain, and transactions.
*   `dqn/` & `DQNAgent/`: Contains the Deep Q-Network (DQN) implementation for AI-powered transaction validation.
*   `gui/`: A graphical user interface for the project.
*   `miner/`: The miner for the blockchain.
*   `node/`: The node implementation for the blockchain.
*   `solana_integration/`: Code for integrating with the Solana blockchain.
*   `tests/`: Tests for the blockchain.
*   `wallet/`: The wallet implementation for signing transactions.

## Usage

To use the blockchain, you need to run the API and interact with it.

1.  **Start the API:**
    ```bash
    python api/main.py
    ```
    The API will be running at `http://localhost:5000`.

2.  **Mine a new block:**
    Use `curl` to send a GET request to the `/mine` endpoint:
    ```bash
    curl http://localhost:5000/mine
    ```

3.  **Create a new transaction:**
    Use `curl` to send a POST request to the `/transactions/new` endpoint with the transaction data:
    ```bash
    curl -X POST -H "Content-Type: application/json" -d '{
     "sender": "your-sender-address",
     "recipient": "your-recipient-address",
     "amount": 5
    }' http://localhost:5000/transactions/new
    ```

4.  **View the full chain:**
    Use `curl` to send a GET request to the `/chain` endpoint:
    ```bash
    curl http://localhost:5000/chain
    ```
