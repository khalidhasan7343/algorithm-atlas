#include "../../common.hpp"
#include <tuple>

namespace atlas_greedy {
struct Activity { Integer start, finish; };
std::vector<std::size_t> activity_selection(const std::vector<Activity>& activities) {
    require(activities.size() <= 10000, "at most 10000 activities required");
    for (const auto& activity : activities) {
        bounded(activity.start, -1000000000, 1000000000);
        bounded(activity.finish, -1000000000, 1000000000);
        require(activity.start < activity.finish, "require start < finish");
    }
    std::vector<std::size_t> ordered(activities.size());
    std::iota(ordered.begin(), ordered.end(), 0);
    std::sort(ordered.begin(), ordered.end(), [&](auto a, auto b) {
        return std::tie(activities[a].finish, activities[a].start, a)
             < std::tie(activities[b].finish, activities[b].start, b);
    });
    std::vector<std::size_t> selected;
    std::optional<Integer> last_finish;
    for (auto index : ordered) {
        if (!last_finish || activities[index].start >= *last_finish) {
            selected.push_back(index);
            last_finish = activities[index].finish;
        }
    }
    return selected;
}
}
#ifndef ALGORITHM_ATLAS_NO_MAIN
int main() {
    return atlas_greedy::cli([] {
        const auto count = atlas_greedy::read_integer();
        atlas_greedy::bounded(count, 0, 10000);
        std::vector<atlas_greedy::Activity> activities;
        for (atlas_greedy::Integer i = 0; i < count; ++i) {
            const auto start = atlas_greedy::read_integer();
            const auto finish = atlas_greedy::read_integer();
            activities.push_back({start, finish});
        }
        atlas_greedy::end_input();
        atlas_greedy::print_vector(atlas_greedy::activity_selection(activities));
    });
}
#endif
