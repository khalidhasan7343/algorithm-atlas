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
using Board = std::vector<std::vector<long long>>;
std::optional<Board> solve_sudoku(const Board& board) {
    if (board.size() != 9) { throw std::invalid_argument("board must be 9 by 9"); }
    for (const auto& row : board) {
        if (row.size() != 9) { throw std::invalid_argument("board must be 9 by 9"); }
    }
    Board work = board;
    std::vector<unsigned> rows(9, 0), cols(9, 0), boxes(9, 0);
    std::vector<std::size_t> blanks;
    for (std::size_t row = 0; row < 9; ++row) {
        for (std::size_t col = 0; col < 9; ++col) {
            const auto value = work[row][col];
            if (value < 0 || value > 9) { throw std::invalid_argument("cells must be in 0..9"); }
            if (!value) { blanks.push_back(row*9 + col); continue; }
            const auto box = (row/3)*3 + col/3;
            const unsigned bit = 1U << static_cast<unsigned>(value);
            if ((rows[row] | cols[col] | boxes[box]) & bit) {
                throw std::invalid_argument("contradictory givens");
            }
            rows[row] |= bit; cols[col] |= bit; boxes[box] |= bit;
        }
    }
    std::optional<Board> answer;
    const auto visit = [&](auto&& self, std::size_t index) -> bool {
        if (index == blanks.size()) { answer = work; return true; }
        const auto row = blanks[index]/9, col = blanks[index]%9, box = (row/3)*3 + col/3;
        for (unsigned value = 1; value <= 9; ++value) {
            const unsigned bit = 1U << value;
            if (!((rows[row] | cols[col] | boxes[box]) & bit)) {
                work[row][col] = value;
                rows[row] |= bit; cols[col] |= bit; boxes[box] |= bit;
                const bool found = self(self, index + 1);
                work[row][col] = 0;
                rows[row] &= ~bit; cols[col] &= ~bit; boxes[box] &= ~bit;
                if (found) { return true; }
            }
        }
        return false;
    };
    visit(visit, 0);
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
        if (numbers.size() != 81) { throw std::invalid_argument("exactly 81 cells required"); }
        algorithm_atlas::Board board(9, std::vector<long long>(9));
        for (std::size_t i = 0; i < 81; ++i) { board[i/9][i%9] = numbers[i]; }
        write_json(algorithm_atlas::solve_sudoku(board));
        std::cout << '\n';
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << '\n';
        return 1;
    }
}
#endif
