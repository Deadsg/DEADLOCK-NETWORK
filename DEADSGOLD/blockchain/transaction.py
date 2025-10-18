
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
