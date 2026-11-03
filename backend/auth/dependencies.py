from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from auth.security import verify_supabase_token

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict:

    print("DEBUG: get_current_user CALLED", flush=True)

    if credentials is None:
        print("DEBUG: NO BEARER TOKEN RECEIVED", flush=True)

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials are missing",
            headers={"WWW-Authenticate": "Bearer"},
        )

    print("DEBUG: BEARER TOKEN RECEIVED", flush=True)

    try:
        payload = verify_supabase_token(credentials.credentials)

        print("DEBUG: TOKEN VERIFIED", flush=True)

        user_id = UUID(payload["sub"])

        return {
            "id": str(user_id),
            "email": payload.get("email"),
        }

    except (ValueError, KeyError, TypeError):
        print("DEBUG: TOKEN VERIFICATION FAILED", flush=True)

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
