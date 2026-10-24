#include "../../common.hpp"

namespace atlas_nt {
inline std::vector<Integer> sieve(Integer limit) {
    bounded(limit,0,1000000);
    std::vector<unsigned char> marked(static_cast<std::size_t>(limit)+1,0);
    for (Integer p=2;p<=limit/p;++p)
        if (!marked[p]) for (Integer multiple=p*p;multiple<=limit;multiple+=p) marked[multiple]=1;
    std::vector<Integer> primes;
    for (Integer p=2;p<=limit;++p) if (!marked[p]) primes.push_back(p);
    return primes;
}
}
#ifndef ALGORITHM_ATLAS_NO_MAIN
int main(){try{auto values=atlas_nt::read_numbers(1);atlas_nt::emit(atlas_nt::sieve(values[0]));std::cout<<'\n';}
catch(const std::exception& error){std::cerr<<"error: "<<error.what()<<'\n';return 2;}}
#endif
