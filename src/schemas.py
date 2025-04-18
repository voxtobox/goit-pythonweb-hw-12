from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, EmailStr

from src.database.models import UserRole


class ContactBase(BaseModel):
    """
    ContactBase serves as the foundational schema for creating or modifying a contact record.

    Attributes:
        first_name (str): Contact's first name. Limited to a maximum of 50 characters.
        last_name (str): Contact's last name. Limited to a maximum of 50 characters.
        email (EmailStr): Contact's email address.
        phone_number (str): Contact's phone number.
        birthday (date): Date of birth of the contact.
        additional_info (Optional[str]): Optional field for providing extra information about the contact.
    """

    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    email: EmailStr
    phone_number: str
    birthday: date
    additional_info: Optional[str]


class ContactUpdate(BaseModel):
    """
    ContactUpdate is intended for modifying an existing contact. All attributes are optional.

    Attributes:
        first_name (Optional[str]): New value for the contact’s first name, if applicable.
        last_name (Optional[str]): New value for the contact’s last name, if applicable.
        email (Optional[EmailStr]): New value for the contact’s email address, if applicable.
        phone_number (Optional[str]): New value for the contact’s phone number, if applicable.
        birthday (Optional[date]): New date of birth for the contact, if applicable.
        additional_info (Optional[str]): Any other updated information about the contact, if applicable.
    """

    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[EmailStr]
    phone_number: Optional[str]
    birthday: Optional[date]
    additional_info: Optional[str]


class ContactResponse(ContactBase):
    """
    ContactResponse inherits from ContactBase and includes an ID field for response purposes.

    Attributes:
        id (int): A unique integer identifier for the contact.
    """

    id: int

    model_config = ConfigDict(from_attributes=True)


class User(BaseModel):
    """
    User defines the structure representing a user in the system, containing basic user data.

    Attributes:
        id (int): Unique identifier assigned to the user.
        username (str): The name used by the user to log in.
        email (str): The user's email address.
        avatar (str): A link to the user's avatar image.
        role (UserRole): Role assigned to the user within the system.
    """

    id: int
    username: str
    email: str
    avatar: str
    role: UserRole

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    """
    UserCreate defines the fields required to register a new user.

    Attributes:
        username (str): Desired username for the new account.
        email (str): Email address used for registration.
        password (str): Chosen password for the new account.
        role (UserRole): Role to be assigned to the new user.
    """

    username: str
    email: str
    password: str
    role: UserRole


class Token(BaseModel):
    """
    Token defines the authentication tokens returned after a successful login.

    Attributes:
        access_token (str): Token used to authorize API requests.
        refresh_token (str): Token used to obtain a new access token.
        token_type (str): Type of token returned, usually 'bearer'.
    """

    access_token: str
    refresh_token: str
    token_type: str


class TokenRefreshRequest(BaseModel):
    refresh_token: str


class RequestEmail(BaseModel):
    """
    RequestEmail defines the structure for email-related requests.

    Attributes:
        email (EmailStr): The email address involved in the request.
    """

    email: EmailStr


class ResetPassword(BaseModel):
    """
    ResetPassword is used to handle requests for setting a new password.

    Attributes:
        email (EmailStr): The email address of the user requesting the password change.
        password (str): The newly chosen password.
    """

    email: EmailStr
    password: str
