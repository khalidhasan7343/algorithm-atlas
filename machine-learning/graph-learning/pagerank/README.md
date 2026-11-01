# PageRank

## 1. Algorithm Name

PageRank: personalized random-surfer ranking with weighted links,dangling-row
completion and dense power iteration. Canonical ID `pagerank` belongs to B9.

## 2. Overview

The result is a probability for every graph node. Links carry attention onward;
teleportation supplies a restart distribution. Scores quantify this model's
stationary traffic,not truth,quality or a causal effect.

## 3. Problem Statement

Input is a real nonnegative adjacency matrix A with1..32 rows/columns. Row i,
column j is the weight of i→j. Output is a length-n float64 distribution and
convergence diagnostics. Empty graphs,negative/nonfinite weights and invalid
probability vectors are errors. See [shared contracts](../../../docs/graph-learning-conventions.md).

## 4. Why Do We Need This Algorithm?

An incoming-link count treats every source equally and ignores multi-step paths.
This fixed-point model propagates influence recursively,while damping makes a
well-defined bounded computation possible even on disconnected directed graphs.

## 5. Real-World Applications

Ranking a small directed citation/link network and exploring personalized graph
navigation are natural examples. This implementation is an educational dense
solver,not a web-scale crawler or production search engine.

## 6. Core Intuition

Normalize each nonzero outgoing row into transition probabilities. A dangling
node redistributes its mass according to v. With probability d follow P; otherwise
restart from v. A node with no outgoing links therefore retains no hidden sink.

## 7. Prerequisites

Probability vectors,matrix multiplication,fixed points and
[graph traversal](../../../dsa/graph-algorithms/breadth-first-search/README.md).
Keep row-stochastic P and column-vector ranks distinct: propagation uses P.T.

## 8. Step-by-Step Working Process

1. Validate A,d,tolerance,budget and personalization v; copy input data.
2. Set P[i,j]=A[i,j]/sum_j A[i,j] for positive-degree rows; otherwise P[i,:]=v.
3. Initialize r=v; update r'=d P.T r+(1-d)v and remove floating mass drift.
4. Compute residual ρ=||d P.T r'+(1-d)v-r'||₁.
5. Stop when ρ/(1-d)<=tolerance or max_iter is exhausted.

P preserves probability mass. In exact arithmetic the map is an L1 contraction
with factor d<1,so a unique fixed point exists and its error is at most ρ/(1-d).
The computed float64 bound is diagnostic; roundoff is not interval-certified.

## 9. Pseudocode

```text
complete outgoing transition rows,including dangling rows
rank = personalization
repeat at most max_iter times:
    rank = damping * transpose(P) * rank + (1-damping) * personalization
    normalize roundoff in rank
    residual = L1(next_update(rank) - rank)
    if residual / (1-damping) <= tolerance: stop
return rank,iterations,residual,converged
```

## 10. Dry Run

For A=[[0,1],[0,0]],v=[1/2,1/2],d=1/2,the completed P is
[[0,1],[1/2,1/2]]. Starting from v gives[3/8,5/8],then[13/32,19/32].
At stationarity r₀=(r₁/4)+1/4 and r₀+r₁=1,so r=[2/5,3/5].
This is also checked against an independent direct linear solve.

## 11. Time Complexity

Let n be nodes and K executed iterations. Validation/transition construction is
O(n²); dense matrix-vector propagation and residual evaluation cost O(K n²).
The best converged case uses one iteration; worst case uses max_iter. No
input-independent average iteration count is claimed. A sparse implementation
could use O(K(n+m)) for m edges,but this implementation always stores dense A/P.
Damping near1 and tighter tolerance can require more iterations.

## 12. Space Complexity

Owned transition storage is O(n²); ranks,degrees and personalization are O(n).
The caller's original adjacency is not modified. There is no recursion or walk
storage. Diagnostics add constant metadata plus up to n dangling indices.

## 13. Python Implementation

[Source](python/solution.py) provides `PageRank(damping=.85,tolerance=1e-10,
max_iter=1000,personalization=None)`. `fit(A)` returns self;
`fit_transform(A)` returns a rank copy. Inspect `scores_`,`transition_matrix_`,
`personalization_`,`dangling_nodes_`,`n_iter_`,`residual_`,`error_bound_`,
`converged_` and `optimization_status_`. A failed refit preserves previous state.

## 14. C++ Implementation

C++ is optional for this ML canonical and absent; no placeholder source/tests
exist. DSA still requires actual Python,C++17 and C++20 tests.

## 15. Input and Output Examples

From repository root,using the existing NumPy environment:

```sh
.venv/bin/python machine-learning/graph-learning/pagerank/python/example.py
```

The [executable example](python/example.py) prints its directed adjacency,
completed transition matrix,damping,ranks,normalization and convergence flag.
For the two-node dry run,`PageRank(damping=.5).fit_transform([[0,1],[0,0]])`
returns values within1e-10 of[0.4,0.6]. Executed output:

```json
{"adjacency": [[0, 1, 1], [0, 0, 1], [0, 0, 0]], "converged": true, "damping": 0.85, "scores": [0.19757965, 0.281551, 0.52086935], "sum": 1.0, "transition": [[0.0, 0.5, 0.5], [0.0, 0.0, 1.0], [0.33333333, 0.33333333, 0.33333333]]}
```

## 16. Edge Cases

A one-node graph ranks its node1,with or without a self-loop. All dangling rows
produce v. Zero damping returns v. Zero entries in v are legal. Disconnected and
isolated nodes do not lose probability mass. A valid exhausted iteration budget
returns an approximation with `converged_=False`; it is not a hidden success.
Damping must be in[0,1); tolerance1e-14..1; iteration budget1..100000.
Personalization must already sum to1 within1e-12; arbitrary weights are rejected.

## 17. Advantages

The stationary equation has an independent small-system oracle. Deterministic
iteration and explicit mass/residual diagnostics make the computation easy to
audit. Personalized and weighted graphs share one explicit probability convention.

## 18. Disadvantages and Limitations

Only dense matrices and sequential integer node indices are accepted. Duplicate
edges must be explicitly aggregated by the caller. No sparse acceleration or
large-graph guarantee is offered. Near1 damping amplifies both convergence cost
and residual-bound roundoff; a small budget need not converge. Importance depends
on graph construction and v,so it need not represent a useful real-world notion.

## 19. When to Use It

Use it for small directed weighted ranking problems where a random-surfer model
and explicit restart distribution express the intended question.

## 20. When Not to Use It

For shortest paths use the existing DSA graph algorithms. For learned vectors or
feature-dependent node classes use the other B9 methods. Million-node networks
need sparse representations and a separately validated numerical implementation.

## 21. Comparison With Related Algorithms

| Method | Output | Learned parameters | Graph contract here |
| --- | --- | --- | --- |
| PageRank | One stationary importance per node | None | Directed/undirected,weighted,self-loops |
| [Node2Vec](../node2vec/README.md) | Node embeddings | Input/context vectors | Undirected,weighted,zero diagonal |
| [GCN](../graph-convolutional-networks/README.md) | Node-class probabilities | Two neural layers | Undirected,weighted,zero input diagonal |

## 22. Interview Questions

1. Why is the transpose required? Rows describe departures; ranks are columns.
2. Why does an isolated node not destroy mass? Its transition row is v.
3. Does symmetry imply equal ranks? Only an appropriate graph/personalization
   symmetry does; unequal weighted degrees alone do not imply equal scores.
4. Is an exhausted budget a convergence proof? No; read the residual and flag.

## 23. Practice Problems

Derive the two-node answer above without iteration. Change v to[1,0] and solve
again. Construct a weighted star and verify equal leaf scores only for equal
leaf weights and symmetric personalization. Build a sparse alternative and
compare operation counts without claiming a measured speedup before execution.

## 24. References

- [The PageRank Citation Ranking: Bringing Order to the Web — original draft,
  29 January1998,university-hosted PDF](https://cs.brown.edu/courses/csci2531/papers/pagerank.pdf).
- [Project graph contracts](../../../docs/graph-learning-conventions.md),
  [independent tests](tests/test_python.py) and [scope](../../../docs/graph-learning-scope.md).

## 25. Author Attribution

Algorithm Atlas is maintained by **[MD.Khalid Hasan](https://github.com/khalidhasan7343)**.
[MIT License](../../../LICENSE); [contribution policy](../../../CONTRIBUTING.md).
The implementation,independent tests and worked derivation are educational
project code; the cited research supplies the underlying method.
