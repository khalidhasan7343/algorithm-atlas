// Independent testing oracles only; standard sorting never replaces lessons.
#define ALGORITHM_ATLAS_NO_MAIN
#include "../../bubble-sort/cpp/solution.cpp"
#include "../../selection-sort/cpp/solution.cpp"
#include "../../insertion-sort/cpp/solution.cpp"
#include "../../merge-sort/cpp/solution.cpp"
#include "../../quick-sort/cpp/solution.cpp"
#include "../../heap-sort/cpp/solution.cpp"
#include "../../counting-sort/cpp/solution.cpp"
#include "../../radix-sort/cpp/solution.cpp"
#include "../../bucket-sort/cpp/solution.cpp"
#include "../../shell-sort/cpp/solution.cpp"
#include "../../tim-sort/cpp/solution.cpp"
#include <cassert>
#include <random>

namespace aa = algorithm_atlas;
using Values = std::vector<long long>;
using Sort = Values (*)(const Values&);

Values counting_default(const Values& values) { return aa::counting_sort(values); }
const std::vector<Sort> sorts = {
    aa::bubble_sort<long long>, aa::selection_sort<long long>,
    aa::insertion_sort<long long>, aa::merge_sort<long long>,
    aa::quick_sort<long long>, aa::heap_sort<long long>, counting_default,
    aa::radix_sort, aa::shell_sort<long long>, aa::tim_sort<long long>
};

void check(const Values& source, Sort sort) {
    const auto before = source;
    auto expected = source;
    std::sort(expected.begin(), expected.end());
    auto result = sort(source);
    assert(result == expected && source == before);
    if (!result.empty()) { result[0] = 123; assert(source == before); }
}

struct Record {
    int key;
    std::size_t tag;
    Record() = delete;
    Record(int key_value, std::size_t tag_value) : key(key_value), tag(tag_value) {}
    bool operator<(const Record& other) const { return key < other.key; }
    bool operator==(const Record& other) const { return key == other.key && tag == other.tag; }
};

struct Counted {
    long long key;
    static std::size_t comparisons;
    bool operator<(const Counted& other) const {
        ++comparisons;
        return key < other.key;
    }
};
std::size_t Counted::comparisons = 0;

void check_quick_adversary() {
    const std::size_t size = 256;
    std::vector<std::size_t> positions;
    Values ranks(size);
    for (std::size_t i = 0; i < size; ++i) { positions.push_back(i); }
    for (std::size_t start = 0; start < size; ++start) {
        const auto pivot = positions[start + (size - start) / 2];
        ranks[pivot] = static_cast<long long>(start);
        auto current = start;
        auto upper = size;
        while (current < upper) {
            if (positions[current] == pivot) { ++current; }
            else { std::swap(positions[current], positions[--upper]); }
        }
    }
    std::vector<Counted> source;
    for (long long key : ranks) { source.push_back({key}); }
    Counted::comparisons = 0;
    const auto result = aa::quick_sort(source);
    for (std::size_t i = 0; i < size; ++i) { assert(result[i].key == static_cast<long long>(i)); }
    assert(Counted::comparisons >= size * size / 2);
}

void check_records(std::mt19937& generator) {
    using Records = std::vector<Record>;
    using RecordSort = Records (*)(const Records&);
    const std::vector<RecordSort> stable = {
        aa::bubble_sort<Record>, aa::insertion_sort<Record>,
        aa::merge_sort<Record>, aa::tim_sort<Record>
    };
    for (const auto size : {0, 1, 2, 31, 63, 64, 65, 127, 128, 129, 513}) {
        for (const bool descending : {false, true}) {
            Records source;
            for (int i = 0; i < size; ++i) {
                source.emplace_back(descending ? (size - i) / 4 : generator() % 9, source.size());
            }
            const auto before = source;
            auto expected = source;
            std::stable_sort(expected.begin(), expected.end());
            for (const auto sort : stable) {
                assert(sort(source) == expected && source == before);
            }
        }
    }
}

void check_tim_details(std::mt19937& generator) {
    namespace tim = aa::tim_sort_detail;
    for (std::size_t size = 0; size <= 32; ++size) {
        Values values;
        for (std::size_t i = 0; i < size; ++i) { values.push_back(static_cast<int>(generator() % 11) - 5); }
        std::sort(values.begin(), values.end());
        for (std::size_t start = 0; start <= size; ++start) {
            for (std::size_t end = start; end <= size; ++end) {
                for (long long pivot : {-6, -2, 0, 2, 6}) {
                    const auto lower = std::lower_bound(values.begin() + start, values.begin() + end, pivot);
                    const auto upper = std::upper_bound(values.begin() + start, values.begin() + end, pivot);
                    assert(tim::gallop_bound(values, start, end, pivot, false) == static_cast<std::size_t>(lower - values.begin()));
                    assert(tim::gallop_bound(values, start, end, pivot, true) == static_cast<std::size_t>(upper - values.begin()));
                }
            }
        }
    }
    for (int trial = 0; trial < 100; ++trial) {
        std::vector<tim::Run> runs;
        std::size_t offset = 0;
        for (int push = 0; push < 200; ++push) {
            const std::size_t length = 1 + generator() % 1024;
            runs.push_back({offset, length});
            offset += length;
            while (const auto choice = tim::collapse_choice(runs)) {
                const auto index = *choice;
                assert(runs[index].start + runs[index].length == runs[index + 1].start);
                runs[index].length += runs[index + 1].length;
                runs.erase(runs.begin() + index + 1);
            }
            for (std::size_t i = 1; i < runs.size(); ++i) {
                assert(runs[i - 1].length > runs[i].length);
            }
            for (std::size_t i = 2; i < runs.size(); ++i) {
                assert(runs[i - 2].length > runs[i - 1].length + runs[i].length);
            }
        }
    }
}

int main() {
    std::size_t integer_checks = 0;
    for (std::size_t size = 0, combinations = 1; size <= 8; ++size, combinations *= 3) {
        for (std::size_t encoded = 0; encoded < combinations; ++encoded) {
            Values values;
            auto digits = encoded;
            for (std::size_t i = 0; i < size; ++i, digits /= 3) {
                values.push_back(2 * static_cast<long long>(digits % 3) - 2);
            }
            for (auto sort : sorts) { check(values, sort); ++integer_checks; }
        }
    }
    assert(integer_checks == 98410);
    std::size_t bucket_checks = 0;
    const double alphabet[] = {0.0, 0.25, 0.5, 1.0};
    for (std::size_t size = 0, combinations = 1; size <= 7; ++size, combinations *= 4) {
        for (std::size_t encoded = 0; encoded < combinations; ++encoded) {
            std::vector<double> values;
            auto digits = encoded;
            for (std::size_t i = 0; i < size; ++i, digits /= 4) { values.push_back(alphabet[digits % 4]); }
            auto expected = values;
            std::sort(expected.begin(), expected.end());
            const auto before = values;
            for (std::size_t count : {0, 1, 3, 7}) {
                assert(aa::bucket_sort(values, count) == expected && values == before);
                ++bucket_checks;
            }
        }
    }
    assert(bucket_checks == 87380);
    std::mt19937 generator(20261021);
    const auto minimum = std::numeric_limits<long long>::min();
    const auto maximum = std::numeric_limits<long long>::max();
    for (std::size_t algorithm = 0; algorithm < sorts.size(); ++algorithm) {
        const int large = algorithm < 3 ? 512 : 8193;
        for (const int size : {0, 1, 2, 31, 32, 63, 64, 65, 127, 128, 129, 257, large}) {
            Values ascending, descending, equal(size, 7), random;
            for (int i = 0; i < size; ++i) {
                ascending.push_back(i);
                descending.push_back(size - i - 1);
                random.push_back(static_cast<int>(generator() % 33) - 16);
            }
            for (const auto& values : {ascending, descending, equal, random}) { check(values, sorts[algorithm]); }
        }
        if (algorithm != 6) { check({minimum, maximum, 0, -1, 1, minimum, maximum}, sorts[algorithm]); }
    }
    for (long long center : {minimum, maximum - 4}) {
        const Values values = {center + 4, center, center + 1, center + 4};
        auto expected = values;
        std::sort(expected.begin(), expected.end());
        assert(aa::counting_sort(values, 5) == expected);
        bool rejected = false;
        try { aa::counting_sort(values, 4); }
        catch (const std::length_error&) { rejected = true; }
        assert(rejected);
    }
    bool rejected = false;
    try { aa::counting_sort({minimum, maximum}, std::numeric_limits<std::size_t>::max()); }
    catch (const std::length_error&) { rejected = true; }
    assert(rejected);
    const std::vector<double> signed_zeros = {-0.0, 0.0, -0.0, 0.0};
    const auto zeros = aa::bucket_sort(signed_zeros);
    for (std::size_t i = 0; i < zeros.size(); ++i) { assert(std::signbit(zeros[i]) == std::signbit(signed_zeros[i])); }
    const std::vector<double> endpoints = {1.0, std::nextafter(1.0, 0.0), 0.0, std::nextafter(0.0, 1.0)};
    for (std::size_t count : {1, 2, 3, 17, 1024}) {
        auto expected = endpoints;
        std::sort(expected.begin(), expected.end());
        assert(aa::bucket_sort(endpoints, count) == expected);
    }
    check_records(generator);
    check_quick_adversary();
    check_tim_details(generator);
    std::cout << "integer_exhaustive=" << integer_checks << " bucket_exhaustive=" << bucket_checks << '\n';
}
