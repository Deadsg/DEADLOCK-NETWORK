
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QTextEdit, QLineEdit
from PyQt5.QtCore import QThread, pyqtSignal
import subprocess
import json

class MinerThread(QThread):
    output_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()

    def __init__(self, miner_command):
        super().__init__()
        self.miner_command = miner_command
        self.process = None

    def run(self):
        try:
            self.process = subprocess.Popen(
                self.miner_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                cwd="DEADSGOLD"
            )
            for line in iter(self.process.stdout.readline, ''):
                self.output_signal.emit(line.strip())
            for line in iter(self.process.stderr.readline, ''):
                self.error_signal.emit(line.strip())
            self.process.wait()
        except Exception as e:
            self.error_signal.emit(f"Error starting miner: {e}")
        finally:
            self.finished_signal.emit()

    def stop(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()
            self.process.wait()

class MiningGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.miner_thread = None
        self.init_ui()
        self.load_token_info()

    def init_ui(self):
        self.setWindowTitle('Deadsgold Mining App')
        self.setGeometry(100, 100, 800, 600)

        self.layout = QVBoxLayout()

        # Token Info Display
        self.token_info_label = QLabel('Token Information:')
        self.layout.addWidget(self.token_info_label)

        self.token_address_label = QLabel('Address: ')
        self.layout.addWidget(self.token_address_label)
        self.token_decimals_label = QLabel('Decimals: ')
        self.layout.addWidget(self.token_decimals_label)
        self.token_pk_label = QLabel('PK: ')
        self.layout.addWidget(self.token_pk_label)
        self.token_wa_label = QLabel('WA: ')
        self.layout.addWidget(self.token_wa_label)
        self.token_account_label = QLabel('Token Account: ')
        self.layout.addWidget(self.token_account_label)

        # Miner Controls
        self.miner_command_input = QLineEdit('cargo run --release -- --rpc-url https://api.mainnet-beta.solana.com --keypair miner_keypair.json deadsgold_miner')
        self.layout.addWidget(QLabel('Miner Command:'))
        self.layout.addWidget(self.miner_command_input)

        self.start_miner_button = QPushButton('Start Miner')
        self.start_miner_button.clicked.connect(self.start_miner)
        self.layout.addWidget(self.start_miner_button)

        self.stop_miner_button = QPushButton('Stop Miner')
        self.stop_miner_button.clicked.connect(self.stop_miner)
        self.stop_miner_button.setEnabled(False)
        self.layout.addWidget(self.stop_miner_button)

        # Miner Output
        self.miner_output_label = QLabel('Miner Output:')
        self.layout.addWidget(self.miner_output_label)
        self.miner_output_text = QTextEdit()
        self.miner_output_text.setReadOnly(True)
        self.layout.addWidget(self.miner_output_text)

        self.setLayout(self.layout)

    def load_token_info(self):
        try:
            # Assuming GEMINI.md is in the parent directory of DEADSGOLD
            # and contains the info as parsed previously.
            # For now, hardcode or parse from a known location.
            # In a real app, you'd parse GEMINI.md or a config file.
            # For this example, I'll use the info from the context.
            token_info = {
                "Address": "BtyvvfnFiC599j5gcswiE13JDUGpySKZJ81BSd3cmzQG",
                "Decimals": "9",
                "PK": "[155,7,113,185,98,138,6,0,195,116,62,127,42,41,120,2,161,32,35,71,123,179,236,37,35,78,67,64,203,52,141,224,251,84,106,205,212,53,39,212,7,36,116,144,33,248,201,240,188,135,115,1,116,98,210,198,195,198,102,59,133,60,122,25]",
                "WA": "Hv5zVCQodjdXFBW3mZoMvxH2gCC79AutRdw7S4qWgnor",
                "Token Account": "Ed6PgnZDt9U6Mow4CMeQewswJ87cyRZhvnfCQRT259cM"
            }
            self.token_address_label.setText(f'Address: {token_info["Address"]}')
            self.token_decimals_label.setText(f'Decimals: {token_info["Decimals"]}')
            self.token_pk_label.setText(f'PK: {token_info["PK"]}')
            self.token_wa_label.setText(f'WA: {token_info["WA"]}')
            self.token_account_label.setText(f'Token Account: {token_info["Token Account"]}')
        except Exception as e:
            self.miner_output_text.append(f"Error loading token info: {e}")

    def start_miner(self):
        if self.miner_thread and self.miner_thread.isRunning():
            self.miner_output_text.append("Miner is already running.")
            return

        miner_command_str = self.miner_command_input.text()
        if not miner_command_str:
            self.miner_output_text.append("Miner command cannot be empty.")
            return

        self.miner_output_text.clear()
        self.miner_output_text.append("Starting miner...")
        self.start_miner_button.setEnabled(False)
        self.stop_miner_button.setEnabled(True)

        self.miner_thread = MinerThread(miner_command_str.split())
        self.miner_thread.output_signal.connect(self.update_miner_output)
        self.miner_thread.error_signal.connect(self.update_miner_output)
        self.miner_thread.finished_signal.connect(self.miner_finished)
        self.miner_thread.start()

    def stop_miner(self):
        if self.miner_thread and self.miner_thread.isRunning():
            self.miner_output_text.append("Stopping miner...")
            self.miner_thread.stop()
        else:
            self.miner_output_text.append("Miner is not running.")

    def miner_finished(self):
        self.miner_output_text.append("Miner stopped.")
        self.start_miner_button.setEnabled(True)
        self.stop_miner_button.setEnabled(False)

    def update_miner_output(self, text):
        self.miner_output_text.append(text)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = MiningGUI()
    gui.show()
    sys.exit(app.exec_())
