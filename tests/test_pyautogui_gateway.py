from __future__ import annotations

from types import SimpleNamespace
import sys

import raid_ops.connectors.pyautogui_gateway as gateway_module
from raid_ops.connectors.pyautogui_gateway import PyAutoGuiInputGateway


class FakeAutoGui:
    def __init__(self) -> None:
        self.FAILSAFE = False
        self.calls: list[tuple[str, object]] = []

    def click(self, x: int, y: int) -> None:
        self.calls.append(("click", (x, y)))

    def press(self, key: str) -> None:
        self.calls.append(("press", key))


def test_gateway_delegates_to_pyautogui(monkeypatch) -> None:
    fake = FakeAutoGui()
    monkeypatch.setitem(sys.modules, "pyautogui", fake)

    gateway = PyAutoGuiInputGateway()
    gateway.click(1, 2)
    gateway.key("space")

    assert fake.FAILSAFE is True
    assert fake.calls == [("click", (1, 2)), ("press", "space")]


def test_gateway_wait_delegates_to_sleep(monkeypatch) -> None:
    slept: list[float] = []
    monkeypatch.setattr(gateway_module, "time", SimpleNamespace(sleep=lambda seconds: slept.append(seconds)))

    gateway = PyAutoGuiInputGateway.__new__(PyAutoGuiInputGateway)
    gateway.wait(0.5)

    assert slept == [0.5]
