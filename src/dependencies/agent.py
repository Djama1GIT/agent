from typing import Generator, Callable

from fastapi import Depends

from src.core.config import Settings
from src.services.agent import Agent


def get_agent(get_settings) -> Callable[[Settings], Generator[Agent, None, None]]:
    """
    Factory function to create a dependency for obtaining an Agent.

    Parameters:
        get_settings: Dependency function to retrieve application settings.

    Returns:
        A FastAPI dependency function that yields a configured Agent.
    """

    def _get_agent(settings: Settings = Depends(get_settings)) -> Generator[Agent, None, None]:
        """
        Inner dependency function that manages the S3 client lifecycle.

        Parameters:
            settings (Settings): Application settings containing S3 configuration.

        Returns:
            BaseClient: Authenticated and configured boto3 S3 client.

        Raises:
            RuntimeError: If S3 client initialization fails.
        """

        yield Agent(settings)

    return _get_agent
