from src.repository.contacts import ContactRepository
from src.schemas import ContactBase, User

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError


def _handle_integrity_error(e: IntegrityError):
    """
    Handle database integrity errors and convert them to meaningful HTTP exceptions.

    Args:
        e (IntegrityError): The original database integrity error.

    Raises:
        HTTPException: 409 Conflict for duplicate email, 400 Bad Request for other integrity errors.
    """
    print(e)
    if "ix_contacts_email" in str(e.orig):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Contact with this email already exists.",
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Data integrity error occurred.",
        )


class ContactService:
    """
    Service layer for handling business logic related to contact operations.

    Attributes:
        repository (ContactRepository): The contact repository handling database operations.
    """

    def __init__(self, db: AsyncSession):
        self.repository = ContactRepository(db)

    async def create_contact(self, body: ContactBase, user: User):
        """
        Create a new contact for the specified user.

        Args:
            body (ContactBase): The contact data to create.
            user (User): The user owning the contact.

        Returns:
            Contact: The newly created contact.

        Raises:
            HTTPException: For data integrity or validation errors.
        """
        try:
            return await self.repository.create_contact(body, user)
        except IntegrityError as e:
            await self.repository.db.rollback()
            _handle_integrity_error(e)

    async def get_contacts(
            self,
            user: User,
            skip: int,
            limit: int,
            first_name: str | None,
            last_name: str | None,
            email: str | None,
    ):
        """
        Retrieve contacts for a user with optional filters and pagination.

        Args:
            user (User): The user to get contacts for.
            skip (int): Number of contacts to skip.
            limit (int): Maximum number of contacts to return.
            first_name (str | None): Filter by first name.
            last_name (str | None): Filter by last name.
            email (str | None): Filter by email.

        Returns:
            List[Contact]: The list of matching contacts.
        """
        return await self.repository.get_contacts(
            user, skip, limit, first_name, last_name, email
        )

    async def get_contact(self, contact: int, user: User):
        """
        Get a single contact by ID for the specified user.

        Args:
            contact (int): The ID of the contact to retrieve.
            user (User): The user owning the contact.

        Returns:
            Contact | None: The requested contact or None if not found.
        """
        return await self.repository.get_contact_by_id(contact, user)

    async def update_contact(self, contact: int, body: ContactBase, user: User):
        """
        Update an existing contact's information.

        Args:
            contact (int): The ID of the contact to update.
            body (ContactBase): The updated contact data.
            user (User): The user owning the contact.

        Returns:
            Contact: The updated contact.

        Raises:
            HTTPException: For data integrity or validation errors.
        """
        try:
            return await self.repository.update_contact(contact, body, user)
        except IntegrityError as e:
            await self.repository.db.rollback()
            _handle_integrity_error(e)

    async def remove_contact(self, contact: int, user: User):
        """
        Delete a contact by ID for the specified user.

        Args:
            contact (int): The ID of the contact to delete.
            user (User): The user owning the contact.

        Returns:
            Contact | None: The deleted contact or None if not found.
        """
        return await self.repository.remove_contact(contact, user)

    async def upcoming_birthdays(self, days: int, user: User):
        """
        Retrieve contacts with upcoming birthdays within the specified days.

        Args:
            days (int): Number of days to look ahead for birthdays.
            user (User): The user owning the contacts.

        Returns:
            List[Contact]: Contacts with upcoming birthdays.
        """
        return await self.repository.get_upcoming_birthdays(user, days)
