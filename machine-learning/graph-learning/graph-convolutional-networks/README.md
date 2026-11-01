# Graph Convolutional Networks

## 1. Algorithm Name

Graph Convolutional Networks (GCN): a two-layer,normalized,tanh graph-convolution
classifier with masked node-label loss. Canonical ID `graph-convolutional-networks`,
B9. The distinct B7 `graph-neural-networks` canonical remains unchanged.

## 2. Overview

Every layer aggregates neighbor features through the graph before applying shared
trainable weights. A second propagation yields class logits per node. Labels may
be known for only a subset; unlabeled node features still participate in graph
propagation. This is not an MLP that ignores adjacency.

## 3. Problem Statement

Input: a symmetric nonnegative weighted n-by-n adjacency with zero diagonal,
features X of shape(n,f),integer labels0..C-1 with -1 for unknowns,and an optional
boolean training mask. Output: n-by-C probabilities and n class predictions.
Bounds:n1..32,f1..16,hidden width1..16,C2..8. Selected training labels must include
all C consecutive classes. See [shared contracts](../../../docs/graph-learning-conventions.md).

## 4. Why Do We Need This Algorithm?

A node's own attributes can be ambiguous; its neighborhood may add useful signal.
Graph-aware shared layers allow a supervised objective to shape that propagation.
A graph is an assumption about useful relationships,not a guarantee that neighbor
aggregation improves prediction.

## 5. Real-World Applications

Small semi-supervised document/social-network node classification exercises and
studying feature propagation are suitable examples. No citation-network dataset,
external weights or GPU is required. The included synthetic graph is an executed
teaching example,not a benchmark or evidence of universal accuracy.

## 6. Core Intuition

Form A_tilde=A+I when self_loops=True; otherwise retain A. Let D contain its
row sums. S=D^(-1/2) A_tilde D^(-1/2),using zero inverse degree for an isolated
node without loops. S is symmetric normalization,not the row-stochastic matrix P
used by PageRank. Two tanh/message-passing layers mix at most two-hop information.

## 7. Prerequisites

Matrix products,degree normalization,tanh,softmax,cross-entropy and chain-rule
backpropagation. Read [B7 GNN](../../deep-learning/graph-neural-networks/README.md)
for the preserved scalar regression counterpart. Its compatible normalization
utility is reused; no approved B7 code,tests or lesson is rewritten.

## 8. Step-by-Step Working Process

Validate/copy A,X,y and the training mask. Add identity exactly once when requested;
reject a pre-existing diagonal instead of duplicating loops. Initialize W1,b1,W2,b2
with a local seeded Generator. Compute

B=S X; H=tanh(B W1+b1); T=S H; Z=T W2+b2; Q=row_softmax(Z).

For m selected nodes,minimize mean masked cross-entropy plus
(l2/2)(||W1||_F²+||W2||_F²). Biases are unpenalized. No held-out label enters loss.
Let Δ=(Q-one_hot(y))/m on selected rows and0 elsewhere. Then

dW2=T.T Δ+l2 W2; db2=sum_rows Δ;
δ1=(S.T(Δ W2.T))*(1-H²);
dW1=B.T δ1+l2 W1; db1=sum_rows δ1.

All graph paths are differentiated through S.T. Update all blocks with one global
norm clip,then recompute the fixed objective. Epoch exhaustion is reported openly.
The hidden tanh,biases,mean loss and clipped full-batch SGD are declared educational
choices; the cited paper's illustrative ReLU/dropout/optimizer setup is not copied
or claimed as an exact architecture/benchmark reproduction.

## 9. Pseudocode

```text
validate undirected zero-diagonal graph,features,known labels and mask
S = normalized adjacency with the declared self-loop convention
initialize two shared parameter layers from local RNG
repeat epochs times:
    propagate features,apply tanh,propagate hidden values,produce logits
    compute stable masked cross-entropy and optional weight L2
    backpropagate output and hidden graph messages
    clip global gradient norm and update parameters
predict by row-softmax and argmax on logits
```

## 10. Dry Run

Take nodes0–1 connected and node2 isolated,with self-loops and X=[[1],[3],[5]].
S has a2-by-2 block filled with1/2 and S[2,2]=1. With W1=1,b1=0,
W2=[1,-1],b2=[0,0],hidden values are[tanh2,tanh2,tanh5]. The first two logits
are[tanh2,-tanh2]; class0 probability is1/(1+exp(-2tanh2)). Its class0 loss is
log(1+exp(-2tanh2)). An independent scalar oracle checks these quantities.

## 11. Time Complexity

For n nodes,f features,h hidden units,c classes,E epochs,normalization costs
O(n²). Each dense forward/backward step costs
O(n²(f+h)+nfh+nhc+fh+hc). Multiply by E for training; inference has one
normalization/forward pass. This implementation recomputes S X during steps.
Epoch count is fixed; there is no data-independent convergence-time claim or
sparse O(m) promise. Sparse message passing could use edge-count-dependent costs
but is outside this bounded dense implementation.

## 12. Space Complexity

O(n²+n(f+h+c)+fh+hc+E) for adjacency/normalization,activations,probabilities and
parameter/gradient blocks. Mask/labels add O(n). Input arrays are copied,there is
no recursion,and parameter/feature widths are checked before training.

The retained loss_history_ includes E+1 objective values,so its O(E) output storage is counted explicitly.

## 13. Python Implementation

[Source](python/solution.py) exports `GCNClassifier`,`normalize_adjacency`,
`initialize`,`forward` and `loss_gradients`. `fit(A,X,y,train_mask=None)` returns
self; `predict_proba(A,X)` returns float64 probabilities and `predict(A,X)` returns
integer class IDs. Helpers accept an explicitly supplied propagation matrix for
mathematical inspection; the estimator always derives S from validated raw A.
Defaults:hidden4,epochs200,learning_rate.1,seed0,self_loops=True,l2=0,clip5.
Inspect `parameters_`,`classes_`,`normalized_adjacency_`,`train_mask_`,
`loss_history_`,`n_updates_` and `optimization_status_`. `converged_` is False
for this fixed-epoch optimizer. Failed refits retain prior fitted state;
predict-before-fit raises ValueError. Inference uses the fitted loop convention.

## 14. C++ Implementation

C++ is optional for ML and absent,with no dummy files. DSA continues to require
Python,C++17 and C++20 implementations and executed tests.

## 15. Input and Output Examples

Run the [semi-supervised example](python/example.py) from repository root:

```sh
.venv/bin/python machine-learning/graph-learning/graph-convolutional-networks/python/example.py
```

Only nodes0 and3 carry training labels. The script prints S,a propagated feature,
initial/final objective,predictions and update count. Exact executed output:

```json
{"first_propagated_feature": [0.928997, 0.099458], "loss_final": 0.00817123, "loss_initial": 0.63393832, "normalized_adjacency": [[0.333333, 0.333333, 0.327913, 0.0, 0.0, 0.0], [0.333333, 0.333333, 0.327913, 0.0, 0.0, 0.0], [0.327913, 0.327913, 0.322581, 0.032258, 0.0, 0.0], [0.0, 0.0, 0.032258, 0.322581, 0.327913, 0.327913], [0.0, 0.0, 0.0, 0.327913, 0.333333, 0.333333], [0.0, 0.0, 0.0, 0.327913, 0.333333, 0.333333]], "predictions": [0, 0, 0, 1, 1, 1], "updates": 200}
```

This example's four unknown labels are not used in training. Their predicted
pattern is an observation on the synthetic data,not a generalization guarantee.

## 16. Edge Cases

Isolated nodes use their own features with loops; without loops,their propagated
row is zero. Disconnected components do not exchange messages. Directed graphs,
nonzero input diagonals,nonfinite/oversized features,invalid masks and unknown
selected labels are rejected. C classes must be consecutive0..C-1 and represented
in the training mask; single-class fitting is outside scope. Width mismatches and
prediction before fitting fail clearly. Epochs1..2000,learning_rate1e-6..1,
l2 in[0,1000],clip1e-6..1000 and a bounded integer seed are required.

## 17. Advantages

Each graph/gradient operation is visible and independently testable. Masked loss
supports semi-supervised experiments without hidden label use. Shared normalization
preserves B7 compatibility without conflating the two canonical lessons.

## 18. Disadvantages and Limitations

Dense small-graph computation,full-batch SGD,no dropout and tanh saturation limit
scope. Poor graph homophily,over-smoothing,conditioning or optimizer choices can
harm predictions. Clipping prevents oversized steps but does not establish
convergence. Features/labels on arbitrary real graphs need separate evaluation.
No pretrained model,large dataset,production framework or sparse-graph parity is
claimed. Floating-point equivariance holds within justified tolerances.

## 19. When to Use It

Use it to study a small undirected node-classification problem with attributes,
known training labels and a defensible graph-neighborhood assumption.

## 20. When Not to Use It

Use PageRank for stationary importance,Node2Vec for an unsupervised walk embedding,
or B7 GNN for its specified node-regression exercise. Directed graphs,large sparse
networks and tasks requiring a different propagation rule need explicit new scope.

## 21. Comparison With Related Algorithms

| Method | Supervision/output | Role of graph |
| --- | --- | --- |
| B9 GCN | Masked node classes/softmax | Two normalized feature/message propagations |
| B7 GNN | Scalar node regression | Preserved tanh normalized regressor |
| Node2Vec | Unsupervised node vectors | Biased walks and context objective |
| Ordinary MLP | Feature-only predictions | Does not consume adjacency |

Node outputs are permutation-equivariant. For permutation Π,S'=Π S Π.T and
X'=Π X imply f(A',X')=Π f(A,X),because shared row-wise affine/activation/softmax
operations commute with node reordering. They are not permutation-invariant.
Labels and masks must also be permuted when comparing training objectives.

## 22. Interview Questions

Why add self-loops? They preserve own-node contributions. Why not row-normalize
and call it the same model? It changes the propagation rule. Why apply S.T in
backpropagation? It is the adjoint of message aggregation. Why ignore unselected
labels? The objective is defined only on the training subset. Does a lower
training loss prove held-out performance? No.

## 23. Practice Problems

Derive S for a weighted path and an isolated node,with and without loops.
Manually differentiate the dry-run softmax loss. Permute A,X,y and mask together
and verify output equivariance. Compare graph-aware logits with S=I. Add a
held-out split and report all seeds before making performance claims.

## 24. References

- Kipf and Welling,[Semi-Supervised Classification with Graph Convolutional
  Networks,ICLR2017; preprint2016](https://arxiv.org/abs/1609.02907).
- Kipf,[Graph Convolutional Networks — author explanation,2016](https://tkipf.github.io/graph-convolutional-networks/).
- [Independent tests](tests/test_python.py),[contracts](../../../docs/graph-learning-conventions.md),
  [preserved normalization source](../../deep-learning/graph-neural-networks/python/solution.py).

## 25. Author Attribution

Algorithm Atlas is maintained by **[MD.Khalid Hasan](https://github.com/khalidhasan7343)**.
[MIT License](../../../LICENSE); [contribution policy](../../../CONTRIBUTING.md).
B7 and B9 retain distinct canonical identities; compatible project code is reused
with its attribution/license preserved.
