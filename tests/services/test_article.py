import pytest
from unittest.mock import Mock, patch

from src.services.article_agent import ArticleAgent, ArticlePrompt
from src.schemas.article import ArticleSchema
from src.schemas.agent import ResponseSchema
from src.core.errors.article import ArticleGenerationException


class TestArticlePrompt:
    """Tests for ArticlePrompt"""

    def test_init_with_default_template(self):
        """Initialization test with default template"""
        prompt = ArticlePrompt()
        assert prompt.template == ArticlePrompt.DEFAULT_TEMPLATE

    def test_init_with_custom_template(self):
        """Initialization test with a custom template"""
        custom_template = "Write article: {title} in {language}"
        prompt = ArticlePrompt(template=custom_template)
        assert prompt.template == custom_template

    def test_format_default_language(self):
        """Formatting test with default language"""
        prompt = ArticlePrompt()
        result = prompt.format(title="Test Title")

        assert "Test Title" in result
        assert "русский" in result
        assert result.startswith("Сгенерируй статью с названием: Test Title")

    def test_format_custom_language(self):
        """Formatting test with custom language"""
        prompt = ArticlePrompt()
        result = prompt.format(title="Test Title", language="English")

        assert "Test Title" in result
        assert "English" in result

    def test_format_with_custom_template(self):
        """Formatting test with custom template"""
        custom_template = "Generate {title} in {language}"
        prompt = ArticlePrompt(template=custom_template)
        result = prompt.format(title="Hello", language="English")

        assert result == "Generate Hello in English"


class TestArticleAgentInitialization:
    """ArticleAgent initialization tests"""

    def test_init_with_default_values(self, agent_config):
        """Initialization test with default values"""
        with patch('src.services.article_agent.Agent.__init__', return_value=None):
            agent = ArticleAgent(config=agent_config)

            assert isinstance(agent.prompt, ArticlePrompt)
            assert agent.language == "русский"
            assert agent.min_paragraphs == 2

    def test_init_with_custom_values(self, agent_config):
        """Initialization test with custom values"""
        with patch('src.services.article_agent.Agent.__init__', return_value=None):
            custom_template = "Custom template: {title}"
            agent = ArticleAgent(
                config=agent_config,
                prompt_template=custom_template,
                language="English",
                min_paragraphs=3
            )

            assert agent.prompt.template == custom_template
            assert agent.language == "English"
            assert agent.min_paragraphs == 3

    def test_init_calls_super(self, agent_config):
        """Parent Constructor call test"""
        with patch('src.services.article_agent.Agent.__init__') as mock_super_init:
            ArticleAgent(config=agent_config)
            mock_super_init.assert_called_once_with(agent_config)


class TestArticleAgentGenerate:
    """Tests of the generate method"""

    def test_generate_success(self, agent_config, mock_agent_response):
        """Successful article generation test"""
        # Arrange
        agent = ArticleAgent(config=agent_config)
        agent.send_message = Mock(return_value=mock_agent_response)

        # Act
        result = agent.generate("Test Title")

        # Assert
        assert isinstance(result, ArticleSchema)
        assert result.summary == "Test summary"
        assert result.article == "Test article content\n\nMore content"

        # Checking the send_message call
        agent.send_message.assert_called_once()
        call_args = agent.send_message.call_args[0][0]
        assert "Test Title" in call_args
        assert "русский" in call_args

    def test_generate_with_custom_language(self, agent_config, mock_agent_response):
        """Generation test in another language"""
        # Arrange
        agent = ArticleAgent(config=agent_config, language="English")
        agent.send_message = Mock(return_value=mock_agent_response)

        # Act
        result = agent.generate("Test Title")

        # Assert
        call_args = agent.send_message.call_args[0][0]
        assert "English" in call_args

    @pytest.mark.parametrize("invalid_title", [
        "",
        "   ",
        "\n",
        "\t",
        None
    ])
    def test_generate_empty_title(self, agent_config, invalid_title):
        """Generation test with an empty header"""
        agent = ArticleAgent(config=agent_config)

        with pytest.raises(ValueError) as exc_info:
            agent.generate(invalid_title)

        assert "Title cannot be empty" in str(exc_info.value)

    def test_generate_single_paragraph(self, agent_config):
        """Generation test when only one paragraph arrives"""
        # Arrange
        response = ResponseSchema(message="Only one paragraph")
        agent = ArticleAgent(config=agent_config)
        agent.send_message = Mock(return_value=response)

        # Act
        result = agent.generate("Test Title")

        # Assert
        assert result.summary == "Only one paragraph"
        assert result.article == ""

    def test_generate_with_empty_paragraphs(self, agent_config):
        """Generation test with empty paragraphs"""
        # Arrange
        response = ResponseSchema(message="First\n\n\n\nSecond\n\n\nThird")
        agent = ArticleAgent(config=agent_config)
        agent.send_message = Mock(return_value=response)

        # Act
        result = agent.generate("Test Title")

        # Assert
        assert result.summary == "First"
        assert result.article == "Second\n\nThird"

    def test_generate_with_whitespace_in_paragraphs(self, agent_config):
        """Generation test with gaps in paragraphs"""
        # Arrange
        response = ResponseSchema(message="  First  \n\n  Second  \n\n  Third  ")
        agent = ArticleAgent(config=agent_config)
        agent.send_message = Mock(return_value=response)

        # Act
        result = agent.generate("Test Title")

        # Assert
        assert result.summary == "First"
        assert result.article == "Second\n\nThird"

    def test_generate_agent_error(self, agent_config):
        """Error handling test from agent"""
        # Arrange
        agent = ArticleAgent(config=agent_config)
        agent.send_message = Mock(side_effect=Exception("Agent error"))

        # Act & Assert
        with pytest.raises(ArticleGenerationException) as exc_info:
            agent.generate("Test Title")

        assert "Article generation failed" in str(exc_info.value)

    def test_generate_empty_response(self, agent_config):
        """Generation test with an empty answer"""
        # Arrange
        response = ResponseSchema(message="")
        agent = ArticleAgent(config=agent_config)
        agent.send_message = Mock(return_value=response)

        # Act & Assert
        with pytest.raises(ArticleGenerationException) as exc_info:
            agent.generate("Test Title")

        assert "Generated article is empty" in str(exc_info.value)

    def test_generate_very_short_summary(self, agent_config, caplog):
        """Generation test with a very short summary"""
        # Arrange
        response = ResponseSchema(message="Short\n\nLong article content here")
        agent = ArticleAgent(config=agent_config)
        agent.send_message = Mock(return_value=response)

        # Act
        with caplog.at_level("WARNING"):
            result = agent.generate("Test Title")

        # Assert
        assert result.summary == "Short"
        assert result.article == "Long article content here"
        assert any("Summary is too short: 5 chars" in record.message
                   for record in caplog.records)


class TestArticleAgentParseArticle:
    """Tests for the static _parse_article method"""

    def test_parse_multiple_paragraphs(self):
        """Multi-paragraph parsing test"""
        text = "First paragraph\n\nSecond paragraph\n\nThird paragraph"
        summary, article = ArticleAgent._parse_article(text)

        assert summary == "First paragraph"
        assert article == "Second paragraph\n\nThird paragraph"

    def test_parse_single_paragraph(self):
        """Single paragraph parsing test"""
        text = "Only one paragraph"
        summary, article = ArticleAgent._parse_article(text)

        assert summary == "Only one paragraph"
        assert article == ""

    def test_parse_with_extra_newlines(self):
        """Parsing test with extra line breaks"""
        text = "First\n\n\n\nSecond\n\n\nThird"
        summary, article = ArticleAgent._parse_article(text)

        assert summary == "First"
        assert article == "Second\n\nThird"

    def test_parse_empty_text(self):
        """Blank text parsing test"""
        summary, article = ArticleAgent._parse_article("")

        assert summary == ""
        assert article == ""

    def test_parse_with_whitespace(self):
        """Parsing test with spaces"""
        text = "  First  \n\n  Second  \n\n  Third  "
        summary, article = ArticleAgent._parse_article(text)

        assert summary == "First"
        assert article == "Second\n\nThird"


class TestArticleAgentValidateArticle:
    """Tests for the static _validate_article method"""

    def test_validate_valid_article(self):
        """Validation test for a valid article"""
        # There should be no exception
        ArticleAgent._validate_article("Valid summary", "Valid article")

    def test_validate_empty_article(self):
        """Validation test for an empty article"""
        with pytest.raises(ArticleGenerationException) as exc_info:
            ArticleAgent._validate_article("", "")

        assert "Generated article is empty" in str(exc_info.value)

    def test_validate_empty_summary_with_article(self):
        """Validation test with an empty summary, but with an article"""
        # There should be no exception, because the article is not empty
        ArticleAgent._validate_article("", "Some article")

    def test_validate_short_summary(self, caplog):
        """Validation test with a short summary"""
        with caplog.at_level("WARNING"):
            ArticleAgent._validate_article("Short", "Valid article")

        assert any("Summary is too short: 5 chars" in record.message
                   for record in caplog.records)


class TestArticleAgentIntegration:
    """ArticleAgent integration tests"""

    @patch('src.services.article_agent.Agent.send_message')
    def test_generate_full_flow(self, mock_send_message, agent_config):
        """Full cycle article generation test"""
        # Arrange
        mock_send_message.return_value = ResponseSchema(
            message="A summary of the article.\n\nThe current text of the article.\n\nThe continuation of the text."
        )

        agent = ArticleAgent(config=agent_config)

        # Act
        result = agent.generate("Test article")

        # Assert
        assert isinstance(result, ArticleSchema)
        assert result.summary == "A summary of the article."
        assert result.article == "The current text of the article.\n\nThe continuation of the text."

        # Checking the prompt formation
        mock_send_message.assert_called_once()
        prompt = mock_send_message.call_args[0][0]
        assert "Test article" in prompt
        assert "русский" in prompt

    @patch('src.services.article_agent.Agent.send_message')
    def test_generate_with_min_paragraphs_check(self, mock_send_message, agent_config, caplog):
        """Minimum number of paragraphs verification test"""
        # Arrange
        mock_send_message.return_value = ResponseSchema(
            message="Just one paragraph",
        )

        agent = ArticleAgent(config=agent_config, min_paragraphs=2)

        # Act
        with caplog.at_level("WARNING"):
            result = agent.generate("Test")

        # Assert
        assert result.summary == "Just one paragraph"
        assert result.article == ""
        assert any("Not enough paragraphs" in record.message for record in caplog.records)


class TestArticleAgentLogging:
    """ArticleAgent logging tests"""

    def test_generate_info_logging(self, agent_config, mock_agent_response, caplog):
        """Information logging test during generation"""
        # Arrange
        agent = ArticleAgent(config=agent_config)
        agent.send_message = Mock(return_value=mock_agent_response)

        # Act
        with caplog.at_level("INFO"):
            result = agent.generate("Test Title")

        # Assert
        info_messages = [record.message for record in caplog.records if record.levelname == "INFO"]

        assert any("Generating article: 'Test Title' in русский" in msg for msg in info_messages)
        assert any("Successfully generated article" in msg for msg in info_messages)
        assert any("Summary length: 12" in msg for msg in info_messages)  # "Test summary" = 12 chars

    def test_generate_error_logging(self, agent_config, caplog):
        """Error logging test"""
        # Arrange
        agent = ArticleAgent(config=agent_config)
        agent.send_message = Mock(side_effect=Exception("Test error"))

        # Act
        with caplog.at_level("ERROR"):
            with pytest.raises(ArticleGenerationException):
                agent.generate("Test Title")

        # Assert
        error_messages = [record.message for record in caplog.records if record.levelname == "ERROR"]
        assert any("Failed to generate article 'Test Title': Test error" in msg for msg in error_messages)

    def test_warning_on_short_summary(self, agent_config, caplog):
        """Short summary warning test"""
        # Arrange
        response = ResponseSchema(message="Short\n\nLong article")
        agent = ArticleAgent(config=agent_config)
        agent.send_message = Mock(return_value=response)

        # Act
        with caplog.at_level("WARNING"):
            agent.generate("Test Title")

        # Assert
        warning_messages = [record.message for record in caplog.records if record.levelname == "WARNING"]
        assert any("Summary is too short: 5 chars" in msg for msg in warning_messages)


# Parameterized tests for different scenarios
class TestArticleAgentParameterized:
    """Parameterized tests"""

    @pytest.mark.parametrize("input_text,expected_summary,expected_article", [
        ("A\n\nB\n\nC", "A", "B\n\nC"),
        ("First\n\nSecond", "First", "Second"),
        ("Single", "Single", ""),
        ("  A  \n\n  B  ", "A", "B"),
        ("", "", ""),
    ])
    def test_parse_article_various_inputs(self, input_text, expected_summary, expected_article):
        """Parsing test with different input data"""
        summary, article = ArticleAgent._parse_article(input_text)
        assert summary == expected_summary
        assert article == expected_article

    @pytest.mark.parametrize("language", [
        "русский",
        "English",
        "Deutsche",
        "français",
        "español"
    ])
    def test_generate_with_different_languages(self, agent_config, language):
        """Generation test in different languages"""
        # Arrange
        agent = ArticleAgent(config=agent_config, language=language)
        agent.send_message = Mock(return_value=ResponseSchema(message="Test\n\nContent"))

        # Act
        agent.generate("Test")

        # Assert
        call_args = agent.send_message.call_args[0][0]
        assert language in call_args

    @pytest.mark.parametrize("summary_length,should_warn", [
        (5, True),  # Too short - there should be a warning
        (9, True),  # Too short - there should be a warning
        (10, False),  # Minimum length - without warning
        (100, False),  # Normal length - without warning
    ])
    def test_summary_length_warning(self, agent_config, summary_length, should_warn, caplog):
        """Summary length warnings test"""
        # Arrange
        summary = "x" * summary_length
        response = ResponseSchema(message=f"{summary}\n\nArticle")
        agent = ArticleAgent(config=agent_config)
        agent.send_message = Mock(return_value=response)

        # Act
        with caplog.at_level("WARNING"):
            agent.generate("Test")

        # Assert
        warning_messages = [record.message for record in caplog.records if record.levelname == "WARNING"]
        has_warning = any(f"Summary is too short: {summary_length} chars" in msg for msg in warning_messages)

        assert has_warning == should_warn