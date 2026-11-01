# GloVe — Global Vectors for Word Representation

## 1. Algorithm Name

**GloVe: Global Vectors for Word Representation.** This implementation trains weighted log-bilinear embeddings of positive corpus co-occurrences; counts or untrained random vectors alone are not GloVe.

## 2. Overview

Aggregate local windows globally, then learn target/context vectors and two bias families explaining positive log-counts. The example demonstrates actual fitting on a tiny corpus, without claiming production embedding quality.

## 3. Problem Statement

Input is a list/tuple of 1–64 independent Unicode strings, at most2048 corpus tokens,128 tokens per text and4096 code points per text. Shared NFC normalization, optional casefold, Unicode word runs and individual punctuation are used consistently. List elements define boundaries; no implicit sentence splitting or truncation. Vocabulary is fit on permitted training data only: count-based pruning with lexical ties, lexical retained IDs and UNK0. Unseen tokens map to UNK; that row is learned when pruning creates training UNK events, otherwise stays zero.

`GloVe(dimension=8, window=2, symmetric=True, x_max=10., alpha=.75, epochs=100, learning_rate=.1, random_state=0, min_count=1, max_size=128, lowercase=True, gradient_clip=5.)` fits and returns self. Diagnostics include the global count matrix, both vector/bias families, history and status. `get_embeddings()` sums target/context vectors; `combine=False` returns target vectors. `embedding(word)` requires one tokenizer token and returns an owned vector.

## 4. Why Do We Need This Algorithm?

Repeated contexts can be aggregated into reusable global statistics. GloVe fits positive matrix cells rather than treating every occurrence as a separate classifier example. Biases absorb broad target/context frequency effects while dot products fit remaining log-count relationships.

## 5. Real-World Applications

Word vectors can provide features for retrieval, similarity and downstream sequence labeling. Representative training corpora and held-out task evaluation are needed. These educational vectors do not replace independently evaluated pretrained representations.

## 6. Core Intuition

For target W[i], context C[j], biases b,c and positive count X[i,j]:

```text
r_ij = W[i] dot C[j] + b[i] + c[j] - log(X[i,j])
f(x) = min((x/x_max)^alpha, 1)
J = sum over X[i,j]>0 of f(X[i,j]) * r_ij^2
delta_ij = 2*f(X[i,j])*r_ij
```

Derivatives are delta*C[j], delta*W[i], and delta for each corresponding bias. Contributions accumulate over shared rows. The objective is the sum, with no undisclosed half/mean factor. Unobserved cells are excluded, never passed through log0. Joint vector fitting is nonconvex; descent does not imply a global optimum.

## 7. Prerequisites

Weighted least squares, logarithms, dot products, the chain rule and corpus count aggregation. Read [B13 text contracts](../../../docs/natural-language-processing-conventions.md) and [Word2Vec](../word2vec/README.md) for the distinct sampled local objective. The fitted vocabulary is shared in convention, not shared mutable state.

## 8. Step-by-Step Working Process

Fit a local vocabulary, then count ordered within-sentence contexts with contribution1/distance. Symmetric mode includes both directions; symmetric=False includes earlier contexts only. Repeated tokens may create diagonal positive cells. Initialize target/context vectors privately and biases at0; unused UNK vectors stay0. Calculate positive-cell loss/all four gradients and apply clipped full-batch descent, at most30 halving backtracks accepting nonincreasing J. Stop on budget, exact stationary gradient or line-search stagnation. Commit fitted state only after successful local computation.

## 9. Pseudocode

```text
vocabulary <- training-only texts
X <- inverse-distance ordered counts, no cross-text windows
W,C <- small seeded random tables; b,c <- zero
repeat at most epochs:
    for each positive cell X[i,j]:
        residual <- W[i] dot C[j]+b[i]+c[j]-log(X[i,j])
        accumulate weighted loss and W,C,b,c gradients
    try at most30 clipped descent steps with halved rate
    accept a nonincreasing objective; otherwise stop
return trained parameters, X, history and honest status
```

## 10. Dry Run

For encoded [0,1,2], window2, symmetric counts are [[0,1,.5],[1,0,1],[.5,1,0]]; distance2 contributes.5. Left-only mode gives [[0,0,0],[1,0,0],[.5,1,0]]. Separate singleton texts contribute no events. With one cell X2, zero parameters and x_max1, J=log(2)^2 and matching target/context bias gradients are -2*log(2), while vector gradients are0. Actual nonzero vector initialization permits vector learning.

## 11. Time Complexity

T is tokens, U raw distinct terms, V mapped vocabulary, w window, d width, M positive cells, E epochs and B≤30 attempts. Vocabulary selection is O(U log U); counts O(Tw); each objective/gradient is O(V²+Md), including dense validation. Training is O(BE(V²+Md)); convergence iterations are data-dependent. The conservative V²*d*E≤20,000,000 work bound applies in addition to B.

## 12. Space Complexity

Dense counts/weights use O(V²), vectors/gradients O(Vd), biases O(V), gathered positive products O(Md), history O(E), and corpus/vocabulary O(T+U). No recursion. V≤128,d≤16,w≤4,E≤200. Public objective inputs require counts0 or finite positive[1e-12,1e6]; generated corpus counts are ordinary inverse-distance sums. Unsupported tiny count regimes fail rather than silently losing their weights.

## 13. Python Implementation

The [solution](python/solution.py) exposes cooccurrence_matrix, weighting, glove_loss_gradients and GloVe. [Tests](tests/test_python.py) use hand matrices, independent scalar objectives/one update and central differences over every coordinate of W,C,b,c. The optimizer is bounded full-batch descent rather than the original large-scale optimizer. Unchanged B7 supplies numerical steps; no complete embedding estimator is used.

## 14. C++ Implementation

C++ is optional for ML and is not implemented here. No placeholder source or C++ test pass is claimed. Existing DSA Python/C++17/C++20 requirements remain mandatory.

## 15. Input and Output Examples

From repository root:

```sh
.venv/bin/python machine-learning/natural-language-processing/glove/python/example.py
.venv/bin/python -m pytest machine-learning/natural-language-processing/glove -q
```

Actual output, rounded only for display:

```json
{"texts": ["red fox runs", "red fox jumps", "blue bird flies", "blue bird sings"], "configuration": {"dimension": 4, "window": 2, "symmetric": true, "x_max": 10.0, "alpha": 0.75, "epochs": 80, "random_state": 21}, "vocabulary": ["<UNK>", "bird", "blue", "flies", "fox", "jumps", "red", "runs", "sings"], "red_fox_count": 2.0, "red_blue_count": 0.0, "loss_initial": 0.993339, "loss_final": 0.003003, "status": "iteration-budget", "red_embedding": [0.2754, 0.0681, -0.0472, 0.2165], "fox_embedding": [0.439, 0.0503, -0.0242, 0.1086], "unknown_embedding": [0.0, 0.0, 0.0, 0.0]}
```

The actual learned parameters and objective decrease demonstrate fitting. They do not establish semantic analogy accuracy.

## 16. Edge Cases

Empty texts may occur but singleton-only/all-empty corpora fail for lack of co-occurrences. Repeated tokens can produce diagonal counts. Zero cells are excluded; X1 has log1=0. Invalid/nonfinite/unsupported subnormal counts, inconsistent parameters/IDs, invalid settings and excessive work fail explicitly. Unknowns use the trained-or-zero UNK rule. Lookup requires one token. Failed refit preserves prior vectors/vocabulary; returned embedding arrays are owned copies.

## 17. Advantages

Global statistics, weighting, two vector families and biases remain auditable. Positive-cell math has exact hand and finite-difference oracles. Private initialization and full-batch steps are reproducible. Training statistics remain separate from query lookup.

## 18. Disadvantages and Limitations

Dense V² storage and strict bounds suit teaching rather than huge corpora. Regex tokenization is not universal linguistic segmentation. Nonconvex solutions are nonunique and vary with seed; low training J does not establish semantic task quality. No pretrained/subword model or calibrated sequence probability is supplied. A zero unknown vector has no semantic knowledge. Fixed budgets report honest status rather than claiming convergence.

## 19. When to Use It

Use to study how aggregated context statistics lead to trained weighted log-count embeddings and inspect every target/context/bias gradient on reproducible small corpora.

## 20. When Not to Use It

Do not expect contextual disambiguation, reliable unseen-word vectors, massive-corpus throughput or production pretrained quality. Use separately evaluated contextual/domain models for those goals; N-Grams answer normalized language-probability questions.

## 21. Comparison With Related Algorithms

| Method | Fitted information |
|---|---|
| Bag of Words / TF-IDF | Document counts / corpus rarity weighting |
| Word2Vec SGNS | Local positive/noise logistic embedding objective |
| GloVe here | Global positive log-count regression and both bias families |
| BERT/GPT | Context-dependent Transformer token objectives |

## 22. Interview Questions

Why exclude zero cells? log0 is undefined and the declared objective uses observed counts. Why two biases? Target/context frequency roles differ. Why accumulate repeated indices? Several cells influence one parameter row. Does low J prove semantic usefulness? No; held-out task evaluation is distinct.

## 23. Practice Problems

Hand-count repeated-token windows and left-only contexts; differentiate W,C,b,c; check finite differences when several cells share a row; vary x_max/alpha without fitting evaluation text; compare training curves across seeds while avoiding coordinate-equality claims.

## 24. References

[Jeffrey Pennington, Richard Socher and Christopher D. Manning, 2014, GloVe: Global Vectors for Word Representation](https://aclanthology.org/D14-1162/), DOI [10.3115/v1/D14-1162](https://doi.org/10.3115/v1/D14-1162). Dense storage, tokenizer, left-only option, bounds and full-batch optimizer are declared conventions. No published benchmark result is attributed to this toy model.

## 25. Author Attribution

Owner and maintainer: **[MD.Khalid Hasan](https://github.com/khalidhasan7343)**. [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas); [MIT license](../../../LICENSE); [contributing](../../../CONTRIBUTING.md).
