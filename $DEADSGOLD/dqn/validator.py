
import onnxruntime
import numpy as np
import json
import os

from blockchain.transaction import Transaction

class DQNValidator:
    def __init__(self, model_path="DQNAgent/Q_Layered_Network/dqn_node_model.onnx"):
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
