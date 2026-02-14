import pytest


@pytest.fixture
def sample_logger_ini():
    """Create a sample logger.ini content."""
    return """
[loggers]
keys=root

[handlers]
keys=fileHandler

[formatters]
keys=simpleFormatter

[logger_root]
level=INFO
handlers=fileHandler

[handler_fileHandler]
class=logging.FileHandler
level=INFO
formatter=simpleFormatter
args=('app.log', 'a')

[formatter_simpleFormatter]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s
"""
