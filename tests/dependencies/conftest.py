import pytest

from src.core.config import Settings


@pytest.fixture
def mock_get_settings(mock_settings: Settings):
    def _get_settings() -> Settings:
        return mock_settings

    return _get_settings
