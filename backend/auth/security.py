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
    try:
        header = jwt.get_unverified_header(token)
        logger.info("JWT algorithm: %s", header.get("alg"))
        logger.info("JWT key ID: %s", header.get("kid"))

        signing_key = jwks_client.get_signing_key_from_jwt(token)

        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["ES256"],
            audience="authenticated",
            issuer=JWT_ISSUER,
        )

        logger.info("JWT verification successful")
        return payload

    except Exception as exc:
        logger.exception("JWT verification failed: %s", type(exc).__name__)
        raise ValueError("Invalid or expired authentication token") from exc
