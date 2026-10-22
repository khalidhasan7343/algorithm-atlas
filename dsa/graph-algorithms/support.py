"""Validation, canonical imports and CLI support; no graph algorithm is hidden here."""
import importlib.util
import json
from pathlib import Path
import sys
from functools import lru_cache


def integer(value, low, high, name):
    if type(value) is not int or not low <= value <= high:
        raise ValueError(f"{name} must be an integer in [{low}, {high}]")
    return value


def graph(n, edges, directed, weighted=False, cap=1000, low=-10**6, high=10**6):
    integer(n, 0, cap, "vertex count")
    if type(directed) is not bool:
        raise ValueError("directed must be bool")
    if not isinstance(edges, (list, tuple)) or len(edges) > 10000:
        raise ValueError("edges must be a sequence of at most 10000 records")
    adj, arcs = [[] for _ in range(n)], []
    for i, edge in enumerate(edges):
        if not isinstance(edge, (list, tuple)) or len(edge) != (3 if weighted else 2):
            raise ValueError("incorrect edge record width")
        u = integer(edge[0], 0, n-1, "edge source")
        v = integer(edge[1], 0, n-1, "edge target")
        w = integer(edge[2], low, high, "weight") if weighted else 1
        adj[u].append((v, w, i)); arcs.append((u, v, w, i))
        if not directed:
            adj[v].append((u, w, i)); arcs.append((v, u, w, i))
    return adj, arcs


def source_vertex(n, source):
    if n == 0 and source is None:
        return None
    return integer(source, 0, n-1, "source")


def path_to(result, target):
    integer(target, 0, len(result["distance"])-1, "target")
    if result["distance"][target] in (None, "-inf"):
        return {"vertices": [], "edges": []}
    vertices, edges, v = [], [], target
    while v is not None:
        vertices.append(v)
        if len(vertices) > len(result["distance"]):
            raise ValueError("cyclic predecessor chain")
        if result["parent_edge"][v] is not None:
            edges.append(result["parent_edge"][v])
        v = result["parent"][v]
    return {"vertices": vertices[::-1], "edges": edges[::-1]}


@lru_cache(None)
def canonical(name):
    location = Path(__file__).parent / name / "python/solution.py"
    spec = importlib.util.spec_from_file_location("atlas_graph_" + name, location)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main(solve):
    try:
        payload = json.load(sys.stdin)
        if not isinstance(payload, dict):
            raise ValueError("input must be a JSON object")
        print(json.dumps(solve(**payload), separators=(",", ":")))
    except (ValueError, TypeError, KeyError) as error:
        print("error: " + str(error), file=sys.stderr)
        raise SystemExit(2)
