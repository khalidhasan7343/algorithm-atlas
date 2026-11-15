"""Depth-Limited Search example: one FOUND, one CUTOFF and one FAILURE outcome.

Run from the repository root:
python artificial-intelligence/uninformed-search/depth-limited-search/python/example.py
"""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("dls_example", Path(__file__).with_name("solution.py"))
dls = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(dls)

# A small one-way road map; actions are road names.
ROADS = {
    "Home": [("lane", "Park"), ("high-st", "Market")],
    "Park": [("river-path", "Bridge"), ("back-lane", "Home")],
    "Market": [("station-rd", "Station")],
    "Bridge": [("hill-rd", "Station")],
    "Station": [("rail", "Airport")],
    "Airport": [],
    "Island": [],
}


def successors(place):
    return ROADS[place]


def show(goal, limit):
    result = dls.depth_limited_search("Home", lambda p: p == goal, successors, limit)
    route = " -> ".join(result.states) if result.found else "-"
    print(f"goal={goal:<8} limit={limit} status={result.status:<7} route={route} "
          f"actions={list(result.actions)} expanded={result.stats['expanded']}")


if __name__ == "__main__":
    show("Station", 2)   # FOUND: Home -> Market -> Station (depth 2 = limit, inclusive).
    show("Airport", 2)   # CUTOFF: Airport needs 3 actions; deeper paths were truncated.
    show("Island", 10)   # FAILURE: no acyclic path reaches Island at any depth.
