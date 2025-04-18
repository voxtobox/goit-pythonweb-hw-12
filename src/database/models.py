from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, func, Date, Boolean, Enum as SqlEnum
from sqlalchemy.orm import relationship, mapped_column, Mapped, DeclarativeBase
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.sql.schema import ForeignKey, UniqueConstraint
from enum import Enum


class Base(DeclarativeBase):
    """
    The foundational class for all SQLAlchemy models, inheriting from DeclarativeBase.
    All table and model classes should extend from this base class.
    """

    pass


class Contact(Base):
    """
    The Contact model stores information about a user's contact entry in the database.

    Attributes:
        id (int): Primary key, uniquely identifies each contact.
        first_name (str): Contact's given name.
        last_name (str): Contact's family name.
        email (str): Contact's email address; must be unique for each user.
        phone_number (str): Contact's phone number.
        birthday (datetime.date): The date of birth for the contact.
        additional_info (str): Supplementary information about the contact.
        created_at (datetime): Timestamp when the contact was created; defaults to current time.
        updated_at (datetime): Timestamp of the last update to the contact; auto-updated on modification.
        user_id (int): Foreign key referring to the associated user.
        user (User): Reference to the related User model.
    """

    __tablename__ = "contacts"
    __table_args__ = (UniqueConstraint("email", "user_id", name="unique_email_user"),)

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True, nullable=False)
    last_name = Column(String, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone_number = Column(String, nullable=False)
    birthday = Column(Date, nullable=True)
    additional_info = Column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        "created_at", DateTime, default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        "updated_at", DateTime, default=func.now(), onupdate=func.now()
    )
    user_id = Column(
        "user_id", ForeignKey("users.id", ondelete="CASCADE"), default=None
    )
    user = relationship("User", backref="contacts")


class UserRole(str, Enum):
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"


class User(Base):
    """
    The User model defines a system user, including authentication and profile data.

    Attributes:
        id (int): Unique identifier for the user.
        username (str): Unique username for authentication.
        email (str): Unique email address for the user.
        hashed_password (str): User's password in hashed format.
        created_at (datetime): Timestamp when the user account was created; defaults to current time.
        avatar (str): URL to the user's avatar image (optional).
        confirmed (bool): Indicates if the user's email address has been verified.
        role (UserRole): The user's assigned role within the system.
        refresh_token (Optional[str]): The user's refresh token for authentication.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=func.now())
    avatar = Column(String(255), nullable=True)
    confirmed = Column(Boolean, default=False)
    role = Column(SqlEnum(UserRole), default=UserRole.USER, nullable=False)
    refresh_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
