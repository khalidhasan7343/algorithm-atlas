#include "../../common.hpp"

namespace atlas_greedy {
struct ScheduleResult { Integer profit; std::vector<std::optional<std::size_t>> slots; };
ScheduleResult job_sequencing(const std::vector<Integer>& deadlines, const std::vector<Integer>& profits) {
    require(deadlines.size() == profits.size() && deadlines.size() <= 10000, "invalid job count");
    for (auto d : deadlines) bounded(d, 0, 1000000000);
    for (auto p : profits) bounded(p, -1000000000, 1000000000);
    const auto maximum = deadlines.empty() ? 0 : *std::max_element(deadlines.begin(),deadlines.end());
    const auto horizon = static_cast<std::size_t>(std::min<Integer>(static_cast<Integer>(deadlines.size()),maximum));
    std::vector<std::size_t> parent(horizon+1), rank(horizon+1,0), available(horizon+1);
    std::iota(parent.begin(),parent.end(),0); std::iota(available.begin(),available.end(),0);
    const auto find = [&](std::size_t slot) {
        while (parent[slot] != slot) { parent[slot] = parent[parent[slot]]; slot = parent[slot]; }
        return slot;
    };
    const auto occupy = [&](std::size_t slot) {
        auto left = find(slot-1), right = find(slot);
        if (rank[left] < rank[right]) std::swap(left,right);
        parent[right] = left;
        available[left] = std::min(available[left],available[right]);
        if (rank[left] == rank[right]) ++rank[left];
    };
    std::vector<std::size_t> ordered;
    for (std::size_t i = 0; i < deadlines.size(); ++i)
        if (deadlines[i] > 0 && profits[i] > 0) ordered.push_back(i);
    std::sort(ordered.begin(),ordered.end(),[&](auto a,auto b) {
        return profits[a] != profits[b] ? profits[a] > profits[b] : a < b;
    });
    ScheduleResult result{0,std::vector<std::optional<std::size_t>>(horizon)};
    for (auto index : ordered) {
        const auto limit = static_cast<std::size_t>(std::min<Integer>(deadlines[index],static_cast<Integer>(horizon)));
        const auto slot = available[find(limit)];
        if (slot) {
            result.slots[slot-1] = index;
            result.profit += profits[index];
            occupy(slot);
        }
    }
    return result;
}
inline void print_schedule(const ScheduleResult& result) {
    std::cout << "{\"profit\":" << result.profit << ",\"slots\":[";
    for (std::size_t i = 0; i < result.slots.size(); ++i) {
        if (i) std::cout << ',';
        if (result.slots[i]) std::cout << *result.slots[i]; else std::cout << "null";
    }
    std::cout << "]}";
}
}
#ifndef ALGORITHM_ATLAS_NO_MAIN
int main() {
    return atlas_greedy::cli([] {
        const auto count = atlas_greedy::read_integer();
        atlas_greedy::bounded(count, 0, 10000);
        std::vector<atlas_greedy::Integer> deadlines, profits;
        for (atlas_greedy::Integer i = 0; i < count; ++i) {
            deadlines.push_back(atlas_greedy::read_integer()); profits.push_back(atlas_greedy::read_integer());
        }
        atlas_greedy::end_input();
        atlas_greedy::print_schedule(atlas_greedy::job_sequencing(deadlines,profits));
    });
}
#endif
