import bcrypt

def hash_password(plain_password: str) -> bytes:
    """Hash the plain text password."""
    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt())


def verify_password(plain_password: str, hashed_password: bytes) -> bool:
    """Verify a password against a given hash."""
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password)



