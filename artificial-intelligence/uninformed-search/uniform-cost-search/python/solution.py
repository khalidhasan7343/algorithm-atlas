"""Uniform Cost Search (UCS) over a state space with nonnegative step costs.

The frontier is a binary heap ordered by ``(g, insertion counter)``; the counter
gives deterministic FIFO tie-breaking and guarantees states are never compared.
A goal is accepted only when it is *removed* from the frontier with its current
best cost, never when it is first generated. See the adjacent README.
"""
from __future__ import annotations

import heapq
import importlib.util
from pathlib import Path
from typing import Any, Callable

_spec = importlib.util.spec_from_file_location(
    "atlas_uninformed_support", Path(__file__).resolve().parents[2] / "support.py")
_support = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_support)

FOUND, FAILURE = _support.FOUND, _support.FAILURE
SearchResult = _support.SearchResult


def uniform_cost_search(start: Any, is_goal: Callable[[Any], bool],
                        successors: Callable[[Any], Any], *,
                        state_key: Callable[[Any], Any] | None = None) -> SearchResult:
    """Return a minimum-cost path to any goal state, or FAILURE.

    ``successors(state)`` yields ``(action, next_state, step_cost)`` records;
    each cost must be a finite, nonnegative real number (zero is allowed).
    Costs are summed exactly as given (``int``/``Fraction`` stay exact; ``float``
    sums follow IEEE-754 rounding). No tolerance is applied to comparisons.
    """
    _support.require_callable(is_goal, "is_goal")
    _support.require_callable(successors, "successors")
    key = _support.key_function(state_key)
    stats = dict(expanded=0, generated=0, goal_tests=0, pushed=1, stale_skipped=0,
                 improvements=0, max_frontier=1)
    start_key = key(start)
    best = {start_key: 0}          # Best known path cost g(n) per state key.
    parent: dict = {start_key: None}  # key -> (parent key, action) for the best path.
    state_of = {start_key: start}
    closed: set = set()
    counter = 1
    frontier = [(0, 0, start_key)]
    while frontier:
        cost, _, current = heapq.heappop(frontier)
        if current in closed or cost != best[current]:
            stats["stale_skipped"] += 1  # Superseded by a cheaper entry for this state.
            continue
        state = state_of[current]
        stats["goal_tests"] += 1
        if is_goal(state):
            states, actions, cursor = [state], [], current
            while parent[cursor] is not None:
                cursor, action = parent[cursor]
                actions.append(action)
                states.append(state_of[cursor])
            return SearchResult(FOUND, tuple(reversed(states)), tuple(reversed(actions)), cost, stats)
        closed.add(current)
        stats["expanded"] += 1
        for action, child, step in _support.records(successors, state, weighted=True):
            stats["generated"] += 1
            child_key = key(child)
            if child_key in closed:
                continue  # Nonnegative costs: a closed state's cost is already optimal.
            candidate = cost + step
            if child_key not in best or candidate < best[child_key]:
                if child_key in best:
                    stats["improvements"] += 1
                best[child_key] = candidate
                parent[child_key] = (current, action)
                state_of[child_key] = child
                heapq.heappush(frontier, (candidate, counter, child_key))
                counter += 1
                stats["pushed"] += 1
                stats["max_frontier"] = max(stats["max_frontier"], len(frontier))
    return SearchResult(FAILURE, (), (), None, stats)


def solve_text(text: str) -> dict:
    """Explicit-graph CLI: ``n m start g goal... u v cost ...`` with integer costs."""
    problem = _support.parse_problem(text, "ucs")
    table = _support.adjacency(problem["n"], problem["edges"])
    goals = set(problem["goals"])
    return uniform_cost_search(problem["start"], goals.__contains__, table.__getitem__).to_dict()


solve = uniform_cost_search

if __name__ == "__main__":
    _support.cli(solve_text)
