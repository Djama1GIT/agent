import pytest
from unittest.mock import Mock

from src.services.agent import Agent, AIClient
from src.schemas.agent import AgentConfig, ResponseSchema
from src.services.article_agent import ArticleAgent


# Fixtures for reuse in tests
@pytest.fixture
def mock_ai_client() -> Mock:
    """Creates an AI mock client"""
    client = Mock(spec=AIClient)
    client.chat_completion = Mock()
    return client


@pytest.fixture
def agent_config(mock_settings: Mock) -> AgentConfig:
    """Creates a test agent configuration with mock Settings"""
    return AgentConfig(
        model="test-model",
        web_search=False,
        settings=mock_settings,
    )


@pytest.fixture
def agent(agent_config: AgentConfig, mock_ai_client: Mock) -> Agent:
    """Creates an agent with a mock client for testing"""
    return Agent(config=agent_config, ai_client=mock_ai_client)


@pytest.fixture
def mock_agent_response() -> ResponseSchema:
    """Creates a mock response from the agent"""
    return ResponseSchema(message="Test summary\n\nTest article content\n\nMore content")


@pytest.fixture
def mock_agent_with_response(mock_agent_response):
    """Creates an ioc agent with a predefined response"""
    agent = Mock(spec=ArticleAgent)
    agent.send_message = Mock(return_value=mock_agent_response)
    agent.language = "русский"
    agent.min_paragraphs = 2
    return agent
