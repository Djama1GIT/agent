import logging.config
from typing import Optional

from src.core.config import Settings
import re
from pathlib import Path
import configparser


def configure_logging(settings: Optional[Settings] = None) -> None:
    # Load application settings
    settings = settings or Settings()  # type: ignore[call-arg]

    # Initialize and read logging configuration
    config = configparser.ConfigParser()
    config.read(settings.APP_FILES_PATH / "logger.ini")

    if "handler_fileHandler" in config.sections():
        """
        Adjust file handler path to be absolute within the application files directory.

        Processes the logging configuration to ensure file paths are properly resolved:
        1. Checks if the fileHandler path is just a filename (no directory)
        2. If so, prepends the APP_FILES_PATH to create an absolute path
        3. Updates the configuration with the full path

        The regex pattern matches the args string format like: ('filename', 'mode')
        and extracts the filename portion for processing.
        """
        # Extract current file path from handler args
        path_match = re.match(
            r'(\()(["\'](.*?)["\'])(,.*\))',
            config["handler_fileHandler"]["args"],
        )
        if path_match is None:
            raise ValueError("Invalid fileHandler args format in logger.ini")

        old_file_path = path_match[3]
        old_file_name = Path(old_file_path).name

        # Only modify if path is just a filename (no directory)
        if old_file_path == old_file_name:
            # Create new absolute path
            new_file_path = str(settings.APP_FILES_PATH / old_file_name)

            # Reconstruct the args string with new path
            args_match = re.match(
                r'(\()(["\'].*["\'])(,.*\))',
                config["handler_fileHandler"]["args"]
            )
            if args_match is None:
                raise ValueError("Invalid fileHandler args format in logger.ini")

            config.set(
                "handler_fileHandler",
                "args",
                f'{args_match.group(1)}"{new_file_path}"{args_match.group(3)}',
            )

    # Configure logging with the updated configuration
    logging.config.fileConfig(
        config,
        disable_existing_loggers=False,  # Preserve any existing loggers
    )
