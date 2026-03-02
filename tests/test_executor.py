from __future__ import annotations

from datetime import datetime, timezone

import pytest

from raid_ops.connectors.executor import ExecutionError, ExecutionPlan, ExecutionStep, PlanExecutor
from raid_ops.connectors.vision_observer import GameState, Screen


class FakeInputGateway:
    def __init__(self) -> None:
        self.events: list[tuple[str, object]] = []

    def click(self, x: int, y: int) -> None:
        self.events.append(("click", (x, y)))

    def key(self, key: str) -> None:
        self.events.append(("key", key))

    def wait(self, seconds: float) -> None:
        self.events.append(("wait", seconds))


class FakeStateGateway:
    def __init__(self, screen: Screen) -> None:
        self._screen = screen

    def latest_state(self) -> GameState:
        return GameState(
            timestamp=datetime.now(timezone.utc),
            screen=self._screen,
            energy=None,
            silver=None,
            gems=None,
            stage_info=None,
            battle_progress=None,
            actionable=(),
            recommended_action=None,
            raw_analysis="",
            screenshot_path=None,
        )


def test_executor_runs_supported_actions() -> None:
    inputs = FakeInputGateway()
    states = FakeStateGateway(Screen.MAIN_MENU)
    executor = PlanExecutor(inputs, states)

    executor.execute(
        ExecutionPlan(
            steps=(
                ExecutionStep(action="assert_screen", params={"screen": "main_menu"}),
                ExecutionStep(action="click", params={"x": 1, "y": 2}),
                ExecutionStep(action="key", params={"key": "space"}),
                ExecutionStep(action="wait", params={"seconds": 0.1}),
            )
        )
    )

    assert inputs.events == [("click", (1, 2)), ("key", "space"), ("wait", 0.1)]


def test_executor_raises_when_screen_assertion_fails() -> None:
    executor = PlanExecutor(FakeInputGateway(), FakeStateGateway(Screen.CAMPAIGN))

    with pytest.raises(ExecutionError, match="State assertion failed"):
        executor.execute(
            ExecutionPlan(
                steps=(ExecutionStep(action="assert_screen", params={"screen": "main_menu"}),)
            )
        )
