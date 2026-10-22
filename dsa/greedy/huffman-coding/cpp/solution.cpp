#include "../../common.hpp"
#include <functional>
#include <map>
#include <queue>
#include <tuple>

namespace atlas_greedy {
class HuffmanCodec {
    struct Node { int symbol; std::size_t left, right; };
    std::vector<Node> nodes_;
    std::optional<std::size_t> root_;
    std::map<Integer, Integer> frequencies_;
    std::map<Integer, std::string> codes_;
public:
    explicit HuffmanCodec(const std::vector<std::pair<Integer, Integer>>& frequencies) {
        require(frequencies.size() <= 256, "at most 256 symbols required");
        for (const auto& entry : frequencies) {
            bounded(entry.first, 0, 255); bounded(entry.second, 1, 1000000000);
            require(frequencies_.emplace(entry).second, "duplicate symbol");
        }
        using Entry = std::tuple<Integer, Integer, std::size_t>;
        std::priority_queue<Entry, std::vector<Entry>, std::greater<Entry>> heap;
        for (const auto& entry : frequencies_) {
            const auto index = nodes_.size();
            nodes_.push_back({static_cast<int>(entry.first), 0, 0});
            heap.emplace(entry.second, entry.first, index);
        }
        while (heap.size() > 1) {
            const auto [weight_left, minimum_left, left] = heap.top(); heap.pop();
            const auto [weight_right, minimum_right, right] = heap.top(); heap.pop();
            const auto index = nodes_.size();
            nodes_.push_back({-1, left, right});
            heap.emplace(weight_left+weight_right, std::min(minimum_left,minimum_right), index);
        }
        if (!heap.empty()) root_ = std::get<2>(heap.top());
        const auto visit = [&](auto&& self, std::size_t index, const std::string& prefix) -> void {
            const auto& node = nodes_[index];
            if (node.symbol >= 0) codes_[node.symbol] = prefix.empty() ? "0" : prefix;
            else { self(self,node.left,prefix+'0'); self(self,node.right,prefix+'1'); }
        };
        if (root_) visit(visit,*root_,"");
    }
    const std::map<Integer, std::string>& codes() const { return codes_; }
    Integer weighted_length() const {
        Integer total = 0;
        for (const auto& entry : frequencies_)
            total += entry.second*static_cast<Integer>(codes_.at(entry.first).size());
        return total;
    }
    std::string encode(const std::vector<Integer>& message) const {
        require(message.size() <= 10000, "message byte limit exceeded");
        std::size_t length = 0;
        for (auto symbol : message) {
            bounded(symbol, 0, 255);
            const auto found = codes_.find(symbol);
            require(found != codes_.end(), "unknown message symbol");
            length += found->second.size();
            require(length <= 1000000, "encoded bit limit exceeded");
        }
        std::string result; result.reserve(length);
        for (auto symbol : message) result += codes_.at(symbol);
        return result;
    }
    std::vector<Integer> decode(const std::string& bits) const {
        require(bits.size() <= 1000000, "bit limit exceeded");
        if (!root_) { require(bits.empty(), "nonempty stream with empty alphabet"); return {}; }
        std::vector<Integer> result;
        auto index = *root_;
        for (auto bit : bits) {
            require(bit == '0' || bit == '1', "nonbinary stream");
            if (nodes_[*root_].symbol >= 0) require(bit == '0', "invalid single-symbol bit");
            else index = bit == '0' ? nodes_[index].left : nodes_[index].right;
            if (nodes_[index].symbol >= 0) {
                result.push_back(nodes_[index].symbol);
                require(result.size() <= 10000, "decoded byte limit exceeded");
                index = *root_;
            }
        }
        require(index == *root_, "truncated codeword");
        return result;
    }
};
inline void print_huffman(const HuffmanCodec& codec, const std::vector<Integer>& message) {
    const auto bits = codec.encode(message);
    const auto decoded = codec.decode(bits);
    std::cout << "{\"codes\":[";
    bool comma = false;
    for (const auto& entry : codec.codes()) {
        if (comma) std::cout << ',';
        comma = true;
        std::cout << '[' << entry.first << ',' << std::quoted(entry.second) << ']';
    }
    std::cout << "],\"bits\":" << std::quoted(bits) << ",\"decoded\":";
    print_vector(decoded);
    std::cout << ",\"cost\":" << codec.weighted_length() << '}';
}
}
#ifndef ALGORITHM_ATLAS_NO_MAIN
int main() {
    return atlas_greedy::cli([] {
        const auto count = atlas_greedy::read_integer();
        atlas_greedy::bounded(count, 0, 256);
        std::vector<std::pair<atlas_greedy::Integer,atlas_greedy::Integer>> frequencies;
        for (atlas_greedy::Integer i = 0; i < count; ++i) {
            const auto symbol = atlas_greedy::read_integer(), frequency = atlas_greedy::read_integer();
            frequencies.emplace_back(symbol,frequency);
        }
        const auto size = atlas_greedy::read_integer();
        atlas_greedy::bounded(size, 0, 10000);
        std::vector<atlas_greedy::Integer> message;
        for (atlas_greedy::Integer i = 0; i < size; ++i) message.push_back(atlas_greedy::read_integer());
        atlas_greedy::end_input();
        atlas_greedy::print_huffman(atlas_greedy::HuffmanCodec(frequencies),message);
    });
}
#endif
