"""Iterative Deepening Depth-First Search (IDDFS) over a general state space.

IDDFS runs the canonical C1 Depth-Limited Search with limits 0, 1, 2, ...
It stops on FOUND, on definitive FAILURE (no reachable goal), or with CUTOFF
when the optional ``max_depth`` has been searched without a solution. See the
adjacent README for the shallowest-solution proof and repeated-work analysis.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any, Callable


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_CATEGORY = Path(__file__).resolve().parents[2]
_support = _load("atlas_uninformed_support", _CATEGORY / "support.py")
# Reuse the one canonical DLS implementation instead of copying it.
_dls = _load("atlas_uninformed_dls", _CATEGORY / "depth-limited-search/python/solution.py")

FOUND, CUTOFF, FAILURE = _support.FOUND, _support.CUTOFF, _support.FAILURE
SearchResult = _support.SearchResult


def iterative_deepening_search(start: Any, is_goal: Callable[[Any], bool],
                               successors: Callable[[Any], Any], *,
                               max_depth: int | None = None,
                               state_key: Callable[[Any], Any] | None = None) -> SearchResult:
    """Return a shallowest solution (fewest actions), FAILURE, or CUTOFF at ``max_depth``.

    With ``max_depth=None`` the limit grows until a solution or a definitive
    failure; on an infinite state space without a reachable goal that loop does
    not terminate, so pass ``max_depth`` for such spaces.
    """
    _support.require_callable(is_goal, "is_goal")
    _support.require_callable(successors, "successors")
    max_depth = _support.depth_value(max_depth, "max_depth", optional=True)
    _support.key_function(state_key)  # Validate state_key before the first iteration.
    totals = dict(iterations=0, final_limit=0, expanded=0, generated=0,
                  goal_tests=0, boundary_checks=0, cycle_skips=0)
    limit = 0
    while True:
        result = _dls.depth_limited_search(start, is_goal, successors, limit, state_key=state_key)
        totals["iterations"] += 1
        totals["final_limit"] = limit
        for name in ("expanded", "generated", "goal_tests", "boundary_checks", "cycle_skips"):
            totals[name] += result.stats[name]
        if result.status == FOUND:
            return SearchResult(FOUND, result.states, result.actions, result.cost, totals)
        if result.status == FAILURE:
            return SearchResult(FAILURE, (), (), None, totals)
        if max_depth is not None and limit >= max_depth:
            return SearchResult(CUTOFF, (), (), None, totals)
        limit += 1


def solve_text(text: str) -> dict:
    """Explicit-graph CLI: ``n m start max_depth g goal... u v ...`` (max_depth -1 = unbounded)."""
    problem = _support.parse_problem(text, "iddfs")
    table = _support.adjacency(problem["n"], problem["edges"])
    goals = set(problem["goals"])
    return iterative_deepening_search(problem["start"], goals.__contains__, table.__getitem__,
                                      max_depth=problem["max_depth"]).to_dict()


solve = iterative_deepening_search

if __name__ == "__main__":
    _support.cli(solve_text)
