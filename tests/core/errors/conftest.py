import pytest
from fastapi import Request


@pytest.fixture
def mock_request():
    """Create a mock request object."""
    return Request(scope={"type": "http"})
