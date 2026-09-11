from datetime import datetime, timedelta, timezone

import pytest
from backend.auth.security import (
    ALGORITHM,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from backend.core.config import settings
from jose import JWTError
from jose import jwt as jose_jwt


def test_hash_password_produces_verifiable_hash():
    h = hash_password("correct horse battery staple")
    assert h != "correct horse battery staple"
    assert verify_password("correct horse battery staple", h) is True


def test_verify_password_rejects_wrong_password():
    h = hash_password("correct horse battery staple")
    assert verify_password("wrong password", h) is False


def test_hash_password_is_salted_and_nondeterministic():
    h1 = hash_password("same-password")
    h2 = hash_password("same-password")
    assert h1 != h2
    assert verify_password("same-password", h1) is True
    assert verify_password("same-password", h2) is True


def test_hash_password_uses_bcrypt_sha256_scheme():
    # Pins the scheme choice itself — bcrypt_sha256 (not plain bcrypt)
    # avoids the 72-byte truncation footgun, see the next test.
    h = hash_password("x")
    assert h.startswith("$bcrypt-sha256$")


def test_hash_password_handles_passwords_over_bcrypts_72_byte_limit():
    """
    Regression test for the "bonus" bug found while verifying finding #11
    live: plain bcrypt rejects (or, on old bcrypt, silently truncates)
    anything over 72 bytes. bcrypt_sha256 pre-hashes with SHA-256 first
    specifically to avoid that — a long password must work end to end,
    not raise.
    """
    long_password = "x" * 200
    h = hash_password(long_password)
    assert verify_password(long_password, h) is True
    assert verify_password("x" * 199, h) is False


def test_verify_password_distinguishes_passwords_that_share_a_72_byte_prefix():
    """Would false-positive under plain bcrypt's truncate-at-72 behavior."""
    h = hash_password("a" * 100)
    assert verify_password("a" * 72 + "b" * 28, h) is False


@pytest.mark.parametrize(
    "user_id,role",
    [
        ("user-123", "student"),
        ("11111111-1111-1111-1111-111111111111", "teacher"),
        ("", "student"),
    ],
)
def test_create_and_decode_access_token_roundtrip(user_id, role):
    token = create_access_token(user_id=user_id, role=role)
    payload = decode_access_token(token)
    assert payload["sub"] == user_id
    assert payload["role"] == role
    assert "exp" in payload
    assert "iat" in payload


def test_access_token_expiry_is_one_hour_out():
    token = create_access_token(user_id="user-123", role="student")
    payload = decode_access_token(token)
    # exp/iat are JWT numeric-date claims (seconds since epoch), not
    # datetime objects, once round-tripped through encode/decode.
    assert payload["exp"] - payload["iat"] == 60 * 60


def test_decode_access_token_rejects_tampered_payload():
    """Flip a character in the payload segment — the signature no longer
    matches, so this must fail exactly like a wrong-signature forgery."""
    token = create_access_token(user_id="user-123", role="student")
    header, payload, sig = token.split(".")
    tampered_payload = ("A" if payload[0] != "A" else "B") + payload[1:]
    tampered = f"{header}.{tampered_payload}.{sig}"

    with pytest.raises(JWTError):
        decode_access_token(tampered)


def test_decode_access_token_rejects_garbage():
    with pytest.raises(JWTError):
        decode_access_token("not-a-real-token")


def test_decode_access_token_rejects_wrong_signature():
    forged = jose_jwt.encode(
        {"sub": "attacker", "role": "teacher"},
        "a-completely-different-secret-key-not-the-real-one",
        algorithm=ALGORITHM,
    )
    with pytest.raises(JWTError):
        decode_access_token(forged)


def test_decode_access_token_rejects_expired_token():
    expired_payload = {
        "sub": "user-123",
        "role": "student",
        "iat": datetime.now(timezone.utc) - timedelta(hours=2),
        "exp": datetime.now(timezone.utc) - timedelta(hours=1),
    }
    expired = jose_jwt.encode(expired_payload, settings.SECRET_KEY, algorithm=ALGORITHM)
    with pytest.raises(JWTError):
        decode_access_token(expired)


def test_decode_access_token_rejects_alg_none():
    # A classic JWT attack: a token with alg=none and no signature at all.
    # python-jose's own encoder refuses to even create one (good sign on
    # its own), so build the three segments by hand to prove decode_access_token
    # — which pins algorithms=["HS256"] — rejects it rather than accepting
    # an unsigned token.
    import base64
    import json

    def b64url(data: bytes) -> str:
        return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

    header = b64url(json.dumps({"alg": "none", "typ": "JWT"}).encode())
    payload = b64url(json.dumps({"sub": "attacker", "role": "teacher"}).encode())
    forged = f"{header}.{payload}."

    with pytest.raises(JWTError):
        decode_access_token(forged)
