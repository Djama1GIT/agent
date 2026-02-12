from typing import Generator, Callable

from fastapi import Depends

from src.core.config import Settings
from src.services.article_agent import ArticleAgent


def get_article_agent(get_settings) -> Callable[[Settings], Generator[ArticleAgent, None, None]]:
    """
    Factory function to create a dependency for obtaining an Article Agent.

    Parameters:
        get_settings: Dependency function to retrieve application settings.

    Returns:
        A FastAPI dependency function that yields a configured Article Agent.
    """

    def _get_article_agent(settings: Settings = Depends(get_settings)) -> Generator[ArticleAgent, None, None]:
        """
        Inner dependency function that manages the S3 client lifecycle.

        Parameters:
            settings (Settings): Application settings containing S3 configuration.

        Returns:
            BaseClient: Authenticated and configured boto3 S3 client.

        Raises:
            RuntimeError: If S3 client initialization fails.
        """

        yield ArticleAgent(settings)

    return _get_article_agent
