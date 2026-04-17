import logging
from types import SimpleNamespace
from unittest.mock import Mock

import screenflix.core.logging.config as config
from screenflix.core.logging.logger import get_logger


def test_resolve_log_level_known_and_unknown():
    assert config._resolve_log_level("DEBUG") == logging.DEBUG
    assert config._resolve_log_level("CRITICAL") == logging.CRITICAL
    assert config._resolve_log_level("NOT_A_LEVEL") == logging.INFO


def test_setup_logging_configures_root_and_binds_app_name(monkeypatch):
    monkeypatch.setattr(config, "get_settings", lambda: SimpleNamespace(log_level="ERROR"))

    bind_context = Mock()
    structlog_configure = Mock()

    monkeypatch.setattr(config, "bind_contextvars", bind_context)
    monkeypatch.setattr(config.structlog, "configure", structlog_configure)

    config.setup_logging(app_name="Screenflix")

    assert logging.getLogger().level == logging.ERROR
    bind_context.assert_called_once_with(app_name="Screenflix")
    structlog_configure.assert_called_once()


def test_get_logger_delegates_to_structlog(monkeypatch):
    expected = object()
    getter = Mock(return_value=expected)
    monkeypatch.setattr("screenflix.core.logging.logger.structlog.get_logger", getter)

    current = get_logger("unit-test")

    assert current is expected
    getter.assert_called_once_with("unit-test")
