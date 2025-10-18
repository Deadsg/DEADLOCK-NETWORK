# Deadsgold Network Project Structure

This document outlines the directory structure and the likely purpose of the main components within the Deadsgold Network project, based on an analysis of the file system.

## Project Root (`/mnt/c/Users/deads/OneDrive/Documents/AGI/DEADLOCK-NETWORK/DEADSGOLD/`)

*   `README.md`: This file, providing an overview of the project structure.
*   `requirements.txt`: Lists Python dependencies required for the project.
*   `run_gui.bat`: A Windows batch script, likely used to launch the graphical user interface.

## Core Modules

### `api/`

*   `__init__.py`: Marks the directory as a Python package.
*   `main.py`: Likely contains the main entry point for the project's API server, handling requests and responses.

### `blockchain/`

*   `__init__.py`: Marks the directory as a Python package.
*   `block.py`: Defines the structure and behavior of individual blocks in the blockchain.
*   `chain.py`: Manages the blockchain itself, including adding blocks, validation, and consensus mechanisms.
*   `transaction.py`: Defines the structure and handling of transactions within the blockchain.
*   `__pycache__/`: Contains compiled Python bytecode files.

### `dqn/`

*   `__init__.py`: Marks the directory as a Python package.
*   `agent.py`: Implements the core logic of a Deep Q-Network (DQN) agent.
*   `validator.py`: Potentially validates the actions or states related to the DQN agent or its environment.
*   `__pycache__/`: Contains compiled Python bytecode files.

### `DQNAgent/`

This directory appears to be a more comprehensive and detailed implementation of the DQN agent, possibly a separate sub-project or a more advanced version.

*   `.gitignore`: Specifies files and directories to be ignored by Git.
*   `DQNAgent.pyproj`, `DQNAgent.sln`: Project and solution files, suggesting a Visual Studio or similar IDE project setup.
*   `Q_Loop_Agent.py`, `Q_Loop_system.py`, `Q_Network_Phi-2.py`: Specific implementations or variations of Q-learning agents and network architectures.
*   `README.md`: A README specific to the DQNAgent sub-project.
*   `setup.py`: Used for packaging and distributing the DQNAgent module.
*   `.git/`: Git version control repository data.
*   `.github/workflows/`: GitHub Actions CI/CD workflows for Python applications.

#### `DQNAgent/DQNAgent/` (Inner Module)

*   `decisionmakingmodule.py`: Handles the agent's decision-making process.
*   `DQN_Bot.py`: Likely an executable bot leveraging the DQN agent.
*   `DQNAgent.py`: Core DQN agent implementation.
*   `integrationmodule.py`: Manages integration with other parts of the system.
*   `learningmodule.py`: Contains the learning algorithms for the DQN agent.
*   `lpmodule.py`: (Purpose unclear without content, possibly related to linear programming or specific learning paradigms).
*   `perceptionmodule.py`: Defines how the agent perceives its environment.
*   `QLAgent.py`: Another Q-learning agent implementation.
*   `QNetwork.py`: Defines the neural network architecture for the Q-function.
*   `reasoningmodule.py`: Handles the agent's reasoning capabilities.
*   `rlmodule.py`: Reinforcement learning utilities.
*   `__pycache__/`: Compiled Python bytecode files.

#### `DQNAgent/Q_Layered_Network/`

*   `dqn_llm_logs.log`, `mistral_dqn_logs.log`: Log files, possibly from training or running DQN models with LLMs.
*   `DQN_LLM_Test_Data.py`, `DQN_LLM.py`: Suggests integration of DQN with Large Language Models (LLMs).
*   `DQN_Node_Agent.py`: A DQN agent specifically designed for node operations.
*   `dqn_node_model.onnx`: An ONNX format model file, likely a pre-trained DQN model for node agents.
*   `DQN_TRANS_LOADER.py`: Likely handles loading and transforming data for DQN training.
*   `Layered_DQN.py`: Implements a layered DQN architecture.
*   `Reasoning_.py`: Further reasoning logic.
*   `requirements.txt`: Dependencies specific to this layered network.
*   `training_data/`: Contains data and scripts (`Agent_Trainer.py`, `test_data.json`, `training_data.json`) for training these advanced DQN models.

#### `DQNAgent/ref/`

*   Contains PDF research papers, likely references for the DQN and AI implementations.

#### `DQNAgent/src/`

*   A source directory, mirroring some of the files in `DQNAgent/DQNAgent/` and `DQNAgent/Q_Layered_Network/`, possibly for a cleaner project structure or deployment.

### `gui/`

*   `main.py`: The main script for the graphical user interface.
*   `.venv/`: A Python virtual environment for the GUI, containing its specific dependencies.

### `miner/`

*   `__init__.py`: Marks the directory as a Python package.
*   `miner.py`: Implements the logic for the blockchain miner.

### `node/`

*   `__init__.py`: Marks the directory as a Python package.
*   `node.py`: Implements the logic for a blockchain network node.

### `solana_integration/`

*   `__init__.py`: Marks the directory as a Python package.
*   `client.py`: Contains code for interacting with the Solana blockchain (e.g., sending transactions, querying data).
*   `__pycache__/`: Compiled Python bytecode files.

### `solana_program_example/`

*   `Anchor.toml`: Configuration file for Anchor, a framework for Solana smart contracts.
*   `programs/hello_world/src/lib.rs`: An example Solana smart contract written in Rust.

### `tests/`

*   `__init__.py`: Marks the directory as a Python package.
*   `test_blockchain.py`: Contains unit or integration tests for the blockchain components.
*   `__pycache__/`: Compiled Python bytecode files.

### `wallet/`

*   `__init__.py`: Marks the directory as a Python package.
*   `wallet.py`: Implements the logic for managing user wallets, including key generation and transaction signing.
*   `__pycache__/`: Compiled Python bytecode files.
