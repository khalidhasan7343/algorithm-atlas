"""Execute the Phase 9 semantic comparison matrix with independent references."""
import argparse
import importlib.util
import json
from pathlib import Path
import random

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"dsa/string-algorithms"
SEED=90909


def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify(through=3):
    batches=(("naive-pattern-matching","knuth-morris-pratt","rabin-karp"),
             ("z-algorithm","boyer-moore","manacher"),
             ("suffix-array","suffix-tree","aho-corasick"))
    modules={name:load(BASE/name/"python/solution.py","cross_"+name)
             for batch in batches[:through] for name in batch}
    oracle=load(BASE/"string_oracles.py","cross_oracle")
    rng=random.Random(SEED)
    counts={}
    for case_id in range(120):
        text=(b"a"*(case_id%70)+b"b") if case_id<40 else bytes(rng.choice(b"abc\0\xff#$") for _ in range(rng.randrange(81)))
        pattern=bytes(rng.choice(b"abc\0\xff#$") for _ in range(rng.randrange(12)))
        if case_id%3==0:
            start=rng.randrange(len(text)+1)
            pattern=text[start:start+case_id%13]
        expected=oracle.occurrences(text,pattern)
        naive=modules["naive-pattern-matching"].solve(text,pattern)
        assert naive==expected
        for name in ("knuth-morris-pratt","rabin-karp","z-algorithm","boyer-moore"):
            if name in modules:
                assert modules[name].solve(text,pattern)==naive
                counts["naive vs "+name]=counts.get("naive vs "+name,0)+1
        if through>=2:
            assert modules["manacher"].solve(text)==oracle.palindromes(text)
            counts["Manacher vs expansion/exhaustive"]=case_id+1
        if through>=3:
            sa=modules["suffix-array"].SuffixArray(text)
            order,lcp=oracle.suffixes(text)
            assert sa.sa==order and sa.lcp==lcp
            assert sa.find(pattern)==naive
            tree=modules["suffix-tree"].SuffixTree(text)
            assert tree.find(pattern)==naive
            patterns=[pattern,b"",b"a",b"aa",pattern,b"ba"]
            ac=modules["aho-corasick"].AhoCorasick(patterns)
            assert ac.find(text)==oracle.multi(text,patterns)
            for query in (b"",b"a",text[:3],b"absent\xfe"):
                ref=oracle.occurrences(text,query)
                assert sa.find(query)==tree.find(query)==ref
                assert tree.contains(query)==bool(ref)
            counts.update({"Suffix Array order/LCP vs direct suffixes":case_id+1,
                           "Suffix Array search vs naive":case_id+1,
                           "Suffix Tree search vs naive":case_id+1,
                           "Aho-Corasick vs repeated naive":case_id+1})
    return dict(seed=SEED,cases_per_comparison=120,through_batch=through,
                comparisons=counts,status="passed")


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--through",type=int,choices=(1,2,3),default=3)
    parser.add_argument("--check-only",action="store_true")
    args=parser.parse_args()
    result=verify(args.through)
    if not args.check_only:
        (ROOT/f"docs/string-algorithms-evidence/cross-matrix-batch{args.through}.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
