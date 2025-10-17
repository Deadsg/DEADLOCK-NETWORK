
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

class Wallet:
    """
    Represents a wallet with a private/public key pair for signing transactions.
    """
    def __init__(self):
        self.private_key = ed25519.Ed25519PrivateKey.generate()
        self.public_key = self.private_key.public_key()

    @property
    def address(self) -> str:
        """
        Returns the wallet's address (the public key serialized as PEM).
        """
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).hex()

    def sign(self, data: bytes) -> bytes:
        """
        Signs the given data with the wallet's private key.
        """
        return self.private_key.sign(data)

    @staticmethod
    def verify(public_key_hex: str, signature: bytes, data: bytes) -> bool:
        """
        Verifies the signature of the given data using the public key.
        """
        try:
            public_key_bytes = bytes.fromhex(public_key_hex)
            public_key = serialization.load_pem_public_key(
                public_key_bytes,
            )
            public_key.verify(signature, data)
            return True
        except Exception:
            return False
