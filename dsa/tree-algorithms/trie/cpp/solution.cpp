#include "../../common.hpp"

namespace atlas_tree {

class Trie{
    struct Node{std::array<std::unique_ptr<Node>,26> children{};bool terminal=false;};
    Node root_;std::size_t size_=0,nodes_=1;
    static void word_checked(const std::string& word){require(word.size()<=256,"word too long");for(unsigned char ch:word)require(ch>='a' && ch<='z',"lowercase ASCII required");}
    const Node* find(const std::string& word)const{const Node* node=&root_;for(char ch:word){node=node->children[static_cast<std::size_t>(ch-'a')].get();if(!node)return nullptr;}return node;}
public:
    std::size_t size()const{return size_;}
    bool contains(const std::string& word)const{word_checked(word);const Node* node=find(word);return node && node->terminal;}
    bool starts_with(const std::string& word)const{word_checked(word);return find(word)!=nullptr;}
    bool insert(const std::string& word){
        word_checked(word);Node* node=&root_;std::size_t matched=0;
        while(matched<word.size()){auto& child=node->children[static_cast<std::size_t>(word[matched]-'a')];if(!child)break;node=child.get();++matched;}
        if(matched==word.size() && node->terminal)return false;
        require(size_<10000 && nodes_+word.size()-matched<=100000,"trie resource limit");
        for(std::size_t j=matched;j<word.size();++j){auto& child=node->children[static_cast<std::size_t>(word[j]-'a')];child=std::make_unique<Node>();node=child.get();++nodes_;}
        node->terminal=true;++size_;return true;
    }
    bool erase(const std::string& word){
        word_checked(word);Node* node=&root_;std::vector<std::pair<Node*,std::size_t>> path;
        for(char ch:word){auto i=static_cast<std::size_t>(ch-'a');if(!node->children[i])return false;path.push_back({node,i});node=node->children[i].get();}
        if(!node->terminal)return false;node->terminal=false;--size_;
        for(auto it=path.rbegin();it!=path.rend();++it){auto& child=it->first->children[it->second];if(child->terminal || std::any_of(child->children.begin(),child->children.end(),[](const auto& p){return static_cast<bool>(p);}))break;child.reset();--nodes_;}
        return true;
    }
};
inline void trie_cli(bool final=true){Trie tree;int q=query_count();std::vector<bool> result;
    for(int i=0;i<q;++i){Integer op=bounded(token(),0,3,"invalid operation");std::string word;require(static_cast<bool>(std::cin>>word),"missing word");if(word=="-")word.clear();result.push_back(op==0?tree.insert(word):op==1?tree.contains(word):op==2?tree.starts_with(word):tree.erase(word));}
    if(final)end_input();emit(result);
}

}
#ifndef ALGORITHM_ATLAS_NO_MAIN
int main(){try{using namespace atlas_tree;
trie_cli();
std::cout<<'\n';
}catch(const std::exception& error){std::cerr<<"error: "<<error.what()<<'\n';return 2;}}
#endif
