from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Protocol

from raid_ops.connectors.executor import ExecutionPlan, ExecutionStep, PlanExecutor
from raid_ops.connectors.vision_observer import GameState
from raid_ops.services.routine_service import RoutineService


class ObserverGateway(Protocol):
    """Observer interface consumed by agent orchestration."""

    @property
    def latest(self) -> GameState | None:
        ...


class AgentLogger(Protocol):
    """Sink for structured decision events."""

    def log(self, payload: dict[str, Any]) -> None:
        ...


class NullAgentLogger:
    """Default no-op logger."""

    def log(self, payload: dict[str, Any]) -> None:
        return None


@dataclass(frozen=True)
class AgentDecision:
    state_screen: str
    routine_name: str | None
    outcome: str


class AgentService:
    """Co-ordinates observation, routine lookup, and execution."""

    def __init__(
        self,
        observer: ObserverGateway,
        routines: RoutineService,
        executor: PlanExecutor,
        logger: AgentLogger | None = None,
    ) -> None:
        self._observer = observer
        self._routines = routines
        self._executor = executor
        self._logger = logger or NullAgentLogger()
        self._paused = False

    def run_once(self) -> AgentDecision:
        if self._paused:
            decision = AgentDecision(state_screen="paused", routine_name=None, outcome="paused")
            self._log(decision, None)
            return decision

        state = self._observer.latest
        if state is None:
            decision = AgentDecision(state_screen="unknown", routine_name=None, outcome="no_state")
            self._log(decision, None)
            return decision

        routine = self._routines.get_routine(state.screen)
        if routine is None:
            decision = AgentDecision(
                state_screen=state.screen.value,
                routine_name=None,
                outcome="no_routine",
            )
            self._log(decision, state)
            return decision

        steps = [ExecutionStep(action="assert_screen", params={"screen": state.screen.value})]
        steps.extend(ExecutionStep(action=action["type"], params=action) for action in routine.actions)
        self._executor.execute(ExecutionPlan(steps=tuple(steps)))

        decision = AgentDecision(
            state_screen=state.screen.value,
            routine_name=routine.name,
            outcome="executed",
        )
        self._log(decision, state)
        return decision

    def run_loop(self, max_iterations: int | None = None) -> list[AgentDecision]:
        decisions: list[AgentDecision] = []
        iterations = 0
        while max_iterations is None or iterations < max_iterations:
            decisions.append(self.run_once())
            iterations += 1
            if self._paused:
                break
        return decisions

    def pause(self) -> None:
        self._paused = True

    def resume(self) -> None:
        self._paused = False

    def _log(self, decision: AgentDecision, state: GameState | None) -> None:
        self._logger.log(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "decision": {
                    "state_screen": decision.state_screen,
                    "routine_name": decision.routine_name,
                    "outcome": decision.outcome,
                },
                "state": state.to_dict() if state else None,
            }
        )
