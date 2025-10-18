
import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
from uuid import uuid4

# Add project root to sys.path for module imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from wallet.wallet import Wallet
from blockchain.chain import Blockchain
from blockchain.transaction import Transaction
from solders.pubkey import Pubkey
from solana_integration.client import SolanaClient

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack(fill="both", expand=True)

        private_key_b58 = tk.simpledialog.askstring("Solana Private Key", "Please enter your Solana private key (base58):")
        if not private_key_b58:
            self.master.destroy()
            return
        try:
            self.wallet = Wallet.from_solana_private_key(private_key_b58)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load wallet from private key: {e}")
            self.master.destroy()
            return
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
        self.private_key_var = tk.StringVar() # New: for private key display
        self.update_wallet_info() # Call a new method to update all wallet info

        ttk.Label(wallet_info_frame, text="Address:").grid(row=0, column=0, sticky="w")
        ttk.Entry(wallet_info_frame, textvariable=self.address_var, state="readonly").grid(row=0, column=1, sticky="ew")

        ttk.Label(wallet_info_frame, text="Balance:").grid(row=1, column=0, sticky="w")
        ttk.Entry(wallet_info_frame, textvariable=self.balance_var, state="readonly").grid(row=1, column=1, sticky="ew")

        ttk.Label(wallet_info_frame, text="Private Key:").grid(row=2, column=0, sticky="w")
        ttk.Entry(wallet_info_frame, textvariable=self.private_key_var, state="readonly", show="*").grid(row=2, column=1, sticky="ew") # show='*' for security

        ttk.Label(wallet_info_frame, text="WARNING: Keep your private key secret!", foreground="red").grid(row=3, column=0, columnspan=2, sticky="w")

        ttk.Button(wallet_info_frame, text="Update Balance", command=self.update_wallet_info).grid(row=4, column=1, sticky="e")

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

    def update_wallet_info(self):
        # Update balance
        balance = self.blockchain.get_balance(self.wallet.address)
        self.balance_var.set(str(balance))
        # Update private key display
        self.private_key_var.set(self.wallet.private_key_hex)

    def update_balance(self):
        # This method is now redundant, update_wallet_info should be called instead
        self.update_wallet_info()

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
            self.update_wallet_info() # Call update_wallet_info here
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
                block.previous_hash[-10:] if block.previous_hash else "",
                block.hash[-10:] if block.hash else "",
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

        # Miner gets 1 Deadsgold reward for mining a block
        self.blockchain.new_transaction(
            Transaction(sender="0", recipient=self.node_identifier, amount=1)
        )

        previous_hash = self.blockchain.last_block.hash
        block = self.blockchain.new_block(proof, previous_hash)

        self.update_wallet_info() # Update Deadsgold balance
        self.update_blockchain_view()

        # --- Simulated Trade for Solana ---
        deadsgold_reward = 1 # The reward for mining
        simulated_dg_to_sol_rate = 0.01 # 1 Deadsgold = 0.01 SOL (simulated)
        simulated_sol_gained = deadsgold_reward * simulated_dg_to_sol_rate

        if self.solana_keypair: # Only simulate if a Solana keypair is loaded
            # Conceptually add SOL to the displayed balance
            current_sol_balance_str = self.solana_balance_var.get().replace(" SOL", "")
            try:
                current_sol_balance = float(current_sol_balance_str) if current_sol_balance_str != "N/A" else 0.0
                new_sol_balance = current_sol_balance + simulated_sol_gained
                self.solana_balance_var.set(f"{new_sol_balance:.4f} SOL")
                messagebox.showinfo("Simulated Trade", f"Miner traded {deadsgold_reward} Deadsgold for {simulated_sol_gained:.4f} SOL (simulated).")
            except ValueError:
                messagebox.showwarning("Simulated Trade", "Could not update Solana balance after simulated trade.")
        else:
            messagebox.showwarning("Simulated Trade", "No Solana keypair loaded to receive simulated SOL.")
        # --- End Simulated Trade ---

        self.mine_button.config(state=tk.NORMAL, text="Start Mining")
        messagebox.showinfo("Success", f"New Block Forged: {block.index}")

    def create_solana_tab(self):
        solana_info_frame = ttk.LabelFrame(self.solana_frame, text="Solana Wallet")
        solana_info_frame.pack(fill="x", padx=10, pady=10)

    def create_solana_tab(self):
        # Solana Wallet Info
        solana_info_frame = ttk.LabelFrame(self.solana_frame, text="Solana Wallet Information")
        solana_info_frame.pack(fill="x", padx=10, pady=10)

        self.solana_public_key_var = tk.StringVar()
        self.solana_balance_var = tk.StringVar()
        self.solana_private_key_input_var = tk.StringVar()
        self.solana_private_key_display_var = tk.StringVar()

        ttk.Label(solana_info_frame, text="Public Key:").grid(row=0, column=0, sticky="w")
        ttk.Entry(solana_info_frame, textvariable=self.solana_public_key_var, state="readonly").grid(row=0, column=1, sticky="ew")

        ttk.Label(solana_info_frame, text="Balance:").grid(row=1, column=0, sticky="w")
        ttk.Entry(solana_info_frame, textvariable=self.solana_balance_var, state="readonly").grid(row=1, column=1, sticky="ew")

        ttk.Label(solana_info_frame, text="Private Key:").grid(row=2, column=0, sticky="w")
        self.solana_private_key_entry = ttk.Entry(solana_info_frame, textvariable=self.solana_private_key_display_var, state="readonly", show="*")
        self.solana_private_key_entry.grid(row=2, column=1, sticky="ew")

        # Buttons for key management and balance update
        button_frame = ttk.Frame(solana_info_frame)
        button_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=5)
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)

        ttk.Button(button_frame, text="Generate New Keypair", command=self.generate_solana_keypair).grid(row=0, column=0, sticky="ew", padx=2)
        ttk.Button(button_frame, text="Load Keypair from Input", command=self.load_solana_keypair_from_input).grid(row=0, column=1, sticky="ew", padx=2)
        ttk.Button(button_frame, text="Toggle Private Key", command=self.toggle_solana_private_key_visibility).grid(row=0, column=2, sticky="ew", padx=2)

        ttk.Button(solana_info_frame, text="Update Solana Balance", command=self.update_solana_balance).grid(row=4, column=0, columnspan=2, sticky="ew", pady=5)

        # New: Private Key Input (moved to its own section for clarity)
        load_key_frame = ttk.LabelFrame(self.solana_frame, text="Load Private Key")
        load_key_frame.pack(fill="x", padx=10, pady=10)
        load_key_frame.columnconfigure(1, weight=1)

        ttk.Label(load_key_frame, text="Private Key (Base58):").grid(row=0, column=0, sticky="w")
        ttk.Entry(load_key_frame, textvariable=self.solana_private_key_input_var, show="*").grid(row=0, column=1, sticky="ew")

        # Airdrop
        airdrop_frame = ttk.LabelFrame(self.solana_frame, text="Solana Airdrop (Devnet/Testnet)")
        airdrop_frame.pack(fill="x", padx=10, pady=10)
        airdrop_frame.columnconfigure(1, weight=1)

        self.airdrop_amount_var = tk.StringVar(value="1.0")
        ttk.Label(airdrop_frame, text="Amount (SOL):").grid(row=0, column=0, sticky="w")
        ttk.Entry(airdrop_frame, textvariable=self.airdrop_amount_var).grid(row=0, column=1, sticky="ew")
        ttk.Button(airdrop_frame, text="Request Airdrop", command=self.request_solana_airdrop).grid(row=1, column=0, columnspan=2, sticky="ew")

        # Transfer SOL
        transfer_sol_frame = ttk.LabelFrame(self.solana_frame, text="Transfer SOL")
        transfer_sol_frame.pack(fill="x", padx=10, pady=10)
        transfer_sol_frame.columnconfigure(1, weight=1)

        self.solana_recipient_var = tk.StringVar()
        self.solana_transfer_amount_var = tk.StringVar()

        ttk.Label(transfer_sol_frame, text="Recipient Public Key:").grid(row=0, column=0, sticky="w")
        ttk.Entry(transfer_sol_frame, textvariable=self.solana_recipient_var).grid(row=0, column=1, sticky="ew")

        ttk.Label(transfer_sol_frame, text="Amount (SOL):").grid(row=1, column=0, sticky="w")
        ttk.Entry(transfer_sol_frame, textvariable=self.solana_transfer_amount_var).grid(row=1, column=1, sticky="ew")

        ttk.Button(transfer_sol_frame, text="Transfer", command=self.transfer_solana_tokens).grid(row=2, column=0, columnspan=2, sticky="ew")

    def toggle_solana_private_key_visibility(self):
        current_show = self.solana_private_key_entry.cget("show")
        if current_show == "*":
            self.solana_private_key_entry.config(show="")
        else:
            self.solana_private_key_entry.config(show="*")

    def load_solana_keypair_from_input(self):
        private_key_str = self.solana_private_key_input_var.get()
        if not private_key_str:
            messagebox.showerror("Error", "Please enter a private key.")
            return

        try:
            from solders.keypair import Keypair
            self.solana_keypair = Keypair.from_base58_string(private_key_str)
            self.solana_public_key_var.set(str(self.solana_keypair.pubkey()))
            self.solana_private_key_display_var.set(self.solana_keypair.secret().to_base58_string()) # Corrected
            self.update_solana_balance()
            messagebox.showinfo("Solana", "Keypair loaded successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load keypair: {e}\nEnsure it is a valid Base58 encoded private key.")

    def generate_solana_keypair(self):
        from solders.keypair import Keypair
        self.solana_keypair = Keypair()
        self.solana_public_key_var.set(str(self.solana_keypair.pubkey()))
        self.solana_private_key_display_var.set(self.solana_keypair.secret().to_base58_string()) # Corrected
        self.update_solana_balance()
        messagebox.showinfo("Solana", "New Solana Keypair Generated!")

    def update_solana_balance(self):
        if self.solana_keypair:
            balance = self.solana_client.get_balance(self.solana_keypair.pubkey())
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
            signature = self.solana_client.request_airdrop(self.solana_keypair.pubkey(), amount)
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
            recipient_public_key = Pubkey.from_string(recipient_pubkey_str)
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
    root.configure(bg="black") # Set root background to black

    # Configure ttk style for a black background
    style = ttk.Style()
    style.theme_use('clam') # 'clam' theme is often easier to customize
    style.configure('TFrame', background='black')
    style.configure('TNotebook', background='black')
    style.configure('TNotebook.Tab', background='black', foreground='white')
    style.map('TNotebook.Tab', background=[('selected', '#333333')], foreground=[('selected', 'white')])
    style.configure('TLabel', background='black', foreground='white')
    style.configure('TLabelFrame', background='black', foreground='white')
    style.configure('TLabelFrame.Label', background='black', foreground='white')
    style.configure('TEntry', fieldbackground='#333333', foreground='white', insertcolor='white')
    style.configure('TButton', background='#333333', foreground='white')
    style.map('TButton', background=[('active', '#555555')])
    style.configure('Treeview', background='black', foreground='white', fieldbackground='black')
    style.map('Treeview', background=[('selected', '#555555')])
    style.configure('Treeview.Heading', background='#333333', foreground='white')

    app = Application(master=root)
    app.mainloop()
