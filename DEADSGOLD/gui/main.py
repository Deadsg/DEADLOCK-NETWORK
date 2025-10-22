import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QLineEdit, QTextEdit
from PySide6.QtGui import QColor, QPalette
from PySide6.QtCore import Qt, QTimer

from gui.deadsgold_client import DeadsgoldClient

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DEADSGOLD Network")
        self.setGeometry(100, 100, 1000, 700)

        self.deadsgold_client = DeadsgoldClient()

        self.setup_ui()
        self.apply_dark_theme()
        self.start_auto_update()

    def setup_ui(self):
        main_layout = QVBoxLayout()

        # Blockchain Status
        blockchain_layout = QHBoxLayout()
        self.block_height_label = QLabel("Block Height: N/A")
        self.last_block_hash_label = QLabel("Last Block Hash: N/A")
        self.difficulty_label = QLabel("Difficulty: N/A")
        blockchain_layout.addWidget(self.block_height_label)
        blockchain_layout.addWidget(self.last_block_hash_label)
        blockchain_layout.addWidget(self.difficulty_label)
        main_layout.addLayout(blockchain_layout)

        # Wallet Section
        wallet_layout = QVBoxLayout()
        wallet_layout.addWidget(QLabel("--- Wallet ---"))
        self.wallet_address_label = QLabel(f"Address: {self.deadsgold_client.get_wallet_address()}")
        self.wallet_balance_label = QLabel(f"Balance: {self.deadsgold_client.get_wallet_balance()} ORE")
        wallet_layout.addWidget(self.wallet_address_label)
        wallet_layout.addWidget(self.wallet_balance_label)

        send_tx_layout = QHBoxLayout()
        self.recipient_input = QLineEdit()
        self.recipient_input.setPlaceholderText("Recipient Address")
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Amount")
        self.send_button = QPushButton("Send ORE")
        self.send_button.clicked.connect(self.send_transaction)
        send_tx_layout.addWidget(self.recipient_input)
        send_tx_layout.addWidget(self.amount_input)
        send_tx_layout.addWidget(self.send_button)
        wallet_layout.addLayout(send_tx_layout)
        main_layout.addLayout(wallet_layout)

        # Miner Controls
        miner_layout = QVBoxLayout()
        miner_layout.addWidget(QLabel("--- Miner ---"))
        miner_buttons_layout = QHBoxLayout()
        self.start_mining_button = QPushButton("Start Mining")
        self.start_mining_button.clicked.connect(self.start_mining)
        self.stop_mining_button = QPushButton("Stop Mining")
        self.stop_mining_button.clicked.connect(self.stop_mining)
        miner_buttons_layout.addWidget(self.start_mining_button)
        miner_buttons_layout.addWidget(self.stop_mining_button)
        miner_layout.addLayout(miner_buttons_layout)
        self.mining_status_label = QLabel("Mining Status: Idle")
        miner_layout.addWidget(self.mining_status_label)
        main_layout.addLayout(miner_layout)

        # DQN Status
        dqn_layout = QVBoxLayout()
        dqn_layout.addWidget(QLabel("--- DQN Agent ---"))
        self.dqn_status_label = QLabel(f"Status: {self.deadsgold_client.get_dqn_status()['status']}")
        self.dqn_model_label = QLabel(f"Model Version: {self.deadsgold_client.get_dqn_status()['model_version']}")
        dqn_layout.addWidget(self.dqn_status_label)
        dqn_layout.addWidget(self.dqn_model_label)
        main_layout.addLayout(dqn_layout)

        self.setLayout(main_layout)

    def apply_dark_theme(self):
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(30, 30, 30)) # Dark background
        palette.setColor(QPalette.WindowText, QColor(200, 200, 200)) # Light text
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(30, 30, 30))
        palette.setColor(QPalette.ToolTipBase, QColor(200, 200, 200))
        palette.setColor(QPalette.ToolTipText, QColor(200, 200, 200))
        palette.setColor(QPalette.Text, QColor(200, 200, 200))
        palette.setColor(QPalette.Button, QColor(50, 50, 50))
        palette.setColor(QPalette.ButtonText, QColor(200, 200, 200))
        palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
        self.setPalette(palette)

    def start_auto_update(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(1000) # Update every 1 second

    def update_ui(self):
        # Update Blockchain Status
        status = self.deadsgold_client.get_blockchain_status()
        self.block_height_label.setText(f"Block Height: {status['block_height']}")
        self.last_block_hash_label.setText(f"Last Block Hash: {status['last_block_hash'][:10]}...")
        self.difficulty_label.setText(f"Difficulty: {status['difficulty']}")

        # Update Wallet Balance
        self.wallet_balance_label.setText(f"Balance: {self.deadsgold_client.get_wallet_balance()} ORE")

        # Update DQN Status (if dynamic)
        dqn_status = self.deadsgold_client.get_dqn_status()
        self.dqn_status_label.setText(f"Status: {dqn_status['status']}")
        self.dqn_model_label.setText(f"Model Version: {dqn_status['model_version']}")

    def send_transaction(self):
        recipient = self.recipient_input.text()
        amount_str = self.amount_input.text()
        try:
            amount = float(amount_str)
            if self.deadsgold_client.send_transaction(recipient, amount):
                print(f"Transaction sent to {recipient} for {amount} ORE")
                self.recipient_input.clear()
                self.amount_input.clear()
                self.update_ui() # Update balance immediately
            else:
                print("Transaction failed!")
        except ValueError:
            print("Invalid amount. Please enter a number.")

    def start_mining(self):
        if self.deadsgold_client.start_mining(callback=self.update_mining_status):
            self.mining_status_label.setText("Mining Status: Running...")
            self.start_mining_button.setEnabled(False)
            self.stop_mining_button.setEnabled(True)

    def stop_mining(self):
        if self.deadsgold_client.stop_mining():
            self.mining_status_label.setText("Mining Status: Idle")
            self.start_mining_button.setEnabled(True)
            self.stop_mining_button.setEnabled(False)

    def update_mining_status(self, block_index, block_hash, difficulty):
        # This callback is called from the mining thread, so update UI safely
        self.block_height_label.setText(f"Block Height: {block_index}")
        self.last_block_hash_label.setText(f"Last Block Hash: {block_hash[:10]}...")
        self.difficulty_label.setText(f"Difficulty: {difficulty}")
        self.mining_status_label.setText(f"Mining Status: Block {block_index} found!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())