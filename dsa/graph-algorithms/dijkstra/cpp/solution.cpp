#ifndef ALGORITHM_ATLAS_DIJKSTRA_HPP
#define ALGORITHM_ATLAS_DIJKSTRA_HPP
#include "../../common.hpp"

namespace atlas_graph {

inline Paths dijkstra(const Graph& g,int source) {
    for(const auto& e:g.edges) bounded(e.weight,0,1000000000000LL,"Dijkstra requires nonnegative bounded weights");
    source=source_vertex(g.n,source);Paths r(g.n);
    using Item=std::pair<Integer,int>;
    std::priority_queue<Item,std::vector<Item>,std::greater<Item>> heap;
    if(source!=-1) {r.distance[source]=0;heap.push({0,source});}
    while(!heap.empty()) {
        auto [cost,u]=heap.top();heap.pop();if(cost!=r.distance[u]) continue;
        for(const auto& a:g.adj[u]) if(cost+a.weight<r.distance[a.to]) {
            r.distance[a.to]=cost+a.weight;r.parent[a.to]=u;r.parent_edge[a.to]=a.id;
            heap.push({r.distance[a.to],a.to});
        }
    }return r;
}
}
#ifndef ALGORITHM_ATLAS_NO_MAIN
int main() {
    try {
        using namespace atlas_graph;
        auto in=read_input(true,true,false);
        emit(dijkstra(make_graph(in.n,in.edges,in.directed,1000,0,1000000000000LL),source_vertex(in.n,in.source)));
        std::cout<<'\n';
    } catch(const std::exception& error) { std::cerr<<"error: "<<error.what()<<'\n'; return 2; }
}
#endif

#endif
