import pytest
from unittest.mock import Mock, AsyncMock
from src.services.agent import Agent
from src.schemas.agent import ResponseSchema
from src.services.article_agent import ArticleAgent


@pytest.fixture
def mock_agent_response():
    """Fixture for creating an ioc agent response"""
    return ResponseSchema(
        message="success",
    )


@pytest.fixture
def mock_agent():
    """Fixture for creating an ioc agent"""
    agent = Mock(spec=Agent)
    agent.send_message = Mock(return_value=ResponseSchema(
        message="success",
    ))
    return agent


@pytest.fixture
def mock_article_agent():
    """Fixture for article agent mock"""
    agent = Mock(spec=ArticleAgent)
    agent.generate = Mock()
    return agent


@pytest.fixture
def async_mock_agent():
    """Fixture for creating an asynchronous ioc agent"""
    agent = Mock(spec=Agent)
    agent.send_message = AsyncMock(return_value=ResponseSchema(
        message="success",
    ))
    return agent
