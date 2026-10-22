#ifndef ALGORITHM_ATLAS_BELLMAN_FORD_HPP
#define ALGORITHM_ATLAS_BELLMAN_FORD_HPP
#include "../../common.hpp"

namespace atlas_graph {

inline Paths bellman_ford_initialized(const Graph& g,Paths r) {
    for(const auto& e:g.edges) bounded(e.weight,-1000000,1000000,"Bellman-Ford weight outside contract");
    for(int pass=0;pass<g.n-1;++pass) {
        bool changed=false;
        for(int u=0;u<g.n;++u) for(const auto& a:g.adj[u])
            if(r.distance[u]!=INF && r.distance[u]+a.weight<r.distance[a.to]) {
                r.distance[a.to]=r.distance[u]+a.weight;r.parent[a.to]=u;r.parent_edge[a.to]=a.id;changed=true;
            }
        if(!changed) break;
    }
    std::vector<bool> affected(g.n,false);std::deque<int> queue;
    for(int u=0;u<g.n;++u) for(const auto& a:g.adj[u])
        if(r.distance[u]!=INF && r.distance[u]+a.weight<r.distance[a.to] && !affected[a.to]) {
            affected[a.to]=true;queue.push_back(a.to);
        }
    while(!queue.empty()) {
        int u=queue.front();queue.pop_front();
        for(const auto& a:g.adj[u]) if(!affected[a.to]) {affected[a.to]=true;queue.push_back(a.to);}
    }
    for(int v=0;v<g.n;++v)if(affected[v]){r.distance[v]=NEG;r.parent[v]=-1;r.parent_edge[v]=-1;}
    return r;
}
inline Paths bellman_ford(const Graph& g,int source) {
    source=source_vertex(g.n,source);Paths r(g.n);if(source!=-1)r.distance[source]=0;
    return bellman_ford_initialized(g,r);
}
inline Paths potentials(const Graph& g) {
    require(g.directed,"potentials require directed mode");Paths r(g.n);
    std::fill(r.distance.begin(),r.distance.end(),0);return bellman_ford_initialized(g,r);
}

}
#ifndef ALGORITHM_ATLAS_NO_MAIN
int main() {
    try {
        using namespace atlas_graph;
        auto in=read_input(true,true,false);
        emit(bellman_ford(make_graph(in.n,in.edges,in.directed),source_vertex(in.n,in.source)));
        std::cout<<'\n';
    } catch(const std::exception& error) { std::cerr<<"error: "<<error.what()<<'\n'; return 2; }
}
#endif

#endif
