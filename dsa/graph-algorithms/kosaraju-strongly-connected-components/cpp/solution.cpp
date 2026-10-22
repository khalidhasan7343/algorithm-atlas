#include "../../common.hpp"

namespace atlas_graph {

inline std::vector<std::vector<int>> kosaraju_scc(const Graph& g) {
    require(g.directed,"SCC API requires directed mode");std::vector<bool> seen(g.n,false);std::vector<int> finish;
    for(int root=0;root<g.n;++root)if(!seen[root]) {
        seen[root]=true;std::vector<std::pair<int,std::size_t>> frames{{root,0}};
        while(!frames.empty()) {
            int u=frames.back().first;
            if(frames.back().second==g.adj[u].size()){finish.push_back(u);frames.pop_back();}
            else {int v=g.adj[u][frames.back().second++].to;if(!seen[v]){seen[v]=true;frames.push_back({v,0});}}
        }
    }
    std::vector<std::vector<int>> transpose(g.n),components;
    for(const auto& e:g.edges)transpose[static_cast<int>(e.to)].push_back(static_cast<int>(e.from));
    std::fill(seen.begin(),seen.end(),false);
    for(auto it=finish.rbegin();it!=finish.rend();++it)if(!seen[*it]) {
        std::vector<int> stack{*it},group;seen[*it]=true;
        while(!stack.empty()) {int u=stack.back();stack.pop_back();group.push_back(u);
            for(int v:transpose[u])if(!seen[v]){seen[v]=true;stack.push_back(v);}
        }
        std::sort(group.begin(),group.end());components.push_back(group);
    }std::sort(components.begin(),components.end());return components;
}
}
#ifndef ALGORITHM_ATLAS_NO_MAIN
int main() {
    try {
        using namespace atlas_graph;
        auto in=read_input(false,false,false);
        emit(kosaraju_scc(make_graph(in.n,in.edges,in.directed)));
        std::cout<<'\n';
    } catch(const std::exception& error) { std::cerr<<"error: "<<error.what()<<'\n'; return 2; }
}
#endif
