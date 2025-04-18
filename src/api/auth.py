from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    status,
    Security,
    BackgroundTasks,
    Request,
)
from requests import Session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from src.schemas import (
    UserCreate,
    Token,
    User,
    RequestEmail,
    ResetPassword,
    TokenRefreshRequest,
)
from src.services.auth import (
    create_access_token,
    Hash,
    get_email_from_token,
    get_password_from_token,
    get_current_moderator_user,
    get_current_admin_user,
    create_refresh_token,
    verify_refresh_token,
)
from src.services.users import UserService
from src.database.db import get_db
from src.services.email import send_email, send_reset_password_email

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new user.

    Args:
        user_data (UserCreate): Data for creating the user.
        background_tasks (BackgroundTasks): Task manager for sending confirmation email.
        request (Request): The incoming HTTP request.
        db (AsyncSession): The database session.

    Returns:
        User: The newly created user.

    Raises:
        HTTPException: If the email or username is already taken.
    """
    user_service = UserService(db)

    email_user = await user_service.get_user_by_email(user_data.email)
    if email_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )

    username_user = await user_service.get_user_by_username(user_data.username)
    if username_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this username already exists",
        )

    user_data.password = Hash().get_password_hash(user_data.password)
    new_user = await user_service.create_user(user_data)
    background_tasks.add_task(
        send_email, new_user.email, new_user.username, request.base_url
    )
    return new_user


@router.post("/login", response_model=Token)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    """
    Authenticate and log in a user.

    Args:
        form_data (OAuth2PasswordRequestForm): User credentials (username and password).
        db (AsyncSession): The database session.

    Returns:
        Token: An access token for the authenticated user.
        Refresh Token: An refresh token to get new access token.

    Raises:
        HTTPException: If the credentials are invalid or email is unconfirmed.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_username(form_data.username)
    if not user or not Hash().verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email is not confirmed",
        )
    access_token = await create_access_token(data={"sub": user.username})
    refresh_token = await create_refresh_token(data={"sub": user.username})

    await user_service.refresh_token(user.id, refresh_token)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
    }


@router.post("/refresh-token", response_model=Token)
async def new_token(request: TokenRefreshRequest, db: Session = Depends(get_db)):
    """
    Refresh token for an access token.

    Args:
        request (TokenRefreshRequest): The incoming HTTP request.
        db (AsyncSession): The database session.

    Returns:  Pair of tokens and token_type.
    """
    user = verify_refresh_token(request.refresh_token, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    new_access_token = await create_access_token(data={"sub": user.username})
    return {
        "access_token": new_access_token,
        "refresh_token": request.refresh_token,
        "token_type": "bearer",
    }


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    """
    Confirm a user's email address using a token.

    Args:
        token (str): The confirmation token.
        db (AsyncSession): The database session.

    Returns:
        dict: A message indicating the confirmation status.

    Raises:
        HTTPException: If the token is invalid or user not found.
    """
    email = await get_email_from_token(token)
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await user_service.confirmed_email(email)
    return {"message": "Email confirmed"}


@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Resend a confirmation email to the user.

    Args:
        body (RequestEmail): Request containing the email address.
        background_tasks (BackgroundTasks): Task manager for sending email.
        request (Request): The incoming HTTP request.
        db (AsyncSession): The database session.

    Returns:
        dict: A message indicating the email has been sent.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)

    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(
            send_email, user.email, user.username, request.base_url
        )
    return {"message": "Check your email for confirmation"}


@router.post("/reset_password")
async def reset_password_request(
    body: ResetPassword,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Handles a password reset request by generating a reset token and sending a reset password email.

    Args:
        body (ResetPassword): The request body containing the user's email and new password.
        background_tasks (BackgroundTasks): Task manager for sending email.
        request (Request): The incoming HTTP request.
         db (AsyncSession): The database session.

    Returns:
        dict: A message indicating that the user should check their email.

    Raises:
        HTTPException: If the user's email is not confirmed.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)

    if not user:
        return {"message": "Verification error"}

    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Your email is not confirmed"},
        )

    hashed_password = Hash().get_password_hash(body.password)

    reset_token = await create_access_token(
        data={"sub": user.email, "password": hashed_password}
    )

    background_tasks.add_task(
        send_reset_password_email,
        email=body.email,
        username=user.username,
        host=str(request.base_url),
        reset_token=reset_token,
    )

    return {"message": "Check your email for confirmation"}


@router.get("/confirm_reset_password/{token}")
async def confirm_reset_password(token: str, db: AsyncSession = Depends(get_db)):
    """
    Confirm and reset the user's password using the provided token.

    Args:
        token (str): The token containing the user's email and new password.
        db (Session, optional): The database session dependency.

    Raises:
        HTTPException: If the token is invalid or the user is not found.

    Returns:
        dict: A message indicating the password has been reset.

    """
    email = await get_email_from_token(token)
    hashed_password = await get_password_from_token(token)

    if not email or not hashed_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token is invalid or the user is not found.",
        )

    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token is invalid or the user is not found.",
        )

    await user_service.reset_password(user.id, hashed_password)

    return {"message": "Password reset successful"}


@router.get("/public")
def read_public():
    """
    Route available for any role

    """
    return {"message": "Public content"}


@router.get("/moderator")
def read_moderator(
    current_user: User = Depends(get_current_moderator_user),
):
    """
    Route available for admin and moderator

    """
    return {
        "message": f"Hello, {current_user.username}! This route is available for moderators and admins.",
    }


@router.get("/admin")
def read_admin(current_user: User = Depends(get_current_admin_user)):
    """
    Route available for admin

    """
    return {
        "message": f"Hello, {current_user.username}!  This route is available for admins."
    }
