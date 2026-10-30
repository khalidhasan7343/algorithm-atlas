# Apriori

## 1. Algorithm Name

Apriori

## 2. Overview

Find all nonempty frequent itemsets by level-wise prefix joins and anti-monotonic subset pruning, then use a separate shared utility to derive association rules.

## 3. Problem Statement

For N binary transactions and relative minimum support s, return every nonempty itemset X with count(X)>=ceil(s*N), together with its integer support count. Do not confuse this mapping with association rules.

## 4. Why Do We Need This Algorithm?

Scanning every possible subset wastes work on patterns already ruled out by an infrequent subset. Apriori uses that information before counting candidates.

## 5. Real-World Applications

Small basket co-occurrence exploration and auditable rule discovery in discrete event collections. Empirical co-occurrence suggests hypotheses, not causation or an invented deployment.

## 6. Core Intuition

If a large itemset appears often, all its smaller subsets must appear at least as often. Grow only from frequent smaller patterns.

## 7. Prerequisites

Sets, immutable keys, counting, sorted order and basic conditional probability. Read [B6 contracts](../../../../docs/association-rule-learning-conventions.md). Relative support=count/N, confidence(A→B)=count(A∪B)/count(A), lift=N*count(A∪B)/(count(A)*count(B)); this lesson returns counts before deriving rules.

## 8. Step-by-Step Working Process

Count singletons, sort surviving tuples, join size-k tuples only when their first k-1 items agree, and prune a size-(k+1) candidate unless every size-k subset was frequent. Scan the original immutable rows to count each retained candidate; repeat until a level is empty. The core does not enumerate the full powerset.

Correctness: For Y subset X, every row containing X also contains Y, so count(X)<=count(Y). Every frequent (k+1)-set has frequent k-subsets; its two compatible sorted k-prefix extensions are joined, and subset pruning cannot remove it. By induction from singleton counting, all and only frequent sets are retained. Each join has a unique pair of parents, avoiding duplicate output.

## 9. Pseudocode

```text
normalize rows; count singletons; retain frequent level1
while current level is nonempty:
  join same-prefix sorted itemsets
  prune candidates missing any immediate subset
  scan rows and count surviving candidates
  emit counts>=minimum and advance level
```

## 10. Dry Run

Use rows [abc,abc,ab,ac,bc], N=5 and min_support0.4, so min_count2. Singleton counts: a4,b4,c4. Level2 candidates are ab,ac,bc, each count3. All three immediate subsets of abc exist, so level3 contains abc with count2. There is no level4. levels_ sizes=(3,3,1), candidate_counts_=(3,1,0). If bc were absent at level2, joining ab/ac would prune abc before scanning.

The exact frequent map is a4,b4,c4,ab3,ac3,bc3,abc2. For a→b: support3/5=0.6, confidence3/4=0.75, lift(3/4)/(4/5)=15/16=0.9375. For ab→c: support2/5=0.4, confidence2/3, lift(2/3)/(4/5)=5/6. At min_confidence0.6, there are nine rules: six singleton→singleton and three pair→remaining-singleton; singleton→pair confidence0.5 fails. This illustrates why high confidence alone is not high lift or causation.

## 11. Time Complexity

Let U be unique items, N transactions, Lk frequent k-sets and Ck candidates after pruning. This implementation uses pair joins O(Lk²*k) in the conservative bound, subset checks up to O(k²) per candidate, and horizontal containment scans O(N*k*Ck). Total across levels is output/candidate-sensitive, exponential in U in the worst case. Already infrequent singletons stop further joins. There is no distribution-independent average speed guarantee.

## 12. Space Complexity

Input storage O(N+M), M total unique row memberships. Pattern output O(sum_X |X|); current candidates/levels and retained diagnostic levels add comparable output/candidate storage. No recursion. Raw input, universe, work and pattern caps bound this educational implementation.

## 13. Python Implementation

[Apriori / apriori source](python/solution.py) implements this named mechanism with standard-library sets/dicts/integers, not a wrapper. [Example](python/example.py), [tests](tests/test_python.py), [shared rules](../rules.py). fit installs state only after successful validation and a complete bounded search. Independent tests use direct raw-row powerset counting, hand-derived counts and sparse incidence references, never another miner as the sole truth.

## 14. C++ Implementation

C++ is optional for this ML scope and absent. No placeholder source/test is provided; DSA Python/C++17/C++20 requirements remain unchanged.

## 15. Input and Output Examples

From repository root with the established development environment:

```sh
python machine-learning/unsupervised-learning/association-rule-learning/apriori/python/example.py
```

The example prints the seven count records in size/lexicographic order. solution.py also accepts JSON with transactions, optional parameters and min_confidence; adding min_confidence0.6 prints the nine rules above. The category-local rule utility is a separate fourth internal gate. Executed inputs/outputs live in Phase18 evidence.

## 16. Edge Cases

Empty input returns{}; empty rows remain in N; repeated items within a row count once; duplicate rows remain distinct. Homogeneous native integer IDs or nonempty strings only; reject bool/float/mixed/unhashable IDs and generator/bare-string inputs. min_support is a finite native float in(0,1], never an absolute count; min_confidence is a finite native float in[0,1]. Decimal strings of thresholds are compared as exact rational values, with no tolerance. max_patterns/max_work exhaustion raises MiningLimitError with no partial result and preserves prior state.

## 17. Advantages

Simple exact counts, explicit anti-monotonic reasoning, useful level/candidate diagnostics, deterministic presentation, and easy horizontal-data inspection.

## 18. Disadvantages and Limitations

Repeated scans and candidate joins can dominate on dense low-support data. Frequent output may have2^U-1 sets, so no implementation can avoid that output cost. max_patterns also bounds candidate collections even if many would later be infrequent; an exceeded budget is an explicit incomplete search error, never a successful truncated mapping.

Resource domain: N<=4096,U<=32, each raw row<=128 entries and total<=65536. Defaults min_support0.5,max_patterns10000,max_work1000000; documented maxima50000 patterns and5000000 charged work. No CPU/byte guarantee, arbitrary hashable IDs, weighted public rows, missing values, streaming updates or absolute-support threshold.

## 19. When to Use It

Use for a small sparse transaction database when explainable candidate levels and downward closure are the learning goal.

## 20. When Not to Use It

Use Eclat when TID intersections are preferable, or FP-Growth when common prefixes compress well; none is universally fastest.

## 21. Comparison With Related Algorithms

Apriori grows breadth-first candidate levels and scans rows; Eclat extends vertical TID sets; FP-Growth builds weighted conditional prefix trees without Apriori candidate generation. Shared rule generation applies exactly the same formulas to each complete count map.

## 22. Interview Questions

Why prune when one subset is infrequent? Anti-monotonic support makes the superset infrequent. Why retain empty rows? They count in N even though they support no nonempty pattern. Why not deduplicate transactions? Repeated observations change support counts and probabilities.

## 23. Practice Problems

Remove one bc occurrence and recalculate which level3 patterns survive at support0.4. Construct a dataset with many singleton survivors but no frequent pair. Prove each candidate can be joined only once with sorted common prefixes.

## 24. References

[Agrawal and Srikant, Fast Algorithms for Mining Association Rules,1994](https://rsrikant.com/papers/vldb94.pdf), author-hosted primary paper. This implementation uses Apriori, not AprioriTid or AprioriHybrid.

## 25. Author Attribution

**MD.Khalid Hasan**, [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../../LICENSE); [contribution policy](../../../../CONTRIBUTING.md). Phase18 B6 owner review remains pending.
