"""C++ bidirectional BFS: executed under C++17 and C++20 against Python and an independent BFS."""
import json
import random
import subprocess

import pytest

pytestmark = pytest.mark.cpp


def test_random_cases_match_python_and_bfs_oracle(cpp_api, case_driver, algorithm, oracles, encoding):
    rng = random.Random(27311)
    problems = []
    for _ in range(500):
        n = rng.randint(1, 9)
        edges = oracles.random_graph(rng, n, rng.randint(0, 16))
        start, goal, directed = rng.randrange(n), rng.randrange(n), rng.random() < 0.6
        problems.append((n, edges, start, goal, directed,
                         encoding.encode("bidirectional", n, start, edges, goal=goal, directed=directed)))
    outputs = cpp_api(case_driver("bidirectional"))("\n".join(p[-1] for p in problems) + "\n")
    assert len(outputs) == len(problems)
    for (n, edges, start, goal, directed, text), output in zip(problems, outputs):
        assert output == algorithm.solve_text(text), text
        assert output["depth"] == oracles.bfs_distances(n, edges, start, directed=directed)[goal], text
        if output["status"] == "FOUND":
            oracles.assert_valid_path(edges, output["states"], output["actions"], start=start, goals={goal},
                                      directed=directed)


def test_cli_success_and_error_exit_codes(cpp_cli):
    ok = subprocess.run([str(cpp_cli)], input="6 6 0 5 0  0 1 1 2 2 5 0 3 3 4 4 5", text=True,
                        capture_output=True, timeout=30)
    assert ok.returncode == 0 and json.loads(ok.stdout)["states"] == [0, 1, 2, 5]
    for text in ["", "2 0 0 1 2", "2 0 0 2 1", "2 1 0 1 1 0"]:
        bad = subprocess.run([str(cpp_cli)], input=text, text=True, capture_output=True, timeout=30)
        assert bad.returncode == 2 and bad.stderr.startswith("error:") and not bad.stdout, text


GENERIC_API = r'''
struct PairHash { std::size_t operator()(const std::pair<int, int>& p) const { return std::hash<long long>()(p.first * 1000003LL + p.second); } };
using Cell = std::pair<int, int>;
auto moves = [](const Cell& c) {
    return std::vector<Step<Cell, char>>{{'E', {c.first + 1, c.second}}, {'W', {c.first - 1, c.second}},
                                         {'N', {c.first, c.second + 1}}, {'S', {c.first, c.second - 1}}};
};
auto grid = bidirectional_search_undirected<Cell, char, decltype(moves), PairHash>(Cell{0, 0}, Cell{2, 1}, moves);
std::cout << (grid.found() && grid.depth() == 3 && grid.states.back() == Cell{2, 1}) << '\n';
std::vector<std::vector<Step<int, int>>> succ(3), pred(3);
succ[0] = {{0, 1}}; pred[1] = {{0, 0}}; pred[2] = {{9, 1}};  // pred claims 1 -> 2, which is false.
bool threw = false;
try { bidirectional_search<int, int>(0, 2, [&](int s) { return succ[s]; }, [&](int s) { return pred[s]; }); }
catch (const std::invalid_argument&) { threw = true; }
std::cout << threw << '\n';
std::vector<std::vector<Step<int, int>>> f(4), b(4);
f[1] = {{0, 3}}; f[0] = {{1, 1}, {2, 3}}; b[3] = {{0, 1}, {2, 0}}; b[1] = {{1, 0}};
auto direct = bidirectional_search<int, int>(0, 3, [&](int s) { return f[s]; }, [&](int s) { return b[s]; });
std::cout << (direct.depth() == 1 && direct.actions == std::vector<int>{2}) << '\n';
auto same = bidirectional_search<int, int>(2, 2, [&](int s) { return f[s]; }, [&](int s) { return b[s]; });
std::cout << (same.found() && same.states == std::vector<int>{2} && same.stats.at("meeting_index") == 0) << '\n';
'''


def test_generic_api_contract(cpp_api):
    assert cpp_api(GENERIC_API)() == [1] * 4
