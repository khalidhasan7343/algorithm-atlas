"""Bounded supplementary oracle probes; seed 20261024, no historical writes.

This audit-only harness supplements the canonical Python/C++ tests. Its fresh
probes run Python APIs. C++ parity/oracle and mutation tests run through pytest
under both standards; do not report these probes as fresh C++ executions.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from fractions import Fraction
from functools import lru_cache
import importlib.util
import itertools as it
import json
import math
from pathlib import Path
import random
import sys
import time

import yaml

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).parent / "evidence"
CAT = yaml.safe_load((ROOT / "catalog.yaml").read_text())
RECORDS = {a["id"]: a for a in CAT["algorithms"] if a["canonical_location"].startswith("dsa/")}
RNG = random.Random(20261024)
RESULTS = {}


def load(path, name):
    spec = importlib.util.spec_from_file_location("audit_" + name.replace("-", "_"), path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@lru_cache(None)
def module(aid):
    return load(ROOT / RECORDS[aid]["canonical_location"] / "python/solution.py", aid)


def record(aid, oracle):
    row = RESULTS.setdefault(aid, dict(status="passed", checks=0, oracles=[], language="Python API"))
    row["checks"] += 1
    if oracle not in row["oracles"]:
        row["oracles"].append(oracle)


def check(aid, expected, *args, method=None, **kwargs):
    before = deepcopy((args, kwargs))
    actual = getattr(module(aid), method or aid.replace("-", "_"))(*args, **kwargs)
    assert actual == expected, (aid, args, kwargs, actual, expected)
    assert (args, kwargs) == before, (aid, "unexpected input mutation")
    record(aid, "fresh bounded reference and input preservation")
    return actual


def subsets(values):
    return [list(x) for n in range(len(values) + 1) for x in it.combinations(values, n)]


def brute_subarray(values):
    all_ranges = [(sum(values[i:j]), i, j) for i in range(len(values)) for j in range(i + 1, len(values) + 1)]
    return min(all_ranges, key=lambda x: (-x[0], x[1], x[2])) if all_ranges else None


def early_categories():
    for _ in range(80):
        values = [RNG.randrange(-30, 31) for _ in range(RNG.randrange(40))]
        for a in RECORDS.values():
            if a["category"] == "A1":
                data = [RNG.randrange(101) / 100 for _ in values] if a["id"] == "bucket-sort" else values
                check(a["id"], sorted(data), data)
            elif a["category"] == "A2":
                data = values if a["id"] == "linear-search" else sorted(values)
                target = RNG.randrange(-35, 36)
                expected = next((i for i, v in enumerate(data) if v == target), -1)
                check(a["id"], expected, data, target)
        check("maximum-subarray-divide-and-conquer", brute_subarray(values), values, method="maximum_subarray")
        check("kadane", brute_subarray(values), values, method="maximum_subarray")
        a, b = RNG.randrange(-2**250, 2**250), RNG.randrange(-2**250, 2**250)
        check("karatsuba-multiplication", a * b, a, b)
        points = [(RNG.randrange(-8, 9), RNG.randrange(-8, 9)) for _ in range(RNG.randrange(12))]
        expected = min((((x - u)**2 + (y - v)**2, i, j)
                        for i, (x, y) in enumerate(points) for j, (u, v) in enumerate(points) if i < j), default=None)
        check("closest-pair-of-points", expected, points, method="closest_pair")
        n = RNG.randrange(8)
        a = [[RNG.randrange(-9, 10) for _ in range(n)] for _ in range(n)]
        b = [[RNG.randrange(-9, 10) for _ in range(n)] for _ in range(n)]
        product = [[sum(a[i][k] * b[k][j] for k in range(n)) for j in range(n)] for i in range(n)]
        check("strassen-matrix-multiplication", product, a, b, method="strassen_multiply")
    for _ in range(40):
        values = [RNG.randrange(-2, 3) for _ in range(RNG.randrange(7))]
        powers = [[v for v, selected in zip(values, bits) if selected] for bits in it.product((0, 1), repeat=len(values))]
        check("power-set-generation", powers, values)
        check("permutations", list(map(list, it.permutations(values))), values)
        k = RNG.randrange(len(values) + 3)
        check("combinations", list(map(list, it.combinations(values, k))), values, k)
        target = RNG.randrange(-8, 9)
        # Include-first preorder, stopping immediately on reaching target.
        candidates = [list(indices) for indices in subsets(list(range(len(values))))
                      if sum(values[i] for i in indices) == target]
        key = lambda indices: tuple(0 if i in indices else 1 for i in range(indices[-1] + 1)) if indices else ()
        expected = min(candidates, key=key) if candidates else None
        check("subset-sum-backtracking", expected, values, target)
    for n in range(8):
        solutions = [list(p) for p in it.permutations(range(n))
                     if len({i + c for i, c in enumerate(p)}) == n and len({i - c for i, c in enumerate(p)}) == n]
        check("n-queens", solutions, n)
    # Existing independently structured references supply Sudoku, maze and
    # graph-enumeration contracts; fresh randomized inputs supplement old vectors.
    for aid in ("sudoku-solver", "rat-in-a-maze", "graph-coloring", "hamiltonian-path"):
        cases = load(ROOT / RECORDS[aid]["canonical_location"] / "tests/cases.py", aid + "_references")
        if aid == "sudoku-solver":
            for _ in range(30):
                board = deepcopy(cases.SOLUTION)
                for index in RNG.sample(range(81), 18):
                    board[index // 9][index % 9] = 0
                actual = module(aid).solve_sudoku(board)
                cases.solved(actual, board)
                record(aid, "fresh removed-clue Sudoku: independent row/column/box invariants")
        elif aid == "rat-in-a-maze":
            for _ in range(40):
                grid = [[RNG.randrange(2) for _ in range(3)] for _ in range(2)]
                check(aid, cases.oracle(grid), grid)
        else:
            for _ in range(40):
                n = RNG.randrange(5)
                graph = [[0] * n for _ in range(n)]
                for u in range(n):
                    for v in range(u + 1, n):
                        graph[u][v] = graph[v][u] = RNG.randrange(2)
                if aid == "graph-coloring":
                    colors = RNG.randrange(5)
                    check(aid, cases.oracle(graph, colors), graph, colors)
                else:
                    check(aid, cases.oracle(graph), graph)


def dynamic_and_greedy():
    for n in range(93):
        # Closed combinatorial identity F(n)=sum choose(n-k-1,k).
        expected = sum(math.comb(n - k - 1, k) for k in range((n - 1) // 2 + 1)) if n else 0
        check("fibonacci", expected, n)
    for _ in range(60):
        n = RNG.randrange(8)
        values = [RNG.randrange(-8, 10) for _ in range(n)]
        weights = [RNG.randrange(6) for _ in range(n)]
        capacity = RNG.randrange(12)
        choices = subsets(list(range(n)))
        optimum = max(sum(values[i] for i in indices) for indices in choices if sum(weights[i] for i in indices) <= capacity)
        check("zero-one-knapsack", optimum, weights, values, capacity, method="knapsack")
        nonnegative = list(map(abs, values))
        check("subset-sum", any(sum(row) == capacity for row in subsets(nonnegative)), nonnegative, capacity)
        check("longest-increasing-subsequence", max((len(row) for row in subsets(values) if all(a < b for a, b in zip(row, row[1:]))), default=0), values, method="lis_length")
        a, b = ("".join(RNG.choice("abé") for _ in range(RNG.randrange(7))) for _ in range(2))
        sa, sb = {tuple(x) for x in subsets(a)}, {tuple(x) for x in subsets(b)}
        check("longest-common-subsequence", max(map(len, sa & sb)), a, b, method="lcs_length")
        @lru_cache(None)
        def edit(x, y):
            if not x or not y:
                return len(x) + len(y)
            return min(edit(x[1:], y) + 1, edit(x, y[1:]) + 1, edit(x[1:], y[1:]) + (x[0] != y[0]))
        check("edit-distance", edit(a, b), a, b)
        dims = [RNG.randrange(1, 10) for _ in range(RNG.randrange(2, 8))]
        def chain(i, j):
            return min((chain(i, k) + chain(k + 1, j) + dims[i] * dims[k + 1] * dims[j + 1] for k in range(i, j)), default=0)
        check("matrix-chain-multiplication", chain(0, len(dims) - 2), dims, method="matrix_chain_cost")
        coins = list(set(RNG.randrange(1, 7) for _ in range(RNG.randrange(5))))
        amount = RNG.randrange(15)
        possibilities = [counts for counts in it.product(*(range(amount // c + 1) for c in coins))
                         if sum(c * count for c, count in zip(coins, counts)) == amount]
        check("coin-change", min(map(sum, possibilities), default=None), coins, amount, method="minimum_coins")
        check("coin-change", len(possibilities), coins, amount, method="count_combinations")
        prices = [RNG.choice([None, -4, 0, 3, 8]) for _ in range(RNG.randrange(5))]
        def cut(length):
            if not length:
                return 0
            options = [p + remainder for k, p in enumerate(prices, 1) if k <= length and p is not None
                       for remainder in [cut(length - k)] if remainder is not None]
            return max(options, default=None)
        length = RNG.randrange(9)
        check("rod-cutting", cut(length), prices, length)
        def partitions(text):
            if not text:
                return 0
            return min(1 + partitions(text[i:]) for i in range(1, len(text) + 1) if text[:i] == text[:i][::-1])
        check("palindrome-partitioning", max(0, partitions(a) - 1), a, method="minimum_palindrome_cuts")
        # Exhaustive feasible subsets, independent of greedy ordering.
        acts = [(RNG.randrange(-5, 5), RNG.randrange(1, 7)) for _ in range(n)]
        acts = [(start, start + duration) for start, duration in acts]
        selected = module("activity-selection").activity_selection(acts)
        best = max(len(row) for row in subsets(list(range(n)))
                   if all(acts[u][1] <= acts[v][0] or acts[v][1] <= acts[u][0] for u, v in it.combinations(row, 2)))
        assert len(selected) == best and all(acts[u][1] <= acts[v][0] for u, v in zip(selected, selected[1:]))
        record("activity-selection", "all feasible interval subsets")
        deadlines = [RNG.randrange(6) for _ in range(n)]
        best = max(sum(values[i] for i in row) for row in choices
                   if all(deadlines[i] >= slot for slot, i in enumerate(sorted(row, key=lambda i: deadlines[i]), 1)))
        profit, slots = module("job-sequencing-with-deadlines").job_sequencing(deadlines, values)
        assert profit == best and len([i for i in slots if i is not None]) == len(set(i for i in slots if i is not None))
        assert all(i is None or deadlines[i] >= slot for slot, i in enumerate(slots, 1))
        record("job-sequencing-with-deadlines", "all feasible job subsets and slot constraints")
        weights = [w + 1 for w in weights]
        revenues = list(map(abs, values))
        extreme_values = []
        for row in choices:
            used = sum(weights[i] for i in row)
            if used > capacity:
                continue
            whole = sum(revenues[i] for i in row)
            extreme_values.append(Fraction(whole))
            for i in set(range(n)) - set(row):
                extreme_values.append(whole + revenues[i] * min(Fraction(1), Fraction(capacity - used, weights[i])))
        total, fractions = module("fractional-knapsack").fractional_knapsack(weights, revenues, capacity)
        assert total == max(extreme_values) and sum(w * f for w, f in zip(weights, fractions)) <= capacity
        record("fractional-knapsack", "all LP vertices: full subset plus one fractional item")
        frequencies = {i: RNG.randrange(1, 10) for i in range(RNG.randrange(7))}
        @lru_cache(None)
        def merge_cost(counts):
            if len(counts) < 2:
                return 0
            return min(counts[i] + counts[j] + merge_cost(tuple(sorted([c for k, c in enumerate(counts) if k not in (i, j)] + [counts[i] + counts[j]])))
                       for i in range(len(counts)) for j in range(i + 1, len(counts)))
        codec = module("huffman-coding").HuffmanCodec(frequencies)
        expected = next(iter(frequencies.values())) if len(frequencies) == 1 else merge_cost(tuple(sorted(frequencies.values())))
        codes = list(codec.codes.values())
        message = bytes(RNG.choices(list(frequencies), k=20)) if frequencies else b""
        assert codec.weighted_length() == expected and codec.decode(codec.encode(message)) == message
        assert all(not x.startswith(y) for i, x in enumerate(codes) for j, y in enumerate(codes) if i != j)
        record("huffman-coding", "all merge orders, prefix freedom, round trip")


def graph_and_trees():
    # These references are separate from the canonical algorithm implementations;
    # their provenance is retained, rather than described as newly written oracles.
    graph = load(ROOT / "dsa/graph-algorithms/oracles.py", "graph_references")
    for a in RECORDS.values():
        aid = a["id"]
        if a["category"] == "A5":
            cases = load(ROOT / a["canonical_location"] / "tests/cases.py", aid + "_references")
            for case, expected in cases.vectors():
                actual = module(aid).solve(**case)
                if hasattr(cases, "check"):
                    cases.check(actual, expected, case)
                else:
                    assert actual == expected, (aid, case)
                record(aid, "re-executed independent canonical graph reference vectors")
    for _ in range(60):
        n = RNG.randrange(1, 7)
        edges = [(RNG.randrange(n), RNG.randrange(n), RNG.randrange(7)) for _ in range(RNG.randrange(10))]
        source = RNG.randrange(n)
        expected = graph.simple_distances(n, edges, source, True)
        for aid in ("dijkstra", "bellman-ford"):
            assert module(aid).solve(n, edges, source)["distance"] == expected
            record(aid, "fresh nonnegative graphs vs independent simple-path enumeration")
        potential = [RNG.randrange(-10, 11) for _ in range(n)]
        signed = [(u, v, w + potential[v] - potential[u]) for u, v, w in edges]
        matrix = [graph.simple_distances(n, signed, s, True) for s in range(n)]
        for aid in ("floyd-warshall", "johnson"):
            assert module(aid).solve(n, signed) == matrix
            record(aid, "fresh potential-transformed graphs vs all simple paths")
        for aid in ("prim", "kruskal"):
            case = dict(n=n, edges=signed, directed=False)
            graph.check_mst(module(aid).solve(**case), graph.mst_weight(n, signed), case)
            record(aid, "fresh multigraph forests vs exhaustive edge subsets")
        plain = [(u, v) for u, v, w in edges]
        for aid in ("tarjan-strongly-connected-components", "kosaraju-strongly-connected-components", "bridges-detection", "articulation-points"):
            assert module(aid).solve(n, plain) == graph.structural_expected(aid, n, plain)
            record(aid, "fresh multigraphs vs reachability/removal reference")
        goal = RNG.randrange(n)
        result = module("a-star-search").solve(n, edges, source, goal, [0] * n)
        assert result["cost"] == expected[goal]
        record("a-star-search", "fresh zero-heuristic shortest paths vs all simple paths")
    tree = load(ROOT / "dsa/tree-algorithms/oracles.py", "tree_references")
    names = [a["id"] for a in RECORDS.values() if a["category"] == "A6"]
    for aid in names:
        if aid.endswith("traversal"):
            for _ in range(40):
                case = tree.random_binary(RNG, RNG.randrange(50))
                check(aid, tree.traversal_reference(aid, case), method="solve", **case)
        elif aid in ("lowest-common-ancestor", "binary-lifting", "euler-tour"):
            for _ in range(40):
                parents = [None] + [RNG.randrange(v) for v in range(1, RNG.randrange(1, 70))]
                pairs = [[RNG.randrange(len(parents)), RNG.randrange(len(parents))] for _ in range(20)]
                if aid == "euler-tour":
                    check(aid, tree.euler_reference(parents, 0), parents, 0, method="solve")
                elif aid == "lowest-common-ancestor":
                    check(aid, [tree.lca_reference(parents, a, b) for a, b in pairs], parents, 0, pairs, method="solve")
                else:
                    check(aid, [tree.lca_reference(parents, a, b) for a, b in pairs], parents, 0, [[1, *p] for p in pairs], method="solve")
        elif aid in ("fenwick-tree", "segment-tree"):
            for _ in range(30):
                values = [RNG.randrange(-50, 51) for _ in range(30)]
                obj = getattr(module(aid), "FenwickTree" if aid == "fenwick-tree" else "SegmentTree")(values)
                for _ in range(80):
                    i, value = RNG.randrange(30), RNG.randrange(-50, 51)
                    if aid == "fenwick-tree":
                        obj.add(i, value - values[i])
                    else:
                        obj.set(i, value)
                    values[i] = value
                    lo, hi = sorted([RNG.randrange(31), RNG.randrange(31)])
                    assert obj.range_sum(lo, hi) == sum(values[lo:hi])
                    record(aid, "fresh mutation streams vs naive range sums")
        elif aid == "trie":
            for case, expected in tree.trie_vectors():
                check(aid, expected, method="solve", **case)
        else:
            make = getattr(module(aid), {"avl-tree-rotations": "AVLTree", "red-black-tree-operations": "RedBlackTree",
                                        "b-tree-operations": "BTree", "b-plus-tree-operations": "BPlusTree"}[aid])
            for degree in range(2, 9):
                obj = make(degree) if aid in ("b-tree-operations", "b-plus-tree-operations") else make()
                state = set()
                for _ in range(400):
                    key, insert = RNG.randrange(-100, 101), RNG.choice([True, False])
                    expected = key not in state if insert else key in state
                    assert (obj.insert(key) if insert else obj.erase(key)) == expected
                    state.add(key) if insert else state.discard(key)
                    assert obj.keys() == sorted(state)
                    if aid in ("b-tree-operations", "b-plus-tree-operations"):
                        plus = aid == "b-plus-tree-operations"
                        tree.check_multiway_snapshot(tree.multiway_snapshot(obj.root, plus), state, degree, plus)
                    else:
                        kind = "avl" if aid == "avl-tree-rotations" else "red-black"
                        tree.check_binary_snapshot(tree.binary_snapshot(obj.root, kind), state, kind)
                    record(aid, "fresh mutations; reference set plus independent structural invariant walker")


def strings_bits_math_windows():
    for _ in range(100):
        text = bytes(RNG.choice(b"ab\0\xff#$") for _ in range(RNG.randrange(60)))
        pattern = text[:RNG.randrange(8)] if RNG.randrange(2) else bytes(RNG.choice(b"ab\0\xff#$") for _ in range(RNG.randrange(8)))
        expected = [i for i in range(len(text) + 1) if text[i:i + len(pattern)] == pattern]
        for aid in ("naive-pattern-matching", "knuth-morris-pratt", "rabin-karp", "z-algorithm", "boyer-moore"):
            check(aid, expected, text, pattern, method="solve")
        for aid, name in (("suffix-array", "SuffixArray"), ("suffix-tree", "SuffixTree")):
            obj = getattr(module(aid), name)(text)
            assert obj.find(pattern) == expected
            if aid == "suffix-array":
                assert obj.sa == sorted(range(len(text)), key=lambda i: text[i:])
            record(aid, "fresh binary text vs direct slicing and suffix sorting")
        # Manacher's full radii and deterministic longest interval, using the
        # existing independent expansion reference (no production-code reuse).
        oracle = load(ROOT / "dsa/string-algorithms/string_oracles.py", "string_reference")
        check("manacher", oracle.palindromes(text), text, method="solve")
        patterns = [pattern, b"", b"a", pattern]
        ac = module("aho-corasick").AhoCorasick(patterns)
        assert ac.find(text) == oracle.multi(text, patterns)
        record("aho-corasick", "fresh binary multi-pattern data vs repeated naive slices")
        unique = RNG.sample(range(-100, 101), 8)
        paired = unique[2:] * 2
        one, two = paired + unique[:1], paired + unique[:2]
        RNG.shuffle(one); RNG.shuffle(two)
        check("xor-unique-elements", unique[0], one, method="solve")
        check("two-non-repeating-elements", sorted(unique[:2]), two, method="solve")
        value = RNG.randrange(-2**31, 2**31)
        check("brian-kernighan-set-bit-counting", (value & (2**32 - 1)).bit_count(), value, method="solve")
        values = [RNG.randrange(-4, 5) for _ in range(RNG.randrange(10))]
        masks = [[v for i, v in enumerate(values) if (mask // 2**i) % 2] for mask in range(2**len(values))]
        check("subset-generation-bitmasking", masks, values, method="solve")
        a, b = RNG.randrange(-10**9, 10**9 + 1), RNG.randrange(-10**9, 10**9 + 1)
        check("euclidean-algorithm", math.gcd(a, b), a, b, method="solve")
        check("least-common-multiple", math.lcm(a, b), a, b, method="solve")
        g, x, y = module("extended-euclidean-algorithm").solve(a, b)
        assert a*x + b*y == g == math.gcd(a, b)
        record("extended-euclidean-algorithm", "fresh full-domain integers: Bezout and math.gcd")
        base, exponent, modulus = RNG.randrange(-8, 9), RNG.randrange(20), RNG.randrange(1, 1000000008)
        check("fast-exponentiation", pow(base, exponent), base, exponent, method="solve")
        check("modular-exponentiation", pow(base, exponent, modulus), base, exponent, modulus, method="solve")
        n = RNG.randrange(1, 20000)
        factors = module("prime-factorization").solve(n)
        assert math.prod(p**e for p, e in factors) == n
        assert all(p >= 2 and e > 0 and all(p % d for d in range(2, math.isqrt(p) + 1)) for p, e in factors)
        assert [p for p, e in factors] == sorted(set(p for p, e in factors))
        record("prime-factorization", "fresh integers: reconstruction, ascending prime factors, exponents")
        limit = RNG.randrange(1000)
        check("sieve-of-eratosthenes", [n for n in range(2, limit + 1) if all(n % d for d in range(2, math.isqrt(n) + 1))], limit, method="solve")
        ordered = sorted(values)
        target = RNG.randrange(-8, 9)
        pairs = [[i, j] for i in range(len(ordered)) for j in range(i + 1, len(ordered)) if ordered[i] + ordered[j] == target]
        check("two-sum-sorted-array", min(pairs, default=[]), ordered, target, method="solve")
        k = RNG.randrange(1, len(values) + 1) if values else 0
        check("sliding-window-maximum", [max(values[i:i + k]) for i in range(len(values) - k + 1)] if k else [], values, k, method="solve")
        intervals = [(i, j) for i in range(len(text) + 1) for j in range(i, len(text) + 1) if len(set(text[i:j])) == j - i]
        best = min(intervals, key=lambda x: (x[0] - x[1], x[0], x[1]))
        check("longest-substring-without-repeating-characters", list(best), text, method="solve")


def performance():
    """Bounded practical-size checks; elapsed times are observations, not CI limits."""
    measurements = []
    def timed(label, action):
        start = time.monotonic()
        action()
        measurements.append(dict(check=label, status="passed", elapsed_seconds=round(time.monotonic() - start, 6)))
    def sorts():
        values = [RNG.randrange(-100000, 100001) for _ in range(20000)]
        for aid in ("quick-sort", "tim-sort", "heap-sort", "counting-sort", "radix-sort"):
            check(aid, sorted(values), values)
    timed("five sorting cores vs sorted, 20000 integers", sorts)
    def chains():
        n = 10000
        children = [[i + 1 if i + 1 < n else None, None] for i in range(n)]
        for aid, expected in (("preorder-traversal", list(range(n))), ("inorder-traversal", list(range(n - 1, -1, -1))),
                              ("postorder-traversal", list(range(n - 1, -1, -1))), ("level-order-traversal", [[i] for i in range(n)])):
            check(aid, expected, [0] * n, children, 0, method="solve")
        parents = [None, *range(n - 1)]
        jumps = module("binary-lifting").BinaryLifting(parents, 0)
        assert jumps.lca(n - 1, n // 2) == n // 2 and jumps.kth_ancestor(n - 1, n - 1) == 0
    timed("10000-node chain traversals and ancestor queries", chains)
    def balanced():
        for aid, name in (("avl-tree-rotations", "AVLTree"), ("red-black-tree-operations", "RedBlackTree"),
                          ("b-tree-operations", "BTree"), ("b-plus-tree-operations", "BPlusTree")):
            obj = getattr(module(aid), name)()
            for key in range(1000):
                assert obj.insert(key)
            assert obj.keys() == list(range(1000))
            for key in range(1000):
                assert obj.erase(key)
            assert obj.keys() == []
    timed("four balanced sets, 1000 ascending inserts then complete deletion", balanced)
    def graph_chain():
        n = 1000
        edges = [(i, i + 1) for i in range(n - 1)]
        assert module("breadth-first-search").solve(n, edges, 0)["distance"] == list(range(n))
        assert module("depth-first-search").solve(n, edges)["order"] == list(range(n))
        assert module("bridges-detection").solve(n, edges) == list(range(n - 1))
        assert module("articulation-points").solve(n, edges) == list(range(1, n - 1))
    timed("1000-node graph chain and low-link boundaries", graph_chain)
    def strings():
        text = b"a" * 10000
        assert module("knuth-morris-pratt").solve(text, b"aaa") == list(range(9998))
        assert module("boyer-moore").solve(text, b"aaa") == list(range(9998))
        assert module("suffix-tree").SuffixTree(text[:2048]).find(b"aaa") == list(range(2046))
        assert module("manacher").solve(text)[2] == [0, 10000]
        assert module("longest-substring-without-repeating-characters").solve(bytes(range(256)) * 39) == [0, 256]
    timed("repetitive 10000-byte matching/palindromes; 2048-byte suffix tree", strings)
    def numbers():
        primes = module("sieve-of-eratosthenes").solve(1000000)
        assert len(primes) == 78498 and primes[-1] == 999983
        assert module("prime-factorization").solve(10**12) == [[2, 12], [5, 12]]
        values = list(range(10000))
        assert module("sliding-window-maximum").solve(values, 500) == list(range(499, 10000))
    timed("sieve inclusive 1000000, factorization 10^12, 10000-item window", numbers)
    OUT.mkdir(exist_ok=True)
    (OUT / "performance.json").write_text(json.dumps(dict(seed=20261024, measurements=measurements,
                                                          timing_thresholds="none; bounded smoke checks only"), indent=2) + "\n")
    print(json.dumps(measurements, indent=2))


def main():
    started = time.monotonic()
    try:
        early_categories()
        dynamic_and_greedy()
        graph_and_trees()
        strings_bits_math_windows()
        assert set(RESULTS) == set(RECORDS), sorted(set(RECORDS) - RESULTS.keys())
    except Exception as error:
        OUT.mkdir(exist_ok=True)
        (OUT / "independent-probes.json").write_text(json.dumps(dict(seed=20261024, status="failed", error=repr(error), algorithms=RESULTS), indent=2) + "\n")
        raise
    result = dict(seed=20261024, status="passed", algorithm_count=len(RESULTS),
                  checks=sum(r["checks"] for r in RESULTS.values()),
                  elapsed_seconds=round(time.monotonic() - started, 3),
                  scope="Python supplementary probes; C++ reference/parity suites recorded separately",
                  algorithms=RESULTS)
    OUT.mkdir(exist_ok=True)
    (OUT / "independent-probes.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "algorithms"}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--performance", action="store_true")
    args = parser.parse_args()
    performance() if args.performance else main()
