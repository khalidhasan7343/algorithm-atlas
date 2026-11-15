"""C++ UCS: executed under C++17 and C++20 against Python, Bellman-Ford and cost validation."""
import json
import random
import subprocess

import pytest

pytestmark = pytest.mark.cpp


def test_random_cases_match_python_and_bellman_ford(cpp_api, case_driver, algorithm, oracles, encoding):
    rng = random.Random(27211)
    problems = []
    for _ in range(400):
        n = rng.randint(1, 8)
        edges = oracles.random_graph(rng, n, rng.randint(0, 16), max_cost=rng.choice([0, 2, 9, 10**12]))
        start = rng.randrange(n)
        goals = set(rng.sample(range(n), rng.randint(0, min(3, n))))
        problems.append((n, edges, start, goals, encoding.encode("ucs", n, start, edges, goals=goals)))
    outputs = cpp_api(case_driver("ucs"))("\n".join(p[-1] for p in problems) + "\n")
    assert len(outputs) == len(problems)
    for (n, edges, start, goals, text), output in zip(problems, outputs):
        assert output == algorithm.solve_text(text), text
        assert output["cost"] == oracles.cheapest_goal_cost(n, edges, start, goals), text
        if output["status"] == "FOUND":
            oracles.assert_valid_path(edges, output["states"], output["actions"], start=start, goals=goals)
            assert oracles.path_cost(edges, output["actions"]) == output["cost"]


def test_cli_success_and_error_exit_codes(cpp_cli):
    ok = subprocess.run([str(cpp_cli)], input="4 4 0 1 3  0 1 1 1 3 5 0 2 2 2 3 2", text=True,
                        capture_output=True, timeout=30)
    assert ok.returncode == 0 and json.loads(ok.stdout)["cost"] == 4
    for text in ["", "2 1 0 1 1 0 1 -1", "2 1 0 1 1 0 1 1000000000001", "2 1 0 1 1 0 1", "2 1 0 1 1 0 1 2.5"]:
        bad = subprocess.run([str(cpp_cli)], input=text, text=True, capture_output=True, timeout=30)
        assert bad.returncode == 2 and bad.stderr.startswith("error:") and not bad.stdout, text


GENERIC_API = r'''
using WS = WeightedStep<std::string, std::string, double>;
auto roads = [](const std::string& s) {
    if (s == "A") return std::vector<WS>{{"A-C", "C", 10.0}, {"A-B", "B", 1.0}};
    if (s == "B") return std::vector<WS>{{"B-C", "C", 2.5}, {"B-B", "B", 0.0}};
    return std::vector<WS>{};
};
auto r = uniform_cost_search<std::string, std::string, double>(std::string("A"), [](const std::string& s) { return s == "C"; }, roads);
std::cout << (r.found() && r.cost == 3.5 && r.actions == std::vector<std::string>{"A-B", "B-C"} && r.stats.at("improvements") == 1) << '\n';
for (double bad : {-1.0, std::nan(""), std::numeric_limits<double>::infinity(), -std::numeric_limits<double>::infinity()}) {
    bool threw = false;
    try {
        uniform_cost_search<int, int, double>(0, [](int) { return false; },
            [bad](int s) { return s == 0 ? std::vector<WeightedStep<int, int, double>>{{0, 1, bad}} : std::vector<WeightedStep<int, int, double>>{}; });
    } catch (const std::invalid_argument&) { threw = true; }
    std::cout << threw << '\n';
}
auto zero = uniform_cost_search<int, int, long long>(0, [](int s) { return s == 2; }, [](int s) {
    std::vector<WeightedStep<int, int, long long>> out;
    if (s == 0) { out.push_back({0, 1, 0}); out.push_back({1, 2, 1}); }
    if (s == 1) out.push_back({2, 2, 0});
    return out;
});
std::cout << (zero.cost == 0 && zero.states == std::vector<int>{0, 1, 2}) << '\n';
'''


def test_generic_api_contract(cpp_api):
    assert cpp_api(GENERIC_API)() == [1] * 6
