// Shared C1 state-space contract for the C++ implementations (C++17 and C++20).
// No search algorithm lives here: each canonical solution.cpp implements its own.
// This header defines the result type, ordered statistics, the explicit-graph
// token grammar and JSON output used identically by the Python programs.
#pragma once

#include <algorithm>
#include <cmath>
#include <cstddef>
#include <initializer_list>
#include <iostream>
#include <iterator>
#include <limits>
#include <optional>
#include <stdexcept>
#include <string>
#include <tuple>
#include <type_traits>
#include <utility>
#include <vector>

namespace atlas_search {

enum class Status { Found, Cutoff, Failure };

inline const char* status_name(Status status) {
    switch (status) {
        case Status::Found: return "FOUND";
        case Status::Cutoff: return "CUTOFF";
        default: return "FAILURE";
    }
}

// Ordered named counters; insertion order is the documented output order.
class Stats {
public:
    Stats() = default;
    Stats(std::initializer_list<const char*> names) {
        for (const char* name : names) items_.emplace_back(name, 0);
    }
    long long& operator[](const std::string& name) {
        for (auto& item : items_) if (item.first == name) return item.second;
        items_.emplace_back(name, 0);
        return items_.back().second;
    }
    long long at(const std::string& name) const {
        for (const auto& item : items_) if (item.first == name) return item.second;
        throw std::out_of_range("unknown statistic " + name);
    }
    const std::vector<std::pair<std::string, long long>>& items() const { return items_; }
private:
    std::vector<std::pair<std::string, long long>> items_;
};

// One unweighted transition: applying `action` leads to `next`.
template <class State, class Action>
struct Step { Action action; State next; };

// One weighted transition with a finite nonnegative step cost.
template <class State, class Action, class Cost>
struct WeightedStep { Action action; State next; Cost cost; };

// states.front() is the initial state; actions[i] labels states[i] -> states[i+1].
// Unsuccessful searches keep both vectors empty and has_cost false.
template <class State, class Action, class Cost = long long>
struct SearchResult {
    Status status = Status::Failure;
    std::vector<State> states;
    std::vector<Action> actions;
    Cost cost{};
    bool has_cost = false;
    Stats stats;
    bool found() const { return status == Status::Found; }
    std::size_t depth() const { return actions.size(); }
};

template <class Cost>
Cost checked_step_cost(Cost cost) {
    static_assert(std::is_arithmetic_v<Cost> && !std::is_same_v<Cost, bool>, "costs must be numeric");
    if constexpr (std::is_floating_point_v<Cost>) {
        if (!std::isfinite(cost)) throw std::invalid_argument("step cost must be finite");
    }
    if (cost < Cost{}) throw std::invalid_argument("step cost must be nonnegative");
    return cost;
}

// ---------------------------------------------------------------------------
// Explicit-graph programs: vertices 0..n-1, action = zero-based edge index.
// ---------------------------------------------------------------------------
constexpr long long kMaxVertices = 100000;
constexpr long long kMaxEdges = 200000;
constexpr long long kMaxDepth = 100000;
constexpr long long kMaxCost = 1000000000000LL;

class TokenReader {
public:
    explicit TokenReader(std::istream& in) {
        std::string token;
        while (in >> token) tokens_.push_back(parse(token));
    }
    long long take(long long low, long long high, const std::string& name) {
        if (position_ >= tokens_.size()) throw std::invalid_argument("missing " + name);
        long long value = tokens_[position_++];
        if (value < low || value > high)
            throw std::invalid_argument(name + " must be in [" + std::to_string(low) + ", " + std::to_string(high) + "]");
        return value;
    }
    void finish() const {
        if (position_ != tokens_.size()) throw std::invalid_argument("unexpected trailing tokens");
    }
private:
    // Canonical ASCII decimal: optional '-', 1..18 digits, no leading zeros, no -0.
    static long long parse(const std::string& token) {
        std::size_t begin = token.size() > 0 && token[0] == '-' ? 1 : 0;
        std::string digits = token.substr(begin);
        bool ok = !digits.empty() && digits.size() <= 18 && (digits == "0" || digits[0] != '0') && token != "-0";
        for (char c : digits) ok = ok && c >= '0' && c <= '9';
        if (!ok) throw std::invalid_argument("expected canonical decimal integer token, got '" + token + "'");
        long long value = 0;
        for (char c : digits) value = value * 10 + (c - '0');
        return begin ? -value : value;
    }
    std::vector<long long> tokens_;
    std::size_t position_ = 0;
};

struct Edge { int u; int v; long long cost; };

struct Problem {
    int n = 0;
    int start = 0;
    long long limit = 0;                 // dls
    std::optional<long long> max_depth;  // iddfs (nullopt = unbounded)
    int goal = 0;                        // bidirectional
    bool directed = true;                // bidirectional
    std::vector<int> goals;              // dls, iddfs, ucs
    std::vector<Edge> edges;
};

inline Problem parse_problem(std::istream& in, const std::string& kind) {
    TokenReader reader(in);
    Problem p;
    p.n = static_cast<int>(reader.take(1, kMaxVertices, "vertex count"));
    long long m = reader.take(0, kMaxEdges, "edge count");
    p.start = static_cast<int>(reader.take(0, p.n - 1, "start"));
    if (kind == "dls") p.limit = reader.take(0, kMaxDepth, "depth limit");
    if (kind == "iddfs") {
        long long value = reader.take(-1, kMaxDepth, "maximum depth");
        if (value != -1) p.max_depth = value;
    }
    if (kind == "bidirectional") {
        p.goal = static_cast<int>(reader.take(0, p.n - 1, "goal"));
        p.directed = reader.take(0, 1, "directed flag") == 1;
    } else {
        long long count = reader.take(0, p.n, "goal count");
        for (long long i = 0; i < count; ++i) p.goals.push_back(static_cast<int>(reader.take(0, p.n - 1, "goal")));
    }
    for (long long i = 0; i < m; ++i) {
        Edge e{};
        e.u = static_cast<int>(reader.take(0, p.n - 1, "edge source"));
        e.v = static_cast<int>(reader.take(0, p.n - 1, "edge target"));
        e.cost = kind == "ucs" ? reader.take(0, kMaxCost, "edge cost") : 1;
        p.edges.push_back(e);
    }
    reader.finish();
    return p;
}

using GraphSteps = std::vector<std::vector<Step<int, int>>>;
using WeightedGraphSteps = std::vector<std::vector<WeightedStep<int, int, long long>>>;

inline GraphSteps adjacency(const Problem& p, bool directed = true, bool reverse = false) {
    GraphSteps table(static_cast<std::size_t>(p.n));
    for (std::size_t i = 0; i < p.edges.size(); ++i) {
        int u = reverse ? p.edges[i].v : p.edges[i].u, v = reverse ? p.edges[i].u : p.edges[i].v;
        table[static_cast<std::size_t>(u)].push_back({static_cast<int>(i), v});
        if (!directed) table[static_cast<std::size_t>(v)].push_back({static_cast<int>(i), u});
    }
    return table;
}

inline WeightedGraphSteps weighted_adjacency(const Problem& p) {
    WeightedGraphSteps table(static_cast<std::size_t>(p.n));
    for (std::size_t i = 0; i < p.edges.size(); ++i)
        table[static_cast<std::size_t>(p.edges[i].u)].push_back({static_cast<int>(i), p.edges[i].v, p.edges[i].cost});
    return table;
}

inline std::vector<char> goal_mask(const Problem& p) {
    std::vector<char> mask(static_cast<std::size_t>(p.n), 0);
    for (int g : p.goals) mask[static_cast<std::size_t>(g)] = 1;
    return mask;
}

template <class T>
void emit_list(std::ostream& out, const std::vector<T>& values) {
    out << '[';
    for (std::size_t i = 0; i < values.size(); ++i) out << (i ? "," : "") << values[i];
    out << ']';
}

// Same keys and value conventions as the Python SearchResult.to_dict().
template <class Cost>
void emit(std::ostream& out, const SearchResult<int, int, Cost>& r) {
    out << "{\"status\":\"" << status_name(r.status) << "\",\"states\":";
    emit_list(out, r.states);
    out << ",\"actions\":";
    emit_list(out, r.actions);
    out << ",\"cost\":";
    if (r.has_cost) out << r.cost; else out << "null";
    out << ",\"depth\":";
    if (r.found()) out << r.depth(); else out << "null";
    out << ",\"stats\":{";
    const auto& items = r.stats.items();
    for (std::size_t i = 0; i < items.size(); ++i)
        out << (i ? "," : "") << '"' << items[i].first << "\":" << items[i].second;
    out << "}}\n";
}

template <class Solve>
int run_cli(Solve solve) {
    try {
        solve();
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << '\n';
        return 2;
    }
}

}  // namespace atlas_search
