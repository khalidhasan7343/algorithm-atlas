"""C++ DLS: executed under C++17 and C++20 against Python and the exhaustive oracle."""
import json
import random
import subprocess

import pytest

pytestmark = pytest.mark.cpp


def cases(oracles, encoding, seed=27011, count=400):
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        n = rng.randint(1, 7)
        edges = oracles.random_graph(rng, n, rng.randint(0, 12))
        start, limit = rng.randrange(n), rng.randint(0, 6)
        goals = set(rng.sample(range(n), rng.randint(0, min(2, n))))
        out.append((n, edges, start, goals, limit, encoding.encode("dls", n, start, edges, limit=limit, goals=goals)))
    return out


def test_random_cases_match_python_and_exhaustive_oracle(cpp_api, case_driver, algorithm, oracles, encoding):
    problems = cases(oracles, encoding)
    outputs = cpp_api(case_driver("dls"))("\n".join(p[-1] for p in problems) + "\n")
    assert len(outputs) == len(problems)
    for (n, edges, start, goals, limit, text), output in zip(problems, outputs):
        assert output == algorithm.solve_text(text), text  # Identical results and statistics.
        status, states, actions = oracles.dls_expected(n, edges, start, goals, limit)
        assert (output["status"], output["states"], output["actions"]) == (status, list(states), list(actions)), text


def test_cli_success_and_error_exit_codes(cpp_cli):
    ok = subprocess.run([str(cpp_cli)], input="5 5 0 2 1 4  0 1 1 2 2 4 0 3 3 4", text=True,
                        capture_output=True, timeout=30)
    assert ok.returncode == 0 and not ok.stderr
    assert json.loads(ok.stdout)["states"] == [0, 3, 4]
    for text in ["", "1 0 0", "1 0 0 -1 0", "2 1 0 1 1 1 0 2", "1 0 0 0 0 9", "1 0 0 0 0 1.5",
                 "1 0 00 0 0", "1 0 0 0 0 -0", "1 0 0 1000000000000000000000 0"]:
        bad = subprocess.run([str(cpp_cli)], input=text, text=True, capture_output=True, timeout=30)
        assert bad.returncode == 2 and bad.stderr.startswith("error:") and not bad.stdout, text


GENERIC_API = r'''
auto grow = [](const std::string& s) {
    std::vector<Step<std::string, char>> out;
    if (s.size() < 6) { out.push_back({'a', s + "a"}); out.push_back({'b', s + "b"}); }
    return out;
};
auto r = depth_limited_search<std::string, char>(std::string(), [](const std::string& s) { return s == "ba"; }, grow, 2);
std::cout << (r.found() && r.states.back() == "ba" && r.depth() == 2 && r.actions[0] == 'b') << '\n';
auto cut = depth_limited_search<std::string, char>(std::string(), [](const std::string& s) { return s == "aaa"; }, grow, 2);
std::cout << (cut.status == Status::Cutoff && cut.states.empty() && !cut.has_cost) << '\n';
auto fail = depth_limited_search<std::string, char>(std::string(), [](const std::string&) { return false; }, grow, 6);
std::cout << (fail.status == Status::Failure && fail.stats.at("expanded") == 63) << '\n';
bool threw = false;
try { depth_limited_search<int, int>(0, [](int) { return false; }, [](int) { return std::vector<Step<int, int>>{}; }, -1); }
catch (const std::invalid_argument&) { threw = true; }
std::cout << threw << '\n';
std::vector<std::vector<Step<int, int>>> g(5);
g[0] = {{0, 1}}; g[1] = {{1, 2}}; g[2] = {{2, 3}}; g[0].push_back({3, 3}); g[3] = {{4, 4}};
auto shallow = depth_limited_search<int, int>(0, [](int s) { return s == 4; }, [&](int s) { return g[s]; }, 3);
std::cout << (shallow.found() && shallow.states == std::vector<int>{0, 3, 4}) << '\n';
auto chain = depth_limited_search<int, int>(0, [](int s) { return s == 20000; },
    [](int s) { return std::vector<Step<int, int>>{{s, s + 1}}; }, 20000);
std::cout << (chain.found() && chain.depth() == 20000) << '\n';
'''


def test_generic_api_contract(cpp_api):
    assert cpp_api(GENERIC_API)() == [1] * 6
