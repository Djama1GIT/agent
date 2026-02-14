import pytest
from unittest.mock import Mock, patch
from typing import Any

from src.core.config import Settings
from src.services.agent import Agent, G4FClientAdapter, AIClient
from src.schemas.agent import ResponseSchema, AgentConfig
from src.core.errors.agent import AgentException


class TestG4FClientAdapter:
    """Tests for the G4F client adapter"""

    @patch('src.services.agent.Client')
    def test_chat_completion_success(self, mock_g4f_client: Mock):
        """G4F Response Success Test"""
        # Arrange
        mock_completion = Mock()
        mock_completion.choices = [Mock()]
        mock_completion.choices[0].message.content = "Test response"

        mock_g4f_instance = Mock()
        mock_g4f_instance.chat.completions.create.return_value = mock_completion
        mock_g4f_client.return_value = mock_g4f_instance

        adapter = G4FClientAdapter()

        # Act
        result = adapter.chat_completion(
            model="test-model",
            messages=[{"role": "user", "content": "Hello"}],
            web_search=False
        )

        # Assert
        assert result == "Test response"
        mock_g4f_instance.chat.completions.create.assert_called_once_with(
            model="test-model",
            messages=[{"role": "user", "content": "Hello"}],
            web_search=False
        )

    @patch('src.services.agent.Client')
    def test_chat_completion_error(self, mock_g4f_client: Mock):
        """Error handling test when requesting G4F"""
        # Arrange
        mock_g4f_instance = Mock()
        mock_g4f_instance.chat.completions.create.side_effect = Exception("API Error")
        mock_g4f_client.return_value = mock_g4f_instance

        adapter = G4FClientAdapter()

        # Act & Assert
        with pytest.raises(AgentException) as exc_info:
            adapter.chat_completion(
                model="test-model",
                messages=[],
                web_search=False
            )

        assert "AI service error" in str(exc_info.value)


class TestAgentInitialization:
    """Agent initialization tests"""

    def test_init_with_custom_config(self, agent_config: AgentConfig, mock_ai_client: Mock):
        """Initialization test with custom configuration"""
        agent = Agent(config=agent_config, ai_client=mock_ai_client)

        assert agent.config == agent_config
        assert agent.ai_client == mock_ai_client

    def test_init_with_default_config(self, mock_settings):
        """Initialization test with default configuration"""
        agent = Agent(settings=mock_settings)

        assert isinstance(agent.config, AgentConfig)
        assert isinstance(agent.ai_client, G4FClientAdapter)
        assert agent.config.model == "test-model"
        assert agent.config.web_search is False

    def test_create_default_config(self, mock_settings):
        """Default configuration creation test"""
        # Arrange
        mock_settings.DEFAULT_MODEL = "gpt-4"

        # Act
        config = Agent(settings=mock_settings)._create_default_config()

        # Assert
        assert config.model == "gpt-4"
        assert config.web_search is False
        assert isinstance(config.settings, Settings)


class TestAgentSendMessage:
    """send_message method tests"""

    def test_send_message_success(self, agent: Agent, mock_ai_client: Mock):
        """Successful message sending test"""
        # Arrange
        expected_response = "Test AI response"
        mock_ai_client.chat_completion.return_value = expected_response

        # Act
        response = agent.send_message("Hello, AI!")

        # Assert
        assert isinstance(response, ResponseSchema)
        assert response.message == expected_response

        # We check that the client was called with the correct parameters
        mock_ai_client.chat_completion.assert_called_once()
        call_args = mock_ai_client.chat_completion.call_args[1]
        assert call_args['model'] == agent.config.model
        assert call_args['web_search'] == agent.config.web_search
        assert len(call_args['messages']) == 1
        assert call_args['messages'][0]['role'] == "user"
        assert call_args['messages'][0]['content'] == "Hello, AI!"

    @pytest.mark.parametrize("invalid_message", [
        "",
        "   ",
        "\n",
        "\t",
        None
    ])
    def test_send_message_empty_input(self, agent: Agent, invalid_message: Any):
        """Test sending an empty message"""
        with pytest.raises(ValueError) as exc_info:
            agent.send_message(invalid_message)

        assert "Message cannot be empty" in str(exc_info.value)

    def test_send_message_ai_client_error(self, agent: Agent, mock_ai_client: Mock):
        """Error handling test from AI client"""
        # Arrange
        mock_ai_client.chat_completion.side_effect = Exception("Connection error")

        # Act & Assert
        with pytest.raises(AgentException) as exc_info:
            agent.send_message("Hello")

        assert "Failed to communicate with AI" in str(exc_info.value)

    def test_send_message_with_different_models(self, mock_settings: Settings):
        """Test of working with different models"""
        # Arrange
        mock_client = Mock(spec=AIClient)
        mock_client.chat_completion = Mock(return_value="Response")

        # Test with different models
        models = ["gpt-4", "gpt-3.5-turbo", "claude-2"]

        for model in models:
            # Creating a new configuration for each model
            config = AgentConfig(
                model=model,
                web_search=False,
                settings=mock_settings,
            )
            agent = Agent(config=config, ai_client=mock_client)

            # Act
            agent.send_message("Test")

            # Assert
            mock_client.chat_completion.assert_called_with(
                model=model,
                messages=[{'role': 'user', 'content': 'Test'}],
                web_search=False
            )

    def test_send_message_with_web_search_enabled(self, agent_config: AgentConfig, mock_ai_client: Mock):
        """Test of sending a message with web search enabled"""
        # Arrange
        config = AgentConfig(
            model=agent_config.model,
            web_search=True,
            settings=agent_config.settings,
        )
        agent = Agent(config=config, ai_client=mock_ai_client)
        mock_ai_client.chat_completion.return_value = "Response with web search"

        # Act
        agent.send_message("Search something")

        # Assert
        mock_ai_client.chat_completion.assert_called_once()
        assert mock_ai_client.chat_completion.call_args[1]['web_search'] is True


class TestAgentEdgeCases:
    """Boundary case tests"""

    def test_concurrent_messages(self, agent: Agent, mock_ai_client: Mock):
        """Test for sending multiple messages sequentially"""
        # Arrange
        responses = ["Response 1", "Response 2", "Response 3"]
        mock_ai_client.chat_completion.side_effect = responses

        # Act
        results = []
        for msg in ["First", "Second", "Third"]:
            response = agent.send_message(msg)
            results.append(response.message)

        # Assert
        assert results == responses
        assert mock_ai_client.chat_completion.call_count == 3

    def test_special_characters_in_message(self, agent: Agent, mock_ai_client: Mock):
        """Test for sending messages with special characters"""
        # Arrange
        special_message = "Hello! @#$%^&*()_+{}[]|\\:;'<>?,./"
        mock_ai_client.chat_completion.return_value = "Response with special chars"

        # Act
        response = agent.send_message(special_message)

        # Assert
        assert response.message == "Response with special chars"
        call_args = mock_ai_client.chat_completion.call_args[1]
        assert call_args['messages'][0]['content'] == special_message

    def test_very_long_response(self, agent: Agent, mock_ai_client: Mock):
        """Very long response processing test"""
        # Arrange
        long_response = "x" * 10000
        mock_ai_client.chat_completion.return_value = long_response

        # Act
        response = agent.send_message("Generate long text")

        # Assert
        assert len(response.message) == 10000
        assert response.message == long_response


class TestAgentLogging:
    """Logging verification tests"""

    def test_info_logging_on_init(self, caplog, mock_settings):
        """Logging test during initialization"""
        mock_settings.DEFAULT_MODEL = "test-model"

        with caplog.at_level("INFO"):
            Agent(settings=mock_settings)

        assert any(f"Agent initialized with model: test-model" in record.message
                   for record in caplog.records)

    def test_debug_logging_on_send(self, agent: Agent, mock_ai_client: Mock, caplog):
        """Debug logging test when sending a message"""
        # Arrange
        mock_ai_client.chat_completion.return_value = "Response"

        # Act
        with caplog.at_level("DEBUG"):
            agent.send_message("Test message")

        # Assert
        debug_messages = [record.message for record in caplog.records if record.levelname == "DEBUG"]
        assert any("Sending message to agent:" in msg for msg in debug_messages)
        assert any("Received response from agent" in msg for msg in debug_messages)

    def test_error_logging_on_failure(self, agent: Agent, mock_ai_client: Mock, caplog):
        """Error logging test"""
        # Arrange
        mock_ai_client.chat_completion.side_effect = Exception("Test error")

        # Act
        with caplog.at_level("ERROR"):
            with pytest.raises(AgentException):
                agent.send_message("Hello")

        # Assert
        assert any("Failed to send message: Test error" in record.message
                   for record in caplog.records)


class TestAgentIntegration:
    """Integration tests (with real components, but locked external services)"""

    @patch('src.services.agent.Client')
    def test_real_adapter_with_mock(self, mock_g4f_client: Mock, mock_settings: Settings):
        """Test of a real adapter with a locked G4F client"""
        # Arrange
        mock_settings.DEFAULT_MODEL = "test-model"

        mock_completion = Mock()
        mock_completion.choices = [Mock()]
        mock_completion.choices[0].message.content = "Real adapter response"

        mock_g4f_instance = Mock()
        mock_g4f_instance.chat.completions.create.return_value = mock_completion
        mock_g4f_client.return_value = mock_g4f_instance

        # Creating an agent with a real adapter
        agent = Agent(settings=mock_settings)

        # Act
        response = agent.send_message("Hello")

        # Assert
        assert response.message == "Real adapter response"
        mock_g4f_instance.chat.completions.create.assert_called_once()
