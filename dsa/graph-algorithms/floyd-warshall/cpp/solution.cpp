#include "../../common.hpp"

namespace atlas_graph {

using Matrix=std::vector<std::vector<Integer>>;
inline Matrix floyd_warshall(const Graph& g) {
    require(g.n<=100,"Floyd-Warshall vertex cap is 100");
    for(const auto& e:g.edges)bounded(e.weight,-1000000,1000000,"Floyd weight outside contract");
    Matrix d(g.n,std::vector<Integer>(g.n,INF));for(int v=0;v<g.n;++v)d[v][v]=0;
    for(int u=0;u<g.n;++u)for(const auto& a:g.adj[u])d[u][a.to]=std::min(d[u][a.to],a.weight);
    for(int k=0;k<g.n;++k)for(int u=0;u<g.n;++u)if(d[u][k]!=INF)
        for(int v=0;v<g.n;++v)if(d[k][v]!=INF)
            d[u][v]=std::min(d[u][v],std::max(-1000000000000LL,d[u][k]+d[k][v]));
    Matrix result=d;
    for(int k=0;k<g.n;++k)if(d[k][k]<0)
        for(int u=0;u<g.n;++u)if(d[u][k]!=INF)
            for(int v=0;v<g.n;++v)if(d[k][v]!=INF)result[u][v]=NEG;
    return result;
}
}
#ifndef ALGORITHM_ATLAS_NO_MAIN
int main() {
    try {
        using namespace atlas_graph;
        auto in=read_input(true,false,false);
        emit(floyd_warshall(make_graph(in.n,in.edges,in.directed,100)));
        std::cout<<'\n';
    } catch(const std::exception& error) { std::cerr<<"error: "<<error.what()<<'\n'; return 2; }
}
#endif
