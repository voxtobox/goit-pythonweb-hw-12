from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.schemas import ContactBase, ContactResponse, User
from src.services.auth import get_current_user
from src.services.contacts import ContactService

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("/", response_model=List[ContactResponse])
async def read_contacts(
    user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    first_name: str = None,
    last_name: str = None,
    email: str = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve a list of contacts for the current user.

    :param user: The current authenticated user.
    :type user: User
    :param skip: Number of contacts to skip (pagination).
    :type skip: int
    :param limit: Maximum number of contacts to retrieve.
    :type limit: int
    :param first_name: Filter by first name (optional).
    :type first_name: str
    :param last_name: Filter by last name (optional).
    :type last_name: str
    :param email: Filter by email address (optional).
    :type email: str
    :param db: The database session.
    :type db: AsyncSession
    :return: A list of contact objects.
    :rtype: List[ContactResponse]
    """
    contact_service = ContactService(db)
    contacts = await contact_service.get_contacts(
        user, skip, limit, first_name, last_name, email
    )
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def read_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Retrieve a specific contact by ID.

    :param contact_id: The ID of the contact to retrieve.
    :type contact_id: int
    :param db: The database session.
    :type db: AsyncSession
    :param user: The current authenticated user.
    :type user: User
    :return: The contact object.
    :rtype: ContactResponse
    :raises HTTPException: If the contact is not found.
    """
    contact_service = ContactService(db)
    contact = await contact_service.get_contact(contact_id, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    body: ContactBase,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Create a new contact.

    :param body: The contact data to create.
    :type body: ContactBase
    :param db: The database session.
    :type db: AsyncSession
    :param user: The current authenticated user.
    :type user: User
    :return: The newly created contact object.
    :rtype: ContactResponse
    """
    contact_service = ContactService(db)
    return await contact_service.create_contact(body, user)


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    body: ContactBase,
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Update an existing contact.

    :param body: The updated contact data.
    :type body: ContactBase
    :param contact_id: The ID of the contact to update.
    :type contact_id: int
    :param db: The database session.
    :type db: AsyncSession
    :param user: The current authenticated user.
    :type user: User
    :return: The updated contact object.
    :rtype: ContactResponse
    :raises HTTPException: If the contact is not found.
    """
    contact_service = ContactService(db)
    contact = await contact_service.update_contact(contact_id, body, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.delete("/{contact_id}", response_model=ContactResponse)
async def remove_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Delete an existing contact.

    :param contact_id: The ID of the contact to delete.
    :type contact_id: int
    :param db: The database session.
    :type db: AsyncSession
    :param user: The current authenticated user.
    :type user: User
    :return: The deleted contact object.
    :rtype: ContactResponse
    :raises HTTPException: If the contact is not found.
    """
    contact_service = ContactService(db)
    contact = await contact_service.remove_contact(contact_id, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.get("/contacts/birthdays/", response_model=List[ContactResponse])
async def upcoming_birthdays(
    days: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Retrieve contacts with upcoming birthdays.

    :param days: Number of days to look ahead for birthdays.
    :type days: int
    :param db: The database session.
    :type db: AsyncSession
    :param user: The current authenticated user.
    :type user: User
    :return: A list of contacts with upcoming birthdays.
    :rtype: List[ContactResponse]
    """
    contact_service = ContactService(db)
    contacts = await contact_service.upcoming_birthdays(days, user)
    return contacts
