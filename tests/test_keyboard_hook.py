from __future__ import annotations

import sys

from raid_ops.connectors.keyboard_hook import KeyboardHook
from raid_ops.connectors.routine_recorder import UserAction


class FakeRecorder:
    def __init__(self) -> None:
        self.actions: list[UserAction] = []

    def record_action(self, action: UserAction) -> None:
        self.actions.append(action)


class FakeKey:
    def __init__(self, text: str, char: str | None = None) -> None:
        self._text = text
        self.char = char

    def __str__(self) -> str:
        return self._text


class FakeListener:
    def __init__(self, on_press):
        self._on_press = on_press
        self.started = False
        self.stopped = False

    def start(self) -> None:
        self.started = True

    def stop(self) -> None:
        self.stopped = True

    def fire(self, key) -> None:
        self._on_press(key)


def test_hotkeys_filter_records_only_matching(monkeypatch) -> None:
    recorder = FakeRecorder()
    listener_holder: dict[str, FakeListener] = {}

    class FakeKeyboardModule:
        @staticmethod
        def Listener(on_press):
            listener = FakeListener(on_press)
            listener_holder["listener"] = listener
            return listener

    class FakePynputModule:
        keyboard = FakeKeyboardModule

    monkeypatch.setitem(sys.modules, "pynput", FakePynputModule)

    hook = KeyboardHook(recorder=recorder, hotkeys={"space"})
    hook.start()
    listener_holder["listener"].fire(FakeKey("Key.space"))
    listener_holder["listener"].fire(FakeKey("a", char="a"))

    assert [action.key for action in recorder.actions] == ["space"]


def test_unfiltered_records_all(monkeypatch) -> None:
    recorder = FakeRecorder()
    listener_holder: dict[str, FakeListener] = {}

    class FakeKeyboardModule:
        @staticmethod
        def Listener(on_press):
            listener = FakeListener(on_press)
            listener_holder["listener"] = listener
            return listener

    class FakePynputModule:
        keyboard = FakeKeyboardModule

    monkeypatch.setitem(sys.modules, "pynput", FakePynputModule)

    hook = KeyboardHook(recorder=recorder)
    hook.start()
    listener_holder["listener"].fire(FakeKey("Key.enter"))
    listener_holder["listener"].fire(FakeKey("b", char="b"))

    assert [action.key for action in recorder.actions] == ["enter", "b"]


def test_stop_prevents_further_recording(monkeypatch) -> None:
    recorder = FakeRecorder()
    listener_holder: dict[str, FakeListener] = {}

    class FakeKeyboardModule:
        @staticmethod
        def Listener(on_press):
            listener = FakeListener(on_press)
            listener_holder["listener"] = listener
            return listener

    class FakePynputModule:
        keyboard = FakeKeyboardModule

    monkeypatch.setitem(sys.modules, "pynput", FakePynputModule)

    hook = KeyboardHook(recorder=recorder)
    hook.start()
    hook.stop()
    listener_holder["listener"].fire(FakeKey("Key.space"))

    assert recorder.actions == []
