import os
from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)
EXPECTED_API_KEY = os.getenv("API_KEY", "demo-key")

async def verify_api_key(api_key_header: str = Security(API_KEY_HEADER)):
    """Verify the X-API-Key header matches the expected API key."""
    if not api_key_header or api_key_header != EXPECTED_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Invalid or missing API key"
        )
    return api_key_header
