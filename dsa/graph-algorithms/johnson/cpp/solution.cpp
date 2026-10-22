#include "../../common.hpp"
#ifndef ALGORITHM_ATLAS_NO_MAIN
#define ATLAS_JOHNSON_RESTORE_MAIN
#define ALGORITHM_ATLAS_NO_MAIN
#endif
#include "../../bellman-ford/cpp/solution.cpp"
#include "../../dijkstra/cpp/solution.cpp"
#ifdef ATLAS_JOHNSON_RESTORE_MAIN
#undef ALGORITHM_ATLAS_NO_MAIN
#undef ATLAS_JOHNSON_RESTORE_MAIN
#endif

namespace atlas_graph {

inline std::optional<std::vector<std::vector<Integer>>> johnson(const Graph& g) {
    require(g.directed,"Johnson requires directed mode");require(g.n<=100,"Johnson vertex cap is 100");
    auto h=potentials(g).distance;
    if(std::find(h.begin(),h.end(),NEG)!=h.end())return std::nullopt;
    std::vector<Edge> edges;
    for(const auto& e:g.edges)edges.push_back({e.from,e.to,e.weight+h[static_cast<int>(e.from)]-h[static_cast<int>(e.to)]});
    auto reweighted=make_graph(g.n,edges,true,100,0,1000000000000LL);
    std::vector<std::vector<Integer>> result;
    for(int source=0;source<g.n;++source) {
        auto row=dijkstra(reweighted,source).distance;
        for(int v=0;v<g.n;++v)if(row[v]!=INF)row[v]=row[v]-h[source]+h[v];
        result.push_back(row);
    }return result;
}
}
#ifndef ALGORITHM_ATLAS_NO_MAIN
int main() {
    try {
        using namespace atlas_graph;
        auto in=read_input(true,false,false);
        auto result=johnson(make_graph(in.n,in.edges,in.directed,100));if(result)emit(*result);else std::cout<<"null";
        std::cout<<'\n';
    } catch(const std::exception& error) { std::cerr<<"error: "<<error.what()<<'\n'; return 2; }
}
#endif
