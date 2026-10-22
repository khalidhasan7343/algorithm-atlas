#include <algorithm>
#include <array>
#include <charconv>
#include <cstddef>
#include <cstdint>
#include <iostream>
#include <limits>
#include <optional>
#include <stdexcept>
#include <string>
#include <tuple>
#include <utility>
#include <vector>

namespace algorithm_atlas {
bool decimal_token(const std::string& token) {
    if (token.empty()) { return false; }
    std::size_t i = (token[0] == '+' || token[0] == '-') ? 1 : 0;
    if (i == token.size()) { return false; }
    for (; i < token.size(); ++i) { if (token[i] < '0' || token[i] > '9') { return false; } }
    return true;
}
std::vector<long long> read_integers() {
    std::vector<long long> values;
    std::string token;
    while (std::cin >> token) {
        if (!decimal_token(token)) { throw std::invalid_argument("expected decimal integers"); }
        const char* first = token.data() + (token[0] == '+' ? 1 : 0);
        long long value = 0;
        const auto result = std::from_chars(first, token.data() + token.size(), value);
        if (result.ec != std::errc{} || result.ptr != token.data() + token.size()) {
            throw std::invalid_argument("integer outside long long range");
        }
        values.push_back(value);
    }
    if (!std::cin.eof()) { throw std::invalid_argument("input failure"); }
    return values;
}
constexpr long long coordinate_limit = 1000000000LL;
struct Point { long long x, y; std::size_t index; };
struct ClosestPair { long long squared_distance; std::size_t first, second; };
ClosestPair candidate(const Point& a, const Point& b) {
    const auto dx=a.x-b.x, dy=a.y-b.y;
    return {dx*dx+dy*dy,std::min(a.index,b.index),std::max(a.index,b.index)};
}
ClosestPair better(ClosestPair a, ClosestPair b) {
    return std::tie(a.squared_distance,a.first,a.second) <
           std::tie(b.squared_distance,b.first,b.second) ? a : b;
}
bool y_less(const Point& a, const Point& b) {
    return std::tie(a.y,a.x,a.index) < std::tie(b.y,b.x,b.index);
}
std::optional<ClosestPair> closest_pair(const std::vector<std::pair<long long,long long>>& points) {
    std::vector<Point> ordered;
    for (std::size_t i=0;i<points.size();++i) {
        const auto x=points[i].first,y=points[i].second;
        if (x < -coordinate_limit || x > coordinate_limit ||
            y < -coordinate_limit || y > coordinate_limit) {
            throw std::invalid_argument("coordinate outside [-10^9,10^9]");
        }
        ordered.push_back({x,y,i});
    }
    if (ordered.size() < 2) { return std::nullopt; }
    std::sort(ordered.begin(),ordered.end(),[](const Point& a,const Point& b) {
        return std::tie(a.x,a.y,a.index) < std::tie(b.x,b.y,b.index);
    });
    std::optional<ClosestPair> duplicate;
    for (std::size_t i=1;i<ordered.size();++i) {
        if (ordered[i-1].x==ordered[i].x && ordered[i-1].y==ordered[i].y) {
            const auto pair=candidate(ordered[i-1],ordered[i]);
            duplicate=duplicate ? better(*duplicate,pair) : pair;
        }
    }
    if (duplicate) { return duplicate; }
    struct Solved { ClosestPair best; std::vector<Point> by_y; };
    const auto solve=[&](auto&& self,std::size_t lo,std::size_t hi)->Solved {
        if (hi-lo <= 3) {
            auto best=candidate(ordered[lo],ordered[lo+1]);
            for (auto i=lo;i<hi;++i) { for (auto j=i+1;j<hi;++j) {
                best=better(best,candidate(ordered[i],ordered[j]));
            } }
            std::vector<Point> by_y(ordered.begin()+lo,ordered.begin()+hi);
            std::sort(by_y.begin(),by_y.end(),y_less);
            return {best,std::move(by_y)};
        }
        const auto mid=lo+(hi-lo)/2;
        const auto split_x=ordered[mid].x;
        auto left=self(self,lo,mid),right=self(self,mid,hi);
        auto best=better(left.best,right.best);
        std::vector<Point> merged;merged.reserve(hi-lo);
        std::size_t i=0,j=0;
        while (i<left.by_y.size() && j<right.by_y.size()) {
            if (y_less(left.by_y[i],right.by_y[j])) { merged.push_back(left.by_y[i++]); }
            else { merged.push_back(right.by_y[j++]); }
        }
        while (i<left.by_y.size()) { merged.push_back(left.by_y[i++]); }
        while (j<right.by_y.size()) { merged.push_back(right.by_y[j++]); }
        std::vector<Point> strip;
        for (const auto& p:merged) {
            const auto dx=p.x-split_x;
            if (dx*dx <= best.squared_distance) { strip.push_back(p); }
        }
        for (i=0;i<strip.size();++i) {
            for (j=i+1;j<strip.size();++j) {
                const auto dy=strip[j].y-strip[i].y;
                if (dy*dy > best.squared_distance) { break; }
                best=better(best,candidate(strip[i],strip[j]));
            }
        }
        return {best,std::move(merged)};
    };
    return solve(solve,0,ordered.size()).best;
}
void print_result(const std::optional<ClosestPair>& result) {
    if (!result) { std::cout << "null"; }
    else { std::cout << '[' << result->squared_distance << ',' << result->first << ',' << result->second << ']'; }
}

}  // namespace algorithm_atlas
#ifndef ALGORITHM_ATLAS_NO_MAIN
int main() {
    try {
        const auto numbers=algorithm_atlas::read_integers();
        if (numbers.empty() || numbers[0]<0 || numbers.size()%2!=1 ||
            static_cast<unsigned long long>(numbers[0])!=(numbers.size()-1)/2) { throw std::invalid_argument("point count mismatch"); }
        std::vector<std::pair<long long,long long>> points;
        for (std::size_t i=1;i<numbers.size();i+=2) { points.emplace_back(numbers[i],numbers[i+1]); }
        algorithm_atlas::print_result(algorithm_atlas::closest_pair(points));
        std::cout << '\n';
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << '\n';
        return 1;
    }
}
#endif
