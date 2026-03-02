from __future__ import annotations

import base64
import io
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from threading import Event, Lock, Thread
from typing import Any, Callable, Protocol


logger = logging.getLogger(__name__)


class Screen(str, Enum):
    """Known Raid UI screens."""

    UNKNOWN = "unknown"
    MAIN_MENU = "main_menu"
    CAMPAIGN = "campaign"
    CAMPAIGN_BATTLE = "campaign_battle"
    DUNGEON_SELECT = "dungeon_select"
    DUNGEON_BATTLE = "dungeon_battle"
    CLAN_BOSS = "clan_boss"
    ARENA_LOBBY = "arena_lobby"
    ARENA_BATTLE = "arena_battle"
    DAILY_QUESTS = "daily_quests"
    REWARD_SCREEN = "reward_screen"
    BATTLE_RESULT = "battle_result"
    LOADING = "loading"

    @classmethod
    def _missing_(cls, value: object) -> Screen:
        return cls.UNKNOWN


@dataclass(frozen=True)
class ActionableElement:
    label: str
    confidence: float
    position_hint: str
    action_type: str


@dataclass(frozen=True)
class GameState:
    timestamp: datetime
    screen: Screen
    energy: int | None
    silver: int | None
    gems: int | None
    stage_info: str | None
    battle_progress: str | None
    actionable: tuple[ActionableElement, ...]
    recommended_action: str | None
    raw_analysis: str
    screenshot_path: Path | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "screen": self.screen.value,
            "energy": self.energy,
            "silver": self.silver,
            "gems": self.gems,
            "stage_info": self.stage_info,
            "battle_progress": self.battle_progress,
            "actionable": [
                {
                    "label": item.label,
                    "confidence": item.confidence,
                    "position_hint": item.position_hint,
                    "action_type": item.action_type,
                }
                for item in self.actionable
            ],
            "recommended_action": self.recommended_action,
            "raw_analysis": self.raw_analysis,
            "screenshot_path": str(self.screenshot_path) if self.screenshot_path else None,
        }


class VisionBackend(Protocol):
    def analyze(self, img: Any, timestamp: datetime) -> GameState:
        ...


class ScreenCapture(Protocol):
    def capture(self) -> Any | None:
        ...


class PlariumVisionObserver:
    """Polls a capture+analysis backend and publishes immutable game states."""

    def __init__(self, capture: ScreenCapture, backend: VisionBackend, interval_s: float = 1.0) -> None:
        self._capture = capture
        self._backend = backend
        self._interval_s = interval_s
        self._latest: GameState | None = None
        self._lock = Lock()
        self._thread: Thread | None = None
        self._stop_event = Event()

    def capture_once(self) -> GameState | None:
        image = self._capture.capture()
        if image is None:
            return None
        state = self._backend.analyze(image, datetime.now(timezone.utc))
        with self._lock:
            self._latest = state
        return state

    def start(self, callback: Callable[[GameState], None] | None = None) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()

        def _run() -> None:
            while not self._stop_event.wait(self._interval_s):
                state = self.capture_once()
                if state is not None and callback is not None:
                    callback(state)

        self._thread = Thread(target=_run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=1.0)

    @property
    def latest(self) -> GameState | None:
        with self._lock:
            return self._latest


class PlariumWindowCapture:
    """Captures the Plarium game window when present."""

    _WINDOW_TITLES = ["Plarium Play", "Raid: Shadow Legends", "RAID: Shadow Legends"]

    def capture(self) -> Any | None:
        try:
            import pygetwindow
            from PIL import ImageGrab
        except Exception as exc:  # pragma: no cover - environment specific
            logger.warning("Screen capture dependencies unavailable: %s", exc)
            return None

        for title in self._WINDOW_TITLES:
            windows = pygetwindow.getWindowsWithTitle(title)
            if windows:
                window = windows[0]
                try:
                    return ImageGrab.grab(bbox=(window.left, window.top, window.right, window.bottom))
                except Exception as exc:  # pragma: no cover - platform specific
                    logger.warning("Failed to capture window '%s': %s", title, exc)
                    return None
        logger.warning("No Plarium Play window found for known titles")
        return None


class ClaudeVisionBackend:
    """Anthropic Claude Vision backend for analyzing game screenshots."""

    _SYSTEM_PROMPT = (
        "You are analyzing a Raid: Shadow Legends screenshot. "
        "Return ONLY valid JSON with these fields: "
        "screen, energy, silver, gems, stage_info, battle_progress, actionable, recommended_action. "
        "For actionable use an array of objects with: label, confidence, position_hint, action_type."
    )

    def __init__(self, model: str = "claude-opus-4-5", max_tokens: int = 1024) -> None:
        import anthropic

        self._anthropic = anthropic
        self._client = anthropic.Anthropic()
        self._model = model
        self._max_tokens = max_tokens

    def analyze(self, img: Any, timestamp: datetime) -> GameState:
        try:
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=85)
            encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
            message = self._client.messages.create(
                model=self._model,
                max_tokens=self._max_tokens,
                system=self._SYSTEM_PROMPT,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": encoded,
                                },
                            },
                            {
                                "type": "text",
                                "text": "Analyze the screenshot and return only the JSON object.",
                            },
                        ],
                    }
                ],
            )
            response_text = "".join(
                block.text for block in message.content if getattr(block, "type", "") == "text"
            )
            payload = json.loads(response_text)
            actionable = tuple(
                ActionableElement(
                    label=str(item.get("label", "")),
                    confidence=float(item.get("confidence", 0.0)),
                    position_hint=str(item.get("position_hint", "")),
                    action_type=str(item.get("action_type", "")),
                )
                for item in payload.get("actionable", [])
                if isinstance(item, dict)
            )
            return GameState(
                timestamp=timestamp,
                screen=Screen(payload.get("screen", Screen.UNKNOWN.value)),
                energy=_as_int(payload.get("energy")),
                silver=_as_int(payload.get("silver")),
                gems=_as_int(payload.get("gems")),
                stage_info=_as_optional_str(payload.get("stage_info")),
                battle_progress=_as_optional_str(payload.get("battle_progress")),
                actionable=actionable,
                recommended_action=_as_optional_str(payload.get("recommended_action")),
                raw_analysis=response_text,
                screenshot_path=None,
            )
        except (self._anthropic.APIError, json.JSONDecodeError) as exc:
            logger.error("Vision analysis failed: %s", exc)
            return GameState(
                timestamp=timestamp,
                screen=Screen.UNKNOWN,
                energy=None,
                silver=None,
                gems=None,
                stage_info=None,
                battle_progress=None,
                actionable=(),
                recommended_action=None,
                raw_analysis=str(exc),
                screenshot_path=None,
            )


def _as_int(value: object) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _as_optional_str(value: object) -> str | None:
    if value is None:
        return None
    return str(value)


def make_default_observer(interval_s: float = 3.0, save_screenshots: bool = False) -> PlariumVisionObserver:
    _ = save_screenshots
    return PlariumVisionObserver(
        capture=PlariumWindowCapture(),
        backend=ClaudeVisionBackend(),
        interval_s=interval_s,
    )
