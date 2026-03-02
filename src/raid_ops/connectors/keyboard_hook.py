from __future__ import annotations

import logging
from typing import Any

from raid_ops.connectors.routine_recorder import RoutineRecorder, UserAction


logger = logging.getLogger(__name__)


class KeyboardHook:
    """Listens for keypresses and records them as UserActions."""

    def __init__(self, recorder: RoutineRecorder, hotkeys: set[str] | None = None) -> None:
        self._recorder = recorder
        self._hotkeys = hotkeys
        self._listener: Any | None = None
        self._running = False

    def start(self) -> None:
        if self._running:
            return
        from pynput import keyboard

        self._listener = keyboard.Listener(on_press=self._on_press)
        self._listener.start()
        self._running = True

    def stop(self) -> None:
        self._running = False
        if self._listener is not None:
            self._listener.stop()
            self._listener = None

    def _on_press(self, key: Any) -> None:
        if not self._running:
            return
        key_str = self._to_key_string(key)
        if key_str is None:
            return
        if self._hotkeys is not None and key_str not in self._hotkeys:
            return
        self._recorder.record_action(UserAction(type="key", key=key_str))

    def _to_key_string(self, key: Any) -> str | None:
        char = getattr(key, "char", None)
        if isinstance(char, str):
            return char
        text = str(key)
        if text.startswith("Key."):
            return text.split(".", 1)[1]
        if text:
            return text
        logger.debug("Unable to normalize key object: %r", key)
        return None
