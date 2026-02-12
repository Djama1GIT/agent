import json
from pathlib import Path
from typing import List, Dict, Any

from dotenv import load_dotenv
from pydantic import field_validator
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    """
    Application configuration settings loaded from environment variables.

    This class defines all configuration parameters needed by the application,
    with values loaded from environment variables and/or .env file. Includes
    validation and parsing of complex values from JSON strings.

    Configuration:
        - env_file (str): Specifies the .env file to load (default: '.env')
    """

    class Config:
        env_file = ".env"

    # Application settings
    APP_FILES_PATH: Path
    """Base path for local file storage operations."""

    # FastAPI documentation settings
    TITLE: str
    """Title of the API documentation."""

    DEFAULT_MODEL: str
    """Default of LLM."""

    DESCRIPTION: str
    """Detailed description of the API."""

    SUMMARY: str
    """Brief summary of the API's purpose."""

    VERSION: str
    """Current version of the API."""

    CONTACT: Dict[str, str]
    """Contact information for API maintainers (parsed from JSON string)."""

    LICENSE_INFO: Dict[str, str]
    """License information for the API (parsed from JSON string)."""

    # CORS settings
    ALLOW_ORIGINS: List[str] = ["*"]
    """List of allowed origins for CORS (parsed from JSON string). Defaults to ["*"]."""

    ALLOW_CREDENTIALS: bool = True
    """Whether to allow credentials in CORS requests. Defaults to True."""

    ALLOW_METHODS: List[str] = ["*"]
    """List of allowed HTTP methods for CORS (parsed from JSON string). Defaults to ["*"]."""

    ALLOW_HEADERS: List[str] = ["*"]
    """List of allowed HTTP headers for CORS (parsed from JSON string). Defaults to ["*"]."""

    @field_validator(
        "CONTACT",
        "LICENSE_INFO",
        "ALLOW_ORIGINS",
        "ALLOW_METHODS",
        "ALLOW_HEADERS",
        mode="before",
    )
    @classmethod
    def parse_json(cls, value: Any) -> Any:
        """
        Parse string values as JSON if possible.

        Parameters:
            value (Any): The input value to parse

        Returns:
            Any: Parsed JSON object if input was a JSON string, original value otherwise
        """
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return value
