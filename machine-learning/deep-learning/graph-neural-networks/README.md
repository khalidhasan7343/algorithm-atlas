# Graph Neural Network — normalized two-layer GCN regressor

## 1. Algorithm Name

Graph Neural Network — normalized two-layer GCN regressor

## 2. Overview

Aggregate neighboring features with normalized graph weights before learned transforms; share parameters over nodes so node permutations commute with prediction.

## 3. Problem Statement

Fit node features X=(N,p),2<=N<=32,p<=16; y=(N,1). Adjacency A=(N,N) finite,nonnegative,symmetric within1e-12 and zero diagonal. self_loops strict bool controls added I; query graphs may have1..32 nodes with fitted p. Full-graph training only, no batch_size option.

Trainable shapes: W1(p,h),b1(h),W2(h,1),b2(1). The N×N normalized adjacency is fixed data, not a parameter.

## 4. Why Do We Need This Algorithm?

Node features alone omit graph relationships. Normalized neighborhood aggregation mixes each node with its neighbors before learned transformations. Relabeling nodes should only relabel predictions, making permutation equivariance an independently testable property.

## 5. Real-World Applications

Scalar node regression on tiny undirected weighted graphs, including isolates. Larger GNNs support relational tasks, but this model uses one dense two-layer normalized GCN, not attention-based messages, edge prediction or graph-level pooling.

## 6. Core Intuition

Aggregate neighboring features with normalized graph weights before learned transforms; share parameters over nodes so node permutations commute with prediction.

Atilde=A+I if self_loops else A; S=D^-1/2 Atilde D^-1/2,with zero inverse degree for isolated nodes. H=tanh(S X W1+b1),R=S H W2+b2,L=mean((R-y)²). Biases are shared over nodes. Input graph weights are fixed,not optimized.

## 7. Prerequisites

Matrix shapes, derivatives/chain rule, floating-point arithmetic and the declared learning objective. Read [B7 contracts](../../../docs/neural-networks-and-deep-learning-conventions.md) and [scope](../../../docs/neural-networks-and-deep-learning-scope.md).

## 8. Step-by-Step Working Process

D=2(R-y)/N,dW2=(S H).T D,db2=sum D. Hidden preactivation adjoint=(S.T D W2.T)*(1-H²); dW1=(S X).T dH,db1=sum dH. Full-graph SGD preserves node ordering rather than shuffling/splitting rows away from their neighbors.

Copy/validate inputs, initialize locally, run bounded CPU gradient updates, and install fitted state only after a finite completed run. Mini-batches are shuffled with a local RNG except full-graph GNN. Defaults epochs100,learning_rate0.1,batch_size16,gradient_clip5 where supported; model-specific architecture controls are stated above. At most10000 updates,20000 parameter values and the common array limits apply. Histories are pre-update minibatch averages; fixed-budget status explicitly does not certify convergence.

## 9. Pseudocode

```text
validate symmetric nonnegative zero-diagonal adjacency A and node features X
add identity when self_loops=True; compute row degree d
set inverse sqrt degree to0 for isolates; S=D^(-1/2)@A_aug@D^(-1/2)
initialize two feature projections and biases
repeat fixed full-graph epochs:
  H=tanh(S@X@W1+b1); R=S@H@W2+b2
  D=2*(R-y)/node_count; accumulate W2,b2 adjoints
  G=(S.T@D@W2.T)*(1-H*H)
  accumulate W1,b1 adjoints through S@X
  clip parameter gradients and take one full-graph SGD step
predict with the new graph's independently validated normalization
```

## 10. Dry Run

For A linking nodes0–1 and isolated node2, adding self-loops yields S=[[0.5,0.5,0],[0.5,0.5,0],[0,0,1]]. With scalar W1=W2=1,bias0, output=S*tanh(S*X). Without loops the isolate row is zero; trained output bias can still supply its baseline. Tests verify node-permutation equivariance and all trainable gradients. The executable example below runs fixed-seed training and emits the actual learned outputs and first/final losses; they are recorded in Phase19 evidence rather than invented.

## 11. Time Complexity

For dense N-node graph,p features,h hidden, fit O(E*(N²*p+N*p*h+N²*h)); normalization O(N²). This bounded dense implementation does not claim sparse O(edges) performance.

## 12. Space Complexity

O(N²+N*(p+h)+p*h) graph/states/parameters. No graph traversal substitutes for neural aggregation, recursion or neighborhood sampler.

## 13. Python Implementation

[GCNRegressor source](python/solution.py) contains the actual architecture and analytic gradients. [Example](python/example.py); [tests](tests/test_python.py). Core imports NumPy/stdlib/local primitives only, never a framework estimator. Loss/forward/backward functions take explicit parameter arrays so independent finite differences can freeze all stochastic inputs. Tests independently check this model’s forward equations/objective, every weight and bias by central finite differences with fixed stochastic inputs, controlled training and repeated seeded outputs. Common tests add invalid rank/domain/shape/limits, constant/duplicate rows, global RNG/input copies, finite-state detection and atomic failed refits.

## 14. C++ Implementation

C++ is optional and absent under the Phase19 ML policy. No placeholder source/test. DSA still requires actual Python/C++17/C++20 tests.

## 15. Input and Output Examples

Run the fixed-seed example from the repository root:

```sh
python machine-learning/deep-learning/graph-neural-networks/python/example.py
```

The equivalent JSON input to `python/solution.py` is:

```json
{"X":[[1,0],[0,1],[1,1],[0.5,0.2]],"y":[[1],[1],[2],[0.7]],"adjacency":[[0,1,0,0],[1,0,1,0],[0,1,0,0],[0,0,0,0]],"parameters":{"hidden_dim":3,"epochs":100}}
```

Observed output in this phase's [executed example records](../../../docs/neural-networks-and-deep-learning-evidence/examples-results.json):

```json
{"loss_initial":2.321356563571144,"loss_final":0.12605095314837006,"optimization_status":"fixed-budget-completed","prediction":[[1.120533558235357],[1.397483985016623],[1.426129052922147],[0.6838637467975222]]}
```

Floating-point last digits may vary across numerical environments. Losses describe the actual small training run and its declared reduction; fixed-budget completion does not establish convergence or generalization.

## 16. Edge Cases

The architecture sizes and loss-normalization axes above are part of the API, not inferred by broadcasting. Fitted tensor trailing dimensions must match at inference; unsupported sequence/image/graph forms fail explicitly. Two-layer undirected weighted normalized GCN with scalar node regression; no directed graphs,input self-loops,edge features,attention,trainable adjacency,graph pooling,mini-batch graph collections or GNN architecture zoo. Other graph-learning canonicals remain distinct/planned. Isolate behavior depends on self_loops and biases.

Inputs copy caller arrays and use local default_rng. Reject nonfinite/nonreal arrays, bool data, invalid dimensions/learning rates/batches/seeds, excess compute budgets and inference before fit. Fit commits state only after a complete finite run; invalid/failed refits preserve a prior successful model.

## 17. Advantages

The specific Graph Neural Network — normalized two-layer GCN regressor forward and reverse equations are visible in a compact NumPy implementation; independent mathematical invariants and per-entry gradients make the mechanism inspectable.

## 18. Disadvantages and Limitations

Two-layer undirected weighted normalized GCN with scalar node regression; no directed graphs,input self-loops,edge features,attention,trainable adjacency,graph pooling,mini-batch graph collections or GNN architecture zoo. Other graph-learning canonicals remain distinct/planned. Isolate behavior depends on self_loops and biases.

## 19. When to Use It

Use for learning and validating the stated Graph Neural Network — normalized two-layer GCN regressor mechanism on a small controlled CPU dataset.

## 20. When Not to Use It

Use a validated production architecture for large-scale workloads or features excluded by this contract. A short synthetic fit does not establish generalization or generative quality.

## 21. Comparison With Related Algorithms

| Method | Dependence on graph |
| --- | --- |
| This GCN | Two trainable normalized neighborhood aggregations |
| Plain MLP | No adjacency-based messages |
| Graph traversal | Visits topology but does not optimize neural parameters/loss |

## 22. Interview Questions

Why must nodes permute in A and X together? Their row/column identities encode the same graph. Why symmetric normalization? It balances weighted message scale by endpoint degrees. Unlike an ordinary MLP, each output depends on graph-aggregated features and two message passes.

## 23. Practice Problems

Compute S by hand for a two-node edge with self-loops. Explain why a zero-degree node has an all-zero aggregation row when loops are disabled. Permute adjacency, features and targets together and compare the correspondingly permuted fitted predictions.

## 24. References

[Kipf and Welling, Semi-Supervised Classification with Graph Convolutional Networks](https://arxiv.org/abs/1609.02907). This lesson uses their normalized message form with an explicitly different scalar MSE task.

## 25. Author Attribution

**MD.Khalid Hasan**, [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../LICENSE); [contribution policy](../../../CONTRIBUTING.md). New Phase19 B7 owner review pending.
