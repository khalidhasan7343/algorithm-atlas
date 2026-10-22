#include "../../common.hpp"

namespace atlas_graph {

inline std::vector<int> bridges(const Graph& g) {
    require(!g.directed,"undirected mode required");
    std::vector<int> discovery(g.n,-1),low(g.n),parent(g.n,-1),parent_edge(g.n,-1),children(g.n),result;
    std::vector<bool> cut(g.n,false);int clock=0;
    for(int root=0;root<g.n;++root)if(discovery[root]==-1) {
        discovery[root]=low[root]=clock++;std::vector<std::pair<int,std::size_t>> frames{{root,0}};
        while(!frames.empty()) {
            int u=frames.back().first;
            if(frames.back().second<g.adj[u].size()) {
                const auto a=g.adj[u][frames.back().second++];
                if(a.id==parent_edge[u])continue;
                if(discovery[a.to]==-1) {
                    parent[a.to]=u;parent_edge[a.to]=a.id;++children[u];
                    discovery[a.to]=low[a.to]=clock++;frames.push_back({a.to,0});
                } else low[u]=std::min(low[u],discovery[a.to]);
            } else {
                frames.pop_back();int p=parent[u];
                if(p!=-1) {low[p]=std::min(low[p],low[u]);if(low[u]>discovery[p])result.push_back(parent_edge[u]);}
                else if(children[u]>1)cut[u]=true;
            }
        }
    }std::sort(result.begin(),result.end());return result;
}
}
#ifndef ALGORITHM_ATLAS_NO_MAIN
int main() {
    try {
        using namespace atlas_graph;
        auto in=read_input(false,false,false);
        emit(bridges(make_graph(in.n,in.edges,in.directed)));
        std::cout<<'\n';
    } catch(const std::exception& error) { std::cerr<<"error: "<<error.what()<<'\n'; return 2; }
}
#endif
