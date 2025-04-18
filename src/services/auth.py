from datetime import datetime, timedelta, UTC
from typing import Optional, Literal
import pickle

from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from requests import Session
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt

from src.database.db import get_db
from src.conf.config import settings
from src.database.models import UserRole
from src.schemas import User
from src.services.users import UserService
from src.redis.redis import get_redis


class Hash:
    """
    Provides password hashing and verification using bcrypt algorithm.

    Attributes:
        pwd_context: CryptContext instance configured for bcrypt hashing.
    """

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password, hashed_password):
        """Verify if plain password matches hashed password."""
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """Generate hashed version of the plain password."""
        return self.pwd_context.hash(password)


# OAuth2 scheme for handling bearer tokens in authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def create_token(
    data: dict, expires_delta: timedelta, token_type: Literal["access", "refresh"]
) -> str:
    """
    Generate JWT token with specified type and expiration time.

    Args:
        data: Payload data to include in token
        expires_delta: Token lifetime duration
        token_type: Type of token (access/refresh)

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    now = datetime.now(UTC)
    expire = now + expires_delta
    to_encode.update({"exp": expire, "iat": now, "token_type": token_type})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


async def create_access_token(data: dict, expires_delta: Optional[float] = None) -> str:
    """
    Create access token with default expiration from settings.

    Args:
        data: Payload data for token
        expires_delta: Optional custom expiration time in seconds

    Returns:
        Encoded access JWT token
    """
    if expires_delta:
        access_token = create_token(data, expires_delta, "access")
    else:
        access_token = create_token(
            data, timedelta(seconds=settings.JWT_EXPIRATION_SECONDS), "access"
        )
    return access_token


async def create_refresh_token(
    data: dict, expires_delta: Optional[float] = None
) -> str:
    """
    Create refresh token with default expiration from settings.

    Args:
        data: Payload data for token
        expires_delta: Optional custom expiration time in seconds

    Returns:
        Encoded refresh JWT token
    """
    if expires_delta:
        refresh_token = create_token(data, expires_delta, "refresh")
    else:
        refresh_token = create_token(
            data, timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES), "refresh"
        )
    return refresh_token


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
) -> User:
    """
    Dependency to get current authenticated user from JWT token.

    Raises:
        HTTPException: 401 if credentials are invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode JWT
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        username = payload["sub"]
        token_type = payload["token_type"]

        if username is None or token_type != "access":
            raise credentials_exception

    except JWTError as e:
        raise credentials_exception
    user = redis.get(str(username))
    if user is None:
        user_service = UserService(db)
        user = await user_service.get_user_by_username(username)
        if user is None:
            raise credentials_exception
        redis.set(str(username), pickle.dumps(user))
        redis.expire(str(username), 3600)
    else:
        user = pickle.loads(user)
    return user


def create_email_token(data: dict) -> str:
    """
    Generate email verification token with 7-day expiration.

    Args:
        data: Payload containing email address

    Returns:
        Encoded JWT token for email verification
    """
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=7)
    to_encode.update({"iat": datetime.now(UTC), "exp": expire})
    token = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token


async def get_email_from_token(token: str) -> str:
    """
    Extract email address from verification token.

    Raises:
        HTTPException: 422 if token is invalid
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        email = payload["sub"]
        return email
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Token is not correct",
        )


async def get_password_from_token(token: str) -> str:
    """
    Extract password from reset token (used in password reset flow).

    Raises:
        HTTPException: 422 if token is invalid
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        password = payload["password"]
        return password
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Token is not correct",
        )


def get_current_moderator_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Verify user has moderator or admin role.

    Raises:
        HTTPException: 403 if insufficient permissions
    """
    if current_user.role not in [UserRole.MODERATOR, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user


def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Verify user has admin role.

    Raises:
        HTTPException: 403 if insufficient permissions
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user


def verify_refresh_token(refresh_token: str, db: Session) -> Optional[User]:
    """
    Validate refresh token and return associated user.

    Args:
        refresh_token: JWT refresh token
        db: Database session

    Returns:
        User if valid token, None otherwise
    """
    try:
        payload = jwt.decode(
            refresh_token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        username: str = payload.get("sub")
        token_type: str = payload.get("token_type")
        if username is None or token_type != "refresh":
            return None
        user = (
            db.query(User)
            .filter(User.username == username, User.refresh_token == refresh_token)
            .first()
        )
        return user
    except JWTError:
        return None
