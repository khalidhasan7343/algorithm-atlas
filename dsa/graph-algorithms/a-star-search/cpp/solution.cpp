#include "../../common.hpp"

namespace atlas_graph {

struct AStarResult {Integer cost;std::vector<int> path,edges;};
inline AStarResult a_star(const Graph& g,int source,int goal,const std::vector<Integer>& heuristic) {
    for(const auto& e:g.edges)bounded(e.weight,0,1000000,"A* requires bounded nonnegative weights");
    source=source_vertex(g.n,source);goal=source_vertex(g.n,goal);
    require(heuristic.size()==static_cast<std::size_t>(g.n),"one heuristic per vertex required");
    for(auto h:heuristic)bounded(h,0,1000000000,"invalid heuristic");
    if(goal!=-1)require(heuristic[goal]==0,"goal heuristic must be zero");
    Paths r(g.n);using Item=std::tuple<Integer,Integer,int>;
    std::priority_queue<Item,std::vector<Item>,std::greater<Item>> heap;
    if(source!=-1){r.distance[source]=0;heap.push({heuristic[source],0,source});}
    while(!heap.empty()) {
        auto [priority,cost,u]=heap.top();heap.pop();(void)priority;
        if(cost!=r.distance[u])continue;
        if(u==goal){auto path=path_to(r,goal);return {cost,path.first,path.second};}
        for(const auto& a:g.adj[u])if(cost+a.weight<r.distance[a.to]) {
            r.distance[a.to]=cost+a.weight;r.parent[a.to]=u;r.parent_edge[a.to]=a.id;
            heap.push({r.distance[a.to]+heuristic[a.to],r.distance[a.to],a.to});
        }
    }return {INF,{},{}};
}
inline void emit(const AStarResult& r) {
    std::cout<<"{\"cost\":";emit(r.cost);std::cout<<",\"path\":";emit(r.path);std::cout<<",\"edges\":";emit(r.edges);std::cout<<'}';
}
}
#ifndef ALGORITHM_ATLAS_NO_MAIN
int main() {
    try {
        using namespace atlas_graph;
        auto in=read_input(true,true,true);
        emit(a_star(make_graph(in.n,in.edges,in.directed,1000,0,1000000),source_vertex(in.n,in.source),source_vertex(in.n,in.goal),in.heuristic));
        std::cout<<'\n';
    } catch(const std::exception& error) { std::cerr<<"error: "<<error.what()<<'\n'; return 2; }
}
#endif
