from __future__ import annotations

from raid_ops.connectors.vision_observer import GameState, PlariumVisionObserver


class ObserverStateGateway:
    """StateGateway that reads from a live PlariumVisionObserver."""

    def __init__(self, observer: PlariumVisionObserver) -> None:
        self._observer = observer

    def latest_state(self) -> GameState | None:
        return self._observer.latest
