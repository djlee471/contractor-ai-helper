import os
import hmac
import hashlib
import secrets
from base64 import urlsafe_b64encode
from cryptography.fernet import Fernet

# ==========================================
# CONFIG
# ==========================================

ACCESS_CODE_KEY_PATH = os.getenv("ACCESS_CODE_KEY_PATH")
ACCESS_CODE_KEY_VERSION = int(os.getenv("ACCESS_CODE_KEY_VERSION", "1"))

# Allowed characters (no O, 0, I, 1, L)
ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"


# ==========================================
# KEY LOADING
# ==========================================

def _load_master_key() -> bytes:
    if not ACCESS_CODE_KEY_PATH:
        raise RuntimeError("ACCESS_CODE_KEY_PATH not set")

    with open(ACCESS_CODE_KEY_PATH, "r") as f:
        hex_key = f.read().strip()

    return bytes.fromhex(hex_key)


def _derive_fernet_key(master_key: bytes) -> bytes:
    """
    Fernet requires a 32-byte base64 key.
    We'll hash the master key to ensure proper length,
    then base64-encode it.
    """
    digest = hashlib.sha256(master_key).digest()
    return urlsafe_b64encode(digest)


def _get_fernet() -> Fernet:
    master_key = _load_master_key()
    fernet_key = _derive_fernet_key(master_key)
    return Fernet(fernet_key)


# ==========================================
# ACCESS CODE GENERATION
# ==========================================

def generate_access_code(length: int = 8) -> str:
    return "".join(secrets.choice(ALPHABET) for _ in range(length))


def normalize_access_code(code: str) -> str:
    if not code:
        return ""
    return code.strip().replace("-", "").replace(" ", "").upper()


# ==========================================
# STORAGE TRANSFORMS
# ==========================================

def compute_hmac(code: str) -> str:
    master_key = _load_master_key()
    normalized = normalize_access_code(code).encode("utf-8")

    return hmac.new(master_key, normalized, hashlib.sha256).hexdigest()


def encrypt_code(code: str) -> str:
    f = _get_fernet()
    normalized = normalize_access_code(code).encode("utf-8")
    return f.encrypt(normalized).decode("utf-8")


def decrypt_code(token: str) -> str:
    f = _get_fernet()
    return f.decrypt(token.encode("utf-8")).decode("utf-8")
