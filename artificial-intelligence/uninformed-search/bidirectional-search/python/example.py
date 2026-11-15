"""Bidirectional search example: forward and backward frontiers meet in the middle.

Run from the repository root:
python artificial-intelligence/uninformed-search/bidirectional-search/python/example.py
"""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("bidirectional_example", Path(__file__).with_name("solution.py"))
bidirectional = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bidirectional)

# One-way "word ladder" moves between four-letter words (a directed state space).
MOVES = [("cold", "cord"), ("cord", "card"), ("card", "ward"), ("ward", "warm"),
         ("cold", "bold"), ("bold", "bolt"), ("cord", "core"), ("core", "wore"), ("wore", "ware"),
         ("ware", "warm")]
FORWARD, BACKWARD = {}, {}
for source, target in MOVES:
    FORWARD.setdefault(source, []).append((f"{source}->{target}", target))
    BACKWARD.setdefault(target, []).append((f"{source}->{target}", source))
log = []


def successors(word):
    log.append(("forward", word))
    return FORWARD.get(word, [])


def predecessors(word):
    log.append(("backward", word))
    return BACKWARD.get(word, [])


if __name__ == "__main__":
    result = bidirectional.bidirectional_search("cold", "warm", successors, predecessors)
    # Expansions come first in the log; later successor calls only confirm the backward half.
    expanded = log[:result.stats["forward_expanded"] + result.stats["backward_expanded"]]
    print("expansion order:", ", ".join(f"{side}:{word}" for side, word in expanded))
    print("path:", " -> ".join(result.states), "depth", result.depth)
    index = result.stats["meeting_index"]
    print("meeting edge:", result.states[index], "->", result.states[index + 1])
    print("stats:", dict(result.stats))
