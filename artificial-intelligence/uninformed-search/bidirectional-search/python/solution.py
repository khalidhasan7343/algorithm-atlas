"""Bidirectional breadth-first search for unweighted (unit-cost) state spaces.

Forward BFS grows from ``start`` through ``successors``; backward BFS grows from
the single explicit ``goal`` through genuine ``predecessors``. Complete layers
are expanded, always on the side with the smaller frontier; equal sizes pick the
shallower side, then forward.
Every generated transition that touches a state labeled by the other side is a
candidate meeting; the best candidate is accepted only once

    best_length <= forward_depth + backward_depth + 1,

where the depths are those of the two *unexpanded* frontier layers. The README
proves that every shorter path has already been detected at that point.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any, Callable

_spec = importlib.util.spec_from_file_location(
    "atlas_uninformed_support", Path(__file__).resolve().parents[2] / "support.py")
_support = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_support)

FOUND, FAILURE = _support.FOUND, _support.FAILURE
SearchResult = _support.SearchResult
_UNKNOWN = object()  # Backward action not yet recovered (undirected mode).


def bidirectional_search(start: Any, goal: Any, successors: Callable[[Any], Any],
                         predecessors: Callable[[Any], Any] | None = None, *,
                         undirected: bool = False,
                         state_key: Callable[[Any], Any] | None = None) -> SearchResult:
    """Return a shortest (fewest-action) path from ``start`` to ``goal``, or FAILURE.

    ``successors(s)`` yields ``(action, t)`` meaning action leads from s to t.
    ``predecessors(t)`` yields ``(action, s)`` meaning the same forward action
    leads from s to t. A directed space must supply ``predecessors``. Pass
    ``undirected=True`` (and no predecessor function) only when every transition
    is reversible; backward actions are then recovered from forward successors,
    and a missing reverse transition raises ``ValueError``.
    """
    _support.require_callable(successors, "successors")
    if type(undirected) is not bool:
        raise TypeError("undirected must be a bool")
    if undirected and predecessors is not None:
        raise ValueError("pass either predecessors or undirected=True, not both")
    if not undirected:
        if predecessors is None:
            raise ValueError("directed bidirectional search needs a genuine predecessor function; "
                             "forward successors are not reverse edges (use undirected=True only "
                             "for reversible transitions)")
        _support.require_callable(predecessors, "predecessors")
    backward = successors if undirected else predecessors
    key = _support.key_function(state_key)
    stats = dict(forward_expanded=0, backward_expanded=0, generated=0,
                 forward_depth=0, backward_depth=0, meeting_index=-1)
    start_key, goal_key = key(start), key(goal)
    if start_key == goal_key:
        stats["meeting_index"] = 0
        return SearchResult(FOUND, (start,), (), 0, stats)

    state_of = {start_key: start, goal_key: goal}
    dist_f, dist_b = {start_key: 0}, {goal_key: 0}
    parent_f: dict = {start_key: None}  # key -> (previous key, forward action)
    parent_b: dict = {goal_key: None}   # key -> (next key toward goal, action or _UNKNOWN)
    frontier_f, frontier_b = [start_key], [goal_key]
    depth_f = depth_b = 0
    best = None  # (length, forward-side key a, backward-side key b, action a->b or _UNKNOWN)

    def offer(length: int, a: Any, b: Any, action: Any) -> None:
        nonlocal best
        if best is None or length < best[0]:  # Strict: the first shortest meeting wins.
            best = (length, a, b, action)

    while frontier_f and frontier_b:
        if best is not None and best[0] <= depth_f + depth_b + 1:
            break
        layer = []
        # Smaller frontier first; on equal sizes the shallower side, then forward.
        if (len(frontier_f), depth_f) <= (len(frontier_b), depth_b):
            for current in frontier_f:
                stats["forward_expanded"] += 1
                for action, child in _support.records(successors, state_of[current], weighted=False):
                    stats["generated"] += 1
                    child_key = key(child)
                    if child_key not in dist_f:
                        dist_f[child_key] = depth_f + 1
                        parent_f[child_key] = (current, action)
                        state_of.setdefault(child_key, child)
                        layer.append(child_key)
                    if child_key in dist_b:
                        offer(depth_f + 1 + dist_b[child_key], current, child_key, action)
            frontier_f, depth_f = layer, depth_f + 1
        else:
            for current in frontier_b:
                stats["backward_expanded"] += 1
                for action, previous in _support.records(backward, state_of[current], weighted=False,
                                                         name="predecessors" if not undirected else "successors"):
                    stats["generated"] += 1
                    previous_key = key(previous)
                    forward_action = _UNKNOWN if undirected else action
                    if previous_key not in dist_b:
                        dist_b[previous_key] = depth_b + 1
                        parent_b[previous_key] = (current, forward_action)
                        state_of.setdefault(previous_key, previous)
                        layer.append(previous_key)
                    if previous_key in dist_f:
                        offer(dist_f[previous_key] + 1 + depth_b, previous_key, current, forward_action)
            frontier_b, depth_b = layer, depth_b + 1
    stats["forward_depth"], stats["backward_depth"] = depth_f, depth_b
    if best is None:
        return SearchResult(FAILURE, (), (), None, stats)

    _, a, b, meeting_action = best
    forward_keys, actions, cursor = [a], [], a
    while parent_f[cursor] is not None:
        cursor, action = parent_f[cursor]
        forward_keys.append(cursor)
        actions.append(action)
    forward_keys.reverse()
    actions.reverse()
    stats["meeting_index"] = len(forward_keys) - 1
    hops = [(a, b, meeting_action)]
    cursor = b
    while parent_b[cursor] is not None:
        following, action = parent_b[cursor]
        hops.append((cursor, following, action))
        cursor = following
    keys = forward_keys
    for source, target, action in hops:
        actions.append(_forward_action(successors, key, state_of[source], target, action, undirected))
        keys.append(target)
    return SearchResult(FOUND, tuple(state_of[k] for k in keys), tuple(actions), len(actions), stats)


def _forward_action(successors: Callable, key: Callable, state: Any, target_key: Any,
                    action: Any, undirected: bool) -> Any:
    """Confirm a backward-discovered hop is a real forward transition."""
    for candidate, child in _support.records(successors, state, weighted=False):
        if key(child) == target_key and (action is _UNKNOWN or candidate == action):
            return candidate
    if undirected:
        raise ValueError("undirected=True but a reverse transition has no forward successor")
    raise ValueError("predecessors(state) reported a transition that successors does not contain")


def solve_text(text: str) -> dict:
    """Explicit-graph CLI: ``n m start goal directed u v ...`` (actions = edge indexes)."""
    problem = _support.parse_problem(text, "bidirectional")
    n, edges, directed = problem["n"], problem["edges"], problem["directed"]
    forward = _support.adjacency(n, edges, directed=directed)
    if directed:
        reverse = _support.adjacency(n, edges, reverse=True)
        result = bidirectional_search(problem["start"], problem["goal"], forward.__getitem__,
                                      reverse.__getitem__)
    else:
        result = bidirectional_search(problem["start"], problem["goal"], forward.__getitem__,
                                      undirected=True)
    return result.to_dict()


solve = bidirectional_search

if __name__ == "__main__":
    _support.cli(solve_text)
