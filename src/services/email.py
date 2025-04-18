from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.services.auth import create_email_token
from src.conf.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.USE_CREDENTIALS,
    VALIDATE_CERTS=settings.VALIDATE_CERTS,
    TEMPLATE_FOLDER=Path(__file__).parent / "templates",
)


async def send_email(email: EmailStr, username: str, host: str):
    """
    Sends a verification email to the user using FastMail with a confirmation token.

    Parameters:
        email (EmailStr): The recipient’s email address.
        username (str): The username of the recipient.
        host (str): The domain or base URL used to generate the confirmation link.

    This function creates a token for email verification, populates the email template
    with required data, and sends an HTML email to the user to confirm their email address.

    If sending fails due to a connection issue, the error will be printed to the console.
    """
    try:
        token_verification = create_email_token({"sub": email})
        message = MessageSchema(
            subject="Confirm your email",
            recipients=[email],
            template_body={
                "host": host,
                "username": username,
                "token": token_verification,
            },
            subtype=MessageType.html,
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="verify_email.html")
    except ConnectionErrors as err:
        print(err)


async def send_reset_password_email(
        email: EmailStr, username: str, host: str, reset_token: str
):
    """
    Sends a password reset email containing a secure reset link to the user.

    Parameters:
        email (EmailStr): The recipient’s email address.
        username (str): The name of the user requesting the reset.
        host (str): The base URL or host used for generating the reset link.
        reset_token (str): A unique token used to validate the password reset request.

    This function constructs a reset password link and fills the HTML template with
    the necessary data before sending the message using FastMail.

    In case of connection issues during sending, the error will be printed to the console.
    """
    try:
        reset_link = f"{host}api/auth/confirm_reset_password/{reset_token}"

        message = MessageSchema(
            subject="Reset password",
            recipients=[email],
            template_body={"reset_link": reset_link, "username": username},
            subtype=MessageType.html,
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="reset_password.html")
    except ConnectionErrors as err:
        print(err)
