#include "../../common.hpp"

namespace atlas_string {
class AhoCorasick {
public:
    struct Node {
        std::array<int,256> next;
        int failure=0,output_link=-1,depth=0;
        std::vector<int> terminal;
        Node(){next.fill(-1);}
    };
private:
    std::vector<std::string> patterns_;
    std::vector<Node> nodes_;
public:
    explicit AhoCorasick(const std::vector<std::string>& patterns) {
        require(patterns.size()<=256,"too many patterns");
        std::size_t total=0;
        for (const auto& p:patterns){checked(p);total+=p.size();}
        require(total<=4096,"total pattern bytes exceed 4096");
        patterns_=patterns;
        nodes_.emplace_back();
        for (int id=0;id<static_cast<int>(patterns.size());++id) {
            int node=0;
            for (char ch:patterns[id]) {
                int value=byte(ch),child=nodes_[node].next[value];
                if (child<0) {
                    child=static_cast<int>(nodes_.size());
                    nodes_[node].next[value]=child;
                    int depth=nodes_[node].depth+1;
                    nodes_.emplace_back();
                    nodes_[child].depth=depth;
                }
                node=child;
            }
            nodes_[node].terminal.push_back(id);
        }
        std::queue<int> queue;
        for (int ch=0;ch<256;++ch) {
            int child=nodes_[0].next[ch];
            if (child<0) nodes_[0].next[ch]=0;
            else queue.push(child);
        }
        while (!queue.empty()) {
            int node=queue.front();queue.pop();
            int f=nodes_[node].failure;
            nodes_[node].output_link=(f && !nodes_[f].terminal.empty())?f:nodes_[f].output_link;
            for (int ch=0;ch<256;++ch) {
                int child=nodes_[node].next[ch];
                if (child<0) nodes_[node].next[ch]=nodes_[f].next[ch];
                else {nodes_[child].failure=nodes_[f].next[ch];queue.push(child);}
            }
        }
    }
    const std::vector<Node>& nodes() const {return nodes_;}
    std::vector<std::vector<int>> find(const std::string& text) const {
        checked(text);
        std::vector<std::vector<int>> result;
        for (int id:nodes_[0].terminal) result.push_back({0,id,0});
        int state=0;
        for (int i=0;i<static_cast<int>(text.size());++i) {
            int end=i+1;
            state=nodes_[state].next[byte(text[i])];
            for (int output=state;output>0;output=nodes_[output].output_link)
                for (int id:nodes_[output].terminal)
                    result.push_back({end,id,end-static_cast<int>(patterns_[id].size())});
            for (int id:nodes_[0].terminal) result.push_back({end,id,end});
        }
        return result;
    }
};
inline std::vector<std::vector<int>> solve(const std::string& text,const std::vector<std::string>& patterns) {
    return AhoCorasick(patterns).find(text);
}
}
#ifndef ALGORITHM_ATLAS_NO_MAIN
int main() {
    try {
        auto text=atlas_string::read_bytes();
        int count=atlas_string::read_count();
        std::vector<std::string> patterns;
        for(int i=0;i<count;++i) patterns.push_back(atlas_string::read_bytes());
        atlas_string::end_input();
        atlas_string::emit(atlas_string::solve(text,patterns));
        std::cout << '\n';
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << '\n';
        return 2;
    }
}
#endif
