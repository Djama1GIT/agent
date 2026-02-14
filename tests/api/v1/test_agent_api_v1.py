import inspect
import logging

import pytest
from unittest.mock import Mock, patch

from src.api.v1.agent import router, send_message
from src.schemas.agent import ResponseSchema


class TestAgentRouter:
    """Tests for agent router"""

    def test_router_prefix(self):
        """Check router prefix correctness"""
        assert router.prefix == "/agent"

    def test_router_tags(self):
        """Check router tags correctness"""
        assert router.tags == ["Agent"]


class TestSendMessage:
    """Tests for send_message endpoint"""

    @pytest.mark.asyncio
    async def test_send_message_success(self, mock_agent, caplog):
        """
        Test successful message sending
        Checks:
        - Correct agent method call
        - Proper response return
        - Request and response logging
        """
        # Arrange
        test_message = "Hello, agent!"
        expected_response = ResponseSchema(
            message="success"
        )

        mock_agent.send_message.return_value = expected_response

        # Act
        with caplog.at_level(logging.INFO):
            result = await send_message(
                message=test_message,
                agent=mock_agent
            )

        # Assert
        assert result == expected_response
        mock_agent.send_message.assert_called_once_with(test_message)

        # Check logging
        assert f"Sending message: {test_message}" in caplog.text
        assert "Received response:" in caplog.text

    @pytest.mark.asyncio
    async def test_send_message_with_empty_message(self, mock_agent):
        """
        Test sending empty message
        Checks empty message handling
        """
        # Arrange
        empty_message = ""
        expected_response = ResponseSchema(
            message="warning"
        )

        mock_agent.send_message.return_value = expected_response

        # Act
        result = await send_message(
            message=empty_message,
            agent=mock_agent
        )

        # Assert
        assert result == expected_response
        mock_agent.send_message.assert_called_once_with(empty_message)

    @pytest.mark.asyncio
    async def test_send_message_with_long_message(self, mock_agent):
        """
        Test sending long message
        Checks long text handling
        """
        # Arrange
        long_message = "a" * 10000
        expected_response = ResponseSchema(
            message="success"
        )

        mock_agent.send_message.return_value = expected_response

        # Act
        result = await send_message(
            message=long_message,
            agent=mock_agent
        )

        # Assert
        assert result == expected_response
        mock_agent.send_message.assert_called_once_with(long_message)

    @pytest.mark.asyncio
    async def test_send_message_with_special_characters(self, mock_agent):
        """
        Test sending message with special characters
        Checks special characters handling
        """
        # Arrange
        special_message = "Hello! @#$%^&*()_+{}[]|\\:;\"'<>,.?/~`"
        expected_response = ResponseSchema(
            message="success"
        )

        mock_agent.send_message.return_value = expected_response

        # Act
        result = await send_message(
            message=special_message,
            agent=mock_agent
        )

        # Assert
        assert result == expected_response
        mock_agent.send_message.assert_called_once_with(special_message)

    @pytest.mark.asyncio
    async def test_send_message_with_unicode(self, mock_agent):
        """
        Test sending message with Unicode symbols
        Checks Unicode handling
        """
        # Arrange
        unicode_message = "Привет, мир! こんにちは 🌍"
        expected_response = ResponseSchema(
            message="success"
        )

        mock_agent.send_message.return_value = expected_response

        # Act
        result = await send_message(
            message=unicode_message,
            agent=mock_agent
        )

        # Assert
        assert result == expected_response
        mock_agent.send_message.assert_called_once_with(unicode_message)

    @pytest.mark.asyncio
    async def test_send_message_agent_error(self, mock_agent):
        """
        Test error handling from agent
        Checks correct exception propagation
        """
        # Arrange
        test_message = "Test message"
        mock_agent.send_message.side_effect = ValueError("Agent error")

        # Act & Assert
        with pytest.raises(ValueError, match="Agent error"):
            await send_message(
                message=test_message,
                agent=mock_agent
            )

    @pytest.mark.asyncio
    async def test_send_message_with_custom_logging(self, mock_agent, caplog):
        """
        Test logging verification with different levels
        """
        # Arrange
        test_message = "Test logging"
        expected_response = ResponseSchema(
            message="success"
        )

        mock_agent.send_message.return_value = expected_response

        # Act
        with caplog.at_level(logging.DEBUG):
            result = await send_message(
                message=test_message,
                agent=mock_agent
            )

        # Assert
        assert result == expected_response
        assert len(caplog.records) >= 2  # Should be at least 2 log records

    @pytest.mark.asyncio
    async def test_send_message_dependency_injection(self):
        """
        Test dependency injection correctness
        """
        # Check that Depends is used correctly
        endpoint = send_message

        # Get function parameters
        signature = inspect.signature(endpoint)
        agent_param = signature.parameters['agent']

        # Check that Annotated is used
        assert hasattr(agent_param.annotation, '__metadata__')

        # Get dependency from metadata
        depends = agent_param.annotation.__metadata__[0]

        # Check that it's a Depends object (not a class, but an instance)
        assert depends.__class__.__name__ == 'Depends'

        # Check that the callable object in Depends is get_agent
        assert depends.dependency.__name__ == '_get_agent'

    @pytest.mark.asyncio
    async def test_send_message_response_model(self):
        """
        Test response model verification
        """
        # Check that response_model is correctly set
        assert router.routes
        for route in router.routes:
            if route.path == "/agent/":
                assert route.response_model == ResponseSchema
                break


# Integration tests
class TestAgentRouterIntegration:
    """Integration tests for agent router"""

    @pytest.mark.asyncio
    @patch('src.api.v1.agent.get_agent')
    @patch('src.api.v1.agent.get_settings')
    async def test_full_message_flow(
            self,
            mock_get_settings,
            mock_get_agent,
            mock_agent
    ):
        """
        Integration test for full message sending flow
        """
        # Arrange
        test_message = "Integration test message"
        expected_response = ResponseSchema(
            message="success"
        )

        mock_get_settings.return_value = Mock()
        mock_get_agent.return_value = mock_agent
        mock_agent.send_message.return_value = expected_response

        # Act
        result = await send_message(
            message=test_message,
            agent=mock_agent
        )

        # Assert
        assert result == expected_response
        mock_agent.send_message.assert_called_once_with(test_message)


# Router configuration tests
class TestRouterConfiguration:
    """Router configuration tests"""

    def test_router_has_correct_routes(self):
        """Check correct routes presence"""
        routes = router.routes
        assert len(routes) == 1  # Only POST /agent/

        post_route = routes[0]
        assert post_route.path == "/agent/"
        assert post_route.methods == {"POST"}

    def test_router_tags_configuration(self):
        """Check tags configuration"""
        assert router.tags == ["Agent"]
        assert "Agent" in router.tags
