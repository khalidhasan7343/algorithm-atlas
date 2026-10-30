# FP-Growth

## 1. Algorithm Name

FP-Growth

## 2. Overview

Compress repeated transaction prefixes in an FP-tree and mine exact frequent patterns through weighted conditional pattern bases and conditional trees.

## 3. Problem Statement

Find every nonempty itemset meeting the common support threshold without Apriori-style candidate generation or an external mining implementation.

## 4. Why Do We Need This Algorithm?

Candidate enumeration and repeated database scans can be costly. Shared prefixes and conditional databases can reuse occurrence information instead.

## 5. Real-World Applications

Educational basket pattern discovery where transaction prefixes repeat after frequency ordering. Compression effectiveness depends on the data and does not imply universal speed or causal rules.

## 6. Core Intuition

Represent many rows with shared counted tree paths. For each suffix item, gather its ancestor prefixes with node counts; mine a smaller weighted database conditioned on that suffix.

## 7. Prerequisites

Sets, immutable keys, counting, sorted order and basic conditional probability. Read [B6 contracts](../../../../docs/association-rule-learning-conventions.md). Relative support=count/N, confidence(A→B)=count(A∪B)/count(A), lift=N*count(A∪B)/(count(A)*count(B)); this lesson returns counts before deriving rules.

## 8. Step-by-Step Working Process

Count weighted item frequencies, remove infrequent items, rank by descending count with natural-ID ties, and insert each ordered path. Nodes have counts, parents, children and next links; headers retain frequency and head/tail links. Mine header items in ascending frequency/ID order. A suffix node contributes its ancestor prefix with that node’s full weight to the conditional base. Build a fresh conditional FP-tree at the original absolute count threshold and extend the suffix. Explicit stack frames replace recursive calls; no single-path shortcut is claimed.

Correctness: Each inserted row contributes its weight once to every node on its ordered path. Header-linked node counts sum to the item’s support. Conditioning on suffix x preserves exactly the weighted occurrences containing x; ancestors encode earlier items allowed by that tree order, so conditional support of Y equals original support of Y union{x}. Each pattern has a unique suffix under the current order, partitioning the search. Induction over conditional trees yields every frequent pattern once. Treating each weighted prefix as one row would violate this argument.

## 9. Pseudocode

```text
count/filter items; rank by descending support then ID
insert each ordered row in FP-tree with parent/child/header links
stack = [(empty suffix, tree, iterator over mining order)]
for each suffix item x:
  emit suffix+x at header support
  traverse x node links; collect ancestor prefixes with node weights
  build conditional weighted tree with original min_count
  descend via explicit stack if conditional tree nonempty
```

## 10. Dry Run

Use rows [abc,abc,ab,ac,bc], N=5 and min_support0.4, so min_count2. All singletons count4, so tie order is a,b,c. Root count5; root/a count4 and root/b count1. Under a: b count3,c count1; under a/b: c count2; under root/b: c count1. Header c counts2+1+1=4. Conditional base for c is (ab,weight2),(a,weight1),(b,weight1), giving conditional a3,b3 and ab2. Therefore ac3,bc3,abc2. Header b’s nonempty conditional prefix is (a,weight3), yielding ab3. The three singleton headers plus these extensions give the same seven patterns.

The exact frequent map is a4,b4,c4,ab3,ac3,bc3,abc2. For a→b: support3/5=0.6, confidence3/4=0.75, lift(3/4)/(4/5)=15/16=0.9375. For ab→c: support2/5=0.4, confidence2/3, lift(2/3)/(4/5)=5/6. At min_confidence0.6, there are nine rules: six singleton→singleton and three pair→remaining-singleton; singleton→pair confidence0.5 fails. This illustrates why high confidence alone is not high lift or causation.

## 11. Time Complexity

For weighted input paths, count O(M), order each path O(length*log U), and insert O(M); M is total path entries. Conditional work is proportional to all visited header nodes, ancestor steps, inserted weighted path entries and ordering across trees. Prefix compression can help but conditional databases/output can still grow exponentially; there is no universally fastest miner.

## 12. Space Complexity

Initial tree has at most1+M nodes. Header tables/parent-child links are linear in tree nodes and U. Active conditional trees on the explicit stack, collected weighted bases and pattern output add data-dependent memory; conservative storage remains exponential with output. Depth<=U<=32 and work/node/output budgets bound this demonstration.

## 13. Python Implementation

[FPGrowth / fp_growth source](python/solution.py) implements this named mechanism with standard-library sets/dicts/integers, not a wrapper. [Example](python/example.py), [tests](tests/test_python.py), [shared rules](../rules.py). fit installs state only after successful validation and a complete bounded search. Independent tests use direct raw-row powerset counting, hand-derived counts and sparse incidence references, never another miner as the sole truth.

## 14. C++ Implementation

C++ is optional for this ML scope and absent. No placeholder source/test is provided; DSA Python/C++17/C++20 requirements remain unchanged.

## 15. Input and Output Examples

From repository root with the established development environment:

```sh
python machine-learning/unsupervised-learning/association-rule-learning/fp-growth/python/example.py
```

The example prints the seven count records in size/lexicographic order. solution.py also accepts JSON with transactions, optional parameters and min_confidence; adding min_confidence0.6 prints the nine rules above. The category-local rule utility is a separate fourth internal gate. Executed inputs/outputs live in Phase18 evidence.

## 16. Edge Cases

Empty input returns{}; empty rows remain in N; repeated items within a row count once; duplicate rows remain distinct. Homogeneous native integer IDs or nonempty strings only; reject bool/float/mixed/unhashable IDs and generator/bare-string inputs. min_support is a finite native float in(0,1], never an absolute count; min_confidence is a finite native float in[0,1]. Decimal strings of thresholds are compared as exact rational values, with no tolerance. max_patterns/max_work exhaustion raises MiningLimitError with no partial result and preserves prior state.

## 17. Advantages

Shared-prefix compression, no Apriori candidate generation, auditable header counts and weighted conditional support propagation.

## 18. Disadvantages and Limitations

Sparse disjoint paths may compress poorly. Basic FP-Growth only: no single-path optimization, closed/maximal-only output, weighted public observations or streaming updates. Node/header diagnostics are mutable inspection objects, not a supported incremental training API. Root count is represented path weight, not a conditional suffix’s support when empty prefixes are omitted.

Resource domain: N<=4096,U<=32, each raw row<=128 entries and total<=65536. Defaults min_support0.5,max_patterns10000,max_work1000000; documented maxima50000 patterns and5000000 charged work. No CPU/byte guarantee, arbitrary hashable IDs, weighted public rows, missing values, streaming updates or absolute-support threshold.

## 19. When to Use It

Use to study exact weighted prefix compression and conditional pattern growth on a modest database with repeated structure.

## 20. When Not to Use It

Use Eclat if vertical sets fit better, or production implementations for large/incremental/distributed datasets; benchmark representative data rather than infer a winner.

## 21. Comparison With Related Algorithms

FP-Growth projects weighted conditional prefix databases; Apriori joins/counts candidate levels; Eclat intersects vertical TID sets. All must match independent direct counts. The shared rule utility is independent of the mining mechanism.

## 22. Interview Questions

Why retain node weights in a conditional base? One compressed node can represent many original observations. Why is root count not sufficient for suffix support? Paths with no remaining ancestor can be omitted. How do header next links help? They enumerate all occurrences of one item without rescanning unrelated nodes.

## 23. Practice Problems

Rebuild the dry-run tree and every c conditional path. Duplicate the whole database and verify all counts double. Construct transactions with disjoint items and explain why prefix compression offers little benefit.

## 24. References

[Han, Pei, Yin and Mao, Mining Frequent Patterns without Candidate Generation: A Frequent-Pattern Tree Approach,2004](https://www.cs.sfu.ca/~jpei/publications/dami03_fpgrowth.pdf), author-hosted expanded primary paper; its original FP-Growth work appeared in2000.

## 25. Author Attribution

**MD.Khalid Hasan**, [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../../LICENSE); [contribution policy](../../../../CONTRIBUTING.md). Phase18 B6 owner review remains pending.
