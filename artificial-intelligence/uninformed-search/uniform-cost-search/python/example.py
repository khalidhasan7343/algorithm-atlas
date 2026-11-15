"""Uniform Cost Search example: the cheapest route is not the route with fewest roads.

Run from the repository root:
python artificial-intelligence/uninformed-search/uniform-cost-search/python/example.py
"""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("ucs_example", Path(__file__).with_name("solution.py"))
ucs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ucs)

# Travel minutes on one-way roads: (road, next town, minutes).
ROADS = {
    "A": [("toll-bridge", "D", 30), ("coast-1", "B", 5), ("ferry", "C", 12)],
    "B": [("coast-2", "C", 4), ("coast-3", "D", 20)],
    "C": [("hill", "D", 9), ("tunnel", "E", 0)],
    "E": [("e-road", "D", 6)],
    "D": [],
}

if __name__ == "__main__":
    result = ucs.uniform_cost_search("A", lambda town: town == "D", lambda town: ROADS[town])
    print("cheapest:", " -> ".join(result.states), "roads", list(result.actions), "minutes", result.cost)
    print("fewest roads: A -> D via toll-bridge costs 30 minutes with 1 road")
    print("stats:", dict(result.stats))
