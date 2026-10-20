// Educational classic Tim Sort: natural runs, corrected stack, and galloping.
#include <algorithm>
#include <charconv>
#include <cstddef>
#include <iostream>
#include <optional>
#include <string>
#include <system_error>
#include <utility>
#include <vector>

namespace algorithm_atlas {
namespace tim_sort_detail {

constexpr std::size_t minimum_gallop = 7;

std::size_t min_run_length(std::size_t length) {
    std::size_t discarded_bit = 0;
    while (length >= 64) {
        discarded_bit |= length & 1;
        length >>= 1;
    }
    return length + discarded_bit;
}

template <typename T>
std::size_t count_run(std::vector<T>& values, std::size_t start) {
    std::size_t end = start + 1;
    if (end == values.size()) { return 1; }
    const bool descending = values[end] < values[start];
    ++end;
    if (descending) {
        while (end < values.size() && values[end] < values[end - 1]) { ++end; }
        std::reverse(values.begin() + start, values.begin() + end);
    } else {
        while (end < values.size() && !(values[end] < values[end - 1])) { ++end; }
    }
    return end - start;
}

template <typename T>
void binary_insertion(std::vector<T>& values, std::size_t start,
                      std::size_t end, std::size_t sorted_end) {
    for (std::size_t index = sorted_end; index < end; ++index) {
        const T item = values[index];
        std::size_t lower = start;
        std::size_t upper = index;
        while (lower < upper) {
            const auto middle = lower + (upper - lower) / 2;
            if (item < values[middle]) { upper = middle; }
            else { lower = middle + 1; }
        }
        for (std::size_t position = index; position > lower; --position) {
            values[position] = values[position - 1];
        }
        values[lower] = item;
    }
}

template <typename T>
std::size_t gallop_bound(const std::vector<T>& values, std::size_t start,
                         std::size_t end, const T& pivot, bool upper) {
    const auto precedes = [&pivot, upper](const T& value) {
        return upper ? !(pivot < value) : value < pivot;
    };
    if (start == end || !precedes(values[start])) { return start; }
    const std::size_t length = end - start;
    std::size_t lower = start + 1;
    std::size_t offset = 1;
    while (offset < length && precedes(values[start + offset])) {
        lower = start + offset + 1;
        // Bound exponential growth by the remaining range before doubling.
        if (offset > (length - 1) / 2) { offset = length; break; }
        offset = 2 * offset + 1;
    }
    std::size_t upper_end = offset < length ? start + offset + 1 : end;
    while (lower < upper_end) {
        const auto middle = lower + (upper_end - lower) / 2;
        if (precedes(values[middle])) { lower = middle + 1; }
        else { upper_end = middle; }
    }
    return lower;
}

template <typename T>
void merge(std::vector<T>& values, std::size_t start,
           std::size_t middle, std::size_t end) {
    if (!(values[middle] < values[middle - 1])) { return; }
    const std::vector<T> left(values.begin() + start, values.begin() + middle);
    const std::vector<T> right(values.begin() + middle, values.begin() + end);
    std::size_t left_index = 0;
    std::size_t right_index = 0;
    std::size_t destination = start;
    std::size_t left_wins = 0;
    std::size_t right_wins = 0;
    while (left_index < left.size() && right_index < right.size()) {
        if (right[right_index] < left[left_index]) {
            values[destination++] = right[right_index++];
            ++right_wins;
            left_wins = 0;
        } else {
            values[destination++] = left[left_index++];
            ++left_wins;
            right_wins = 0;
        }
        if (left_index == left.size() || right_index == right.size()) { break; }
        if (left_wins >= minimum_gallop) {
            const auto boundary = gallop_bound(
                left, left_index, left.size(), right[right_index], true);
            std::copy(left.begin() + left_index, left.begin() + boundary,
                      values.begin() + destination);
            destination += boundary - left_index;
            left_index = boundary;
            left_wins = 0;
        } else if (right_wins >= minimum_gallop) {
            const auto boundary = gallop_bound(
                right, right_index, right.size(), left[left_index], false);
            std::copy(right.begin() + right_index, right.begin() + boundary,
                      values.begin() + destination);
            destination += boundary - right_index;
            right_index = boundary;
            right_wins = 0;
        }
    }
    if (left_index < left.size()) {
        std::copy(left.begin() + left_index, left.end(), values.begin() + destination);
    } else if (right_index < right.size()) {
        std::copy(right.begin() + right_index, right.end(), values.begin() + destination);
    }
}

struct Run {
    std::size_t start;
    std::size_t length;
};

std::optional<std::size_t> collapse_choice(const std::vector<Run>& runs) {
    if (runs.size() < 2) { return std::nullopt; }
    std::size_t index = runs.size() - 2;
    const bool latest_triple_bad = index > 0 &&
        runs[index - 1].length <= runs[index].length + runs[index + 1].length;
    const bool previous_triple_bad = index > 1 &&
        runs[index - 2].length <= runs[index - 1].length + runs[index].length;
    if (latest_triple_bad || previous_triple_bad) {
        if (runs[index - 1].length < runs[index + 1].length) { --index; }
        return index;
    }
    if (runs[index].length <= runs[index + 1].length) { return index; }
    return std::nullopt;
}

template <typename T>
class TimSorter {
public:
    explicit TimSorter(const std::vector<T>& values) : values_(values) {}

    std::vector<T> sort() {
        const auto size = values_.size();
        if (size < 2) { return std::move(values_); }
        const auto minimum_run = min_run_length(size);
        std::size_t start = 0;
        while (start < size) {
            auto run_length = count_run(values_, start);
            const auto required_length = std::min(minimum_run, size - start);
            if (run_length < required_length) {
                binary_insertion(values_, start, start + required_length,
                                 start + run_length);
                run_length = required_length;
            }
            runs_.push_back({start, run_length});
            while (const auto choice = collapse_choice(runs_)) { merge_at(*choice); }
            start += run_length;
        }
        while (runs_.size() > 1) {
            auto index = runs_.size() - 2;
            if (index > 0 && runs_[index - 1].length < runs_[index + 1].length) {
                --index;
            }
            merge_at(index);
        }
        return std::move(values_);
    }

private:
    std::vector<T> values_;
    std::vector<Run> runs_;

    void merge_at(std::size_t index) {
        const Run left = runs_[index];
        const Run right = runs_[index + 1];
        merge(values_, left.start, right.start, right.start + right.length);
        runs_[index].length = left.length + right.length;
        runs_.erase(runs_.begin() + index + 1);
    }
};

}  // namespace tim_sort_detail

template <typename T>
std::vector<T> tim_sort(const std::vector<T>& values) {
    return tim_sort_detail::TimSorter<T>(values).sort();
}

}  // namespace algorithm_atlas

#ifndef ALGORITHM_ATLAS_NO_MAIN
int main() {
    std::vector<long long> values;
    std::string token;
    while (std::cin >> token) {
        const std::size_t digits_start =
            (!token.empty() && (token[0] == '+' || token[0] == '-')) ? 1 : 0;
        bool valid = digits_start < token.size();
        for (std::size_t index = digits_start; index < token.size(); ++index) {
            valid = valid && token[index] >= '0' && token[index] <= '9';
        }
        if (!valid) {
            std::cerr << "error: expected signed decimal integers in long long range\n";
            return 1;
        }
        const char* first = token.data() + (token[0] == '+' ? 1 : 0);
        const char* last = token.data() + token.size();
        long long value = 0;
        const auto parsed = std::from_chars(first, last, value, 10);
        if (parsed.ec != std::errc{} || parsed.ptr != last) {
            std::cerr << "error: expected signed decimal integers in long long range\n";
            return 1;
        }
        values.push_back(value);
    }
    if (!std::cin.eof()) {
        std::cerr << "error: failed to read standard input\n";
        return 1;
    }
    const auto result = algorithm_atlas::tim_sort(values);
    for (std::size_t index = 0; index < result.size(); ++index) {
        if (index != 0) { std::cout << ' '; }
        std::cout << result[index];
    }
    std::cout << '\n';
}
#endif
