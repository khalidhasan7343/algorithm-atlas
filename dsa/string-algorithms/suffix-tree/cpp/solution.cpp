#include "../../common.hpp"

namespace atlas_string {
class SuffixTree {
public:
    struct Node {
        int start=0,end=0,suffix=-1;
        std::map<int,int> children;
        Node(int a=0,int b=0,int s=-1):start(a),end(b),suffix(s){}
    };
private:
    int length_;
    std::vector<int> symbols_;
    std::vector<Node> nodes_;
    int locus(const std::string& pattern) const {
        int node=0,pos=0,m=static_cast<int>(pattern.size());
        while (pos<m) {
            auto it=nodes_[node].children.find(byte(pattern[pos]));
            if (it==nodes_[node].children.end()) return -1;
            int child=it->second;
            const auto& edge=nodes_[child];
            for (int i=edge.start;i<edge.end;++i) {
                if (pos==m) return child;
                if (symbols_[i]!=byte(pattern[pos])) return -1;
                ++pos;
            }
            node=child;
        }
        return node;
    }
public:
    explicit SuffixTree(const std::string& text) {
        checked(text,2048);
        length_=static_cast<int>(text.size());
        for (char ch:text) symbols_.push_back(byte(ch));
        symbols_.push_back(256);
        nodes_.emplace_back();
        int end=static_cast<int>(symbols_.size());
        for (int suffix=0;suffix<end;++suffix) {
            int parent=0,pos=suffix;
            while (pos<end) {
                int ch=symbols_[pos];
                auto it=nodes_[parent].children.find(ch);
                if (it==nodes_[parent].children.end()) {
                    int leaf=static_cast<int>(nodes_.size());
                    nodes_[parent].children[ch]=leaf;
                    nodes_.emplace_back(pos,end,suffix);
                    break;
                }
                int child=it->second,start=nodes_[child].start,matched=0;
                while (start+matched<nodes_[child].end && symbols_[start+matched]==symbols_[pos+matched]) ++matched;
                if (start+matched==nodes_[child].end) {
                    pos+=matched;parent=child;continue;
                }
                int middle=static_cast<int>(nodes_.size());
                nodes_.emplace_back(start,start+matched);
                nodes_[parent].children[ch]=middle;
                nodes_[child].start+=matched;
                nodes_[middle].children[symbols_[nodes_[child].start]]=child;
                int leaf=static_cast<int>(nodes_.size());
                nodes_.emplace_back(pos+matched,end,suffix);
                nodes_[middle].children[symbols_[pos+matched]]=leaf;
                break;
            }
        }
    }
    const std::vector<Node>& nodes() const {return nodes_;}
    const std::vector<int>& symbols() const {return symbols_;}
    bool contains(const std::string& pattern) const {checked(pattern);return locus(pattern)>=0;}
    std::vector<int> find(const std::string& pattern) const {
        checked(pattern);
        if (pattern.empty()) return boundaries(length_);
        int node=locus(pattern);
        if (node<0) return {};
        std::vector<int> result,stack={node};
        while (!stack.empty()) {
            int u=stack.back();stack.pop_back();
            if (nodes_[u].suffix>=0) result.push_back(nodes_[u].suffix);
            for (auto edge:nodes_[u].children) stack.push_back(edge.second);
        }
        std::sort(result.begin(),result.end());
        return result;
    }
};
inline std::vector<int> solve(const std::string& text,const std::string& pattern) {
    return SuffixTree(text).find(pattern);
}
}
#ifndef ALGORITHM_ATLAS_NO_MAIN
int main() {
    try {
        auto text=atlas_string::read_bytes();
        auto pattern=atlas_string::read_bytes();
        atlas_string::end_input();
        atlas_string::emit(atlas_string::solve(text,pattern));
        std::cout << '\n';
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << '\n';
        return 2;
    }
}
#endif
