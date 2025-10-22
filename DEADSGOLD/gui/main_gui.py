import sys
import time

import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QTextEdit, QGroupBox
)
from PySide6.QtCore import QTimer, Signal, QObject

from gui.deadsgold_client import DeadsgoldClient

class WorkerSignals(QObject):
    mining_update = Signal(int, str, int)

class DeadsgoldGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.client = DeadsgoldClient()
        self.init_ui()
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_status)
        self.update_timer.start(1000) # Update every 1 second

        self.worker_signals = WorkerSignals()
        self.worker_signals.mining_update.connect(self.on_mining_update)

    def init_ui(self):
        self.setWindowTitle("DEADSGOLD Miner")
        self.setGeometry(100, 100, 800, 600)

        # Apply dark theme stylesheet
        self.setStyleSheet("""
            QWidget {
                background-color: #212121; /* Dark grey background */
                color: #E0E0E0; /* Light grey text */
            }
            QGroupBox {
                background-color: #212121;
                color: #E0E0E0;
                border: 1px solid #424242; /* Slightly lighter border */
                margin-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 3px;
                color: #E0E0E0;
            }
            QLabel {
                color: #E0E0E0;
            }
            QPushButton {
                background-color: #424242; /* Medium grey button */
                color: #E0E0E0;
                border: 1px solid #616161;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #616161; /* Lighter grey on hover */
            }
            QPushButton:pressed {
                background-color: #757575; /* Even lighter grey when pressed */
            }
            QLineEdit {
                background-color: #303030; /* Darker input field */
                color: #E0E0E0;
                border: 1px solid #424242;
                padding: 3px;
            }
            QTextEdit {
                background-color: #303030;
                color: #E0E0E0;
                border: 1px solid #424242;
            }
        """)

        self.create_widgets()

        main_layout = QVBoxLayout()

        # Blockchain Status Group
        blockchain_group = QGroupBox("Blockchain Status")
        blockchain_layout = QVBoxLayout()
        self.block_height_label = QLabel("Block Height: -")
        self.last_block_hash_label = QLabel("Last Block Hash: -")
        self.difficulty_label = QLabel("Difficulty: -")
        blockchain_layout.addWidget(self.block_height_label)
        blockchain_layout.addWidget(self.last_block_hash_label)
        blockchain_layout.addWidget(self.difficulty_label)
        blockchain_group.setLayout(blockchain_layout)
        main_layout.addWidget(blockchain_group)

        # Wallet Group
        wallet_group = QGroupBox("Wallet")
        wallet_layout = QVBoxLayout()
        
        # Wallet Address Display (Public Key)
        wallet_address_layout = QHBoxLayout()
        wallet_address_label = QLabel("Address:")
        self.wallet_address_input = QLineEdit()
        self.wallet_address_input.setReadOnly(True)
        self.wallet_address_input.setText(self.client.get_wallet_address())
        wallet_address_layout.addWidget(wallet_address_label)
        wallet_address_layout.addWidget(self.wallet_address_input)
        wallet_layout.addLayout(wallet_address_layout)

        # Private Key Display
        private_key_layout = QHBoxLayout()
        private_key_label = QLabel("Private Key:")
        self.private_key_input = QLineEdit()
        self.private_key_input.setReadOnly(True)
        self.private_key_input.setEchoMode(QLineEdit.Password)
        self.private_key_input.setText(self.client.get_private_key_hex())
        self.toggle_private_key_button = QPushButton("Show")
        self.toggle_private_key_button.setCheckable(True)
        self.toggle_private_key_button.clicked.connect(self.toggle_private_key_visibility)
        private_key_layout.addWidget(private_key_label)
        private_key_layout.addWidget(self.private_key_input)
        private_key_layout.addWidget(self.toggle_private_key_button)
        wallet_layout.addLayout(private_key_layout)

        self.wallet_balance_label = QLabel("Balance: -")
        wallet_layout.addWidget(self.wallet_balance_label)

        # Wallet Actions
        wallet_actions_layout = QHBoxLayout()
        new_wallet_button = QPushButton("Generate New Wallet")
        new_wallet_button.clicked.connect(self.generate_new_wallet)
        wallet_actions_layout.addWidget(new_wallet_button)

        refresh_balance_button = QPushButton("Refresh Balance")
        refresh_balance_button.clicked.connect(self.update_status)
        wallet_actions_layout.addWidget(refresh_balance_button)

        wallet_layout.addLayout(wallet_actions_layout)

        wallet_group.setLayout(wallet_layout)
        main_layout.addWidget(wallet_group)

        # Load Wallet Group
        load_wallet_group = QGroupBox("Load Wallet")
        load_wallet_layout = QVBoxLayout()
        load_private_key_layout = QHBoxLayout()
        load_private_key_label = QLabel("Private Key (Hex):")
        self.load_private_key_input = QLineEdit()
        load_private_key_layout.addWidget(load_private_key_label)
        load_private_key_layout.addWidget(self.load_private_key_input)
        load_wallet_layout.addLayout(load_private_key_layout)

        load_wallet_button = QPushButton("Load Wallet")
        load_wallet_button.clicked.connect(self.load_wallet)
        load_wallet_layout.addWidget(load_wallet_button)
        load_wallet_group.setLayout(load_wallet_layout)
        main_layout.addWidget(load_wallet_group)

        # Mining Controls Group
        mining_group = QGroupBox("Mining Controls")
        mining_layout = QHBoxLayout()
        self.start_mining_button = QPushButton("Start Mining")
        self.start_mining_button.clicked.connect(self.start_mining)
        self.stop_mining_button = QPushButton("Stop Mining")
        self.stop_mining_button.clicked.connect(self.stop_mining)
        self.stop_mining_button.setEnabled(False)
        mining_layout.addWidget(self.start_mining_button)
        mining_layout.addWidget(self.stop_mining_button)
        mining_group.setLayout(mining_layout)
        main_layout.addWidget(mining_group)

        # Transaction Group
        transaction_group = QGroupBox("Send Transaction")
        transaction_layout = QVBoxLayout()
        recipient_layout = QHBoxLayout()
        recipient_label = QLabel("Recipient:")
        self.recipient_input = QLineEdit()
        recipient_layout.addWidget(recipient_label)
        recipient_layout.addWidget(self.recipient_input)
        transaction_layout.addLayout(recipient_layout)

        amount_layout = QHBoxLayout()
        amount_label = QLabel("Amount:")
        self.amount_input = QLineEdit()
        amount_layout.addWidget(amount_label)
        amount_layout.addWidget(self.amount_input)
        transaction_layout.addLayout(amount_layout)

        send_transaction_button = QPushButton("Send Transaction")
        send_transaction_button.clicked.connect(self.send_transaction)
        transaction_layout.addWidget(send_transaction_button)
        transaction_group.setLayout(transaction_layout)
        main_layout.addWidget(transaction_group)

        # DQN Status Group
        dqn_group = QGroupBox("DQN Validator Status")
        dqn_layout = QVBoxLayout()
        self.dqn_status_label = QLabel("Status: -")
        dqn_layout.addWidget(self.dqn_status_label)
        dqn_group.setLayout(dqn_layout)
        main_layout.addWidget(dqn_group)

        # Log Output
        log_group = QGroupBox("Log")
        log_layout = QVBoxLayout()
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        log_layout.addWidget(self.log_output)
        log_group.setLayout(log_layout)
        main_layout.addWidget(log_group)

        self.setLayout(main_layout)

        self.update_status()

    def create_widgets(self):
        # Initialize widgets here
        pass

    def update_status(self):
        # Update Blockchain Status
        blockchain_status = self.client.get_blockchain_status()
        if blockchain_status:
            self.block_height_label.setText(f"Block Height: {blockchain_status['block_height']}")
            self.last_block_hash_label.setText(f"Last Block Hash: {blockchain_status['last_block_hash']}")
            self.difficulty_label.setText(f"Difficulty: {blockchain_status['difficulty']}")
        else:
            self.log_message("Failed to fetch blockchain status.")

        # Update Wallet Balance
        balance = self.client.get_wallet_balance()
        if balance is not None:
            self.wallet_balance_label.setText(f"Balance: {balance}")
        else:
            self.log_message("Failed to fetch wallet balance.")

        # Update DQN Status
        dqn_status = self.client.get_dqn_status()
        if dqn_status:
            self.dqn_status_label.setText(f"Status: {dqn_status}")
        else:
            self.log_message("Failed to fetch DQN status.")

    def create_new_wallet(self):
        new_address = self.client.create_new_wallet()
        self.wallet_address_label.setText(f"Address: {new_address}")
        self.log_message(f"New wallet created: {new_address}")
        self.update_status()

    def start_mining(self):
        if self.client.start_mining(callback=self.worker_signals.mining_update.emit):
            self.start_mining_button.setEnabled(False)
            self.stop_mining_button.setEnabled(True)
            self.log_message("Mining started...")
        else:
            self.log_message("Mining is already running.")

    def stop_mining(self):
        if self.client.stop_mining():
            self.start_mining_button.setEnabled(True)
            self.stop_mining_button.setEnabled(False)
            self.log_message("Mining stopped.")
        else:
            self.log_message("Mining is not running.")

    def on_mining_update(self, block_index, block_hash, difficulty):
        self.log_message(f"Mined Block {block_index}: {block_hash} (Difficulty: {difficulty})")
        self.update_status()

    def send_transaction(self):
        recipient = self.recipient_input.text()
        amount_str = self.amount_input.text()
        try:
            amount = float(amount_str)
            if self.client.send_transaction(recipient, amount):
                self.log_message(f"Transaction sent to {recipient} for {amount} DEADSGOLD.")
                self.recipient_input.clear()
                self.amount_input.clear()
                self.update_status()
            else:
                self.log_message("Failed to send transaction.")
        except ValueError:
            self.log_message("Invalid amount. Please enter a number.")

    def log_message(self, message):
        self.log_output.append(f"[{time.strftime('%H:%M:%S')}] {message}")

    def toggle_private_key_visibility(self):
        if self.toggle_private_key_button.isChecked():
            self.private_key_input.setEchoMode(QLineEdit.Normal)
            self.toggle_private_key_button.setText("Hide")
        else:
            self.private_key_input.setEchoMode(QLineEdit.Password)
            self.toggle_private_key_button.setText("Show")

    def generate_new_wallet(self):
        address, private_key_hex = self.client.create_new_wallet()
        self.wallet_address_input.setText(address)
        self.private_key_input.setText(private_key_hex)
        self.log_message(f"New wallet generated: {address}")
        self.update_status()

    def load_wallet(self):
        private_key_hex = self.load_private_key_input.text()
        if private_key_hex:
            if self.client.load_wallet_from_private_key(private_key_hex):
                self.wallet_address_input.setText(self.client.get_wallet_address())
                self.private_key_input.setText(self.client.get_private_key_hex())
                self.log_message(f"Wallet loaded successfully for address: {self.client.get_wallet_address()}")
                self.load_private_key_input.clear()
                self.update_status()
            else:
                self.log_message("Failed to load wallet. Invalid private key.")
        else:
            self.log_message("Please enter a private key to load.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = DeadsgoldGUI()
    gui.show()
    sys.exit(app.exec())
