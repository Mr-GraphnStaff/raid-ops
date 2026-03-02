from __future__ import annotations

import time


class PyAutoGuiInputGateway:
    """Live InputGateway backed by pyautogui."""

    def __init__(self) -> None:
        import pyautogui

        pyautogui.FAILSAFE = True

    def click(self, x: int, y: int) -> None:
        import pyautogui

        pyautogui.click(x, y)

    def key(self, key: str) -> None:
        import pyautogui

        pyautogui.press(key)

    def wait(self, seconds: float) -> None:
        time.sleep(seconds)
