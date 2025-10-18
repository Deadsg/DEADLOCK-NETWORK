
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import base64
import os
import base58
from solders.keypair import Keypair

class Wallet:
    """
    Represents a wallet with a private/public key pair for signing transactions.
    """

    _SALT_SIZE = 16
    _ITERATIONS = 100000

    def _derive_key(self, password: str, salt: bytes) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=self._ITERATIONS,
            backend=default_backend()
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))

    def __init__(self, password: str = None, encrypted_private_key_data: bytes = None, salt: bytes = None, private_key: ed25519.Ed25519PrivateKey = None):
        self._private_key = private_key
        self._encrypted_private_key_data = None
        self._salt = None

        if encrypted_private_key_data and salt and password:
            self._encrypted_private_key_data = encrypted_private_key_data
            self._salt = salt
            self.decrypt_private_key(password)
        elif not self._private_key:
            self._private_key = ed25519.Ed25519PrivateKey.generate()
            if password:
                self.encrypt_private_key(password)

        if self._private_key:
            self.public_key = self._private_key.public_key()

    @classmethod
    def from_solana_private_key(cls, private_key_b58: str):
        private_key_bytes = base58.b58decode(private_key_b58)
        private_key = ed25519.Ed25519PrivateKey.from_private_bytes(private_key_bytes)
        return cls(private_key=private_key)

    @classmethod
    def from_mnemonic(cls, mnemonic_phrase: str):
        # Derive Solana Keypair from mnemonic
        solana_keypair = Keypair.from_seed_phrase_and_passphrase(mnemonic_phrase, "") # No passphrase for simplicity
        
        # Extract private key bytes from Solana Keypair
        private_key_bytes = solana_keypair.secret().to_bytes()
        
        # Create ed25519 private key from bytes
        private_key = ed25519.Ed25519PrivateKey.from_private_bytes(private_key_bytes)
        return cls(private_key=private_key)

    @property
    def private_key(self):
        return self._private_key

    def encrypt_private_key(self, password: str) -> None:
        if not self._private_key:
            raise ValueError("No private key to encrypt.")

        self._salt = os.urandom(self._SALT_SIZE)
        key = self._derive_key(password, self._salt)
        f = Fernet(key)

        serialized_private_key = self._private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption()
        )
        self._encrypted_private_key_data = f.encrypt(serialized_private_key)
        self._private_key = None

    def decrypt_private_key(self, password: str) -> None:
        if not self._encrypted_private_key_data or not self._salt:
            raise ValueError("No encrypted private key data or salt to decrypt.")

        key = self._derive_key(password, self._salt)
        f = Fernet(key)

        try:
            decrypted_private_key_bytes = f.decrypt(self._encrypted_private_key_data)
            self._private_key = ed25519.Ed25519PrivateKey.from_private_bytes(decrypted_private_key_bytes)
        except Exception as e:
            self._private_key = None
            raise ValueError(f"Failed to decrypt private key: {e}")

    @property
    def address(self) -> str:
        """
        Returns the wallet's address (the public key in base58).
        """
        if not self.public_key:
            raise ValueError("Public key not available.")
        return base58.b58encode(self.public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )).decode('utf-8')

    @property
    def private_key_hex(self) -> str:
        """
        Returns the wallet's private key serialized as PEM and then hex-encoded.
        """
        if not self._private_key:
            raise ValueError("Private key not loaded or decrypted.")
        return self._private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).hex()

    def sign(self, data: bytes) -> bytes:
        """
        Signs the given data with the wallet's private key.
        """
        if not self._private_key:
            raise ValueError("Private key not loaded or decrypted.")
        return self._private_key.sign(data)

    @staticmethod
    def verify(public_key_b58: str, signature: bytes, data: bytes) -> bool:
        """
        Verifies the signature of the given data using the public key.
        """
        try:
            public_key_bytes = base58.b58decode(public_key_b58)
            public_key = ed25519.Ed25519PublicKey.from_public_bytes(public_key_bytes)
            public_key.verify(signature, data)
            return True
        except Exception:
            return False
