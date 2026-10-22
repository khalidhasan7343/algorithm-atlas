#include "../../common.hpp"

namespace atlas_graph {

struct DFSResult { std::vector<int> order,finish,parent,parent_edge,component; };
inline DFSResult dfs(const Graph& g) {
    DFSResult r{{},{},std::vector<int>(g.n,-1),std::vector<int>(g.n,-1),std::vector<int>(g.n,-1)};
    std::vector<bool> seen(g.n,false);
    for(int root=0;root<g.n;++root) if(!seen[root]) {
        seen[root]=true;r.component[root]=root;r.order.push_back(root);
        std::vector<std::pair<int,std::size_t>> stack{{root,0}};
        while(!stack.empty()) {
            int u=stack.back().first;
            if(stack.back().second==g.adj[u].size()) {r.finish.push_back(u);stack.pop_back();continue;}
            const auto a=g.adj[u][stack.back().second++];
            if(!seen[a.to]) {
                seen[a.to]=true;r.parent[a.to]=u;r.parent_edge[a.to]=a.id;r.component[a.to]=root;
                r.order.push_back(a.to);stack.push_back({a.to,0});
            }
        }
    }return r;
}
inline void emit(const DFSResult& r) {
    std::cout<<"{\"order\":";emit(r.order);std::cout<<",\"finish\":";emit(r.finish);
    std::cout<<",\"parent\":";parents(r.parent);std::cout<<",\"parent_edge\":";parents(r.parent_edge);
    std::cout<<",\"component\":";emit(r.component);std::cout<<'}';
}
}
#ifndef ALGORITHM_ATLAS_NO_MAIN
int main() {
    try {
        using namespace atlas_graph;
        auto in=read_input(false,false,false);
        emit(dfs(make_graph(in.n,in.edges,in.directed)));
        std::cout<<'\n';
    } catch(const std::exception& error) { std::cerr<<"error: "<<error.what()<<'\n'; return 2; }
}
#endif
