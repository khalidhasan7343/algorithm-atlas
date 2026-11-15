"""C++ IDDFS: executed under C++17 and C++20 against Python and an independent BFS oracle."""
import json
import random
import subprocess

import pytest

pytestmark = pytest.mark.cpp


def test_random_cases_match_python_and_bfs_oracle(cpp_api, case_driver, algorithm, oracles, encoding):
    rng = random.Random(27111)
    problems = []
    for _ in range(400):
        n = rng.randint(1, 8)
        edges = oracles.random_graph(rng, n, rng.randint(0, 14))
        start, cap = rng.randrange(n), rng.choice([None, rng.randint(0, 4)])
        goals = set(rng.sample(range(n), rng.randint(0, min(3, n))))
        problems.append((n, edges, start, goals, cap,
                         encoding.encode("iddfs", n, start, edges, max_depth=cap, goals=goals)))
    outputs = cpp_api(case_driver("iddfs"))("\n".join(p[-1] for p in problems) + "\n")
    assert len(outputs) == len(problems)
    for (n, edges, start, goals, cap, text), output in zip(problems, outputs):
        assert output == algorithm.solve_text(text), text
        expected = oracles.nearest_goal_depth(n, edges, start, goals)
        if expected is not None and (cap is None or expected <= cap):
            assert output["status"] == "FOUND" and output["depth"] == expected, text
            oracles.assert_valid_path(edges, output["states"], output["actions"], start=start, goals=goals)
        elif expected is not None:
            assert output["status"] == "CUTOFF", text
        else:
            assert output["status"] in (("FAILURE",) if cap is None else ("FAILURE", "CUTOFF")), text


def test_cli_success_and_error_exit_codes(cpp_cli):
    ok = subprocess.run([str(cpp_cli)], input="5 5 0 -1 1 4  0 1 1 2 2 4 0 3 3 4", text=True,
                        capture_output=True, timeout=30)
    assert ok.returncode == 0 and json.loads(ok.stdout)["stats"]["iterations"] == 3
    for text in ["", "2 0 0 -2 0", "2 0 0 0 3 0 1 1", "2 1 0 0 1 1 0", "2 0 0 100001 0"]:
        bad = subprocess.run([str(cpp_cli)], input=text, text=True, capture_output=True, timeout=30)
        assert bad.returncode == 2 and bad.stderr.startswith("error:") and not bad.stdout, text


GENERIC_API = r'''
auto moves = [](long long s) { return std::vector<Step<long long, std::string>>{{"+1", s + 1}, {"*2", s * 2}}; };
auto r = iterative_deepening_search<long long, std::string>(1LL, [](long long s) { return s == 10; }, moves, 8);
std::cout << (r.found() && r.depth() == 4 && r.states.back() == 10 && r.stats.at("iterations") == 5) << '\n';
auto capped = iterative_deepening_search<long long, std::string>(1LL, [](long long s) { return s < 0; }, moves, 3);
std::cout << (capped.status == Status::Cutoff && capped.stats.at("final_limit") == 3) << '\n';
std::vector<std::vector<Step<int, int>>> cycle(4);
cycle[0] = {{0, 1}}; cycle[1] = {{1, 2}}; cycle[2] = {{2, 0}};
auto fail = iterative_deepening_search<int, int>(0, [](int s) { return s == 3; }, [&](int s) { return cycle[s]; });
std::cout << (fail.status == Status::Failure && fail.stats.at("iterations") == 3) << '\n';
bool threw = false;
try { iterative_deepening_search<int, int>(0, [](int) { return false; }, [&](int s) { return cycle[s]; }, -1LL); }
catch (const std::invalid_argument&) { threw = true; }
std::cout << threw << '\n';
'''


def test_generic_api_contract(cpp_api):
    assert cpp_api(GENERIC_API)() == [1] * 4
