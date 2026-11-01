# Node2Vec

## 1. Algorithm Name

Node2Vec: weighted undirected second-order graph walks followed by Skip-Gram with
Negative Sampling (SGNS). Canonical ID `node2vec`,owned by B9.

## 2. Overview

Walks turn graph neighborhoods into sequences. A context window yields training
pairs; input/context vectors learn to discriminate observed pairs from sampled
noise. The output is a learned vector per existing node,not an untrained random
initialization and not a spectral decomposition.

## 3. Problem Statement

Input is an exactly symmetric,nonnegative weighted adjacency matrix with1..32
nodes and zero diagonal. Node IDs are row indices. Output has shape(n,dimensions).
An isolated node is retained but has no training signal. A graph/corpus with no
positive pairs cannot train. Directed graphs and pre-existing self-loops are
rejected; no directed-distance convention is guessed. Read [contracts](../../../docs/graph-learning-conventions.md).

## 4. Why Do We Need This Algorithm?

A graph's useful relationships need not fit one hand-written scalar centrality.
Adjustable walk biases collect different neighborhoods; vectors provide compact
features for a separately evaluated downstream task. Utility depends on the graph,
corpus,objective and training budget.

## 5. Real-World Applications

Exploratory node representations,small network visualization features and link
prediction experiments are suitable educational applications. Report downstream
held-out metrics before claiming predictive value. This dense implementation is
not a large-network service or a reproduction of published benchmark results.

## 6. Core Intuition

After t→v,a candidate x receives edge weight w(v,x) times1/p for a return to t,
1 for a neighbor of t,or1/q for a two-hop node. Normalize only over neighbors of v.
The first step uses weights alone. The learned vectors must then change under
the SGNS objective; walks or random coordinates alone are not Node2Vec training.

## 7. Prerequisites

[Graph traversal](../../../dsa/graph-algorithms/breadth-first-search/README.md),
probability,local random generators,dot products and gradients. Compare
[PageRank](../pagerank/README.md) for stationary ranking and
[GCN](../graph-convolutional-networks/README.md) for feature-dependent classification.

## 8. Step-by-Step Working Process

Generate num_walks shuffled passes over all nodes. Each walk ends at its length
limit or at an isolated node. Turn each positional window into ordered pairs;
revisited IDs may legitimately produce a target/context self-pair.

Let u_i be an input vector and v_j a context vector. For a positive pair(i,j)
and fixed negative IDs z₁..zₖ,minimize

L = mean_pairs[softplus(-u_i·v_j) + sum_a softplus(u_i·v_za)].

For s=u_i·v_j,the positive derivative is sigmoid(s)-1; for a negative dot product
the derivative is sigmoid(s). Multiply by the opposite embedding,divide by the
positive-pair count and accumulate every repeated ID. `np.add.at` preserves
collisions,including repeated negatives and noise IDs equal to a positive ID.

Noise probabilities are proportional to positive-context counts^0.75. Draw noise
with replacement once per fit; optimize that fixed sampled objective by clipped
full-batch gradient descent. This is an explicit small educational variant of the
stochastic training procedure,not a claim of production implementation parity.

## 9. Pseudocode

```text
validate undirected zero-diagonal weighted adjacency and bounded settings
for each shuffled node pass:
    build each bounded walk using first-step weights then p/q biases
construct ordered window pairs; reject an empty training corpus
initialize input and context vectors with a local seeded Generator
sample fixed negatives from context-frequency^0.75
repeat epochs times:
    compute stable SGNS loss and all input/context gradients
    clip the global gradient norm and update both parameter tables
return learned input vectors and objective history
```

## 10. Dry Run

Suppose t=0,v=1,with w(1,0)=2,w(1,2)=3,w(1,3)=4 and edge0–2 present.
For p=.5,q=2,the biased weights are[4,3,2],so probabilities at IDs0,2,3
are[4/9,3/9,2/9]. First-step probabilities would instead be[2/9,3/9,4/9].
For walk[0,1,2] and window1,the pairs are(0,1),(1,0),(1,2),(2,1).

For a one-dimensional SGNS example,u₀=1,v₀=v₁=0,positive(0,1),negative0:
loss=2log2,dv₀=1/2,dv₁=-1/2,du₀=0. An unclipped step of size.1 makes
v₀=-.05,v₁=.05 and lowers this sampled objective. The tests check this by hand
and independently perturb every parameter on a corpus with index collisions.

## 11. Time Complexity

Let n be nodes,r passes,L maximum walk length,w window width,d embedding width,
k negatives,M actual positive pairs and E epochs. Dense transition construction
and sampling cost O(r n L n); M<=2w r n L. Pair construction costs O(M).
Training costs O(E[M(k+1)d+nd]),including gradient accumulation/table updates;
noise sampling adds bounded categorical sampling work. No alias tables are used.
Fixed epochs give no convergence-time guarantee. Sparse adjacency or cached
second-order tables would change these bounds and their memory tradeoffs.

## 12. Space Complexity

O(n²+r n L+M(k+1)d+nd+E),including dense adjacency,walks,pairs,negative indices and
advanced-indexing/gradient intermediates. No recursion. Before allocation,fit
requires the conservative pair upper bound<=20000 and upper_bound*E*(k+1)*d<=20million.
The bound can reject a graph whose realized short walks would have used less work.

The retained loss_history_ includes E+1 objective values,so its O(E) output storage is counted explicitly.

## 13. Python Implementation

[Source](python/solution.py) exports `Node2Vec`,`context_pairs` and
`sgns_loss_gradients`. Defaults: dimensions4,walk_length8,num_walks4,p=q=1,
window_size2,negative_samples3,epochs100,learning_rate.5,random_state0,clip5.
`fit(A)` returns self; `fit_transform(A)` and `transform(nodes=None)` return copies.
Transforms only address fitted node IDs; an empty selection returns shape(0,d).
Inspect `walks_`,`positive_pairs_`,`negative_indices_`,`noise_distribution_`,
`embeddings_`,`context_embeddings_`,`initial_embeddings_`,`loss_history_` and
`n_updates_`. `converged_` remains False and status is epoch-budget; improvement
on one fixed corpus is not proof of a global optimum. Failed refits retain old state.

## 14. C++ Implementation

C++ is optional for ML and absent. There are no fake source/test stubs. The DSA
Python/C++17/C++20 requirements remain unchanged.

## 15. Input and Output Examples

Run the [two-community example](python/example.py) from the repository root:

```sh
.venv/bin/python machine-learning/graph-learning/node2vec/python/example.py
```

It uses a weak bridge,p=.5,q=2,d=4,100 epochs,seed21. It prints actual walks,pairs,
objective values and cosine similarities. Executed output:

```json
{"cosine_0_1": 0.99854875, "cosine_0_4": 0.1862712, "loss_final": 1.78973212, "loss_initial": 2.77789917, "pairs": [[0, 1], [0, 0], [1, 0], [1, 0], [1, 2], [0, 0]], "shape": [6, 4], "updates": 100, "walks": [[0, 1, 0, 2, 0, 1, 2, 1], [1, 0, 2, 3, 2, 3, 5, 3]]}
```

A similarity observation on this graph/seed is
not a statistical performance claim or a guarantee of community separation.

## 16. Edge Cases

Isolated walks contain one node and yield no pairs. All-isolated graphs and
walk_length1 cannot fit. Cycles/revisits may repeat target/context/negative IDs.
Weights are rescaled per transition before biasing to protect tiny common scales.
Hyperparameters reject bool/nonfinite/out-of-range values. p,q1e-3..1e3,d1..16,
walk length1..64,passes1..20,window1..8,negatives1..8,epochs1..500; learning
rate1e-6..1,clip1e-6..1000 and a bounded integer seed. Exceeding prospective
pair/operation budgets raises before corpus generation. See the shared contract.

## 17. Advantages

Exact transition probabilities are auditable without sampling-frequency guesses.
The fixed sampled objective permits direct loss checks and finite differences.
Local RNGs and bounded corpora make small demonstrations reproducible.

## 18. Disadvantages and Limitations

Only small weighted undirected matrices are supported. No alias precomputation,
large-network performance,inductive new-node transform or universal embedding
quality is claimed. Fixed sampled negatives can overfit this finite objective;
isolated vectors remain random initial values. Embeddings are not uniquely
identified: rotations and other equivalent parameter transformations can preserve
objectives,so independent implementations need not return identical coordinates.

## 19. When to Use It

Use it when graph-neighborhood features are useful and a small,explicit walk/
noise/training experiment can be evaluated on its intended downstream task.

## 20. When Not to Use It

Use PageRank for a scalar random-surfer score. Use GCN when node attributes and
supervised labels should directly train message-passing parameters. Huge graphs,
directed walks or production inference require separately specified implementations.

## 21. Comparison With Related Algorithms

| Method | Representation | Objective/verification |
| --- | --- | --- |
| Node2Vec | Learned node vectors | Biased walks plus SGNS |
| Unbiased walk | A sequence only | p=q=1 removes second-order bias; not embedding training |
| PageRank | Scalar ranks | Stationary-distribution residual |
| GCN | Feature-conditioned class probabilities | Masked supervised loss and message gradients |

## 22. Interview Questions

Why is the first step different? It has no previous node. Why may a negative ID
equal the positive ID? Noise is sampled unconditionally with replacement.
Why accumulate repeated indices? A batch may use one vector many times.
Why not compare embeddings by exact coordinates? The representation is not unique.

## 23. Practice Problems

Compute the weighted bias dry run for p=q=1,p=.25 and q=.25. Verify pair counts
at window boundaries. Repeat the example across multiple seeds and report every
objective/similarity outcome. Design a held-out link-prediction split without
leaking withheld links into training walks; do not infer its outcome from training loss.

## 24. References

- Grover and Leskovec,[node2vec: Scalable Feature Learning for Networks,
  KDD2016](https://arxiv.org/abs/1607.00653),[author project](https://snap.stanford.edu/node2vec/).
- Mikolov et al.,[Distributed Representations of Words and Phrases and their
  Compositionality,2013](https://arxiv.org/abs/1310.4546).
- [Independent tests](tests/test_python.py),[contracts](../../../docs/graph-learning-conventions.md).

## 25. Author Attribution

Algorithm Atlas is maintained by **[MD.Khalid Hasan](https://github.com/khalidhasan7343)**.
[MIT License](../../../LICENSE); [contribution policy](../../../CONTRIBUTING.md).
The sampled-objective training variant and its resource limits are explicitly
project choices; published benchmark results are not claimed here.
