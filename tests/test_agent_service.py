from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from raid_ops.connectors.executor import ExecutionPlan
from raid_ops.connectors.vision_observer import GameState, Screen
from raid_ops.services.agent_service import AgentService
from raid_ops.services.routine_service import Routine


class FakeObserver:
    def __init__(self, state: GameState | None) -> None:
        self._state = state

    @property
    def latest(self) -> GameState | None:
        return self._state


class FakeRoutineService:
    def __init__(self, routine: Routine | None) -> None:
        self.routine = routine

    def get_routine(self, screen: Screen) -> Routine | None:
        return self.routine


class FakeExecutor:
    def __init__(self) -> None:
        self.plans: list[ExecutionPlan] = []

    def execute(self, plan: ExecutionPlan) -> None:
        self.plans.append(plan)


class FakeLogger:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def log(self, payload: dict[str, Any]) -> None:
        self.rows.append(payload)


def _state() -> GameState:
    return GameState(
        timestamp=datetime.now(timezone.utc),
        screen=Screen.MAIN_MENU,
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


def test_run_once_executes_matching_routine() -> None:
    routine = Routine(
        name="main_menu_routine",
        screen=Screen.MAIN_MENU,
        actions=({"type": "click", "x": 10, "y": 20},),
        source_recording="a.jsonl",
        created_at=datetime.now(timezone.utc),
    )
    executor = FakeExecutor()
    logger = FakeLogger()
    service = AgentService(FakeObserver(_state()), FakeRoutineService(routine), executor, logger)

    decision = service.run_once()

    assert decision.outcome == "executed"
    assert len(executor.plans) == 1
    assert logger.rows[-1]["decision"]["outcome"] == "executed"


def test_run_once_returns_no_state_when_observer_empty() -> None:
    service = AgentService(FakeObserver(None), FakeRoutineService(None), FakeExecutor())

    decision = service.run_once()

    assert decision.outcome == "no_state"
