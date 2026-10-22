#include "../../common.hpp"

namespace atlas_graph {

struct BFSResult { Paths paths; std::vector<int> order; };
inline BFSResult bfs(const Graph& g,int source) {
    source=source_vertex(g.n,source); BFSResult r{Paths(g.n),{}}; std::deque<int> queue;
    if(source!=-1) { r.paths.distance[source]=0; queue.push_back(source); }
    while(!queue.empty()) {
        int u=queue.front();queue.pop_front();r.order.push_back(u);
        for(const auto& a:g.adj[u]) if(r.paths.distance[a.to]==INF) {
            r.paths.distance[a.to]=r.paths.distance[u]+1;
            r.paths.parent[a.to]=u;r.paths.parent_edge[a.to]=a.id;queue.push_back(a.to);
        }
    } return r;
}
inline void emit(const BFSResult& r) {
    std::cout<<"{\"order\":";emit(r.order);std::cout<<",\"distance\":";emit(r.paths.distance);
    std::cout<<",\"parent\":";parents(r.paths.parent);std::cout<<",\"parent_edge\":";parents(r.paths.parent_edge);std::cout<<'}';
}
}
#ifndef ALGORITHM_ATLAS_NO_MAIN
int main() {
    try {
        using namespace atlas_graph;
        auto in=read_input(false,true,false);
        auto g=make_graph(in.n,in.edges,in.directed);emit(bfs(g,source_vertex(in.n,in.source)));
        std::cout<<'\n';
    } catch(const std::exception& error) { std::cerr<<"error: "<<error.what()<<'\n'; return 2; }
}
#endif
