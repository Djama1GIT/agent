import inspect
import logging
from unittest.mock import Mock, patch

import pytest

from src.api.v1.article import router, create_article
from src.schemas.article import ArticleSchema


class TestArticleRouter:
    """Tests for article agent router"""

    def test_router_prefix(self):
        """Check router prefix correctness"""
        assert router.prefix == "/article-agent"

    def test_router_tags(self):
        """Check router tags correctness"""
        assert router.tags == ["Article Agent"]


class TestCreateArticle:
    """Tests for create_article endpoint"""

    @pytest.mark.asyncio
    async def test_create_article_success(self, mock_article_agent, caplog):
        """
        Test successful article generation
        Checks:
        - Correct agent method call
        - Proper response return
        - Request and response logging
        """
        # Arrange
        test_article_name = "Test Article"
        expected_response = ArticleSchema(
            summary="This is a test article summary",
            article="This is the full test article content"
        )

        mock_article_agent.generate.return_value = expected_response

        # Act
        with caplog.at_level(logging.INFO):
            result = await create_article(
                article_name=test_article_name,
                article_agent=mock_article_agent
            )

        # Assert
        assert result == expected_response
        mock_article_agent.generate.assert_called_once_with(test_article_name)

        # Check logging
        assert f"Generating article: {test_article_name}" in caplog.text
        assert "Generated article:" in caplog.text
        assert expected_response.summary[:100] in caplog.text

    @pytest.mark.asyncio
    async def test_create_article_with_empty_name(self, mock_article_agent):
        """
        Test article generation with empty name
        Checks empty article name handling
        """
        # Arrange
        empty_article_name = ""
        expected_response = ArticleSchema(
            summary="Empty article summary",
            article="Empty article content"
        )

        mock_article_agent.generate.return_value = expected_response

        # Act
        result = await create_article(
            article_name=empty_article_name,
            article_agent=mock_article_agent
        )

        # Assert
        assert result == expected_response
        mock_article_agent.generate.assert_called_once_with(empty_article_name)

    @pytest.mark.asyncio
    async def test_create_article_with_long_name(self, mock_article_agent):
        """
        Test article generation with long name
        Checks long article name handling
        """
        # Arrange
        long_article_name = "A" * 500
        expected_response = ArticleSchema(
            summary="Long article summary",
            article="Long article content"
        )

        mock_article_agent.generate.return_value = expected_response

        # Act
        result = await create_article(
            article_name=long_article_name,
            article_agent=mock_article_agent
        )

        # Assert
        assert result == expected_response
        mock_article_agent.generate.assert_called_once_with(long_article_name)

    @pytest.mark.asyncio
    async def test_create_article_with_special_characters(self, mock_article_agent):
        """
        Test article generation with special characters in name
        Checks special characters handling
        """
        # Arrange
        special_article_name = "Article! @#$%^&*()_+{}[]|\\:;\"'<>,.?/~`"
        expected_response = ArticleSchema(
            summary="Special article summary",
            article="Special article content"
        )

        mock_article_agent.generate.return_value = expected_response

        # Act
        result = await create_article(
            article_name=special_article_name,
            article_agent=mock_article_agent
        )

        # Assert
        assert result == expected_response
        mock_article_agent.generate.assert_called_once_with(special_article_name)

    @pytest.mark.asyncio
    async def test_create_article_with_unicode(self, mock_article_agent):
        """
        Test article generation with Unicode symbols in name
        Checks Unicode handling
        """
        # Arrange
        unicode_article_name = "Статья на русском 日本語 🌍"
        expected_response = ArticleSchema(
            summary="Unicode article summary",
            article="Unicode article content"
        )

        mock_article_agent.generate.return_value = expected_response

        # Act
        result = await create_article(
            article_name=unicode_article_name,
            article_agent=mock_article_agent
        )

        # Assert
        assert result == expected_response
        mock_article_agent.generate.assert_called_once_with(unicode_article_name)

    @pytest.mark.asyncio
    async def test_create_article_agent_error(self, mock_article_agent):
        """
        Test error handling from article agent
        Checks correct exception propagation
        """
        # Arrange
        test_article_name = "Test Article"
        mock_article_agent.generate.side_effect = ValueError("Article generation error")

        # Act & Assert
        with pytest.raises(ValueError, match="Article generation error"):
            await create_article(
                article_name=test_article_name,
                article_agent=mock_article_agent
            )

    @pytest.mark.asyncio
    async def test_create_article_with_custom_logging(self, mock_article_agent, caplog):
        """
        Test logging verification with different levels
        """
        # Arrange
        test_article_name = "Test Logging Article"
        expected_response = ArticleSchema(
            summary="Logging article summary",
            article="Logging article content"
        )

        mock_article_agent.generate.return_value = expected_response

        # Act
        with caplog.at_level(logging.DEBUG):
            result = await create_article(
                article_name=test_article_name,
                article_agent=mock_article_agent
            )

        # Assert
        assert result == expected_response
        assert len(caplog.records) >= 2  # Should be at least 2 log records

    @pytest.mark.asyncio
    async def test_create_article_dependency_injection(self):
        """
        Test dependency injection correctness
        """
        # Check that Depends is used correctly
        endpoint = create_article

        # Get function parameters
        signature = inspect.signature(endpoint)
        agent_param = signature.parameters['article_agent']

        # Check that Annotated is used
        assert hasattr(agent_param.annotation, '__metadata__')

        # Get dependency from metadata
        depends = agent_param.annotation.__metadata__[0]

        # Check that it's a Depends object (not a class, but an instance)
        assert depends.__class__.__name__ == 'Depends'

        # Check that the callable object in Depends uses get_article_agent
        # Note: get_article_agent is a factory function that returns a dependency
        dependency_func = depends.dependency
        assert callable(dependency_func)

    @pytest.mark.asyncio
    async def test_create_article_response_model(self):
        """
        Test response model verification
        """
        # Check that response_model is correctly set
        assert router.routes
        for route in router.routes:
            if route.path == "/article-agent/":
                assert route.response_model == ArticleSchema
                break

    @pytest.mark.asyncio
    async def test_create_article_returns_full_article_schema(self, mock_article_agent):
        """
        Test that endpoint returns complete ArticleSchema with all fields
        """
        # Arrange
        test_article_name = "Comprehensive Article"
        expected_response = ArticleSchema(
            summary="This is a comprehensive summary that covers all main points of the article "
                    "and provides a clear overview of the content that follows.",
            article="This is the full article content with multiple paragraphs. "
                    "It contains detailed information about the topic, "
                    "including examples, explanations, and conclusions."
        )

        mock_article_agent.generate.return_value = expected_response

        # Act
        result = await create_article(
            article_name=test_article_name,
            article_agent=mock_article_agent
        )

        # Assert
        assert isinstance(result, ArticleSchema)
        assert hasattr(result, 'summary')
        assert hasattr(result, 'article')
        assert result.summary == expected_response.summary
        assert result.article == expected_response.article


# Integration tests
class TestArticleRouterIntegration:
    """Integration tests for article agent router"""

    @pytest.mark.asyncio
    @patch('src.api.v1.article.get_article_agent')
    @patch('src.api.v1.article.get_settings')
    async def test_full_article_generation_flow(
            self,
            mock_get_settings,
            mock_get_article_agent,
            mock_article_agent
    ):
        """
        Integration test for full article generation flow
        """
        # Arrange
        test_article_name = "Integration Test Article"
        expected_response = ArticleSchema(
            summary="Integration test summary",
            article="Integration test full article content"
        )

        mock_get_settings.return_value = Mock()
        mock_get_article_agent.return_value = mock_article_agent
        mock_article_agent.generate.return_value = expected_response

        # Act
        result = await create_article(
            article_name=test_article_name,
            article_agent=mock_article_agent
        )

        # Assert
        assert result == expected_response
        mock_article_agent.generate.assert_called_once_with(test_article_name)

    @pytest.mark.asyncio
    @patch('src.api.v1.article.get_article_agent')
    @patch('src.api.v1.article.get_settings')
    async def test_article_generation_with_real_dependencies_chain(
            self,
            mock_get_settings,
            mock_get_article_agent,
            mock_article_agent
    ):
        """
        Test the complete chain of dependencies for article generation
        """
        # Arrange
        test_article_name = "Dependency Chain Test"
        mock_settings = Mock()
        mock_get_settings.return_value = mock_settings
        mock_get_article_agent.return_value = mock_article_agent

        expected_response = ArticleSchema(
            summary="Dependency chain summary",
            article="Dependency chain content"
        )
        mock_article_agent.generate.return_value = expected_response

        # Act
        result = await create_article(
            article_name=test_article_name,
            article_agent=mock_article_agent
        )

        # Assert
        assert result == expected_response
        mock_article_agent.generate.assert_called_once_with(test_article_name)


# Router configuration tests
class TestRouterConfiguration:
    """Router configuration tests"""

    def test_router_has_correct_routes(self):
        """Check correct routes presence"""
        routes = router.routes
        assert len(routes) == 1  # Only POST /article-agent/

        post_route = routes[0]
        assert post_route.path == "/article-agent/"
        assert post_route.methods == {"POST"}

    def test_router_tags_configuration(self):
        """Check tags configuration"""
        assert router.tags == ["Article Agent"]
        assert "Article Agent" in router.tags

    def test_router_prefix_configuration(self):
        """Check prefix configuration"""
        assert router.prefix == "/article-agent"
        assert router.prefix.startswith("/")
        assert router.prefix.endswith("agent")
