
import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from uuid import uuid4

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from wallet.wallet import Wallet
from blockchain.chain import Blockchain
from blockchain.transaction import Transaction
from solana_integration.client import SolanaClient

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()

        self.wallet = Wallet()
        self.blockchain = Blockchain()
        self.node_identifier = str(uuid4()).replace('-', '')
        self.solana_client = SolanaClient()
        self.solana_keypair = None

        self.create_widgets()

    def create_widgets(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill='both')

        # Create frames for each tab
        self.wallet_frame = ttk.Frame(self.notebook)
        self.blockchain_frame = ttk.Frame(self.notebook)
        self.miner_frame = ttk.Frame(self.notebook)
        self.solana_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.wallet_frame, text='Wallet')
        self.notebook.add(self.blockchain_frame, text='Blockchain')
        self.notebook.add(self.miner_frame, text='Miner')
        self.notebook.add(self.solana_frame, text='Solana')

        # Add content to the tabs
        self.create_wallet_tab()
        self.create_blockchain_tab()
        self.create_miner_tab()
        self.create_solana_tab()

    def create_wallet_tab(self):
        # Wallet Info
        wallet_info_frame = ttk.LabelFrame(self.wallet_frame, text="Wallet Information")
        wallet_info_frame.pack(fill="x", padx=10, pady=10)

        self.address_var = tk.StringVar(value=self.wallet.address)
        self.balance_var = tk.StringVar()
        self.update_balance()

        ttk.Label(wallet_info_frame, text="Address:").grid(row=0, column=0, sticky="w")
        ttk.Entry(wallet_info_frame, textvariable=self.address_var, state="readonly").grid(row=0, column=1, sticky="ew")

        ttk.Label(wallet_info_frame, text="Balance:").grid(row=1, column=0, sticky="w")
        ttk.Entry(wallet_info_frame, textvariable=self.balance_var, state="readonly").grid(row=1, column=1, sticky="ew")

        ttk.Button(wallet_info_frame, text="Update Balance", command=self.update_balance).grid(row=2, column=1, sticky="e")

        # Send Transaction
        send_frame = ttk.LabelFrame(self.wallet_frame, text="Send Transaction")
        send_frame.pack(fill="x", padx=10, pady=10)

        self.recipient_var = tk.StringVar()
        self.amount_var = tk.StringVar()

        ttk.Label(send_frame, text="Recipient:").grid(row=0, column=0, sticky="w")
        ttk.Entry(send_frame, textvariable=self.recipient_var).grid(row=0, column=1, sticky="ew")

        ttk.Label(send_frame, text="Amount:").grid(row=1, column=0, sticky="w")
        ttk.Entry(send_frame, textvariable=self.amount_var).grid(row=1, column=1, sticky="ew")

        ttk.Button(send_frame, text="Send", command=self.send_transaction).grid(row=2, column=1, sticky="e")

    def update_balance(self):
        balance = self.blockchain.get_balance(self.wallet.address)
        self.balance_var.set(str(balance))

    def send_transaction(self):
        recipient = self.recipient_var.get()
        amount_str = self.amount_var.get()

        if not recipient or not amount_str:
            messagebox.showerror("Error", "Recipient and amount are required.")
            return

        try:
            amount = float(amount_str)
        except ValueError:
            messagebox.showerror("Error", "Invalid amount.")
            return

        transaction = Transaction(sender=self.wallet.address, recipient=recipient, amount=amount)
        signature = self.wallet.sign(transaction.to_bytes())
        transaction.signature = signature

        if self.blockchain.new_transaction(transaction):
            messagebox.showinfo("Success", "Transaction sent successfully!")
            self.recipient_var.set("")
            self.amount_var.set("")
            self.update_balance()
        else:
            messagebox.showerror("Error", "Transaction failed validation and was rejected.")

    def create_blockchain_tab(self):
        blockchain_frame = ttk.Frame(self.blockchain_frame)
        blockchain_frame.pack(fill="both", expand=True)

        self.blockchain_tree = ttk.Treeview(blockchain_frame)
        self.blockchain_tree["columns"] = ("index", "timestamp", "transactions", "previous_hash", "hash", "nonce")

        self.blockchain_tree.column("#0", width=0, stretch=tk.NO)
        self.blockchain_tree.column("index", anchor=tk.W, width=50)
        self.blockchain_tree.column("timestamp", anchor=tk.W, width=150)
        self.blockchain_tree.column("transactions", anchor=tk.W, width=400)
        self.blockchain_tree.column("previous_hash", anchor=tk.W, width=150)
        self.blockchain_tree.column("hash", anchor=tk.W, width=150)
        self.blockchain_tree.column("nonce", anchor=tk.W, width=50)

        self.blockchain_tree.heading("#0", text="", anchor=tk.W)
        self.blockchain_tree.heading("index", text="Index", anchor=tk.W)
        self.blockchain_tree.heading("timestamp", text="Timestamp", anchor=tk.W)
        self.blockchain_tree.heading("transactions", text="Transactions", anchor=tk.W)
        self.blockchain_tree.heading("previous_hash", text="Previous Hash", anchor=tk.W)
        self.blockchain_tree.heading("hash", text="Hash", anchor=tk.W)
        self.blockchain_tree.heading("nonce", text="Nonce", anchor=tk.W)

        self.blockchain_tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(blockchain_frame, orient="vertical", command=self.blockchain_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.blockchain_tree.configure(yscrollcommand=scrollbar.set)

        refresh_button = ttk.Button(self.blockchain_frame, text="Refresh", command=self.update_blockchain_view)
        refresh_button.pack(pady=10)

        self.update_blockchain_view()

    def update_blockchain_view(self):
        for i in self.blockchain_tree.get_children():
            self.blockchain_tree.delete(i)

        for block in self.blockchain.chain:
            transactions_str = ""
            for tx in block.transactions:
                transactions_str += f"Sender: {tx.sender[-10:]}, Recipient: {tx.recipient[-10:]}, Amount: {tx.amount}\n"

            self.blockchain_tree.insert("", tk.END, values=(
                block.index,
                block.timestamp,
                transactions_str,
                block.previous_hash[-10:],
                block.hash[-10:],
                block.nonce
            ))

    def create_miner_tab(self):
        miner_frame = ttk.Frame(self.miner_frame)
        miner_frame.pack(fill="x", padx=10, pady=10)

        self.mine_button = ttk.Button(miner_frame, text="Start Mining", command=self.start_mining_thread)
        self.mine_button.pack()

    def start_mining_thread(self):
        self.mine_button.config(state=tk.DISABLED, text="Mining...")
        mining_thread = threading.Thread(target=self.mine)
        mining_thread.start()

    def mine(self):
        last_block = self.blockchain.last_block
        last_proof = last_block.nonce
        proof = self.blockchain.proof_of_work(last_proof)

        self.blockchain.new_transaction(
            Transaction(sender="0", recipient=self.node_identifier, amount=1)
        )

        previous_hash = self.blockchain.last_block.hash
        block = self.blockchain.new_block(proof, previous_hash)

        self.update_balance()
        self.update_blockchain_view()
        self.mine_button.config(state=tk.NORMAL, text="Start Mining")
        messagebox.showinfo("Success", f"New Block Forged: {block.index}")

    def create_solana_tab(self):
        solana_info_frame = ttk.LabelFrame(self.solana_frame, text="Solana Wallet")
        solana_info_frame.pack(fill="x", padx=10, pady=10)

        self.solana_public_key_var = tk.StringVar()
        self.solana_balance_var = tk.StringVar()

        ttk.Label(solana_info_frame, text="Public Key:").grid(row=0, column=0, sticky="w")
        ttk.Entry(solana_info_frame, textvariable=self.solana_public_key_var, state="readonly").grid(row=0, column=1, sticky="ew")

        ttk.Label(solana_info_frame, text="Balance:").grid(row=1, column=0, sticky="w")
        ttk.Entry(solana_info_frame, textvariable=self.solana_balance_var, state="readonly").grid(row=1, column=1, sticky="ew")

        ttk.Button(solana_info_frame, text="Generate New Keypair", command=self.generate_solana_keypair).grid(row=2, column=0, sticky="w")
        ttk.Button(solana_info_frame, text="Update Solana Balance", command=self.update_solana_balance).grid(row=2, column=1, sticky="e")

        # Airdrop
        airdrop_frame = ttk.LabelFrame(self.solana_frame, text="Solana Airdrop (Devnet/Testnet)")
        airdrop_frame.pack(fill="x", padx=10, pady=10)

        self.airdrop_amount_var = tk.StringVar(value="1.0")
        ttk.Label(airdrop_frame, text="Amount (SOL):").grid(row=0, column=0, sticky="w")
        ttk.Entry(airdrop_frame, textvariable=self.airdrop_amount_var).grid(row=0, column=1, sticky="ew")
        ttk.Button(airdrop_frame, text="Request Airdrop", command=self.request_solana_airdrop).grid(row=1, column=1, sticky="e")

        # Transfer SOL
        transfer_sol_frame = ttk.LabelFrame(self.solana_frame, text="Transfer SOL")
        transfer_sol_frame.pack(fill="x", padx=10, pady=10)

        self.solana_recipient_var = tk.StringVar()
        self.solana_transfer_amount_var = tk.StringVar()

        ttk.Label(transfer_sol_frame, text="Recipient Public Key:").grid(row=0, column=0, sticky="w")
        ttk.Entry(transfer_sol_frame, textvariable=self.solana_recipient_var).grid(row=0, column=1, sticky="ew")

        ttk.Label(transfer_sol_frame, text="Amount (SOL):").grid(row=1, column=0, sticky="w")
        ttk.Entry(transfer_sol_frame, textvariable=self.solana_transfer_amount_var).grid(row=1, column=1, sticky="ew")

        ttk.Button(transfer_sol_frame, text="Transfer", command=self.transfer_solana_tokens).grid(row=2, column=1, sticky="e")

    def generate_solana_keypair(self):
        self.solana_keypair = self.solana_client.generate_keypair()
        self.solana_public_key_var.set(str(self.solana_keypair.public_key))
        self.update_solana_balance()
        messagebox.showinfo("Solana", "New Solana Keypair Generated!")

    def update_solana_balance(self):
        if self.solana_keypair:
            balance = self.solana_client.get_balance(self.solana_keypair.public_key)
            self.solana_balance_var.set(f"{balance:.4f} SOL")
        else:
            self.solana_balance_var.set("N/A")

    def request_solana_airdrop(self):
        if not self.solana_keypair:
            messagebox.showerror("Error", "Please generate a Solana keypair first.")
            return

        try:
            amount = float(self.airdrop_amount_var.get())
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Invalid airdrop amount.")
            return

        try:
            signature = self.solana_client.request_airdrop(self.solana_keypair.public_key, amount)
            messagebox.showinfo("Solana Airdrop", f"Airdrop requested! Signature: {signature}")
            self.update_solana_balance()
        except Exception as e:
            messagebox.showerror("Error", f"Airdrop failed: {e}")

    def transfer_solana_tokens(self):
        if not self.solana_keypair:
            messagebox.showerror("Error", "Please generate a Solana keypair first.")
            return

        recipient_pubkey_str = self.solana_recipient_var.get()
        amount_str = self.solana_transfer_amount_var.get()

        if not recipient_pubkey_str or not amount_str:
            messagebox.showerror("Error", "Recipient and amount are required.")
            return

        try:
            recipient_public_key = PublicKey(recipient_pubkey_str)
        except ValueError:
            messagebox.showerror("Error", "Invalid recipient public key.")
            return

        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Invalid transfer amount.")
            return

        try:
            signature = self.solana_client.transfer_sol(self.solana_keypair, recipient_public_key, amount)
            messagebox.showinfo("Solana Transfer", f"Transfer successful! Signature: {signature}")
            self.update_solana_balance()
            self.solana_recipient_var.set("")
            self.solana_transfer_amount_var.set("")
        except Exception as e:
            messagebox.showerror("Error", f"Transfer failed: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("DEADSGOLD GUI")
    app = Application(master=root)
    app.mainloop()
