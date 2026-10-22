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
std::vector<std::string> rat_in_a_maze(const std::vector<std::vector<long long>>& grid) {
    if (grid.empty()) { return {}; }
    const auto height = grid.size(), width = grid[0].size();
    if (!width) { throw std::invalid_argument("rows must be nonempty"); }
    for (const auto& row : grid) {
        if (row.size() != width) { throw std::invalid_argument("grid must be rectangular"); }
        for (auto value : row) {
            if (value != 0 && value != 1) { throw std::invalid_argument("cells must be binary"); }
        }
    }
    std::vector<std::string> result;
    if (!grid[0][0] || !grid[height-1][width-1]) { return result; }
    std::vector<std::vector<unsigned char>> visited(height, std::vector<unsigned char>(width, 0));
    std::string path;
    const auto visit = [&](auto&& self, std::size_t row, std::size_t col) -> void {
        visited[row][col] = 1;
        if (row == height-1 && col == width-1) { result.push_back(path); }
        else {
            const auto next = [&](std::size_t nr, std::size_t nc, char step) {
                if (grid[nr][nc] && !visited[nr][nc]) {
                    path.push_back(step); self(self, nr, nc); path.pop_back();
                }
            };
            if (row < height-1) { next(row+1, col, 'D'); }
            if (col > 0) { next(row, col-1, 'L'); }
            if (col < width-1) { next(row, col+1, 'R'); }
            if (row > 0) { next(row-1, col, 'U'); }
        }
        visited[row][col] = 0;
    };
    visit(visit, 0, 0);
    return result;
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
        if (numbers.size() < 2) { throw std::invalid_argument("dimensions required"); }
        const auto r = numbers[0], c = numbers[1];
        const auto count = numbers.size() - 2;
        if (r < 0 || c < 0 || ((r == 0) != (c == 0))) {
            throw std::invalid_argument("invalid dimensions");
        }
        if (r == 0) {
            if (count) { throw std::invalid_argument("unexpected cells"); }
            write_json(algorithm_atlas::rat_in_a_maze({}));
        } else {
            const auto ur = static_cast<unsigned long long>(r), uc = static_cast<unsigned long long>(c);
            if (uc > count || count / uc != ur || count % uc != 0) {
                throw std::invalid_argument("cell count mismatch");
            }
            const auto height = static_cast<std::size_t>(ur), width = static_cast<std::size_t>(uc);
            std::vector<std::vector<long long>> grid(height, std::vector<long long>(width));
            std::size_t index = 2;
            for (auto& row : grid) { for (auto& cell : row) { cell = numbers[index++]; } }
            write_json(algorithm_atlas::rat_in_a_maze(grid));
        }
        std::cout << '\n';
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << '\n';
        return 1;
    }
}
#endif
