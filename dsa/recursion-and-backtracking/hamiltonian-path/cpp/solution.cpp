// Direct recursive backtracking. Define ALGORITHM_ATLAS_NO_MAIN for API use.
#include <charconv>
#include <cstddef>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <limits>
#include <optional>
#include <stdexcept>
#include <string>
#include <system_error>
#include <type_traits>
#include <vector>

namespace algorithm_atlas {
using Graph = std::vector<std::vector<long long>>;
void validate_graph(const Graph& adjacency, bool directed) {
    const auto n = adjacency.size();
    for (const auto& row : adjacency) {
        if (row.size() != n) { throw std::invalid_argument("matrix must be square"); }
        for (auto value : row) {
            if (value != 0 && value != 1) { throw std::invalid_argument("edges must be binary"); }
        }
    }
    if (!directed) {
        for (std::size_t row = 0; row < n; ++row) {
            for (std::size_t col = 0; col < row; ++col) {
                if (adjacency[row][col] != adjacency[col][row]) {
                    throw std::invalid_argument("undirected matrix must be symmetric");
                }
            }
        }
    }
}
std::optional<std::vector<std::size_t>> hamiltonian_path(
    const Graph& adjacency, bool directed = false) {
    validate_graph(adjacency, directed);
    const auto n = adjacency.size();
    std::vector<std::size_t> path;
    std::vector<unsigned char> used(n, 0);
    std::optional<std::vector<std::size_t>> answer;
    const auto visit = [&](auto&& self) -> bool {
        if (path.size() == n) { answer = path; return true; }
        for (std::size_t vertex = 0; vertex < n; ++vertex) {
            if (!used[vertex] && (path.empty() || adjacency[path.back()][vertex])) {
                used[vertex] = 1;
                path.push_back(vertex);
                const bool found = self(self);
                path.pop_back();
                used[vertex] = 0;
                if (found) { return true; }
            }
        }
        return false;
    };
    visit(visit);
    return answer;
}

}  // namespace algorithm_atlas

#ifndef ALGORITHM_ATLAS_NO_MAIN
namespace {
bool read_numbers(std::vector<long long>& numbers) {
    std::string token;
    while (std::cin >> token) {
        std::size_t first = (token[0] == '+' || token[0] == '-') ? 1 : 0;
        if (first == token.size()) { return false; }
        for (std::size_t i = first; i < token.size(); ++i) {
            if (token[i] < '0' || token[i] > '9') { return false; }
        }
        const char* begin = token.data() + (token[0] == '+' ? 1 : 0);
        const char* end = token.data() + token.size();
        long long value = 0;
        const auto parsed = std::from_chars(begin, end, value, 10);
        if (parsed.ec != std::errc{} || parsed.ptr != end) { return false; }
        numbers.push_back(value);
    }
    return std::cin.eof();
}
template <typename T> void write_json(const std::vector<T>& value);
template <typename T> void write_json(const std::optional<T>& value);
template <typename T, std::enable_if_t<std::is_integral_v<T>, int> = 0>
void write_json(T value) { std::cout << value; }
[[maybe_unused]] void write_json(const std::string& value) { std::cout << std::quoted(value); }
template <typename T> void write_json(const std::vector<T>& value) {
    std::cout << '[';
    for (std::size_t i = 0; i < value.size(); ++i) {
        if (i) { std::cout << ','; }
        write_json(value[i]);
    }
    std::cout << ']';
}
template <typename T> void write_json(const std::optional<T>& value) {
    if (value) { write_json(*value); }
    else { std::cout << "null"; }
}
}  // namespace

int main() {
    std::vector<long long> numbers;
    if (!read_numbers(numbers)) {
        std::cerr << "error: expected signed decimal long long tokens\n";
        return 1;
    }
    try {
        if (numbers.size() < 2 || numbers[1] < 0) {
            throw std::invalid_argument("mode and nonnegative size required");
        }
        const auto raw = static_cast<unsigned long long>(numbers[1]);
        const auto count = numbers.size() - 2;
        if ((raw == 0 && count != 0) ||
            (raw != 0 && (raw > count || count / raw != raw || count % raw != 0))) {
            throw std::invalid_argument("square cell count mismatch");
        }
        const auto n = static_cast<std::size_t>(raw);
        algorithm_atlas::Graph graph(n, std::vector<long long>(n));
        std::size_t index = 2;
        for (auto& row : graph) { for (auto& value : row) { value = numbers[index++]; } }
        if (numbers[0] != 0 && numbers[0] != 1) { throw std::invalid_argument("directed must be 0 or 1"); }
        write_json(algorithm_atlas::hamiltonian_path(graph, numbers[0] == 1));
        std::cout << '\n';
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << '\n';
        return 1;
    }
}
#endif
