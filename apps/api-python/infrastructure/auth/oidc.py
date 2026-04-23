import httpx
from jose import jwt, JWTError
from fastapi import HTTPException, status
from typing import Dict, Any, Optional
import time
import structlog

from infrastructure.config import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()

class OIDCProvider:
    def __init__(self):
        self.issuer = settings.oidc_issuer
        self.audience = settings.oidc_audience
        self.jwks_uri = settings.oidc_jwks_uri
        self._jwks: Optional[Dict[str, Any]] = None
        self._last_jwks_fetch = 0
        self._jwks_ttl = 3600 # 1 hour

    async def _discover(self):
        if self.jwks_uri:
            return

        discovery_url = f"{self.issuer.rstrip('/')}/.well-known/openid-configuration"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(discovery_url)
                response.raise_for_status()
                config = response.json()
                self.jwks_uri = config.get("jwks_uri")
                if not self.jwks_uri:
                    raise ValueError("Discovery document missing jwks_uri")
            except Exception as e:
                logger.error("oidc_discovery_failed", error=str(e), url=discovery_url)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to discover OIDC configuration"
                )

    async def get_jwks(self) -> Dict[str, Any]:
        now = time.time()
        if self._jwks and (now - self._last_jwks_fetch < self._jwks_ttl):
            return self._jwks

        await self._discover()
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(self.jwks_uri)
                response.raise_for_status()
                self._jwks = response.json()
                self._last_jwks_fetch = now
                return self._jwks
            except Exception as e:
                logger.error("jwks_fetch_failed", error=str(e), url=self.jwks_uri)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to fetch OIDC signing keys"
                )

    async def validate_token(self, token: str) -> Dict[str, Any]:
        jwks = await self.get_jwks()
        
        try:
            # Unverified header to get the kid
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get("kid")
            if not kid:
                raise JWTError("Missing kid in token header")

            # Find the matching key in JWKS
            rsa_key = {}
            for key in jwks.get("keys", []):
                if key.get("kid") == kid:
                    rsa_key = {
                        "kty": key.get("kty"),
                        "kid": key.get("kid"),
                        "use": key.get("use"),
                        "n": key.get("n"),
                        "e": key.get("e")
                    }
                    break
            
            if not rsa_key:
                raise JWTError("Could not find matching key in JWKS")

            # Validate the token
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=["RS256"],
                audience=self.audience,
                issuer=self.issuer
            )
            return payload

        except JWTError as e:
            logger.error("token_validation_failed", error=str(e), audience=self.audience, issuer=self.issuer)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception as e:
            logger.error("unexpected_token_validation_error", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal error during token validation"
            )

    async def fetch_user_info(self, token: str) -> Dict[str, Any]:
        """
        Fetch additional user details from the OIDC userinfo endpoint.
        Useful when the Access Token doesn't contain profile/email claims.
        """
        userinfo_url = f"{self.issuer.rstrip('/')}/userinfo"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    userinfo_url,
                    headers={"Authorization": f"Bearer {token}"}
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error("oidc_userinfo_fetch_failed", error=str(e), url=userinfo_url)
                return {}

oidc_provider = OIDCProvider()
