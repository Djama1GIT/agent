import pytest

from pathlib import Path

from fastapi.testclient import TestClient

from src.core.config import Settings
from src.main import app


@pytest.fixture
def mock_settings() -> Settings:
    return Settings(
        APP_FILES_PATH=Path(__file__).parent.parent,
        TITLE="",
        DEFAULT_MODEL="test-model",
        DESCRIPTION="",
        SUMMARY="API Test",
        VERSION="1.0.0",
        CONTACT={"name": "GADJIIAVOV", "email": "gadjiiavov@dj.ama1.ru"},
        LICENSE_INFO={"name": "MIT License", "url": "https://opensource.org/licenses/MIT"},
        ALLOW_ORIGINS=["*"],
        ALLOW_CREDENTIALS=True,
        ALLOW_METHODS=["*"],
        ALLOW_HEADERS=["*"],
    )


@pytest.fixture
def client():
    """Create test client for the FastAPI application."""
    return TestClient(app)
