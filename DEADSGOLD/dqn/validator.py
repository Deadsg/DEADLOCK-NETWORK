
import onnxruntime
import numpy as np
import json
import os

from blockchain.transaction import Transaction

class DQNValidator:
    def __init__(self, model_path=None):
        if model_path is None:
            # Construct path relative to the project root
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            model_path = os.path.join(project_root, "DQNAgent", "Q_Layered_Network", "dqn_node_model.onnx")

        print(f"Attempting to load ONNX model from: {model_path}") # Debug print
        self.session = onnxruntime.InferenceSession(model_path)
        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name
        self.input_size = 128

    def validate_transaction(self, transaction: Transaction) -> bool:
        """
        Validates a transaction using the DQN model.
        """
        transaction_dict = {
            "sender": transaction.sender,
            "recipient": transaction.recipient,
            "amount": transaction.amount
        }
        transaction_str = json.dumps(transaction_dict)

        # Convert string to numerical vector
        processed_content = [ord(char) for char in transaction_str]

        # Pad the vector
        padded_content = np.zeros(self.input_size, dtype=np.float32)
        padded_content[:len(processed_content)] = processed_content

        # Run inference
        input_tensor = padded_content.reshape(1, -1)
        q_values = self.session.run([self.output_name], {self.input_name: input_tensor})[0]

        # The action with the highest Q-value is chosen
        action = np.argmax(q_values)

        return action == 1 # Assume action 1 is approve

    def get_status(self):
        return {
            "status": "Active",
            "model_path": self.session.get_modelmeta().graph_name,
            "input_name": self.input_name,
            "output_name": self.output_name,
        }
