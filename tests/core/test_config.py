import pytest
from pathlib import Path
from pydantic import ValidationError

from src.core.config import Settings

class TestSettingsParseJson:
    @staticmethod
    def base_settings(**overrides):
        """
        Helper function to create Settings instance
        with default required fields.
        """

        base = {
            "APP_FILES_PATH": Path("/tmp"),
            "TITLE": "Test API",
            "DEFAULT_MODEL": "gpt",
            "DESCRIPTION": "Test description",
            "SUMMARY": "Test summary",
            "VERSION": "1.0.0",
            "CONTACT": {"name": "John"},
            "LICENSE_INFO": {"type": "MIT"},
        }

        base.update(overrides)

        return Settings(**base)


    def test_parse_json_valid_dict_string(self):
        """
        Test that valid JSON string is parsed into dict.
        """

        settings = self.base_settings(
            CONTACT='{"name": "Alice", "email": "test@mail.com"}'
        )

        assert isinstance(settings.CONTACT, dict)
        assert settings.CONTACT["name"] == "Alice"
        assert settings.CONTACT["email"] == "test@mail.com"


    def test_parse_json_valid_list_string(self):
        """
        Test that valid JSON list string is parsed into list.
        """

        settings = self.base_settings(
            ALLOW_ORIGINS='["https://example.com", "https://test.com"]'
        )

        assert isinstance(settings.ALLOW_ORIGINS, list)
        assert len(settings.ALLOW_ORIGINS) == 2
        assert settings.ALLOW_ORIGINS[0] == "https://example.com"


    def test_parse_json_already_dict(self):
        """
        Test that dict value is accepted and preserved semantically.
        """

        contact = {"name": "Bob"}

        settings = self.base_settings(CONTACT=contact)

        assert isinstance(settings.CONTACT, dict)
        assert settings.CONTACT["name"] == "Bob"


    def test_parse_json_already_list(self):
        """
        Test that list value is accepted and preserved.
        """

        origins = ["*"]

        settings = self.base_settings(ALLOW_ORIGINS=origins)

        assert isinstance(settings.ALLOW_ORIGINS, list)
        assert settings.ALLOW_ORIGINS == origins


    def test_parse_json_invalid_json_for_dict(self):
        """
        Test that invalid JSON string for dict field
        raises validation error.
        """

        with pytest.raises(ValidationError):
            self.base_settings(
                CONTACT='{"name": "Alice"'  # broken JSON
            )


    def test_parse_json_plain_string_for_dict(self):
        """
        Test that plain string for dict field
        raises validation error.
        """

        with pytest.raises(ValidationError):
            self.base_settings(
                CONTACT="not a json"
            )


    def test_parse_json_invalid_json_for_list(self):
        """
        Test that invalid JSON for list field
        raises validation error.
        """

        with pytest.raises(ValidationError):
            self.base_settings(
                ALLOW_ORIGINS='["test", "prod"'  # broken JSON
            )


    def test_parse_json_plain_string_for_list(self):
        """
        Test that plain string for list field
        raises validation error.
        """

        with pytest.raises(ValidationError):
            self.base_settings(
                ALLOW_ORIGINS="localhost"
            )


    def test_parse_json_bool_field_untouched(self):
        """
        Test that non-JSON fields are not affected.
        """

        settings = self.base_settings(ALLOW_CREDENTIALS=False)

        assert settings.ALLOW_CREDENTIALS is False
