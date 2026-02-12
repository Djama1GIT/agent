from src.core.config import Settings


def get_settings() -> Settings:
    """
    Dependency function to retrieve application settings.

    This function provides a FastAPI dependency that returns a singleton instance
    of the application settings.

    Returns:
        Settings: An instance of the application Settings class containing all
        configuration parameters loaded from environment variables and .env files.
    """
    return Settings()  # type: ignore[call-arg]
