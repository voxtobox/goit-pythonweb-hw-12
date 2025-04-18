import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.repository.users import UserRepository
from src.schemas import UserCreate


@pytest.fixture
def mock_session():
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def user_repository(mock_session):
    return UserRepository(mock_session)


@pytest.mark.asyncio
async def test_get_user_by_id(user_repository, mock_session):
    # Setup mock
    mock_user = User(id=1, username="testuser", email="test@example.com", role="admin")
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_user
    mock_session.execute = AsyncMock(return_value=mock_result)

    user = await user_repository.get_user_by_id(user_id=1)

    assert user is not None
    assert user.id == 1
    assert user.username == "testuser"


@pytest.mark.asyncio
async def test_get_user_by_username(user_repository, mock_session):
    # Setup mock
    mock_user = User(id=1, username="testuser", email="test@example.com", role="admin")
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_user
    mock_session.execute = AsyncMock(return_value=mock_result)

    user = await user_repository.get_user_by_username(username="testuser")

    assert user is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"


@pytest.mark.asyncio
async def test_get_user_by_email(user_repository, mock_session):
    # Setup mock
    mock_user = User(id=1, username="testuser", email="test@example.com", role="admin")
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_user
    mock_session.execute = AsyncMock(return_value=mock_result)

    user = await user_repository.get_user_by_email(email="test@example.com")

    assert user is not None
    assert user.email == "test@example.com"


@pytest.mark.asyncio
async def test_create_user(user_repository, mock_session):
    user_data = UserCreate(
        username="newuser",
        email="new@example.com",
        password="hashed_password",
        role="admin",
    )
    result = await user_repository.create_user(body=user_data, avatar="avatar_url")

    assert isinstance(result, User)
    assert result.username == "newuser"
    assert result.email == "new@example.com"
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(result)


@pytest.mark.asyncio
async def test_confirmed_email(user_repository, mock_session):
    # Setup
    mock_user = User(
        id=1,
        username="testuser",
        email="test@example.com",
        confirmed=False,
        role="admin",
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_user
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.commit = AsyncMock()

    await user_repository.confirmed_email(email="test@example.com")

    assert mock_user.confirmed is True
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_avatar_url(user_repository, mock_session):
    mock_user = User(
        id=1, username="testuser", email="test@example.com", avatar=None, role="admin"
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_user
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()

    result = await user_repository.update_avatar_url(
        email="test@example.com", url="new_avatar_url"
    )

    assert result is not None
    assert result.avatar == "new_avatar_url"
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(mock_user)
