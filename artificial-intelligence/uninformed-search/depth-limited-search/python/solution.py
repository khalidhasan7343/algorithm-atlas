"""Depth-Limited Search (DLS) over a general state space.

See the adjacent README for the contract, proof sketch and complexity. The
search is depth-first, uses path-local cycle detection (never a global visited
set), treats the initial state as depth 0 and goal-tests every state at depth
0..limit inclusive. States at depth ``limit + 1`` are never goal-tested or
explored; their existence only decides CUTOFF versus FAILURE.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any, Callable

_spec = importlib.util.spec_from_file_location(
    "atlas_uninformed_support", Path(__file__).resolve().parents[2] / "support.py")
_support = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_support)

FOUND, CUTOFF, FAILURE = _support.FOUND, _support.CUTOFF, _support.FAILURE
SearchResult = _support.SearchResult


def depth_limited_search(start: Any, is_goal: Callable[[Any], bool],
                         successors: Callable[[Any], Any], limit: int, *,
                         state_key: Callable[[Any], Any] | None = None) -> SearchResult:
    """Return FOUND with a simple path of at most ``limit`` actions, CUTOFF or FAILURE.

    ``successors(state)`` yields ``(action, next_state)`` records in the order
    they should be explored. FAILURE means no goal is reachable at all: every
    acyclic path from ``start`` ended before the limit without reaching a goal.
    CUTOFF means at least one acyclic path was truncated at the limit.
    """
    _support.require_callable(is_goal, "is_goal")
    _support.require_callable(successors, "successors")
    limit = _support.depth_value(limit, "limit")
    key = _support.key_function(state_key)
    stats = dict(expanded=0, generated=0, goal_tests=0, boundary_checks=0,
                 cycle_skips=0, max_depth_reached=0)

    def goal(state: Any) -> bool:
        stats["goal_tests"] += 1
        return bool(is_goal(state))

    def expand(state: Any) -> list:
        produced = _support.records(successors, state, weighted=False)
        stats["generated"] += len(produced)
        return produced

    start_key = key(start)
    if goal(start):
        return SearchResult(FOUND, (start,), (), 0, stats)

    # Each frame is [state, key, validated records, next record index].
    path_states, path_actions = [start], []
    on_path = {start_key}
    frames: list[list] = []
    cutoff = False

    def enter(state: Any, state_key_value: Any, depth: int) -> None:
        """Expand a non-goal state, or perform the depth-limit boundary check."""
        nonlocal cutoff
        if depth < limit:
            stats["expanded"] += 1
            frames.append([state, state_key_value, expand(state), 0])
            return
        # At the limit: children (depth limit+1) are not goal-tested or explored.
        # Once a cutoff is known, further boundary checks cannot change the result.
        if not cutoff:
            stats["boundary_checks"] += 1
            cutoff = any(key(child) not in on_path for _, child in expand(state))

    enter(start, start_key, 0)
    while frames:
        frame = frames[-1]
        if frame[3] == len(frame[2]):  # All children tried: backtrack.
            frames.pop()
            on_path.discard(frame[1])
            path_states.pop()
            if path_actions:
                path_actions.pop()
            continue
        action, child = frame[2][frame[3]]
        frame[3] += 1
        child_key = key(child)
        if child_key in on_path:  # Path-local cycle: this path would repeat a state.
            stats["cycle_skips"] += 1
            continue
        depth = len(frames)
        stats["max_depth_reached"] = max(stats["max_depth_reached"], depth)
        path_states.append(child)
        path_actions.append(action)
        on_path.add(child_key)
        if goal(child):
            return SearchResult(FOUND, tuple(path_states), tuple(path_actions), depth, stats)
        enter(child, child_key, depth)
        if depth == limit:  # Boundary states are never pushed; undo immediately.
            on_path.discard(child_key)
            path_states.pop()
            path_actions.pop()
    return SearchResult(CUTOFF if cutoff else FAILURE, (), (), None, stats)


def solve_text(text: str) -> dict:
    """Explicit-graph CLI: ``n m start limit g goal... u v ...`` (actions = edge indexes)."""
    problem = _support.parse_problem(text, "dls")
    table = _support.adjacency(problem["n"], problem["edges"])
    goals = set(problem["goals"])
    return depth_limited_search(problem["start"], goals.__contains__, table.__getitem__,
                                problem["limit"]).to_dict()


solve = depth_limited_search

if __name__ == "__main__":
    _support.cli(solve_text)
