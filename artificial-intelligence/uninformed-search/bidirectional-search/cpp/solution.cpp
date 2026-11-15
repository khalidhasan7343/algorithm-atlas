// Bidirectional breadth-first search for unit-cost state spaces (C++17/C++20).
// Forward BFS from start via successors; backward BFS from goal via genuine
// predecessors (or the same successors when explicitly undirected). Whole layers
// are expanded on the smaller frontier (ties: shallower side, then forward). The
// best meeting is accepted once best <= depth_f + depth_b + 1. See ../README.md.
#ifndef ATLAS_UNINFORMED_BIDIRECTIONAL_SOLUTION
#define ATLAS_UNINFORMED_BIDIRECTIONAL_SOLUTION

#include "../../common.hpp"

#include <functional>
#include <optional>
#include <tuple>
#include <unordered_map>

namespace atlas_search {

namespace detail {

// Find the forward action for a hop, confirming that the transition really exists.
template <class State, class Action, class Successors, class Equal>
Action forward_action(Successors& successors, const State& from, const State& to,
                      const std::optional<Action>& known, bool undirected) {
    Equal equal;
    for (const auto& step : successors(from))
        if (equal(step.next, to) && (!known || step.action == *known)) return step.action;
    if (undirected) throw std::invalid_argument("undirected=true but a reverse transition has no forward successor");
    throw std::invalid_argument("predecessors(state) reported a transition that successors does not contain");
}

// Predecessors: State -> std::vector<Step<State, Action>> where {a, s} means s --a--> state.
template <class State, class Action, class Successors, class Predecessors, class Hash, class Equal>
SearchResult<State, Action> bidirectional(const State& start, const State& goal, Successors successors,
                                          Predecessors backward, bool undirected) {
    SearchResult<State, Action> result;
    result.stats = Stats{"forward_expanded", "backward_expanded", "generated", "forward_depth", "backward_depth",
                         "meeting_index"};
    Stats& stats = result.stats;
    stats["meeting_index"] = -1;
    if (Equal{}(start, goal)) {
        stats["meeting_index"] = 0;
        result.status = Status::Found;
        result.states = {start};
        result.has_cost = true;
        return result;
    }
    std::unordered_map<State, std::size_t, Hash, Equal> index;
    std::vector<State> state_of;
    std::vector<long long> dist_f, dist_b;                          // -1 = unlabeled
    std::vector<std::pair<long long, std::optional<Action>>> parent_f, parent_b;
    auto id_of = [&](const State& state) {
        auto found = index.find(state);
        if (found != index.end()) return found->second;
        std::size_t id = state_of.size();
        index.emplace(state, id);
        state_of.push_back(state);
        dist_f.push_back(-1);
        dist_b.push_back(-1);
        parent_f.emplace_back(-1, std::nullopt);
        parent_b.emplace_back(-1, std::nullopt);
        return id;
    };
    std::size_t s = id_of(start), g = id_of(goal);
    dist_f[s] = 0;
    dist_b[g] = 0;
    std::vector<std::size_t> frontier_f{s}, frontier_b{g};
    long long depth_f = 0, depth_b = 0;
    bool have_best = false;
    long long best_length = 0;
    std::size_t best_a = 0, best_b = 0;
    std::optional<Action> best_action;
    auto offer = [&](long long length, std::size_t a, std::size_t b, const std::optional<Action>& action) {
        if (!have_best || length < best_length) {  // Strict: the first shortest meeting wins.
            have_best = true;
            best_length = length;
            best_a = a;
            best_b = b;
            best_action = action;
        }
    };
    while (!frontier_f.empty() && !frontier_b.empty()) {
        if (have_best && best_length <= depth_f + depth_b + 1) break;
        std::vector<std::size_t> layer;
        if (std::make_pair(frontier_f.size(), depth_f) <= std::make_pair(frontier_b.size(), depth_b)) {
            for (std::size_t current : frontier_f) {
                ++stats["forward_expanded"];
                std::vector<Step<State, Action>> children = successors(state_of[current]);
                for (const auto& child : children) {
                    ++stats["generated"];
                    std::size_t c = id_of(child.next);
                    if (dist_f[c] == -1) {
                        dist_f[c] = depth_f + 1;
                        parent_f[c] = {static_cast<long long>(current), child.action};
                        layer.push_back(c);
                    }
                    if (dist_b[c] != -1) offer(depth_f + 1 + dist_b[c], current, c, child.action);
                }
            }
            frontier_f = std::move(layer);
            ++depth_f;
        } else {
            for (std::size_t current : frontier_b) {
                ++stats["backward_expanded"];
                std::vector<Step<State, Action>> parents = backward(state_of[current]);
                for (const auto& step : parents) {
                    ++stats["generated"];
                    std::size_t p = id_of(step.next);
                    std::optional<Action> action;
                    if (!undirected) action = step.action;
                    if (dist_b[p] == -1) {
                        dist_b[p] = depth_b + 1;
                        parent_b[p] = {static_cast<long long>(current), action};
                        layer.push_back(p);
                    }
                    if (dist_f[p] != -1) offer(dist_f[p] + 1 + depth_b, p, current, action);
                }
            }
            frontier_b = std::move(layer);
            ++depth_b;
        }
    }
    stats["forward_depth"] = depth_f;
    stats["backward_depth"] = depth_b;
    if (!have_best) {
        result.status = Status::Failure;
        return result;
    }
    std::vector<std::size_t> keys{best_a};
    std::vector<Action> actions;
    while (parent_f[keys.back()].first != -1) {
        actions.push_back(*parent_f[keys.back()].second);
        keys.push_back(static_cast<std::size_t>(parent_f[keys.back()].first));
    }
    std::reverse(keys.begin(), keys.end());
    std::reverse(actions.begin(), actions.end());
    stats["meeting_index"] = static_cast<long long>(keys.size()) - 1;
    std::vector<std::tuple<std::size_t, std::size_t, std::optional<Action>>> hops{{best_a, best_b, best_action}};
    for (std::size_t cursor = best_b; parent_b[cursor].first != -1;) {
        std::size_t following = static_cast<std::size_t>(parent_b[cursor].first);
        hops.emplace_back(cursor, following, parent_b[cursor].second);
        cursor = following;
    }
    for (const auto& [from, to, known] : hops) {
        actions.push_back(forward_action<State, Action, Successors, Equal>(successors, state_of[from], state_of[to],
                                                                           known, undirected));
        keys.push_back(to);
    }
    for (std::size_t k : keys) result.states.push_back(state_of[k]);
    result.actions = std::move(actions);
    result.status = Status::Found;
    result.cost = static_cast<long long>(result.actions.size());
    result.has_cost = true;
    return result;
}

}  // namespace detail

// Directed state space: predecessors(t) yields {a, s} for every forward transition s --a--> t.
template <class State, class Action, class Successors, class Predecessors,
          class Hash = std::hash<State>, class Equal = std::equal_to<State>>
SearchResult<State, Action> bidirectional_search(const State& start, const State& goal, Successors successors,
                                                 Predecessors predecessors) {
    return detail::bidirectional<State, Action, Successors, Predecessors, Hash, Equal>(
        start, goal, successors, predecessors, false);
}

// Only for spaces whose every transition is reversible; actions are recovered forward.
template <class State, class Action, class Successors,
          class Hash = std::hash<State>, class Equal = std::equal_to<State>>
SearchResult<State, Action> bidirectional_search_undirected(const State& start, const State& goal,
                                                            Successors successors) {
    return detail::bidirectional<State, Action, Successors, Successors, Hash, Equal>(
        start, goal, successors, successors, true);
}

// Solve one explicit-graph problem in the documented token grammar.
inline void solve_bidirectional_problem(const Problem& p, std::ostream& out) {
    GraphSteps forward = adjacency(p, p.directed);
    auto succ = [&](int s) { return forward[static_cast<std::size_t>(s)]; };
    if (p.directed) {
        GraphSteps reverse = adjacency(p, true, true);
        auto pred = [&](int s) { return reverse[static_cast<std::size_t>(s)]; };
        emit(out, bidirectional_search<int, int>(p.start, p.goal, succ, pred));
    } else {
        emit(out, bidirectional_search_undirected<int, int>(p.start, p.goal, succ));
    }
}

}  // namespace atlas_search

#ifndef ATLAS_UNINFORMED_NO_MAIN
int main() {
    using namespace atlas_search;
    return run_cli([] { solve_bidirectional_problem(parse_problem(std::cin, "bidirectional"), std::cout); });
}
#endif
#endif  // ATLAS_UNINFORMED_BIDIRECTIONAL_SOLUTION
