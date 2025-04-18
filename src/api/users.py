from src.conf.config import settings
from fastapi import APIRouter, Depends, Request, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.schemas import User
from src.services.auth import get_current_user
from slowapi.util import get_remote_address
from slowapi import Limiter

from src.services.upload_file import UploadFileService
from src.services.users import UserService

router = APIRouter(prefix="/users", tags=["users"])
limiter = Limiter(key_func=get_remote_address)


# Route to get the current authenticated user's data
@router.get(
    "/me", response_model=User, description="No more than 10 requests per minute"
)
@limiter.limit("10/minute")
async def me(request: Request, user: User = Depends(get_current_user)):
    """
    Get the current authenticated user's information.

    Args:
        request (Request): The HTTP request object.
        user (User): The current authenticated user, injected by FastAPI's Depends function.

    Returns:
        User: The user data (e.g., email, username) for the authenticated user.

    Note:
        This endpoint is rate-limited to 10 requests per minute.
    """
    return user


# Route to update the user's avatar
@router.patch("/avatar", response_model=User)
async def update_avatar_user(
    file: UploadFile = File(),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update the current authenticated user's avatar.

    Args:
        file (UploadFile): The new avatar image file uploaded by the user.
        user (User): The current authenticated user, injected by FastAPI's Depends function.
        db (AsyncSession): The database session used for database queries, injected by FastAPI's Depends function.

    Returns:
        User: The updated user data with the new avatar URL.

    Notes:
        The uploaded file is processed using the UploadFileService and stored in the cloud storage service.
    """
    # Upload the file to cloud storage
    avatar_url = UploadFileService(
        settings.CLD_NAME, settings.CLD_API_KEY, settings.CLD_API_SECRET
    ).upload_file(file, user.username)

    # Update the user's avatar URL in the database
    user_service = UserService(db)
    user = await user_service.update_avatar_url(user.email, avatar_url)

    return user
