#ifndef ALGORITHM_ATLAS_GRAPH_COMMON_HPP
#define ALGORITHM_ATLAS_GRAPH_COMMON_HPP
#include <algorithm>
#include <charconv>
#include <deque>
#include <functional>
#include <iostream>
#include <limits>
#include <numeric>
#include <optional>
#include <queue>
#include <stdexcept>
#include <string>
#include <tuple>
#include <utility>
#include <vector>
namespace atlas_graph {
using Integer = long long;
constexpr Integer INF = 4000000000000000000LL;
constexpr Integer NEG = -INF;
static_assert(std::numeric_limits<Integer>::digits >= 63, "64-bit integer required");
inline void require(bool condition, const char* message) {
    if (!condition) throw std::invalid_argument(message);
}
inline Integer bounded(Integer x, Integer lo, Integer hi, const char* message) {
    require(lo <= x && x <= hi, message); return x;
}
struct Edge { Integer from, to, weight; };
struct Arc { int to; Integer weight; int id; };
struct Graph {
    int n; bool directed; std::vector<Edge> edges;
    std::vector<std::vector<Arc>> adj;
};
inline Graph make_graph(Integer n, const std::vector<Edge>& edges, bool directed,
                        int cap=1000, Integer lo=-1000000, Integer hi=1000000) {
    bounded(n, 0, cap, "vertex count outside contract");
    require(edges.size() <= 10000, "too many edges");
    Graph g{static_cast<int>(n), directed, edges, std::vector<std::vector<Arc>>(static_cast<std::size_t>(n))};
    for (std::size_t i=0; i<edges.size(); ++i) {
        const auto& e=edges[i];
        bounded(e.from,0,n-1,"invalid edge source"); bounded(e.to,0,n-1,"invalid edge target");
        bounded(e.weight,lo,hi,"weight outside contract");
        g.adj[static_cast<int>(e.from)].push_back({static_cast<int>(e.to),e.weight,static_cast<int>(i)});
        if (!directed) g.adj[static_cast<int>(e.to)].push_back({static_cast<int>(e.from),e.weight,static_cast<int>(i)});
    }
    return g;
}
inline int source_vertex(int n, Integer s) {
    if (n==0 && s==-1) return -1;
    return static_cast<int>(bounded(s,0,n-1,"invalid source"));
}
inline Integer token() {
    std::string s; require(static_cast<bool>(std::cin>>s),"missing integer token");
    Integer x=0; auto result=std::from_chars(s.data(),s.data()+s.size(),x);
    require(result.ec==std::errc{} && result.ptr==s.data()+s.size(),"invalid integer token"); return x;
}
inline void end_input() { std::string extra; require(!(std::cin>>extra),"trailing input"); }
inline void emit(Integer x) {
    if(x==INF) std::cout<<"null"; else if(x==NEG) std::cout<<"\"-inf\""; else std::cout<<x;
}
inline void emit(int x) { std::cout<<x; }
inline void emit(bool x) { std::cout<<(x?"true":"false"); }
template<class T> inline void emit(const std::vector<T>& values) {
    std::cout<<'[';
    for(std::size_t i=0;i<values.size();++i) { if(i) std::cout<<','; emit(values[i]); }
    std::cout<<']';
}
inline void parents(const std::vector<int>& values) {
    std::cout<<'['; for(std::size_t i=0;i<values.size();++i) {
        if(i) std::cout<<',';
        if(values[i]<0) std::cout<<"null"; else std::cout<<values[i];
    } std::cout<<']';
}
struct Paths {
    std::vector<Integer> distance;
    std::vector<int> parent, parent_edge;
    explicit Paths(int n): distance(n,INF), parent(n,-1), parent_edge(n,-1) {}
};
inline void emit(const Paths& p) {
    std::cout<<"{\"distance\":"; emit(p.distance);
    std::cout<<",\"parent\":"; parents(p.parent);
    std::cout<<",\"parent_edge\":"; parents(p.parent_edge); std::cout<<'}';
}
inline std::pair<std::vector<int>,std::vector<int>> path_to(const Paths& p,int target) {
    bounded(target,0,static_cast<Integer>(p.distance.size())-1,"invalid target");
    std::vector<int> vertices,edges;
    if(p.distance[target]==INF || p.distance[target]==NEG) return {vertices,edges};
    for(int v=target;v!=-1;v=p.parent[v]) {
        vertices.push_back(v); require(vertices.size()<=p.distance.size(),"cyclic predecessor chain");
        if(p.parent_edge[v]!=-1) edges.push_back(p.parent_edge[v]);
    }
    std::reverse(vertices.begin(),vertices.end());std::reverse(edges.begin(),edges.end());
    return {vertices,edges};
}
struct SpanningForest { Integer weight=0; std::vector<int> edges; };
inline void emit(const SpanningForest& r) {
    std::cout<<"{\"weight\":";emit(r.weight);std::cout<<",\"edges\":";emit(r.edges);std::cout<<'}';
}
struct Input {
    int n, m; bool directed; Integer source=-1, goal=-1;
    std::vector<Integer> heuristic; std::vector<Edge> edges;
};
inline Input read_input(bool weighted, bool sourced=false, bool astar=false, bool final=true) {
    Input in{};
    in.n=static_cast<int>(bounded(token(),0,1000,"invalid n"));
    in.m=static_cast<int>(bounded(token(),0,10000,"invalid m"));
    in.directed=bounded(token(),0,1,"mode must be 0 or 1")==1;
    if(sourced) in.source=token();
    if(astar) { in.goal=token(); for(int i=0;i<in.n;++i) in.heuristic.push_back(token()); }
    for(int i=0;i<in.m;++i) {
        Integer u=token(),v=token(),w=weighted?token():1;
        in.edges.push_back({u,v,w});
    }
    if(final) end_input();
    return in;
}
} // namespace atlas_graph
#endif
