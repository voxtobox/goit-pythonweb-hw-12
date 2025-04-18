from unittest.mock import Mock

import pytest
from sqlalchemy import select

from src.database.models import User
from tests.conftest import TestingSessionLocal

user_data = {
    "username": "test_test",
    "email": "test@gmail.com",
    "password": "00000",
    "role": "admin",
}


def test_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)
    response = client.post("api/auth/register", json=user_data)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "hashed_password" not in data
    assert "avatar" in data


def test_signup_exits(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)
    response = client.post("api/auth/register", json=user_data)
    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == "User with this email already exists"


def test_signup_name_exits(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)
    response = client.post(
        "api/auth/register",
        json={
            "email": "user1@example.com",
            "username": user_data["username"],
            "role": user_data["role"],
            "password": user_data["password"],
        },
    )
    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == "User with this username already exists"


def test_repeat_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)
    response = client.post("api/auth/register", json=user_data)
    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == "User with this email already exists"


def test_not_confirmed_login(client):
    response = client.post(
        "api/auth/login",
        data={
            "username": user_data.get("username"),
            "password": user_data.get("password"),
        },
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Email is not confirmed"


@pytest.mark.asyncio
async def test_login(client):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(
            select(User).where(User.email == user_data.get("email"))
        )
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.confirmed = True
            await session.commit()

    response = client.post(
        "api/auth/login",
        data={
            "username": user_data.get("username"),
            "password": user_data.get("password"),
        },
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert "token_type" in data


def test_wrong_password_login(client):
    response = client.post(
        "api/auth/login",
        data={"username": user_data.get("username"), "password": "password"},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid username or password"


def test_wrong_username_login(client):
    response = client.post(
        "api/auth/login",
        data={"username": "username", "password": user_data.get("password")},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid username or password"


def test_validation_error_login(client):
    response = client.post(
        "api/auth/login", data={"password": user_data.get("password")}
    )
    assert response.status_code == 422, response.text
    data = response.json()
    assert "detail" in data


def test_invalid_refresh_token(client):
    invalid_token = "invalid_refresh_token"
    response = client.post(
        "api/auth/refresh-token", json={"refresh_token": invalid_token}
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid or expired refresh token"


def test_login_admin(client):
    response = client.post("api/auth/login", data=user_data)
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_reset_password_request(client):
    response = client.post(
        "api/auth/reset_password",
        json={"email": "test@gmail.com", "password": "newpassword123"},
    )
    assert response.status_code == 200, response.text
    assert response.json() == {"message": "Check your email for confirmation"}


def test_public_route(client):
    response = client.get("api/auth/public")
    assert response.status_code == 200
    assert "Public content" in response.json()["message"]


def test_confirmed_email_already_confirmed(client, monkeypatch):
    async def mock_get_email_from_token(token):
        return "testuser@example.com"

    monkeypatch.setattr(
        "src.services.auth.get_email_from_token", mock_get_email_from_token
    )
    response = client.get("api/auth/confirmed_email/fake_token")
    assert response.status_code == 422


def test_confirmed_email_invalid_token(client, monkeypatch):
    async def mock_get_email_from_token(token):
        return None

    monkeypatch.setattr(
        "src.services.auth.get_email_from_token", mock_get_email_from_token
    )
    response = client.get("api/auth/confirmed_email/invalid_token")
    assert response.status_code == 422


def test_request_email_already_confirmed(client, monkeypatch):
    class UserMock:
        confirmed = True
        email = "test@example.com"
        username = "testuser"

    async def mock_get_user_by_email(email):
        return UserMock()

    monkeypatch.setattr(
        "src.services.users.UserService.get_user_by_email", mock_get_user_by_email
    )
    response = client.post("api/auth/request_email", json="test@example.com")
    assert response.status_code == 422


def test_email_incorrect_token(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)
    token = "abcde12345"
    response = client.get(f"api/auth/confirmed_email/{token}")
    assert response.status_code == 422, response.text
    data = response.json()
    assert data["detail"] == "Token is not correct"


def test_email_confirmation_not_exist(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)
    response = client.post(
        "api/auth/request_email", json={"email": "testuser@example.com"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Your email is already confirmed"


def test_email_password_reset(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)
    response_create = client.post("api/auth/register", json=user_data)

    monkeypatch.setattr("src.api.auth.send_reset_password_email", mock_send_email)
    response = client.post(
        "api/auth/reset_password",
        json={"email": user_data["email"], "password": "<PASSWORD>"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Check your email for confirmation"
