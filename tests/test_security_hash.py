from app.security import hash_password, verify_password


def test_hash_and_verify_short_password():
    pw = "Password123!"
    hashed = hash_password(pw)
    assert hashed and isinstance(hashed, str)
    assert verify_password(pw, hashed) is True
    assert verify_password("wrong", hashed) is False


def test_hash_and_verify_long_password_80_bytes():
    # bcrypt has a 72-byte limit; our context includes bcrypt_sha256 fallback
    # Build a long password >72 bytes to ensure hashing still works
    pw = "x" * 80
    hashed = hash_password(pw)
    assert verify_password(pw, hashed) is True
