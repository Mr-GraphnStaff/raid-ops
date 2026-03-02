from __future__ import annotations

import argparse
import time
from pathlib import Path

from raid_ops.connectors.executor import ExecutionPlan, ExecutionStep, PlanExecutor
from raid_ops.connectors.keyboard_hook import KeyboardHook
from raid_ops.connectors.observer_state_gateway import ObserverStateGateway
from raid_ops.connectors.pyautogui_gateway import PyAutoGuiInputGateway
from raid_ops.connectors.routine_recorder import JsonlRecorderGateway, RoutineRecorder
from raid_ops.connectors.vision_observer import Screen, make_default_observer
from raid_ops.services.agent_service import AgentService
from raid_ops.services.routine_service import JsonlRoutineRepository, RoutineService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="raid-ops automation CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    record = subparsers.add_parser("record", help="Record state/action pairs")
    record.add_argument("--hotkeys", nargs="*", default=None)

    playback = subparsers.add_parser("playback", help="Play back a routine by screen")
    playback.add_argument("screen")

    run = subparsers.add_parser("run", help="Run the agent loop")
    run.add_argument("--max-iterations", type=int, default=1)

    subparsers.add_parser("list-routines", help="List available routines")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    repository = JsonlRoutineRepository(Path("data/recordings"))
    routines = RoutineService(repository)

    if args.command == "list-routines":
        print("\n".join(routines.list_routines()))
        return

    if args.command == "record":
        observer = make_default_observer()
        recorder = RoutineRecorder(JsonlRecorderGateway())
        keyboard_hook = KeyboardHook(recorder, hotkeys=set(args.hotkeys) if args.hotkeys else None)
        try:
            recorder.start(observer)
            keyboard_hook.start()
            print(f"Recording to {recorder.output_path} — press Ctrl+C to stop")
            while True:
                time.sleep(1.0)
        except KeyboardInterrupt:
            pass
        finally:
            keyboard_hook.stop()
            recorder.stop(observer)
        return

    if args.command == "run":
        observer = make_default_observer()
        try:
            observer.start()
            state_gateway = ObserverStateGateway(observer)
            input_gateway = PyAutoGuiInputGateway()
            executor = PlanExecutor(input_gateway, state_gateway)
            runtime_repository = JsonlRoutineRepository(Path("data/recordings"))
            runtime_routines = RoutineService(runtime_repository)
            agent_service = AgentService(observer, runtime_routines, executor)
            decisions = agent_service.run_loop(max_iterations=args.max_iterations)
            for decision in decisions:
                print(decision)
        finally:
            observer.stop()
        return

    if args.command == "playback":
        observer = make_default_observer()
        try:
            observer.start()
            input_gateway = PyAutoGuiInputGateway()
            state_gateway = ObserverStateGateway(observer)
            executor = PlanExecutor(input_gateway, state_gateway)
            routine = routines.get_routine(Screen(args.screen))
            if routine is None:
                print(f"No routine found for screen '{args.screen}'")
                return
            plan = ExecutionPlan(
                steps=tuple(ExecutionStep(action=action["type"], params=action) for action in routine.actions)
            )
            executor.execute(plan)
            print(f"Playback complete for {routine.name}")
        finally:
            observer.stop()


if __name__ == "__main__":
    main()
