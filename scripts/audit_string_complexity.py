"""Bounded correctness/performance observations; no wall-clock pass threshold."""
import json
from pathlib import Path
import time
from verify_string_cross_algorithms import load,BASE,ROOT

AUDIT={
    "naive-pattern-matching":("alignment comparisons","none","O(nm+r)","O(1)+O(r) result"),
    "knuth-morris-pratt":("border-link amortization","O(m)","O(n+m+r)","O(m+r)"),
    "rabin-karp":("polynomial rolling update and exact candidate verification","O(m)","O(n+m+c*m+r); O(nm) worst case","O(m) initial copy + O(r) result"),
    "z-algorithm":("rightmost-box amortization","combined array O(n+m)","O(n+m+r)","O(n+m+r)"),
    "boyer-moore":("bad-character and strong good-suffix; no Galil rule","O(m+256)","O(nm+r) worst case","O(m+256+r)"),
    "manacher":("separate odd/even rightmost-palindrome passes","none","O(n)","O(n) returned radii"),
    "suffix-array":("rank-pair comparison sorting, doubling, Kasai LCP","O(n log² n)","query O(m log n+r log r)","O(n+r)"),
    "suffix-tree":("direct insertion with range-labelled edge splitting","O(n²) comparisons","contains O(m), find O(m+r log r) for fixed alphabet","O(n+r)"),
    "aho-corasick":("dense transitions, BFS failure, uncopied output links","O(P+k+256V)","scan O(n+z)","O(256V+P+k+z)"),
}


def main():
    records={}
    for name,(mechanism,preprocessing,bound,space) in AUDIT.items():
        module=load(BASE/name/"python/solution.py","performance_"+name)
        text=b"a"*(2048 if name=="suffix-tree" else 10000)
        pattern=b"a"*129
        started=time.perf_counter()
        construction=None
        if name in ("suffix-array","suffix-tree"):
            cls=module.SuffixArray if name=="suffix-array" else module.SuffixTree
            index=cls(text)
            construction=time.perf_counter()-started
            result=index.find(pattern)
            assert result==list(range(len(text)-len(pattern)+1))
            assert index.find(b"b")==[]
        elif name=="aho-corasick":
            patterns=[b"a"*4095,b"b",b""]
            index=module.AhoCorasick(patterns)
            construction=time.perf_counter()-started
            result=index.find(text)
            assert len(result)==(10000-4095+1)+10001
            assert result[0]==[0,2,0] and result[-1]==[10000,2,10000]
            assert sum(hit[1]==0 for hit in result)==5906
        elif name=="manacher":
            result=module.solve(text)
            assert result[2]==[0,10000]
            assert result[0]==[min(i+1,10000-i) for i in range(10000)]
            assert result[1]==[min(i,10000-i) for i in range(10000)]
        else:
            result=module.solve(text,pattern)
            assert result==list(range(len(text)-len(pattern)+1))
        records[name]=dict(mechanism=mechanism,preprocessing=preprocessing,time_bound=bound,
                           space_bound=space,text_bytes=len(text),pattern_bytes=(4096 if name=="aho-corasick" else 0 if name=="manacher" else 129),
                           elapsed_seconds=round(time.perf_counter()-started,6),
                           construction_seconds=round(construction,6) if construction is not None else None,
                           correctness="passed",timing_assertion="none; measured once, not an asymptotic proof")
    document=dict(symbols="n text bytes, m pattern bytes, r positions, c hash candidates, P aggregate pattern bytes, k pattern count, V trie nodes, z triples",
                  scope="Code-path review plus one bounded repeated-byte Python observation per algorithm; C++ bounds use equivalent code paths and are tested separately.",
                  alphabet="All 256 bytes; terminal symbol 256 for suffix tree. C++ map lookup is O(log sigma), sigma<=257.",algorithms=records)
    (ROOT/"docs/string-algorithms-evidence/complexity-results.json").write_text(json.dumps(document,indent=2)+"\n")
    print("9 bounded correctness/performance observations passed; no timing thresholds")


if __name__=="__main__":main()
