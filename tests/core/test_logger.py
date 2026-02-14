import pytest
import configparser
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.core.logger import configure_logging


class TestConfigureLoggingBasic:
    """Basic tests for configure_logging function."""

    def test_configure_logging_without_settings(self):
        """Test configure_logging when called without settings parameter."""
        with patch("src.core.logger.Settings") as mock_settings_class:
            mock_settings = MagicMock()
            mock_settings_class.return_value = mock_settings
            mock_settings.APP_FILES_PATH = Path("/app/files")

            with patch("configparser.ConfigParser.read") as mock_read:
                with patch("logging.config.fileConfig") as mock_file_config:
                    configure_logging()

                    mock_settings_class.assert_called_once()
                    mock_read.assert_called_once_with(mock_settings.APP_FILES_PATH / "logger.ini")
                    mock_file_config.assert_called_once()

    def test_configure_logging_with_settings(self, mock_settings):
        """Test configure_logging with provided settings parameter."""
        with patch("configparser.ConfigParser.read") as mock_read:
            with patch("logging.config.fileConfig") as mock_file_config:
                with patch("src.core.logger.Settings") as mock_settings_class:
                    configure_logging(settings=mock_settings)

                    # Settings should not be called again
                    mock_settings_class.assert_not_called()
                    mock_read.assert_called_once_with(mock_settings.APP_FILES_PATH / "logger.ini")
                    mock_file_config.assert_called_once()

    def test_config_parser_initialization(self, mock_settings):
        """Test that ConfigParser is properly initialized."""
        with patch("configparser.ConfigParser") as mock_config_parser_class:
            mock_config = MagicMock()
            mock_config_parser_class.return_value = mock_config
            mock_config.sections.return_value = []

            with patch("logging.config.fileConfig"):
                configure_logging(settings=mock_settings)

                mock_config_parser_class.assert_called_once()
                mock_config.read.assert_called_once_with(mock_settings.APP_FILES_PATH / "logger.ini")

    def test_file_not_found_handling(self, mock_settings):
        """Test behavior when logger.ini file is not found."""
        with patch("configparser.ConfigParser.read", return_value=[]):
            with patch("logging.config.fileConfig") as mock_file_config:
                with patch("configparser.ConfigParser.sections", return_value=[]):
                    with patch("configparser.ConfigParser", return_value=configparser.ConfigParser()):
                        # Should not raise exception, just continue with empty config
                        configure_logging(settings=mock_settings)
                        mock_file_config.assert_called_once()


class TestFileHandlerPathModification:
    """Tests for file handler path modification functionality."""

    def test_file_handler_path_modification(self, mock_settings, sample_logger_ini):
        """Test that file handler path is modified when it's just a filename."""
        mock_config = configparser.ConfigParser()
        mock_config.read_string(sample_logger_ini)

        with patch("configparser.ConfigParser.read", return_value=None):
            with patch("configparser.ConfigParser.sections", return_value=["handler_fileHandler"]):
                with patch("logging.config.fileConfig") as mock_file_config:
                    with patch("configparser.ConfigParser.set") as mock_set:
                        with patch.object(mock_config, 'sections', return_value=["handler_fileHandler"]):
                            with patch.object(mock_config, '__getitem__', mock_config.__getitem__):
                                with patch.object(mock_config, 'set', mock_set):
                                    with patch("configparser.ConfigParser", return_value=mock_config):
                                        configure_logging(settings=mock_settings)

                                        # Verify that set was called to modify the path
                                        mock_set.assert_called_once()
                                        args = mock_set.call_args[0]
                                        assert args[0] == "handler_fileHandler"
                                        assert args[1] == "args"
                                        assert str(Path(__file__) / "/app.log") in args[2]

    def test_file_handler_path_not_modified_when_absolute(self, mock_settings):
        """Test that file handler path is not modified when it's already an absolute path."""
        # Create config with absolute path
        mock_config = configparser.ConfigParser()
        mock_config.read_string("""
    [loggers]
    keys=root

    [handlers]
    keys=fileHandler

    [logger_root]
    level=INFO
    handlers=fileHandler

    [handler_fileHandler]
    class=logging.FileHandler
    level=INFO
    formatter=simpleFormatter
    args=('/var/log/app.log', 'a')
    """)

        with patch("configparser.ConfigParser.read", return_value=None):
            with patch("configparser.ConfigParser.sections", return_value=["handler_fileHandler"]):
                with patch("logging.config.fileConfig") as mock_file_config:
                    with patch("configparser.ConfigParser.set") as mock_set:
                        with patch.object(mock_config, 'sections', return_value=["handler_fileHandler"]):
                            with patch("configparser.ConfigParser", return_value=mock_config):
                                configure_logging(settings=mock_settings)

                                # Verify that set was NOT called
                                mock_set.assert_not_called()
                                mock_file_config.assert_called_once()

    def test_no_file_handler_section(self, mock_settings, sample_logger_ini):
        """Test when logger.ini doesn't have fileHandler section."""
        # Create config without fileHandler
        mock_config = configparser.ConfigParser()
        mock_config.read_string("""
    [loggers]
    keys=root

    [handlers]
    keys=consoleHandler

    [logger_root]
    level=INFO
    handlers=consoleHandler

    [handler_consoleHandler]
    class=logging.StreamHandler
    level=INFO
    formatter=simpleFormatter
    args=(sys.stdout,)
    """)

        with patch("configparser.ConfigParser.read", return_value=None):
            with patch("configparser.ConfigParser.sections", return_value=[]):
                with patch("logging.config.fileConfig") as mock_file_config:
                    with patch("configparser.ConfigParser.set") as mock_set:
                        with patch.object(mock_config, 'sections', return_value=[]):
                            with patch("configparser.ConfigParser", return_value=mock_config):
                                configure_logging(settings=mock_settings)

                                # Verify that set was NOT called
                                mock_set.assert_not_called()
                                mock_file_config.assert_called_once()

    def test_file_handler_path_modification_edge_case(self, mock_settings):
        """Test file handler path modification with complex args format."""
        # Create config with more complex args format
        mock_config = configparser.ConfigParser()
        mock_config.read_string("""
    [handler_fileHandler]
    class=logging.FileHandler
    level=INFO
    formatter=simpleFormatter
    args=('app.log', 'a', True)
    """)

        # Сохраняем оригинальные значения для проверки
        original_args = mock_config["handler_fileHandler"]["args"]

        with patch("configparser.ConfigParser.read", return_value=None):
            with patch("configparser.ConfigParser.sections", return_value=["handler_fileHandler"]):
                with patch("logging.config.fileConfig") as mock_file_config:
                    with patch("configparser.ConfigParser.set") as mock_set:
                        with patch.object(mock_config, 'sections', return_value=["handler_fileHandler"]):
                            with patch.object(mock_config, '__getitem__', mock_config.__getitem__):
                                with patch.object(mock_config, 'set', mock_set):
                                    with patch("configparser.ConfigParser", return_value=mock_config):
                                        configure_logging(settings=mock_settings)

                                        # Verify that set was called to modify the path
                                        mock_set.assert_called_once()
                                        args = mock_set.call_args[0]
                                        assert args[0] == "handler_fileHandler"
                                        assert args[1] == "args"

                                        # Check that the path was updated
                                        new_args = args[2]
                                        assert str(Path(__file__).parent.parent.parent / "app.log") in new_args

                                        # Выводим фактическое значение для отладки
                                        print(f"Original args: {original_args}")
                                        print(f"New args: {new_args}")

    def test_file_handler_path_modification_with_extra_spaces(self, mock_settings):
        """Test path modification when args have extra spaces."""
        mock_config = configparser.ConfigParser()
        mock_config.read_string("""
    [handler_fileHandler]
    class=logging.FileHandler
    level=INFO
    formatter=simpleFormatter
    args=('app.log',   'a'  ,  True  )
    """)

        with patch("configparser.ConfigParser.read", return_value=None):
            with patch("configparser.ConfigParser.sections", return_value=["handler_fileHandler"]):
                with patch("logging.config.fileConfig") as mock_file_config:
                    with patch("configparser.ConfigParser.set") as mock_set:
                        with patch.object(mock_config, 'sections', return_value=["handler_fileHandler"]):
                            with patch.object(mock_config, '__getitem__', mock_config.__getitem__):
                                with patch.object(mock_config, 'set', mock_set):
                                    with patch("configparser.ConfigParser", return_value=mock_config):
                                        configure_logging(settings=mock_settings)

                                        mock_set.assert_called_once()
                                        new_args = mock_set.call_args[0][2]

                                        # Check that path is updated
                                        assert str(Path(__file__).parent.parent.parent / "app.log") in new_args
                                        # Check that the rest of the args are present
                                        assert "a" in new_args or "'a'" in new_args or '"a"' in new_args
                                        assert "True" in new_args


class TestFileHandlerArgsValidation:
    """Tests for file handler args format validation."""

    def test_invalid_file_handler_args_format_first_regex(self, mock_settings):
        """Test ValueError when first regex pattern fails to match args format."""
        # Create config with invalid args format for first regex
        mock_config = configparser.ConfigParser()
        mock_config.read_string("""
    [handler_fileHandler]
    class=logging.FileHandler
    args=invalid_format_without_quotes
    """)

        with patch("configparser.ConfigParser.read", return_value=None):
            with patch("configparser.ConfigParser.sections", return_value=["handler_fileHandler"]):
                with patch.object(mock_config, 'sections', return_value=["handler_fileHandler"]):
                    with patch("configparser.ConfigParser", return_value=mock_config):
                        with patch.object(mock_config, '__getitem__', return_value=mock_config["handler_fileHandler"]):
                            with pytest.raises(ValueError, match="Invalid fileHandler args format in logger.ini"):
                                configure_logging(settings=mock_settings)

    def test_invalid_file_handler_args_format_second_regex(self, mock_settings):
        """Test ValueError when second regex pattern fails to match args format during reconstruction."""
        # Create config with valid format for first regex but problematic for second
        mock_config = configparser.ConfigParser()
        # The first regex will match, but second regex needs to fail
        mock_config.read_string("""
    [handler_fileHandler]
    class=logging.FileHandler
    args=('app.log', 'a')
    """)

        with patch("configparser.ConfigParser.read", return_value=None):
            with patch("configparser.ConfigParser.sections", return_value=["handler_fileHandler"]):
                with patch.object(mock_config, 'sections', return_value=["handler_fileHandler"]):
                    with patch("configparser.ConfigParser", return_value=mock_config):
                        with patch.object(mock_config, '__getitem__', return_value=mock_config["handler_fileHandler"]):
                            # Mock the first regex to succeed but second to fail
                            with patch("re.match") as mock_re_match:
                                # First call to re.match succeeds
                                first_match = MagicMock()
                                first_match.__getitem__.side_effect = lambda x: ["", "", "", "app.log"][x]
                                first_match.group.return_value = "app.log"

                                # Second call to re.match returns None (fails)
                                mock_re_match.side_effect = [first_match, None]

                                with pytest.raises(ValueError, match="Invalid fileHandler args format in logger.ini"):
                                    configure_logging(settings=mock_settings)

                                # Verify both regex matches were attempted
                                assert mock_re_match.call_count == 2


class TestLoggingConfiguration:
    """Tests for logging configuration behavior."""

    def test_logging_configured_with_disable_existing_loggers_false(self, mock_settings, sample_logger_ini):
        """Test that logging.config.fileConfig is called with disable_existing_loggers=False."""
        mock_config = configparser.ConfigParser()
        mock_config.read_string(sample_logger_ini)

        with patch("configparser.ConfigParser.read", return_value=None):
            with patch("configparser.ConfigParser.sections", return_value=["handler_fileHandler"]):
                with patch("logging.config.fileConfig") as mock_file_config:
                    with patch.object(mock_config, 'sections', return_value=["handler_fileHandler"]):
                        with patch("configparser.ConfigParser", return_value=mock_config):
                            configure_logging(settings=mock_settings)

                            # Verify fileConfig was called with correct parameters
                            mock_file_config.assert_called_once_with(
                                mock_config,
                                disable_existing_loggers=False
                            )
