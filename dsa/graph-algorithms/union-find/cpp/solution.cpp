#ifndef ALGORITHM_ATLAS_UNION_FIND_HPP
#define ALGORITHM_ATLAS_UNION_FIND_HPP
#include "../../common.hpp"

namespace atlas_graph {

class UnionFind {
    std::vector<int> parent_,size_;int count_;
public:
    explicit UnionFind(int n):count_(n) {
        bounded(n,0,1000,"invalid set size");parent_.resize(n);size_.assign(n,1);std::iota(parent_.begin(),parent_.end(),0);
    }
    int find(int v) {
        bounded(v,0,static_cast<Integer>(parent_.size())-1,"invalid vertex");int root=v;
        while(root!=parent_[root]) root=parent_[root];
        while(v!=root) {int next=parent_[v];parent_[v]=root;v=next;}return root;
    }
    bool unite(int a,int b) {
        a=find(a);b=find(b);if(a==b) return false;
        if(size_[a]<size_[b] || (size_[a]==size_[b] && a>b)) std::swap(a,b);
        parent_[b]=a;size_[a]+=size_[b];--count_;return true;
    }
    bool connected(int a,int b) { return find(a)==find(b); }
    int component_size(int v) {return size_[find(v)];}
    int count() const {return count_;}
    std::vector<std::vector<int>> groups() {
        std::vector<std::vector<int>> grouped(parent_.size()),result;
        for(int v=0;v<static_cast<int>(parent_.size());++v) grouped[find(v)].push_back(v);
        for(auto& values:grouped) if(!values.empty()) result.push_back(values);
        std::sort(result.begin(),result.end());return result;
    }
};
inline void union_find_cli(const Graph& g) {
    require(!g.directed,"Union-Find expects undirected mode");UnionFind sets(g.n);
    for(const auto& e:g.edges) sets.unite(static_cast<int>(e.from),static_cast<int>(e.to));
    std::cout<<"{\"groups\":";emit(sets.groups());std::cout<<",\"count\":"<<sets.count()<<'}';
}
}
#ifndef ALGORITHM_ATLAS_NO_MAIN
int main() {
    try {
        using namespace atlas_graph;
        auto in=read_input(false,false,false);
        union_find_cli(make_graph(in.n,in.edges,in.directed));
        std::cout<<'\n';
    } catch(const std::exception& error) { std::cerr<<"error: "<<error.what()<<'\n'; return 2; }
}
#endif

#endif
