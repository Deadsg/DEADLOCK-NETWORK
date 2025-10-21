
import sys
import os
import multiprocessing
from flask import Flask, jsonify
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solana.rpc.api import Client
from spl.token.client import Token

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from miner.miner import main as mine_main, TOKEN_MINT

app = Flask(__name__)

# Global variable to hold the mining process
mining_process = None

@app.route('/start-miner', methods=['POST'])
def start_miner():
    global mining_process
    if mining_process and mining_process.is_alive():
        return jsonify({'status': 'Miner is already running.'}), 400

    mining_process = multiprocessing.Process(target=mine_main)
    mining_process.start()

    return jsonify({'status': 'Miner started.'})

@app.route('/stop-miner', methods=['POST'])
def stop_miner():
    global mining_process
    if not mining_process or not mining_process.is_alive():
        return jsonify({'status': 'Miner is not running.'}), 400

    mining_process.terminate()
    mining_process.join()
    mining_process = None

    return jsonify({'status': 'Miner stopped.'})

@app.route('/status', methods=['GET'])
def status():
    global mining_process
    miner_running = mining_process and mining_process.is_alive()

    try:
        # Load keypair from file
        with open("miner_keypair.json", "r") as f:
            miner_keypair = Keypair.from_json(f.read())
        miner_address = str(miner_keypair.pubkey())

        # Replace with your RPC endpoint
        http_client = Client("https://api.devnet.solana.com")
        
        # Get the associated token account address
        from spl.token.instructions import get_associated_token_address

        ata_address = get_associated_token_address(miner_keypair.pubkey(), TOKEN_MINT)

        # Get balance
        balance_response = http_client.get_token_account_balance(ata_address)
        balance = balance_response.value.ui_amount_string
    except Exception as e:
        miner_address = "Unknown"
        balance = f"Error fetching balance: {e}"


    return jsonify({
        'miner_running': miner_running,
        'miner_pid': mining_process.pid if miner_running else None,
        'miner_address': miner_address,
        'balance': balance
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
