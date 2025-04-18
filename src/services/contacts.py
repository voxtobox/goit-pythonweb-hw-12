from src.repository.contacts import ContactRepository
from src.schemas import ContactBase, User

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError


def _handle_integrity_error(e: IntegrityError):
    print(e)
    if "ix_contacts_email" in str(e.orig):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A contact with such an email already exists.",
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Data integrity error.",
        )


class ContactService:
    def __init__(self, db: AsyncSession):
        self.repository = ContactRepository(db)

    async def create_contact(self, body: ContactBase, user: User):
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
        return await self.repository.get_contacts(
            user, skip, limit, first_name, last_name, email
        )

    async def get_contact(self, contact: int, user: User):
        return await self.repository.get_contact_by_id(contact, user)

    async def update_contact(self, contact: int, body: ContactBase, user: User):
        try:
            return await self.repository.update_contact(contact, body, user)
        except IntegrityError as e:
            await self.repository.db.rollback()
            _handle_integrity_error(e)

    async def remove_contact(self, contact: int, user: User):
        return await self.repository.remove_contact(contact, user)

    async def upcoming_birthdays(self, days: int, user: User):
        return await self.repository.get_upcoming_birthdays(user, days)
