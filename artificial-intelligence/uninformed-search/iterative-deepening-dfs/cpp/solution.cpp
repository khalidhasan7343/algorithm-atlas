// Iterative Deepening DFS over a general state space (C++17/C++20).
// Reuses the canonical C1 depth_limited_search with limits 0, 1, 2, ...
// Stops on FOUND, on definitive FAILURE, or with CUTOFF after max_depth.
#ifndef ATLAS_UNINFORMED_IDDFS_SOLUTION
#define ATLAS_UNINFORMED_IDDFS_SOLUTION

// Include the DLS canonical source without its command-line main().
#ifndef ATLAS_UNINFORMED_NO_MAIN
#define ATLAS_UNINFORMED_NO_MAIN
#define ATLAS_IDDFS_OWNS_MAIN
#endif
#include "../../depth-limited-search/cpp/solution.cpp"

#include <optional>

namespace atlas_search {

template <class State, class Action, class IsGoal, class Successors,
          class Hash = std::hash<State>, class Equal = std::equal_to<State>>
SearchResult<State, Action> iterative_deepening_search(const State& start, IsGoal is_goal, Successors successors,
                                                       std::optional<long long> max_depth = std::nullopt) {
    if (max_depth && *max_depth < 0) throw std::invalid_argument("max_depth must be nonnegative");
    Stats totals{"iterations", "final_limit", "expanded", "generated", "goal_tests", "boundary_checks", "cycle_skips"};
    for (long long limit = 0;; ++limit) {
        SearchResult<State, Action> run =
            depth_limited_search<State, Action, IsGoal, Successors, Hash, Equal>(start, is_goal, successors, limit);
        ++totals["iterations"];
        totals["final_limit"] = limit;
        for (const char* name : {"expanded", "generated", "goal_tests", "boundary_checks", "cycle_skips"})
            totals[name] += run.stats.at(name);
        if (run.status == Status::Found) {
            run.stats = totals;
            return run;
        }
        if (run.status == Status::Failure || (max_depth && limit >= *max_depth)) {
            SearchResult<State, Action> stopped;
            stopped.status = run.status;  // FAILURE, or CUTOFF at the maximum depth.
            stopped.stats = totals;
            return stopped;
        }
    }
}

// Solve one explicit-graph problem in the documented token grammar.
inline void solve_iddfs_problem(const Problem& p, std::ostream& out) {
    GraphSteps table = adjacency(p);
    std::vector<char> goals = goal_mask(p);
    auto result = iterative_deepening_search<int, int>(
        p.start, [&](int s) { return goals[static_cast<std::size_t>(s)] != 0; },
        [&](int s) { return table[static_cast<std::size_t>(s)]; }, p.max_depth);
    emit(out, result);
}

}  // namespace atlas_search

#ifdef ATLAS_IDDFS_OWNS_MAIN
#undef ATLAS_UNINFORMED_NO_MAIN
int main() {
    using namespace atlas_search;
    return run_cli([] { solve_iddfs_problem(parse_problem(std::cin, "iddfs"), std::cout); });
}
#endif
#endif  // ATLAS_UNINFORMED_IDDFS_SOLUTION
