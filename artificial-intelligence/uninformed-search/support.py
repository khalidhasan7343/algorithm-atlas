"""Shared C1 state-space contract: result type, validation and graph CLI parsing.

No search algorithm lives here. Each canonical folder implements its own
algorithm; this module only defines the common contract documented in
``docs/uninformed-search-conventions.md`` so that results, validation errors
and command-line behavior are identical across the four C1 implementations.
"""
from __future__ import annotations

import json
import math
import numbers
import re
import sys
from types import MappingProxyType
from typing import Any, Callable, Hashable, Iterable, Mapping

FOUND = "FOUND"
CUTOFF = "CUTOFF"
FAILURE = "FAILURE"
STATUSES = (FOUND, CUTOFF, FAILURE)

# Resource bounds for the explicit-graph command-line programs only.
MAX_VERTICES = 100_000
MAX_EDGES = 200_000
MAX_DEPTH = 100_000
MAX_COST = 10**12


class SearchResult:
    """Immutable outcome of one search.

    ``states`` includes the initial state first and, when found, the goal state
    last; ``actions[i]`` labels the transition ``states[i] -> states[i + 1]``.
    Unsuccessful searches return empty paths and ``cost=None``. (A plain class
    rather than a dataclass, because canonical modules are loaded by file path.)
    """

    __slots__ = ("status", "states", "actions", "cost", "stats")

    def __init__(self, status: str, states: tuple = (), actions: tuple = (), cost: Any = None,
                 stats: Mapping[str, int] | None = None) -> None:
        if status not in STATUSES:
            raise ValueError(f"unknown search status {status!r}")
        states, actions = tuple(states), tuple(actions)
        if len(states) != (len(actions) + 1 if status == FOUND else 0):
            raise ValueError("a found path needs one more state than actions; others are empty")
        for name, value in (("status", status), ("states", states), ("actions", actions),
                            ("cost", cost), ("stats", MappingProxyType(dict(stats or {})))):
            object.__setattr__(self, name, value)

    def __setattr__(self, name: str, value: Any) -> None:
        raise AttributeError("SearchResult is immutable")

    def __eq__(self, other: object) -> bool:
        return isinstance(other, SearchResult) and self.to_dict() == other.to_dict()

    __hash__ = None

    def __repr__(self) -> str:
        return (f"SearchResult(status={self.status!r}, states={self.states!r}, "
                f"actions={self.actions!r}, cost={self.cost!r}, stats={dict(self.stats)!r})")

    @property
    def found(self) -> bool:
        return self.status == FOUND

    @property
    def depth(self) -> int | None:
        """Number of actions in the returned path, or None without a solution."""
        return len(self.actions) if self.found else None

    def to_dict(self) -> dict:
        return dict(status=self.status, states=list(self.states), actions=list(self.actions),
                    cost=self.cost, depth=self.depth, stats=dict(self.stats))


def require_callable(value: Any, name: str) -> Callable:
    if not callable(value):
        raise TypeError(f"{name} must be callable")
    return value


def key_function(state_key: Callable | None) -> Callable[[Any], Hashable]:
    """Return a key function that rejects unhashable state identities clearly."""
    if state_key is not None:
        require_callable(state_key, "state_key")

    def key(state: Any) -> Hashable:
        identity = state if state_key is None else state_key(state)
        try:
            hash(identity)
        except TypeError as error:
            subject = "state" if state_key is None else "state_key(state)"
            raise TypeError(f"{subject} must be hashable; supply a state_key that returns a "
                            f"hashable identity (got {type(identity).__name__})") from error
        return identity

    return key


def depth_value(value: Any, name: str, *, optional: bool = False) -> int | None:
    if value is None and optional:
        return None
    if type(value) is not int:
        raise TypeError(f"{name} must be an int" + (" or None" if optional else ""))
    if value < 0:
        raise ValueError(f"{name} must be nonnegative")
    return value


def step_cost(value: Any) -> numbers.Real:
    """Accept a finite nonnegative real transition cost (bool is not a cost)."""
    if isinstance(value, bool) or not isinstance(value, numbers.Real):
        raise TypeError(f"step cost must be a real number, got {type(value).__name__}")
    if not isinstance(value, numbers.Rational):  # Exact rationals are always finite.
        if not math.isfinite(float(value)):
            raise ValueError("step cost must be finite")
    if value < 0:
        raise ValueError("step cost must be nonnegative")
    return value


def records(generator: Callable, state: Any, *, weighted: bool, name: str = "successors") -> list:
    """Call a successor/predecessor function and validate every record eagerly.

    Unweighted records are ``(action, state)``; weighted records are
    ``(action, state, step_cost)``. Strings and mappings are rejected because
    their iteration would silently produce a different meaning.
    """
    produced = generator(state)
    if produced is None or isinstance(produced, (str, bytes, Mapping)):
        raise TypeError(f"{name}(state) must return an iterable of transition records")
    try:
        iterator = iter(produced)
    except TypeError as error:
        raise TypeError(f"{name}(state) must return an iterable of transition records") from error
    width = 3 if weighted else 2
    result = []
    for record in iterator:
        if not isinstance(record, (tuple, list)) or len(record) != width:
            shape = "(action, next_state, step_cost)" if weighted else "(action, next_state)"
            raise ValueError(f"{name} records must be {shape} tuples")
        if weighted:
            result.append((record[0], record[1], step_cost(record[2])))
        else:
            result.append((record[0], record[1]))
    return result


# --------------------------------------------------------------------------
# Explicit-graph command-line programs shared by the four canonical folders.
# --------------------------------------------------------------------------

def _tokens(text: str) -> list[int]:
    """Canonical ASCII decimal integers: optional '-', 1..18 digits, no leading zeros, no -0."""
    values = []
    # Split on the six ASCII whitespace bytes only, exactly like C++ stream extraction.
    for token in re.findall(r"[^ \t\n\v\f\r]+", text):
        digits = token[1:] if token.startswith("-") else token
        if (not token.isascii() or not digits.isdigit() or len(digits) > 18
                or (digits.startswith("0") and digits != "0") or token == "-0"):
            raise ValueError(f"expected canonical decimal integer token, got {token!r}")
        values.append(int(token))
    return values


class _Reader:
    def __init__(self, text: str) -> None:
        self.values, self.position = _tokens(text), 0

    def take(self, low: int, high: int, name: str) -> int:
        if self.position >= len(self.values):
            raise ValueError(f"missing {name}")
        value = self.values[self.position]
        self.position += 1
        if not low <= value <= high:
            raise ValueError(f"{name} must be in [{low}, {high}]")
        return value

    def finish(self) -> None:
        if self.position != len(self.values):
            raise ValueError("unexpected trailing tokens")


def parse_problem(text: str, kind: str) -> dict:
    """Parse the token grammar documented in each lesson's Input and Output section.

    ``kind`` is one of ``dls``, ``iddfs``, ``ucs`` or ``bidirectional``. Actions
    are zero-based edge indexes in input order.
    """
    reader = _Reader(text)
    n = reader.take(1, MAX_VERTICES, "vertex count")
    m = reader.take(0, MAX_EDGES, "edge count")
    start = reader.take(0, n - 1, "start")
    problem: dict = dict(n=n, start=start)
    if kind == "dls":
        problem["limit"] = reader.take(0, MAX_DEPTH, "depth limit")
    elif kind == "iddfs":
        value = reader.take(-1, MAX_DEPTH, "maximum depth")
        problem["max_depth"] = None if value == -1 else value
    if kind == "bidirectional":
        problem["goal"] = reader.take(0, n - 1, "goal")
        problem["directed"] = reader.take(0, 1, "directed flag") == 1
    else:
        count = reader.take(0, n, "goal count")
        problem["goals"] = [reader.take(0, n - 1, "goal") for _ in range(count)]
    edges = []
    for _ in range(m):
        u = reader.take(0, n - 1, "edge source")
        v = reader.take(0, n - 1, "edge target")
        edges.append((u, v, reader.take(0, MAX_COST, "edge cost")) if kind == "ucs" else (u, v))
    problem["edges"] = edges
    reader.finish()
    return problem


def adjacency(n: int, edges: Iterable, *, directed: bool = True, reverse: bool = False) -> list[list]:
    """Build successor (or predecessor) records whose action is the edge index."""
    table: list[list] = [[] for _ in range(n)]
    for index, edge in enumerate(edges):
        u, v = edge[0], edge[1]
        tail = tuple(edge[2:])
        if reverse:
            u, v = v, u
        table[u].append((index, v, *tail))
        if not directed:
            table[v].append((index, u, *tail))
    return table


def cli(solve_text: Callable[[str], dict]) -> None:
    """Run a token-grammar program: JSON on success, ``error: ...`` and exit 2 otherwise."""
    try:
        print(json.dumps(solve_text(sys.stdin.read()), separators=(",", ":")))
    except (ValueError, TypeError) as error:
        print("error: " + str(error), file=sys.stderr)
        raise SystemExit(2)
