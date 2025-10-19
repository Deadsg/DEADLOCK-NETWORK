
from dataclasses import dataclass

@dataclass
class Transaction:
    sender: str
    recipient: str
    amount: float
    signature: bytes = None

    def to_bytes(self) -> bytes:
        """
        Serializes the transaction to bytes for signing.
        """
        return f'{self.sender}{self.recipient}{self.amount}'.encode()

    def to_dict(self):
        """
        Returns a dictionary representation of the transaction.
        """
        return {
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": self.amount,
            "signature": self.signature.hex() if self.signature else None # Convert bytes to hex string for JSON serialization
        }
