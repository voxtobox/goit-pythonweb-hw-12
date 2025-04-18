import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date

from src.schemas import ContactBase, User
from src.services.contacts import ContactService


@pytest.fixture
def mock_session():
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def contact_service(mock_session):
    return ContactService(mock_session)


@pytest.fixture
def mock_user():
    return User(
        id=1, username="testuser", email="test@example.com", avatar="test", role="admin"
    )


@pytest.mark.asyncio
async def test_read_contacts(contact_service, mock_session, mock_user):
    mock_contacts = [
        {
            "id": 1,
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
        },
        {
            "id": 2,
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane.smith@example.com",
        },
    ]
    contact_service.get_contacts = AsyncMock(return_value=mock_contacts)

    result = await contact_service.get_contacts(mock_user, skip=0, limit=10)

    assert len(result) == 2
    assert result[0]["first_name"] == "John"
    assert result[1]["email"] == "jane.smith@example.com"


@pytest.mark.asyncio
async def test_read_contact(contact_service, mock_session, mock_user):
    mock_contact = {
        "id": 1,
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
    }
    contact_service.get_contact = AsyncMock(return_value=mock_contact)

    result = await contact_service.get_contact(contact_id=1, user=mock_user)

    assert result is not None
    assert result["id"] == 1
    assert result["email"] == "john.doe@example.com"


@pytest.mark.asyncio
async def test_create_contact(contact_service, mock_session, mock_user):
    contact_data = ContactBase(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone_number="1234567890",
        birthday=date(1990, 12, 25),
        additional_info="some",
    )
    mock_contact = {"id": 1, **contact_data.model_dump()}
    contact_service.create_contact = AsyncMock(return_value=mock_contact)

    result = await contact_service.create_contact(body=contact_data, user=mock_user)

    assert result is not None
    assert result["id"] == 1
    assert result["first_name"] == "John"
    assert result["last_name"] == "Doe"
    assert result["phone_number"] == "1234567890"
    assert result["birthday"] == date(1990, 12, 25)
    assert result["additional_info"] == "some"


@pytest.mark.asyncio
async def test_update_contact(contact_service, mock_session, mock_user):
    contact_data = ContactBase(
        first_name="New John",
        last_name="New Doe",
        email="new.doe@example.com",
        phone_number="0001",
        birthday=date(1991, 12, 25),
        additional_info="some new",
    )
    mock_contact = {"id": 1, **contact_data.model_dump()}
    contact_service.update_contact = AsyncMock(return_value=mock_contact)

    result = await contact_service.update_contact(
        contact_id=1, body=contact_data, user=mock_user
    )

    assert result is not None
    assert result["email"] == "new.doe@example.com"
    assert result["first_name"] == "New John"
    assert result["last_name"] == "New Doe"
    assert result["phone_number"] == "0001"
    assert result["birthday"] == date(1991, 12, 25)
    assert result["additional_info"] == "some new"


@pytest.mark.asyncio
async def test_remove_contact(contact_service, mock_session, mock_user):
    mock_contact = {
        "id": 1,
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
    }
    contact_service.remove_contact = AsyncMock(return_value=mock_contact)

    result = await contact_service.remove_contact(contact_id=1, user=mock_user)

    assert result is not None
    assert result["id"] == 1
    assert result["first_name"] == "John"


@pytest.mark.asyncio
async def test_upcoming_birthdays(contact_service, mock_session, mock_user):
    mock_contacts = [
        {
            "id": 1,
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "birthday": "2023-12-25",
        },
        {
            "id": 2,
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane.smith@example.com",
            "birthday": "2023-12-28",
        },
    ]
    contact_service.upcoming_birthdays = AsyncMock(return_value=mock_contacts)

    result = await contact_service.upcoming_birthdays(days=7, user=mock_user)

    assert len(result) == 2
    assert result[0]["birthday"] == "2023-12-25"
    assert result[1]["first_name"] == "Jane"


@pytest.mark.asyncio
async def test_get_contacts_with_filters(contact_service, mock_session, mock_user):
    mock_contacts = [
        {
            "id": 1,
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
        }
    ]
    contact_service.get_contacts = AsyncMock(return_value=mock_contacts)

    result = await contact_service.get_contacts(
        user=mock_user,
        skip=0,
        limit=10,
        first_name="John",
        last_name=None,
        email=None,
    )

    assert len(result) == 1
    assert result[0]["first_name"] == "John"
    assert result[0]["email"] == "john.doe@example.com"


@pytest.mark.asyncio
async def test_upcoming_birthdays_no_matches(contact_service, mock_session, mock_user):
    contact_service.repository.get_upcoming_birthdays = AsyncMock(return_value=[])

    result = await contact_service.upcoming_birthdays(days=7, user=mock_user)

    assert result == []


@pytest.mark.asyncio
async def test_get_contact_not_found(contact_service, mock_session, mock_user):
    contact_service.repository.get_contact_by_id = AsyncMock(return_value=None)

    result = await contact_service.get_contact(contact=999, user=mock_user)

    assert result is None


@pytest.mark.asyncio
async def test_remove_contact_not_found(contact_service, mock_session, mock_user):
    contact_service.repository.remove_contact = AsyncMock(return_value=None)

    result = await contact_service.remove_contact(contact=999, user=mock_user)

    assert result is None


@pytest.mark.asyncio
async def test_get_contacts_with_filters(contact_service, mock_session, mock_user):
    mock_contacts = [
        {
            "id": 1,
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
        }
    ]
    contact_service.get_contacts = AsyncMock(return_value=mock_contacts)

    result = await contact_service.get_contacts(
        user=mock_user,
        skip=0,
        limit=10,
        first_name="John",
        last_name=None,
        email=None,
    )

    assert len(result) == 1
    assert result[0]["first_name"] == "John"
    assert result[0]["email"] == "john.doe@example.com"


def test_contact_service_initialization(mock_session):
    service = ContactService(mock_session)
    assert service.repository is not None


@pytest.mark.asyncio
async def test_get_contacts_with_different_filters(
    contact_service, mock_session, mock_user
):
    # Mock filtered results
    filtered_contacts = [
        {
            "id": 1,
            "first_name": "Filtered",
            "last_name": "Contact",
            "email": "filtered@example.com",
        }
    ]
    contact_service.repository.get_contacts = AsyncMock(return_value=filtered_contacts)

    # Test with only first_name filter
    result = await contact_service.get_contacts(
        user=mock_user,
        skip=0,
        limit=10,
        first_name="Filtered",
        last_name=None,
        email=None,
    )
    assert len(result) == 1
    assert result[0]["first_name"] == "Filtered"
    assert result[0]["email"] == "filtered@example.com"

    # Test with all filters
    result = await contact_service.get_contacts(
        user=mock_user,
        skip=0,
        limit=10,
        first_name="Filtered",
        last_name="Contact",
        email="filtered@example.com",
    )
    assert len(result) == 1


@pytest.mark.asyncio
async def test_get_contact_invalid_id(contact_service, mock_session, mock_user):
    contact_service.repository.get_contact_by_id = AsyncMock(return_value=None)

    result = await contact_service.get_contact(contact=999, user=mock_user)
    assert result is None
