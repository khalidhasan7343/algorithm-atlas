#include "../../common.hpp"

namespace atlas_graph {

inline SpanningForest prim(const Graph& g) {
    require(!g.directed,"Prim requires undirected mode");
    for(const auto& e:g.edges)bounded(e.weight,-1000000,1000000,"MST weight outside contract");
    std::vector<bool> seen(g.n,false);SpanningForest r;
    using Item=std::tuple<Integer,int,int,int>;
    for(int root=0;root<g.n;++root)if(!seen[root]) {
        seen[root]=true;std::priority_queue<Item,std::vector<Item>,std::greater<Item>> heap;
        for(const auto& a:g.adj[root])heap.push({a.weight,a.id,root,a.to});
        while(!heap.empty()) {
            auto [weight,id,from,v]=heap.top();heap.pop();(void)from;
            if(seen[v])continue;
            seen[v]=true;r.edges.push_back(id);r.weight+=weight;
            for(const auto& a:g.adj[v])if(!seen[a.to])heap.push({a.weight,a.id,v,a.to});
        }
    }return r;
}
}
#ifndef ALGORITHM_ATLAS_NO_MAIN
int main() {
    try {
        using namespace atlas_graph;
        auto in=read_input(true,false,false);
        emit(prim(make_graph(in.n,in.edges,in.directed)));
        std::cout<<'\n';
    } catch(const std::exception& error) { std::cerr<<"error: "<<error.what()<<'\n'; return 2; }
}
#endif
