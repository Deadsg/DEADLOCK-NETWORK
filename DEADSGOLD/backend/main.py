from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from DEADSGOLD.blockchain.chain import Blockchain
from DEADSGOLD.blockchain.transaction import Transaction
from DEADSGOLD.wallet.wallet import Wallet

app = FastAPI()

# Configure CORS to allow requests from the frontend
frontend_urls_str = os.getenv("FRONTEND_URLS", "http://localhost:3000")
origins = [url.strip() for url in frontend_urls_str.split(',')]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instantiate the blockchain
blockchain = Blockchain()

class TransactionRequest(BaseModel):
    sender: str
    recipient: str
    amount: float
    private_key: str # For signing the transaction

@app.get("/")
async def read_root():
    return {"message": "Welcome to the DEADSGOLD API"}

@app.get("/blockchain/status")
async def get_blockchain_status():
    return {
        "chain_length": len(blockchain.chain),
        "last_block": blockchain.last_block.to_dict(),
        "pending_transactions": [tx.to_dict() for tx in blockchain.pending_transactions]
    }

@app.get("/wallet/{address}/balance")
async def get_wallet_balance(address: str):
    balance = blockchain.get_balance(address)
    return {"address": address, "balance": balance}

@app.post("/transaction/new")
async def new_transaction(tx_request: TransactionRequest):
    wallet = Wallet.from_private_key_hex(tx_request.private_key)

    if wallet.address != tx_request.sender:
        raise HTTPException(status_code=400, detail="Sender address does not match private key")

    transaction = Transaction(tx_request.sender, tx_request.recipient, tx_request.amount)
    transaction.sign_transaction(wallet)

    if blockchain.new_transaction(transaction):
        return {"message": "Transaction added to pending transactions"}
    else:
        raise HTTPException(status_code=400, detail="Invalid transaction")

@app.post("/mine")
async def mine_block():
    last_block = blockchain.last_block
    last_proof = last_block.nonce

    # Reward the miner
    miner_address = "DEADSGOLD_MINER_ADDRESS" # Placeholder for a persistent miner address
    reward_transaction = Transaction("0", miner_address, 1) # Reward of 1 coin
    blockchain.new_transaction(reward_transaction)

    block = blockchain.mine()
    return {
        "message": "New Block Forged",
        "index": block.index,
        "transactions": [tx.to_dict() for tx in block.transactions],
        "proof": block.nonce,
        "previous_hash": block.previous_hash,
    }

@app.post("/wallet/new")
async def create_new_wallet():
    wallet = Wallet()
    return {"public_key": wallet.address, "private_key": wallet.private_key_hex}
