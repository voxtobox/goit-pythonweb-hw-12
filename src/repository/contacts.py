from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.schemas import ContactBase

from sqlalchemy.sql.expression import and_, extract, or_

from datetime import date, timedelta


class ContactRepository:
    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_contacts(
        self,
        user: User,
        skip: int = 0,
        limit: int = 10,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
    ) -> List[Contact]:
        filters = []

        if first_name:
            filters.append(Contact.first_name.like(f"%{first_name}%"))
        if last_name:
            filters.append(Contact.last_name.like(f"%{last_name}%"))
        if email:
            filters.append(Contact.email.like(f"%{email}%"))

        # Build the query dynamically
        stmt = (
            select(Contact)
            .filter_by(user=user)
            .where(and_(*filters))
            .offset(skip)
            .limit(limit)
        )

        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()

    async def get_contact_by_id(self, contact_id: int, user: User) -> Contact | None:
        stmt = select(Contact).filter_by(id=contact_id, user=user)
        contact = await self.db.execute(stmt)
        return contact.scalar_one_or_none()

    async def create_contact(self, body: ContactBase, user: User) -> Contact:
        contact = Contact(**body.model_dump(exclude_unset=True), user=user)
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def update_contact(
        self, contact_id: int, body: ContactBase, user: User
    ) -> Contact | None:
        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            contact.first_name = body.first_name
            contact.last_name = body.last_name
            contact.birthday = body.birthday
            contact.additional_info = body.additional_info
            contact.email = body.email
            contact.phone_number = body.phone_number

            await self.db.commit()
            await self.db.refresh(contact)
        return contact

    async def remove_contact(self, contact_id: int, user: User) -> Contact | None:
        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
        return contact

    async def get_upcoming_birthdays(self, user: User, days: int = 7) -> List:
        today = date.today()
        target_date = today + timedelta(days=days)

        if target_date.year == today.year:
            # Query stays within the same year
            stmt = (
                select(Contact)
                .filter_by(user=user)
                .filter(
                    or_(
                        and_(
                            extract("month", Contact.birthday) == today.month,
                            extract("day", Contact.birthday) >= today.day,
                        ),
                        and_(
                            extract("month", Contact.birthday) == target_date.month,
                            extract("day", Contact.birthday) <= target_date.day,
                        ),
                        and_(
                            extract("month", Contact.birthday) > today.month,
                            extract("month", Contact.birthday) < target_date.month,
                        ),
                    )
                )
            )
        else:
            # Range crosses into the next year
            stmt = select(Contact).filter(
                or_(
                    # Birthdays in the current year
                    and_(
                        extract("month", Contact.birthday) == today.month,
                        extract("day", Contact.birthday) >= today.day,
                    ),
                    and_(
                        extract("month", Contact.birthday) > today.month,
                    ),
                    # Birthdays in the next year
                    and_(
                        extract("month", Contact.birthday) == target_date.month,
                        extract("day", Contact.birthday) <= target_date.day,
                    ),
                    and_(
                        extract("month", Contact.birthday) < target_date.month,
                    ),
                )
            )

        result = await self.db.execute(stmt)

        return result.scalars().all()