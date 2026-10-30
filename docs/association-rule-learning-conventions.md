# B6 transaction, threshold and rule contracts

Owner: **MD.Khalid Hasan**, MIT. Three miners expose fit(transactions),
frequent_itemsets_ mapping frozenset -> positive integer support count,
n_transactions_, items_ tuple, min_count_ and work_units_. Functional wrappers
apriori/eclat/fp_growth return that ordered count mapping. No fitted NumPy array,
classifier, neural framework or duplicate algorithm canonical.

Outer input must be list/tuple, at most4096 transactions. Each transaction is a
list/tuple/set/frozenset; at most128 raw entries per row,65536 total raw entries
and32 unique items. Supported IDs are homogeneous native int64-range integers or
nonempty native strings of at most128 characters. Reject bool, float, None, mixed
families, arbitrary hashable objects, nested/unhashable values, dicts, bare strings
and generator inputs. Repeated row items count once; duplicate rows remain separate
observations. Empty rows are retained in N; empty database returns{} with N=0.
Inputs are copied to immutable sets; no caller mutation or global RNG use.

min_support is **native float only**, 0<value<=1, default0.5: always a relative
threshold, never a support count. Pass1.0 for all rows; integer1 is rejected.
Interpret its shortest decimal representation exactly: fraction=Fraction(str(value)),
min_count=max(1,ceil(fraction*N)). This avoids binary product rounding at e.g.
0.14*100 and has **no epsilon tolerance**. A nextafter threshold just above a rational
boundary is intentionally distinct. Empty input has min_count1 and no patterns.

Output dict insertion order is ascending(itemset size, tuple(sorted items)); counts
are integers, not fractions. IDs within each family use natural numeric/Unicode
ordering. Sorting, FP-tree frequency ties and TID extension order are explicit,
independent of hash seed or transaction ordering. Nonempty itemsets only.

Resource limits: max_patterns default10000, native int1..50000, bounds output and
intermediate candidate/extension collection sizes; max_work default1000000, native
int1..5000000, bounds explicitly charged row/candidate/intersection/tree/path/rule
operations. Budget accounting is conservative algorithm-specific work, not a CPU
or byte guarantee. Exceeding any bound raises MiningLimitError, returns no partial
mapping and preserves any earlier fitted state. Universe32 bounds depth; Eclat and
FP-Growth also use explicit stacks, not Python recursion. No exhaustive powerset
preallocation in core mining. Output and rule sets are inherently exponential.

Shared rules.generate_rules(counts,n_transactions,min_confidence=0.5,
max_rules=10000,max_work=1000000) validates a complete downward-closed support map
with positive native integer counts<=N and immediate-subset anti-monotonicity.
Missing subsets and inconsistent counts fail. Empty mapping at N=0 returns[];
nonempty mapping at N=0 fails. min_confidence is native float in[0,1], decimal-exact
comparison by integer cross multiplication. For each frequent union S, stream all
nonempty proper antecedents A; B=S-A. Rule support=count(S)/N,
confidence=count(S)/count(A), lift=N*count(S)/(count(A)*count(B)). Denominators are
validated positive; results are immutable Rule records with support_count, support,
confidence and lift plus frozen antecedent/consequent. Numeric metrics are floats
for presentation, while filtering uses exact rationals. Return order is ascending
antecedent size/tuple then consequent size/tuple. Support bounds and confidence[0,1]
follow from integer count constraints; lift can exceed1, equal1 or fall below1.
Association is empirical, not causal; high confidence need not imply high lift.

The API does not verify whether an arbitrary supplied support map is realizable by
some database; mine from validated transactions for that provenance. No lift filter,
conviction, weights, streaming data, missing values or absolute-support API is claimed.
B6 NumPy conversions are unnecessary; reference tests may use independent sparse
incidence primitives without making them core dependencies.
