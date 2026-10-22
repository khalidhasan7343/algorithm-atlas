#include "../../common.hpp"
#ifndef ALGORITHM_ATLAS_NO_MAIN
#define ATLAS_KRUSKAL_RESTORE_MAIN
#define ALGORITHM_ATLAS_NO_MAIN
#endif
#include "../../union-find/cpp/solution.cpp"
#ifdef ATLAS_KRUSKAL_RESTORE_MAIN
#undef ALGORITHM_ATLAS_NO_MAIN
#undef ATLAS_KRUSKAL_RESTORE_MAIN
#endif

namespace atlas_graph {

inline SpanningForest kruskal(const Graph& g) {
    require(!g.directed,"Kruskal requires undirected mode");UnionFind sets(g.n);
    for(const auto& e:g.edges)bounded(e.weight,-1000000,1000000,"MST weight outside contract");
    std::vector<int> ids(g.edges.size());std::iota(ids.begin(),ids.end(),0);
    std::sort(ids.begin(),ids.end(),[&](int a,int b){return std::tie(g.edges[a].weight,a)<std::tie(g.edges[b].weight,b);});
    SpanningForest r;
    for(int id:ids) {const auto& e=g.edges[id];if(sets.unite(static_cast<int>(e.from),static_cast<int>(e.to))) {r.weight+=e.weight;r.edges.push_back(id);}}
    return r;
}
}
#ifndef ALGORITHM_ATLAS_NO_MAIN
int main() {
    try {
        using namespace atlas_graph;
        auto in=read_input(true,false,false);
        emit(kruskal(make_graph(in.n,in.edges,in.directed)));
        std::cout<<'\n';
    } catch(const std::exception& error) { std::cerr<<"error: "<<error.what()<<'\n'; return 2; }
}
#endif
