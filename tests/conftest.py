"""Shared test fixtures."""

from unittest.mock import AsyncMock, patch

import pytest


@pytest.fixture
def mock_db():
    """Provide a mock database session and patch get_db to yield it.

    Usage:
        def test_something(mock_db):
            # mock_db is an AsyncMock session
            # maple_return.main.get_db is already patched
    """
    mock_session = AsyncMock()

    async def fake_get_db():
        yield mock_session

    with patch("maple_return.main.get_db", fake_get_db):
        yield mock_session
