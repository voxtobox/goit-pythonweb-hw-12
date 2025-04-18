from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.schemas import ContactBase

from sqlalchemy.sql.expression import and_, extract, or_

from datetime import date, timedelta


class ContactRepository:
    def __init__(self, session: AsyncSession):
        """
        Instantiate the ContactRepository with a database session.

        Args:
            session: An AsyncSession instance connected to the database.
        """
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
        """
        Retrieve a paginated list of contacts belonging to a specific user, with optional filters.

        Args:
            skip: Number of contacts to skip from the beginning of the result set.
            limit: Maximum number of contacts to return.
            user: The user whose contacts are to be retrieved.
            first_name: Filter contacts by first name (partial matches allowed).
            last_name: Filter contacts by last name (partial matches allowed).
            email: Filter contacts by email address (partial matches allowed).

        Returns:
            A list containing the filtered contacts.
        """

        filters = []

        if first_name:
            filters.append(Contact.first_name.like(f"%{first_name}%"))
        if last_name:
            filters.append(Contact.last_name.like(f"%{last_name}%"))
        if email:
            filters.append(Contact.email.like(f"%{email}%"))

        # Dynamically construct the query with provided filters
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
        """
        Retrieve a contact by its unique identifier for a given user.

        Args:
            contact_id: The unique identifier of the contact to fetch.
            user: The user who owns the contact.

        Returns:
            The contact object matching the provided ID, or None if not found.
        """
        stmt = select(Contact).filter_by(id=contact_id, user=user)
        contact = await self.db.execute(stmt)
        return contact.scalar_one_or_none()

    async def create_contact(self, body: ContactBase, user: User) -> Contact:
        """
        Add a new contact to the database for a specified user.

        Args:
            body: An instance of ContactBase containing the contact's details.
            user: The user who will own the new contact.

        Returns:
            The newly created contact object.
        """

        contact = Contact(**body.model_dump(exclude_unset=True), user=user)
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def update_contact(
            self, contact_id: int, body: ContactBase, user: User
    ) -> Contact | None:
        """
        Modify the details of an existing contact for a specific user.

        Args:
            contact_id: The unique identifier of the contact to update.
            body: An instance of ContactBase with updated contact information.
            user: The user who owns the contact.

        Returns:
            The updated contact object, or None if the contact does not exist.
        """

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
        """
        Remove a contact from the database by its unique identifier.

        Args:
            contact_id: The unique identifier of the contact to remove.
            user: The user who owns the contact.

        Returns:
            The deleted contact object, or None if no such contact exists.
        """

        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
        return contact

    async def get_upcoming_birthdays(self, user: User, days: int = 7) -> List:
        """
        Retrieve contacts with birthdays occurring within the next specified number of days.

        Args:
            days: The number of days ahead to check for upcoming birthdays.
            user: The user whose contacts are to be checked.

        Returns:
            A list of contacts who have birthdays within the specified upcoming period.
        """

        today = date.today()
        target_date = today + timedelta(days=days)

        if target_date.year == today.year:
            # If the target date is within the same calendar year
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
            # If the range spans into the next calendar year
            stmt = select(Contact).filter(
                or_(
                    # Birthdays remaining in the current year
                    and_(
                        extract("month", Contact.birthday) == today.month,
                        extract("day", Contact.birthday) >= today.day,
                    ),
                    and_(
                        extract("month", Contact.birthday) > today.month,
                    ),
                    # Birthdays in the next calendar year
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
