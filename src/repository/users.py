from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.schemas import UserCreate


class UserRepository:
    """
    This repository class encapsulates all database operations related to users.

    Attributes:
        db (AsyncSession): Asynchronous database session instance.
    """

    def __init__(self, session: AsyncSession):
        """
        Construct a UserRepository instance with a provided database session.

        Args:
            session (AsyncSession): An asynchronous session for database interaction.
        """
        self.db = session

    async def get_user_by_id(self, user_id: int) -> User | None:
        """
        Fetch a user from the database using their unique identifier.

        Args:
            user_id (int): Unique identifier of the user to look up.

        Returns:
            User | None: Returns the user object if present, otherwise returns None.
        """
        stmt = select(User).filter_by(id=user_id)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> User | None:
        """
        Look up a user in the database by their username.

        Args:
            username (str): The username of the user to find.

        Returns:
            User | None: Returns the user object if found, or None if no user matches the username.
        """
        stmt = select(User).filter_by(username=username)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User | None:
        """
        Search for a user in the database using their email address.

        Args:
            email (str): The email address associated with the user.

        Returns:
            User | None: The user object if a match is found, or None otherwise.
        """
        stmt = select(User).filter_by(email=email)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def create_user(self, body: UserCreate, avatar: str = None) -> User:
        """
        Add a new user record to the database.

        Args:
            body (UserCreate): Data required to create a new user.
            avatar (str, optional): URL for the user's avatar image. Defaults to None.

        Returns:
            User: The newly created user object.
        """
        user = User(
            **body.model_dump(exclude_unset=True, exclude={"password"}),
            hashed_password=body.password,
            avatar=avatar
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def reset_password(self, user_id: int, password: str) -> User | None:
        """
        Update the password for a user specified by their unique ID.

        Args:
            user_id (int): The unique identifier of the user whose password will be updated.
            password (str): The new password to assign to the user.

        Returns:
            User: The user object with the updated password, or None if the user does not exist.
        """
        user = await self.get_user_by_id(user_id)
        if user:
            user.hashed_password = password
            await self.db.commit()
            await self.db.refresh(user)

        return user

    async def refresh_token(self, user_id: int, token: str) -> User | None:
        """
        Update the refresh token for a user identified by their unique ID.

        Args:
            user_id (int): The unique identifier of the user whose refresh token will be updated.
            token (str): The new refresh token value to set for the user.

        Returns:
            User: The user object with the updated refresh token, or None if the user is not found.
        """
        user = await self.get_user_by_id(user_id)
        if user:
            user.refresh_token = token
            await self.db.commit()
            await self.db.refresh(user)

        return user

    async def confirmed_email(self, email: str) -> None:
        """
        Set the user's email status as confirmed in the database.

        Args:
            email (str): The email address of the user whose email should be confirmed.

        Returns:
            None
        """
        user = await self.get_user_by_email(email)
        user.confirmed = True
        await self.db.commit()

    async def update_avatar_url(self, email: str, url: str) -> User:
        """
        Modify the avatar URL for a user based on their email address.

        Args:
            email (str): The email address of the user whose avatar will be updated.
            url (str): The updated URL for the user's avatar.

        Returns:
            User: The user object reflecting the new avatar URL.
        """
        user = await self.get_user_by_email(email)
        user.avatar = url
        await self.db.commit()
        await self.db.refresh(user)
        return user
