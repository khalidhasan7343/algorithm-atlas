# Eclat

## 1. Algorithm Name

Eclat

## 2. Overview

Find frequent itemsets by depth-first extension of vertical transaction-ID sets, using intersections rather than repeated horizontal candidate scans.

## 3. Problem Statement

Return exactly the same nonempty itemset-to-integer-count mapping as Apriori for the declared transaction and relative-support contract, through a genuine vertical database.

## 4. Why Do We Need This Algorithm?

An item’s occurrence rows can be retained once and intersected to count extensions efficiently on suitable data.

## 5. Real-World Applications

Small repeated-query discrete pattern exploration when vertical membership sets fit memory, including dense basket examples. Rules remain empirical associations, not causal effects.

## 6. Core Intuition

A row contains both patterns exactly when its stable transaction ID belongs to both TID sets. Intersections can only shrink.

## 7. Prerequisites

Sets, immutable keys, counting, sorted order and basic conditional probability. Read [B6 contracts](../../../../docs/association-rule-learning-conventions.md). Relative support=count/N, confidence(A→B)=count(A∪B)/count(A), lift=N*count(A∪B)/(count(A)*count(B)); this lesson returns counts before deriving rules.

## 8. Step-by-Step Working Process

Assign row IDs0..N-1 including empty rows. Build an item->frozen TID-set index; discard infrequent singleton extensions. Traverse sorted prefix equivalence classes with explicit stack frames. For each chosen extension, intersect its TIDs with each later extension, retain frequent intersections and descend. Earlier IDs/items are never reintroduced, so each itemset is enumerated once.

Correctness: TID(A union B)=TID(A) intersection TID(B), because a row contains the union iff it contains both. Thus intersection size is the exact support and cannot exceed either parent count. Every frequent itemset has a unique increasing item order and frequent prefixes, so no necessary extension is pruned. Induction over this unique path gives completeness without calling Apriori.

## 9. Pseudocode

```text
build vertical[item]={row IDs containing item}
keep frequent singleton extensions in sorted order
stack = [(empty prefix, extensions, index0)]
advance one extension at a time:
  emit prefix+item with its TID count
  intersect with each later extension; prune counts below minimum
  descend into resulting equivalence class via explicit stack
```

## 10. Dry Run

Use rows [abc,abc,ab,ac,bc], N=5 and min_support0.4, so min_count2. TID(a)={0,1,2,3}, TID(b)={0,1,2,4}, TID(c)={0,1,3,4}. Pair intersections each have3 rows; TID(ab) intersect TID(ac)={0,1}, giving abc count2. Empty rows, if added, receive IDs and increase N but appear in no singleton index. Duplicate original rows receive distinct IDs.

The exact frequent map is a4,b4,c4,ab3,ac3,bc3,abc2. For a→b: support3/5=0.6, confidence3/4=0.75, lift(3/4)/(4/5)=15/16=0.9375. For ab→c: support2/5=0.4, confidence2/3, lift(2/3)/(4/5)=5/6. At min_confidence0.6, there are nine rules: six singleton→singleton and three pair→remaining-singleton; singleton→pair confidence0.5 fails. This illustrates why high confidence alone is not high lift or causation.

## 11. Time Complexity

Building the vertical database costs O(N+M). Python set intersection costs expected O(min(|TA|,|TB|)) under ordinary integer-hash assumptions; sum this over explored extensions. Ordering/stack work and output storage remain additional costs. Dense/low-support data can have exponentially many frequent patterns; no universal average advantage over Apriori/FP-Growth is claimed.

## 12. Space Complexity

O(N+M) normalized input/index plus active depth-first equivalence-class TID sets and O(sum_X |X|) pattern output. In a conservative bound active intersection storage can reach O(U²*N), while output itself is exponential. Depth<=U<=32 and an explicit stack avoids Python recursion failure.

## 13. Python Implementation

[Eclat / eclat source](python/solution.py) implements this named mechanism with standard-library sets/dicts/integers, not a wrapper. [Example](python/example.py), [tests](tests/test_python.py), [shared rules](../rules.py). fit installs state only after successful validation and a complete bounded search. Independent tests use direct raw-row powerset counting, hand-derived counts and sparse incidence references, never another miner as the sole truth.

## 14. C++ Implementation

C++ is optional for this ML scope and absent. No placeholder source/test is provided; DSA Python/C++17/C++20 requirements remain unchanged.

## 15. Input and Output Examples

From repository root with the established development environment:

```sh
python machine-learning/unsupervised-learning/association-rule-learning/eclat/python/example.py
```

The example prints the seven count records in size/lexicographic order. solution.py also accepts JSON with transactions, optional parameters and min_confidence; adding min_confidence0.6 prints the nine rules above. The category-local rule utility is a separate fourth internal gate. Executed inputs/outputs live in Phase18 evidence.

## 16. Edge Cases

Empty input returns{}; empty rows remain in N; repeated items within a row count once; duplicate rows remain distinct. Homogeneous native integer IDs or nonempty strings only; reject bool/float/mixed/unhashable IDs and generator/bare-string inputs. min_support is a finite native float in(0,1], never an absolute count; min_confidence is a finite native float in[0,1]. Decimal strings of thresholds are compared as exact rational values, with no tolerance. max_patterns/max_work exhaustion raises MiningLimitError with no partial result and preserves prior state.

## 17. Advantages

Exact integer support through a transparent intersection identity, explicit TID diagnostics, and fewer horizontal scans when vertical sets remain manageable.

## 18. Disadvantages and Limitations

Dense large TID sets and many retained extensions consume memory. This is basic set-based Eclat, without diffsets, compressed bitmaps, closed/maximal-only mining or parallel/distributed variants. Reordering rows changes TID diagnostics but leaves support results unchanged.

Resource domain: N<=4096,U<=32, each raw row<=128 entries and total<=65536. Defaults min_support0.5,max_patterns10000,max_work1000000; documented maxima50000 patterns and5000000 charged work. No CPU/byte guarantee, arbitrary hashable IDs, weighted public rows, missing values, streaming updates or absolute-support threshold.

## 19. When to Use It

Use when vertical occurrence sets fit memory and intersection-based pattern growth is the intended lesson.

## 20. When Not to Use It

Use a prefix tree when repeated horizontal prefixes compress effectively, or a production bitmap miner for large databases; measure rather than assume speed.

## 21. Comparison With Related Algorithms

Apriori counts candidates horizontally; Eclat counts vertical intersections; FP-Growth counts weighted conditional paths. Their mechanism differs, while their complete frequent itemset map and downstream rules must agree.

## 22. Interview Questions

Why are duplicate transactions distinct? IDs represent observations, not unique row contents. Why consider only later extensions? It partitions the search by one sorted item order. Why can an infrequent intersection be pruned? Future intersections cannot add row IDs.

## 23. Practice Problems

Write all vertical sets and pair/triple intersections for the dry run. Insert an empty row at the beginning and recalculate IDs and threshold. Construct disjoint singleton TID sets and explain why no pair can survive.

## 24. References

[Mohammed J. Zaki, Scalable Algorithms for Association Mining,2000—author publication index](https://www.cs.rpi.edu/~zaki/publications/). The implemented scope is basic Eclat vertical intersection mining, not MaxEclat.

## 25. Author Attribution

**MD.Khalid Hasan**, [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../../LICENSE); [contribution policy](../../../../CONTRIBUTING.md). Phase18 B6 owner review remains pending.
