"""Callback mixin for hub entities."""
from __future__ import annotations

import asyncio
import functools
import logging
from collections.abc import Callable
from typing import Any

_LOGGER = logging.getLogger(__name__)


class CallbackMixin:
    """Mixin for entities that support update callbacks."""

    def __init__(self) -> None:
        """Initialize callback list."""
        self._update_callbacks: list[Callable[..., None]] = []

    def callback_subscribe(self, callback: Callable[..., None]) -> None:
        """Add a callback for updates."""
        self._update_callbacks.append(callback)

    def callback_unsubscribe(self, callback: Callable[..., None]) -> None:
        """Remove a callback for updates."""
        if callback in self._update_callbacks:
            self._update_callbacks.remove(callback)

    def notify_callback(self, *args: Any) -> None:
        """Notify all callbacks of an update."""
        for callback in self._update_callbacks:
            self._schedule_callback(callback, *args)

    def _schedule_callback(
        self, target: Callable[..., Any], *args: Any
    ) -> asyncio.Task[None] | None:
        """Schedule a callback to run asynchronously.

        Must be called from within the event loop.
        """
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            _LOGGER.warning("No running event loop, callback not scheduled")
            return None

        # Check for partials to properly determine if coroutine function
        check_target = target
        while isinstance(check_target, functools.partial):
            check_target = check_target.func

        if asyncio.iscoroutine(check_target):
            return loop.create_task(target)  # type: ignore
        elif asyncio.iscoroutinefunction(check_target):
            return loop.create_task(target(*args))
        else:
            return loop.run_in_executor(None, target, *args)  # type: ignore
