import hashlib
import secrets

def hash_password(password):
    salt = secrets.token_bytes(24)
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 600000)
    return f'pbkdf2_sha256$600000${salt.hex()}${hashed.hex()}'

def verify_password(password, encoded):
    try:
        scheme, rounds, salt, expected = encoded.split('$')
        if scheme != 'pbkdf2_sha256' or int(rounds) != 600000:
            return False
        actual = hashlib.pbkdf2_hmac('sha256', password.encode(), bytes.fromhex(salt), int(rounds)).hex()
        return secrets.compare_digest(actual, expected)
    except (ValueError, TypeError, AttributeError):
        return False

# Equal-cost negative path for unknown accounts. This is not an account password.
DUMMY_HASH = hash_password(secrets.token_urlsafe(32))