"""
Utility functions for managing structured logging context variables.

This module provides a set of functions to manage and control logging
context using `structlog.contextvars`. These functions enable the binding,
unbinding, and clearing of context variables such as trace identifiers,
user details, event information, and HTTP request metadata. It also
includes a context manager for temporarily binding event-specific context.

Functions:
    - set_trace_id_context: Binds a unique trace identifier to the logging
      context.
    - bind_request_context: Binds optional metadata (e.g., user ID, site ID,
      path, method) related to an HTTP request to the logging context.
    - clear_context: Clears all bound context variables.
    - bind_event_context: Binds an event-specific identifier to the logging
      context.
    - unbind_event_context: Unbinds the event-specific identifier from the
      logging context.
    - bound_event_context: Context manager for safely binding and unbinding
      an event-specific identifier.
"""
from __future__ import annotations

import uuid
from contextlib import contextmanager
from typing import Optional

from structlog.contextvars import bind_contextvars, clear_contextvars, unbind_contextvars


def set_trace_id_context():
    bind_contextvars(trace_id=uuid.uuid4().hex)

def bind_request_context(
        user_id: Optional[str] = None,
        site_id: Optional[str] = None,
        path: Optional[str] = None,
        method: Optional[str] = None
):
    options = {'user_id': user_id, 'site_id': site_id, 'path': path, 'method': method}
    attrs = {k: v for k, v in options.items() if v is not None}
    bind_contextvars(**attrs)

def clear_context():
    clear_contextvars()

def bind_event_context(event: str):
    bind_contextvars(event=event)

def unbind_event_context():
    unbind_contextvars("event")


@contextmanager
def bound_event_context(event: str):
    bind_event_context(event)
    try:
        yield
    finally:
        unbind_event_context()