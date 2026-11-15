// Depth-Limited Search over a general state space (C++17/C++20).
// Depth-first, path-local cycle detection, inclusive limit (initial state = depth 0).
// States at depth limit+1 are never goal-tested or explored; their existence only
// distinguishes CUTOFF from FAILURE. See ../README.md.
#ifndef ATLAS_UNINFORMED_DLS_SOLUTION
#define ATLAS_UNINFORMED_DLS_SOLUTION

#include "../../common.hpp"

#include <functional>
#include <unordered_set>

namespace atlas_search {

// Successors: State -> std::vector<Step<State, Action>> in exploration order.
// IsGoal: State -> bool. State needs Hash and Equal (std::hash/== by default).
template <class State, class Action, class IsGoal, class Successors,
          class Hash = std::hash<State>, class Equal = std::equal_to<State>>
SearchResult<State, Action> depth_limited_search(const State& start, IsGoal is_goal,
                                                 Successors successors, long long limit) {
    if (limit < 0) throw std::invalid_argument("limit must be nonnegative");
    SearchResult<State, Action> result;
    result.stats = Stats{"expanded", "generated", "goal_tests", "boundary_checks", "cycle_skips", "max_depth_reached"};
    Stats& stats = result.stats;
    auto goal = [&](const State& state) { ++stats["goal_tests"]; return static_cast<bool>(is_goal(state)); };
    if (goal(start)) {
        result.status = Status::Found;
        result.states = {start};
        result.has_cost = true;
        return result;
    }
    struct Frame { State state; std::vector<Step<State, Action>> children; std::size_t next; };
    std::vector<Frame> frames;
    std::vector<State> path_states{start};
    std::vector<Action> path_actions;
    std::unordered_set<State, Hash, Equal> on_path{start};
    bool cutoff = false;

    // Expand a non-goal state below the limit, or run the boundary check at the limit.
    auto enter = [&](const State& state, long long depth) {
        if (depth < limit) {
            ++stats["expanded"];
            std::vector<Step<State, Action>> children = successors(state);
            stats["generated"] += static_cast<long long>(children.size());
            frames.push_back(Frame{state, std::move(children), 0});
            return;
        }
        if (cutoff) return;  // A known cutoff cannot be changed by further checks.
        ++stats["boundary_checks"];
        std::vector<Step<State, Action>> children = successors(state);
        stats["generated"] += static_cast<long long>(children.size());
        for (const auto& child : children)
            if (on_path.count(child.next) == 0) { cutoff = true; break; }
    };

    enter(start, 0);
    while (!frames.empty()) {
        Frame& frame = frames.back();
        if (frame.next == frame.children.size()) {  // All children tried: backtrack.
            on_path.erase(frame.state);
            frames.pop_back();
            path_states.pop_back();
            if (!path_actions.empty()) path_actions.pop_back();
            continue;
        }
        Step<State, Action> step = frame.children[frame.next++];  // Copy: frames may grow.
        if (on_path.count(step.next) != 0) { ++stats["cycle_skips"]; continue; }
        long long depth = static_cast<long long>(frames.size());
        stats["max_depth_reached"] = std::max(stats["max_depth_reached"], depth);
        path_states.push_back(step.next);
        path_actions.push_back(step.action);
        on_path.insert(step.next);
        if (goal(step.next)) {
            result.status = Status::Found;
            result.states = std::move(path_states);
            result.actions = std::move(path_actions);
            result.cost = depth;
            result.has_cost = true;
            return result;
        }
        enter(step.next, depth);
        if (depth == limit) {  // Boundary states are never pushed; undo immediately.
            on_path.erase(step.next);
            path_states.pop_back();
            path_actions.pop_back();
        }
    }
    result.status = cutoff ? Status::Cutoff : Status::Failure;
    return result;
}

// Solve one explicit-graph problem in the documented token grammar.
inline void solve_dls_problem(const Problem& p, std::ostream& out) {
    GraphSteps table = adjacency(p);
    std::vector<char> goals = goal_mask(p);
    auto result = depth_limited_search<int, int>(
        p.start, [&](int s) { return goals[static_cast<std::size_t>(s)] != 0; },
        [&](int s) { return table[static_cast<std::size_t>(s)]; }, p.limit);
    emit(out, result);
}

}  // namespace atlas_search

#ifndef ATLAS_UNINFORMED_NO_MAIN
int main() {
    using namespace atlas_search;
    return run_cli([] { solve_dls_problem(parse_problem(std::cin, "dls"), std::cout); });
}
#endif
#endif  // ATLAS_UNINFORMED_DLS_SOLUTION
