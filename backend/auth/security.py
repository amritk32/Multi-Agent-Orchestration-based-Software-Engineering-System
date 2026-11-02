from functools import lru_cache

import jwt
from jwt import PyJWKClient
import logging

logger = logging.getLogger(__name__)

SUPABASE_URL = "https://qtehhmnsjvnfwaktqvlt.supabase.co"

JWKS_URL = f"{SUPABASE_URL}/auth/v1/.well-known/jwks.json"
JWT_ISSUER = f"{SUPABASE_URL}/auth/v1"

jwks_client = PyJWKClient(JWKS_URL)


def verify_supabase_token(token: str) -> dict:
    """
    Verify a Supabase access token and return its claims.
    """

    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        header = jwt.get_unverified_header(token)
        logger.info("Incoming JWT algorithm: %s", header.get("alg"))
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["ES256"],
            audience="authenticated",
            issuer=JWT_ISSUER,
        )

        return payload

    except jwt.PyJWTError as exc:
        raise ValueError("Invalid or expired authentication token") from exc
