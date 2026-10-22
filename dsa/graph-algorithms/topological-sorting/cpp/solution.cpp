#include "../../common.hpp"

namespace atlas_graph {

inline std::optional<std::vector<int>> topological_sort(const Graph& g) {
    require(g.directed,"topological sorting requires directed mode");std::vector<int> degree(g.n,0),order;
    for(const auto& e:g.edges) ++degree[static_cast<int>(e.to)];
    std::priority_queue<int,std::vector<int>,std::greater<int>> ready;
    for(int v=0;v<g.n;++v) if(degree[v]==0) ready.push(v);
    while(!ready.empty()) {
        int u=ready.top();ready.pop();order.push_back(u);
        for(const auto& a:g.adj[u]) if(--degree[a.to]==0) ready.push(a.to);
    }
    if(static_cast<int>(order.size())!=g.n) return std::nullopt;
    return order;
}
}
#ifndef ALGORITHM_ATLAS_NO_MAIN
int main() {
    try {
        using namespace atlas_graph;
        auto in=read_input(false,false,false);
        auto result=topological_sort(make_graph(in.n,in.edges,in.directed));if(result) emit(*result);else std::cout<<"null";
        std::cout<<'\n';
    } catch(const std::exception& error) { std::cerr<<"error: "<<error.what()<<'\n'; return 2; }
}
#endif
