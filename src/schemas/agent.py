from typing import Optional

from pydantic import BaseModel, Field

from src.core.config import Settings


class AgentConfig(BaseModel):
    """Agent Configuration.

    Defines the configuration parameters for an agent instance.

    Attributes:
        model: The name or identifier of the AI model to use for the agent.
        web_search: Flag indicating whether the agent can perform web searches.
                   Defaults to False.
        settings: Application settings object containing global configuration.
                 Optional, can be None if not needed.

    Example:
        >>> config = AgentConfig(
        ...     model="gpt-4",
        ...     web_search=True,
        ...     settings=Settings()
        ... )
    """
    model: str = Field(..., description="The AI model identifier to use for the agent")
    web_search: bool = Field(
        default=False,
        description="Enable or disable web search capabilities for the agent"
    )
    settings: Optional[Settings] = Field(
        default=None,
        description="Global application settings instance"
    )


class ResponseSchema(BaseModel):
    """Response Schema.

    Defines the standard structure for agent responses.

    Attributes:
        message: The main content or response text from the agent.

    Example:
        >>> response = ResponseSchema(message="Hello, how can I help you?")
        >>> print(response.message)
        Hello, how can I help you?
    """
    message: str = Field(..., description="The response message content from the agent")