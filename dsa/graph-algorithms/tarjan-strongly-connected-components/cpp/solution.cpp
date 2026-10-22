#include "../../common.hpp"

namespace atlas_graph {

inline std::vector<std::vector<int>> tarjan_scc(const Graph& g) {
    require(g.directed,"SCC API requires directed mode");
    std::vector<int> index(g.n,-1),low(g.n),parent(g.n,-1),active;
    std::vector<bool> on_stack(g.n,false);std::vector<std::vector<int>> components;int clock=0;
    for(int root=0;root<g.n;++root)if(index[root]==-1) {
        index[root]=low[root]=clock++;active.push_back(root);on_stack[root]=true;
        std::vector<std::pair<int,std::size_t>> frames{{root,0}};
        while(!frames.empty()) {
            int u=frames.back().first;
            if(frames.back().second<g.adj[u].size()) {
                int v=g.adj[u][frames.back().second++].to;
                if(index[v]==-1) {
                    parent[v]=u;index[v]=low[v]=clock++;active.push_back(v);on_stack[v]=true;frames.push_back({v,0});
                } else if(on_stack[v])low[u]=std::min(low[u],index[v]);
            } else {
                frames.pop_back();if(parent[u]!=-1)low[parent[u]]=std::min(low[parent[u]],low[u]);
                if(low[u]==index[u]) {
                    std::vector<int> group;
                    while(true){int v=active.back();active.pop_back();on_stack[v]=false;group.push_back(v);if(v==u)break;}
                    std::sort(group.begin(),group.end());components.push_back(group);
                }
            }
        }
    }std::sort(components.begin(),components.end());return components;
}
}
#ifndef ALGORITHM_ATLAS_NO_MAIN
int main() {
    try {
        using namespace atlas_graph;
        auto in=read_input(false,false,false);
        emit(tarjan_scc(make_graph(in.n,in.edges,in.directed)));
        std::cout<<'\n';
    } catch(const std::exception& error) { std::cerr<<"error: "<<error.what()<<'\n'; return 2; }
}
#endif
