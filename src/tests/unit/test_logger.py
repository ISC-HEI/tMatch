import sys
from unittest.mock import MagicMock

sys.modules["streamlit"] = MagicMock()

import pytest
from unittest.mock import patch, MagicMock
from importlib import reload

from utils.logger import Logger


class TestLoggerSingleton:
    """Tests for the Logger singleton pattern."""

    @pytest.fixture(autouse=True)
    def reset_singleton(self):
        """Reset singleton instance before each test."""
        Logger._instance = None
        Logger._initialized = False
        yield
        Logger._instance = None
        Logger._initialized = False

    def test_singleton_returns_same_instance(self):
        """Multiple Logger() calls return the same instance."""
        l1 = Logger()
        l2 = Logger()
        assert l1 is l2

    def test_is_initialized_returns_true(self):
        """is_initialized returns True after init."""
        l = Logger()
        assert l.is_initialized() is True


class TestLoggerMethods:
    """Tests for Logger public methods."""

    @pytest.fixture(autouse=True)
    def reset_singleton(self):
        """Reset singleton instance before each test."""
        Logger._instance = None
        Logger._initialized = False
        yield

    @patch("utils.logger.open", new_callable=MagicMock)
    def test_info_writes_to_file(self, mock_open):
        """info() writes a log line to file."""
        l = Logger()
        l.init()
        l.info("test message")

        mock_open.assert_called()
        mock_open.return_value.__enter__.return_value.write.assert_called()

    @patch("utils.logger.open", new_callable=MagicMock)
    def test_warn_writes_to_file(self, mock_open):
        """warn() writes a log line to file."""
        l = Logger()
        l.init()
        l.warn("warning message")

        mock_open.assert_called()

    @patch("utils.logger.open", new_callable=MagicMock)
    def test_error_writes_to_file(self, mock_open):
        """error() writes a log line to file."""
        l = Logger()
        l.init()
        l.error("error message")

        mock_open.assert_called()


class TestLoggerModuleExport:
    """Tests for the module-level logger export."""

    @pytest.fixture(autouse=True)
    def reset_singleton(self):
        """Reset singleton instance before each test."""
        import utils.logger as logger_module
        Logger._instance = None
        Logger._initialized = False
        logger_module._logger = None
        yield
        Logger._instance = None
        Logger._initialized = False
        logger_module._logger = None

    def test_module_level_logger_is_singleton(self):
        """The module-level logger export is the singleton instance."""
        import utils.logger as logger_module
        reload(logger_module)

        assert logger_module.logger is logger_module._logger
        assert logger_module.logger is logger_module.get_logger()