"""Execute frequency/count/backtracking relationships and all differing bits."""
from collections import Counter
import argparse
import importlib.util
import json
from pathlib import Path
import random

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"dsa/bit-manipulation"


def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify():
    modules={name:load(BASE/name/"python/solution.py","bit_cross_"+name) for name in (
        "xor-unique-elements","two-non-repeating-elements",
        "brian-kernighan-set-bit-counting","subset-generation-bitmasking")}
    oracle=load(BASE/"bit_oracles.py","bit_cross_reference")
    power=load(ROOT/"dsa/recursion-and-backtracking/power-set-generation/python/solution.py","bit_cross_power")
    counts={}
    for number,name in ((1,"xor-unique-elements"),(2,"two-non-repeating-elements")):
        cases=oracle.xor_vectors(number)
        for values in cases:
            assert modules[name].solve(values)==oracle.frequencies(values,number)
        counts[name+" vs frequency"]=len(cases)
    rng=random.Random(10109)
    for _ in range(120):
        value=rng.randrange(-(2**31),2**31)
        assert modules["brian-kernighan-set-bit-counting"].solve(value)==oracle.bit_count(value)
        values=[rng.randrange(-2,3) for _ in range(rng.randrange(10))]
        actual=modules["subset-generation-bitmasking"].solve(values)
        assert actual==oracle.recursive_subsets(values)
        assert Counter(map(tuple,actual))==Counter(map(tuple,power.power_set_generation(values)))
    counts["Kernighan vs binary representation"]=120
    counts["Bitmask vs independent positional recursion"]=120
    counts["Bitmask vs existing Power Set multiset"]=120
    for bit in range(32):
        value=2**bit if bit<31 else -(2**31)
        values=[0,-3,-3,value]
        assert modules["two-non-repeating-elements"].solve(values)==sorted([0,value])
    return dict(seed=10109,comparisons=counts,all_32_differing_bits="passed",
                phase9_approval="explicit owner approval on 2026-10-24 Asia/Dhaka",
                sequence="normal roadmap Phase 10",status="passed")


if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--check-only",action="store_true")
    args=parser.parse_args();result=verify()
    if not args.check_only:
        (ROOT/"docs/bit-manipulation-evidence/oracle-matrix.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
