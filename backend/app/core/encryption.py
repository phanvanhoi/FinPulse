"""Encrypt/decrypt sensitive data like API keys and OAuth tokens at rest."""

from cryptography.fernet import Fernet

from app.config import settings

# Derive a Fernet key from SECRET_KEY (must be 32 url-safe base64-encoded bytes)
# In production, use a dedicated encryption key via AWS KMS or similar
_key = Fernet.generate_key()  # TODO: derive from settings or KMS in production
_fernet = Fernet(_key)


def encrypt(plaintext: str) -> str:
    return _fernet.encrypt(plaintext.encode()).decode()


def decrypt(ciphertext: str) -> str:
    return _fernet.decrypt(ciphertext.encode()).decode()
