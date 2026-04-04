from datetime import datetime, timedelta, timezone
from uuid import uuid4
from pathlib import Path
from fastapi import HTTPException,status
import jwt
from app.config import security_settings
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

_serializer=URLSafeTimedSerializer(security_settings.JWT_SECRET)




APP_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = APP_DIR / "templates"

def generate_access_token(
    data: dict,
    expiry: timedelta = timedelta(days=1),
) -> str:
    return jwt.encode(
        payload={
            **data,
            "jti":str(uuid4()),
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


def generate_url_safe_token(data:dict) -> str:
    return _serializer.dumps(data)

def decode_url_safe_token(
        token:str,
        expiry:timedelta | None = None,
    ) -> dict | None:
    try:
        return _serializer.loads(
        token,
        max_age=expiry.total_seconds() if expiry else None,
        )
    except (BadSignature,SignatureExpired):
        return None


