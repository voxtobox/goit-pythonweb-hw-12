from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from src.repository.users import UserRepository
from src.schemas import UserCreate


class UserService:
    """
    UserService provides a service layer for performing user-related operations,
    delegating data persistence to the UserRepository.
    """

    def __init__(self, db: AsyncSession):
        """
        Initializes the UserService instance with a database session.

        Parameters:
            db (AsyncSession): An asynchronous SQLAlchemy session for database interaction.
        """
        self.repository = UserRepository(db)

    async def create_user(self, body: UserCreate):
        """
        Creates a new user and attempts to generate an avatar using Gravatar.

        Parameters:
            body (UserCreate): The data required to register a new user.

        Returns:
            The result of the repository’s create_user method, including an avatar URL if available.
        """
        avatar = None
        try:
            g = Gravatar(body.email)
            avatar = g.get_image()
        except Exception as e:
            # If Gravatar fails, print the exception and proceed without an avatar.
            print(e)

        return await self.repository.create_user(body, avatar)

    async def get_user_by_id(self, user_id: int):
        """
        Retrieves a user from the database based on their unique ID.

        Parameters:
            user_id (int): The unique identifier of the user.

        Returns:
            The user object if found; otherwise, None.
        """
        return await self.repository.get_user_by_id(user_id)

    async def get_user_by_username(self, username: str):
        """
        Retrieves a user by their username.

        Parameters:
            username (str): The username to search for.

        Returns:
            The user object if a match is found; otherwise, None.
        """
        return await self.repository.get_user_by_username(username)

    async def get_user_by_email(self, email: str):
        """
        Retrieves a user using their email address.

        Parameters:
            email (str): The email address associated with the user.

        Returns:
            The user object if found; otherwise, None.
        """
        return await self.repository.get_user_by_email(email)

    async def confirmed_email(self, email: str):
        """
        Marks the user's email as confirmed.

        Parameters:
            email (str): The email address to confirm.

        Returns:
            The result of the repository’s confirmed_email method.
        """
        return await self.repository.confirmed_email(email)

    async def update_avatar_url(self, email: str, url: str):
        """
        Updates the avatar URL for the user with the given email.

        Parameters:
            email (str): The user’s email address.
            url (str): The new avatar URL to be stored.

        Returns:
            The result of the update operation from the repository.
        """
        return await self.repository.update_avatar_url(email, url)

    async def reset_password(self, user_id: int, password: str):
        """
        Updates the password for the specified user.

        Parameters:
            user_id (int): The unique identifier of the user.
            password (str): The new password to set.

        Returns:
            The result of the repository’s reset_password method.
        """
        return await self.repository.reset_password(user_id, password)

    async def refresh_token(self, user_id: int, token: str):
        """
        Updates the refresh token for the user.

        Parameters:
            user_id (int): The ID of the user whose token is being updated.
            token (str): The new refresh token to assign.

        Returns:
            The result of the token update operation.
        """
        return await self.repository.refresh_token(user_id, token)
