"""Unit tests for app.core.security."""

from datetime import timedelta

import pytest
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
    get_password_hash,
    verify_password,
)
from fastapi import HTTPException


class TestPasswordHashing:
    def test_hash_is_not_plaintext(self):
        hashed = get_password_hash("mysecret")
        assert hashed != "mysecret"

    def test_verify_correct_password(self):
        hashed = get_password_hash("correctpassword")
        assert verify_password("correctpassword", hashed) is True

    def test_verify_wrong_password(self):
        hashed = get_password_hash("correctpassword")
        assert verify_password("wrongpassword", hashed) is False

    def test_same_password_different_hashes(self):
        h1 = get_password_hash("password")
        h2 = get_password_hash("password")
        assert h1 != h2

    def test_empty_password_can_be_hashed(self):
        hashed = get_password_hash("")
        assert verify_password("", hashed) is True

    def test_unicode_password(self):
        pw = "pässwörد123"
        hashed = get_password_hash(pw)
        assert verify_password(pw, hashed) is True

    def test_long_password(self):
        pw = "a" * 200
        hashed = get_password_hash(pw)
        assert verify_password(pw, hashed) is True


class TestAccessToken:
    def test_create_and_decode(self):
        token = create_access_token({"sub": "user@example.com"})
        token_data = decode_access_token(token)
        assert token_data.email == "user@example.com"

    def test_custom_expiry(self):
        token = create_access_token(
            {"sub": "user@example.com"}, expires_delta=timedelta(minutes=5)
        )
        token_data = decode_access_token(token)
        assert token_data.email == "user@example.com"

    def test_missing_sub_raises_401(self):
        token = create_access_token({"data": "no_sub_field"})
        with pytest.raises(HTTPException) as exc:
            decode_access_token(token)
        assert exc.value.status_code == 401

    def test_garbage_token_raises_401(self):
        with pytest.raises(HTTPException) as exc:
            decode_access_token("not.a.jwt.token")
        assert exc.value.status_code == 401

    def test_expired_token_raises_401(self):
        token = create_access_token(
            {"sub": "user@example.com"}, expires_delta=timedelta(seconds=-1)
        )
        with pytest.raises(HTTPException) as exc:
            decode_access_token(token)
        assert exc.value.status_code == 401

    def test_refresh_token_rejected_as_access(self):
        refresh = create_refresh_token({"sub": "user@example.com"})
        with pytest.raises(HTTPException) as exc:
            decode_access_token(refresh)
        assert exc.value.status_code == 401

    def test_empty_string_raises_401(self):
        with pytest.raises(HTTPException) as exc:
            decode_access_token("")
        assert exc.value.status_code == 401


class TestRefreshToken:
    def test_create_and_decode(self):
        token = create_refresh_token({"sub": "user@example.com"})
        token_data = decode_refresh_token(token)
        assert token_data.email == "user@example.com"

    def test_access_token_rejected_as_refresh(self):
        access = create_access_token({"sub": "user@example.com"})
        with pytest.raises(HTTPException) as exc:
            decode_refresh_token(access)
        assert exc.value.status_code == 401

    def test_garbage_token_raises_401(self):
        with pytest.raises(HTTPException) as exc:
            decode_refresh_token("garbage.token.here")
        assert exc.value.status_code == 401

    def test_expired_refresh_token_raises_401(self):
        import time

        from app.core.security import ALGORITHM, SECRET_KEY
        from jose import jwt

        payload = {
            "sub": "user@example.com",
            "type": "refresh",
            "exp": int(time.time()) - 10,
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        with pytest.raises(HTTPException) as exc:
            decode_refresh_token(token)
        assert exc.value.status_code == 401

    def test_missing_sub_raises_401(self):
        token = create_refresh_token({"data": "no_sub"})
        with pytest.raises(HTTPException) as exc:
            decode_refresh_token(token)
        assert exc.value.status_code == 401
