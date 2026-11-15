// Uniform Cost Search with finite nonnegative step costs (C++17/C++20).
// Frontier: min-heap on (g, insertion counter). A goal is accepted only when it is
// popped with its current best cost; stale heap entries are skipped. See ../README.md.
#ifndef ATLAS_UNINFORMED_UCS_SOLUTION
#define ATLAS_UNINFORMED_UCS_SOLUTION

#include "../../common.hpp"

#include <functional>
#include <queue>
#include <tuple>
#include <unordered_map>

namespace atlas_search {

// Successors: State -> std::vector<WeightedStep<State, Action, Cost>>.
template <class State, class Action, class Cost, class IsGoal, class Successors,
          class Hash = std::hash<State>, class Equal = std::equal_to<State>>
SearchResult<State, Action, Cost> uniform_cost_search(const State& start, IsGoal is_goal, Successors successors) {
    SearchResult<State, Action, Cost> result;
    result.stats = Stats{"expanded", "generated", "goal_tests", "pushed", "stale_skipped", "improvements", "max_frontier"};
    Stats& stats = result.stats;
    std::unordered_map<State, std::size_t, Hash, Equal> index;  // State -> dense id.
    std::vector<State> state_of;
    std::vector<Cost> best;                                      // g(n) per id.
    std::vector<long long> parent;                               // -1 for the start.
    std::vector<std::optional<Action>> parent_action;
    std::vector<char> closed;
    auto id_of = [&](const State& state) {
        auto found = index.find(state);
        if (found != index.end()) return std::make_pair(found->second, false);
        std::size_t id = state_of.size();
        index.emplace(state, id);
        state_of.push_back(state);
        best.push_back(Cost{});
        parent.push_back(-1);
        parent_action.emplace_back();
        closed.push_back(0);
        return std::make_pair(id, true);
    };
    using Entry = std::tuple<Cost, unsigned long long, std::size_t>;  // Counter is unique.
    std::priority_queue<Entry, std::vector<Entry>, std::greater<Entry>> frontier;
    id_of(start);
    unsigned long long counter = 0;
    frontier.emplace(Cost{}, counter++, 0);
    stats["pushed"] = 1;
    stats["max_frontier"] = 1;
    while (!frontier.empty()) {
        auto [cost, order, current] = frontier.top();
        (void)order;
        frontier.pop();
        if (closed[current] || cost != best[current]) { ++stats["stale_skipped"]; continue; }
        ++stats["goal_tests"];
        if (is_goal(state_of[current])) {
            std::vector<std::size_t> chain{current};
            while (parent[chain.back()] != -1) chain.push_back(static_cast<std::size_t>(parent[chain.back()]));
            for (auto it = chain.rbegin(); it != chain.rend(); ++it) {
                result.states.push_back(state_of[*it]);
                if (parent[*it] != -1) result.actions.push_back(*parent_action[*it]);
            }
            result.status = Status::Found;
            result.cost = cost;
            result.has_cost = true;
            return result;
        }
        closed[current] = 1;
        ++stats["expanded"];
        std::vector<WeightedStep<State, Action, Cost>> children = successors(state_of[current]);
        for (const auto& child : children) checked_step_cost(child.cost);  // Validate every record.
        for (const auto& child : children) {
            ++stats["generated"];
            auto [child_id, fresh] = id_of(child.next);
            if (closed[child_id]) continue;  // Its cost is already optimal.
            Cost candidate = cost + child.cost;
            if (fresh || candidate < best[child_id]) {
                if (!fresh) ++stats["improvements"];
                best[child_id] = candidate;
                parent[child_id] = static_cast<long long>(current);
                parent_action[child_id] = child.action;
                frontier.emplace(candidate, counter++, child_id);
                ++stats["pushed"];
                stats["max_frontier"] = std::max(stats["max_frontier"], static_cast<long long>(frontier.size()));
            }
        }
    }
    result.status = Status::Failure;
    return result;
}

// Solve one explicit-graph problem in the documented token grammar.
inline void solve_ucs_problem(const Problem& p, std::ostream& out) {
    WeightedGraphSteps table = weighted_adjacency(p);
    std::vector<char> goals = goal_mask(p);
    auto result = uniform_cost_search<int, int, long long>(
        p.start, [&](int s) { return goals[static_cast<std::size_t>(s)] != 0; },
        [&](int s) { return table[static_cast<std::size_t>(s)]; });
    emit(out, result);
}

}  // namespace atlas_search

#ifndef ATLAS_UNINFORMED_NO_MAIN
int main() {
    using namespace atlas_search;
    return run_cli([] { solve_ucs_problem(parse_problem(std::cin, "ucs"), std::cout); });
}
#endif
#endif  // ATLAS_UNINFORMED_UCS_SOLUTION
