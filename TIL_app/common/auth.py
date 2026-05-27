import base64
import hashlib
import hmac
import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import StrEnum
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from config import get_settings


ALGORITHM = "HS256"


class Role(StrEnum):
    USER = "USER"
    ADMIN = "ADMIN"


@dataclass
class CurrentUser:
    id: str
    role: Role

    def __str__(self):
        return f"{self.id}({self.role})"


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")


def _get_secret_key() -> str:
    try:
        return get_settings().jwt_secret
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


def _base64url_encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("utf-8")


def _base64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def create_access_token(
    payload: dict,
    role: Role,
    expires_delta: timedelta = timedelta(hours=6),
):
    header = {
        "alg": ALGORITHM,
        "typ": "JWT",
    }
    body = {
        **payload,
        "role": role.value,
        "exp": int((datetime.now(timezone.utc) + expires_delta).timestamp()),
    }

    encoded_header = _base64url_encode(
        json.dumps(header, separators=(",", ":")).encode("utf-8")
    )
    encoded_body = _base64url_encode(
        json.dumps(body, separators=(",", ":")).encode("utf-8")
    )
    signing_input = f"{encoded_header}.{encoded_body}".encode("utf-8")
    signature = hmac.new(
        _get_secret_key().encode("utf-8"),
        signing_input,
        hashlib.sha256,
    ).digest()

    return f"{encoded_header}.{encoded_body}.{_base64url_encode(signature)}"


def decode_access_token(token: str):
    try:
        encoded_header, encoded_body, encoded_signature = token.split(".")
        signing_input = f"{encoded_header}.{encoded_body}".encode("utf-8")
        expected_signature = hmac.new(
            _get_secret_key().encode("utf-8"),
            signing_input,
            hashlib.sha256,
        ).digest()
        signature = _base64url_decode(encoded_signature)

        if not hmac.compare_digest(signature, expected_signature):
            raise ValueError

        payload = json.loads(_base64url_decode(encoded_body))
        if payload.get("exp") < int(datetime.now(timezone.utc).timestamp()):
            raise ValueError

        return payload
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    payload = decode_access_token(token)

    user_id = payload.get("user_id")
    role = payload.get("role")
    if not user_id or role != Role.USER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    return CurrentUser(id=user_id, role=Role(role))