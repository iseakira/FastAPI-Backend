from datetime import datetime, timedelta, timezone
from fastapi import HTTPException,status
import jwt
from app.config import security_settings


def generate_access_token(
    data: dict,
    expiry: timedelta = timedelta(days=1),
) -> str:
    return jwt.encode(
        payload={
            **data,
            "exp": datetime.now(timezone.utc) + expiry,
        },
        key=security_settings.JWT_SECRET,
        algorithm=security_settings.JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(
            token,
            key=security_settings.JWT_SECRET,
            algorithms=[security_settings.JWT_ALGORITHM],
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="expired token"
    )
    except jwt.PyJWTError as e:
        print("JWT decode error:", type(e).__name__, str(e))
        print("DECODE secret repr:", repr(security_settings.JWT_SECRET))
        print("DECODE secret len:", len(security_settings.JWT_SECRET))
        print("DECODE alg:", security_settings.JWT_ALGORITHM)
        return None


