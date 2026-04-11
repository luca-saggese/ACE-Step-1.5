"""Bearer-token authentication dependency."""

from __future__ import annotations

from typing import Annotated, Optional

from fastapi import Depends, Header, HTTPException, status

from app.config import Settings, get_settings


def verify_token(
    authorization: Annotated[Optional[str], Header()] = None,
    settings: Settings = Depends(get_settings),
) -> str:
    """Validate the Bearer token from the Authorization header.

    If ``settings.api_key`` is None, authentication is disabled and every
    request is accepted.

    Raises:
        HTTPException: 401 if auth is required and the token is missing or wrong.
    """
    if not settings.api_key:
        return ""

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or malformed Authorization header. Expected: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization.removeprefix("Bearer ").strip()
    if token != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return token


AuthToken = Annotated[str, Depends(verify_token)]
