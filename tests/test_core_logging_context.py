from unittest.mock import Mock

import pytest

import screenflix.core.logging.context as context


def test_set_trace_id_context(monkeypatch):
    bind = Mock()
    monkeypatch.setattr(context, "bind_contextvars", bind)
    monkeypatch.setattr(context.uuid, "uuid4", Mock(return_value=type("U", (), {"hex": "abc123"})()))

    context.set_trace_id_context()

    bind.assert_called_once_with(trace_id="abc123")


def test_bind_request_context_filters_none(monkeypatch):
    bind = Mock()
    monkeypatch.setattr(context, "bind_contextvars", bind)

    context.bind_request_context(user_id="1", site_id=None, path="/x", method="GET")

    bind.assert_called_once_with(user_id="1", path="/x", method="GET")


def test_clear_context(monkeypatch):
    clear = Mock()
    monkeypatch.setattr(context, "clear_contextvars", clear)

    context.clear_context()

    clear.assert_called_once_with()


def test_bind_and_unbind_event_context(monkeypatch):
    bind = Mock()
    unbind = Mock()
    monkeypatch.setattr(context, "bind_contextvars", bind)
    monkeypatch.setattr(context, "unbind_contextvars", unbind)

    context.bind_event_context("ingestion")
    context.unbind_event_context()

    bind.assert_called_once_with(event="ingestion")
    unbind.assert_called_once_with("event")


def test_bound_event_context_always_unbinds(monkeypatch):
    bind_event = Mock()
    unbind_event = Mock()
    monkeypatch.setattr(context, "bind_event_context", bind_event)
    monkeypatch.setattr(context, "unbind_event_context", unbind_event)

    with pytest.raises(ValueError):
        with context.bound_event_context("catalog"):
            raise ValueError("fail")

    bind_event.assert_called_once_with("catalog")
    unbind_event.assert_called_once_with()
