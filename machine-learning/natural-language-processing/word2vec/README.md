# Word2Vec — Skip-Gram with Negative Sampling

## 1. Algorithm Name

Word2Vec, implemented as **Skip-Gram with Negative Sampling (SGNS)**. This is genuine trainable local-context embedding learning, not CBOW, hierarchical softmax, SVD or pretrained vectors.

## 2. Overview

Learn separate input and output vector tables by distinguishing observed center/context pairs from noise pairs. Actual gradient updates optimize the declared objective. The tiny example establishes training behavior, not production semantic quality.

## 3. Problem Statement

Input is a list/tuple of 1–64 independent Unicode strings, at most2048 corpus tokens,128 tokens per text and4096 code points per text. Shared NFC normalization, optional casefold, Unicode word runs and individual punctuation are used consistently. List elements define boundaries; no implicit sentence splitting or truncation. Vocabulary is fit on permitted training data only: count-based pruning with lexical ties, lexical retained IDs and UNK0. Unseen tokens map to UNK; that row is learned when pruning creates training UNK events, otherwise stays zero.

`Word2Vec(dimension=8, window=2, negative_samples=5, epochs=100, learning_rate=.3, random_state=0, min_count=1, max_size=128, lowercase=True, gradient_clip=5.)` returns self from fit. Output diagnostics include trained input/output matrices, actual pairs/noise samples, loss history and status. `get_embeddings()` returns input vectors; `combine=True` sums both families. `embedding(word)` requires exactly one tokenizer token and returns an owned vector.

## 4. Why Do We Need This Algorithm?

Bag of Words gives unrelated coordinates to tokens. SGNS instead learns compact vectors from repeated local prediction relationships. Its inspectable dot products and noise model make it useful for studying learned representations. A reduced training objective does not prove useful semantic analogies.

## 5. Real-World Applications

Word embeddings can supply features for similarity search, clustering and downstream language tasks when learned on appropriate representative data. These bounded examples teach the mechanism; independent held-out task evaluation is needed before relying on the representations.

## 6. Core Intuition

For center input v_w, positive context output u_c and K negatives n_k, minimize the mean over M observed pairs:

```text
L = (1/M) sum_pairs [softplus(-u_c dot v_w)
                     + sum_k softplus(u_nk dot v_w)]
q(t) = mapped_training_count(t)^(3/4) / sum mapped_count^(3/4)
```

Noise draws are iid with replacement; repeated IDs and positive-context collisions are allowed. One table is sampled and fixed per fit, defining a finite Monte Carlo SGNS objective, rather than claiming exact expected-noise optimization. The positive derivative is sigmoid(z)-1, each noise derivative sigmoid(z), divided by M. Every repeated input/output index contributes to an accumulated gradient.

## 7. Prerequisites

Dot products, binary logistic loss, the chain rule, random sampling and vocabulary indexing. Read [Bag of Words](../bag-of-words/README.md) and [B13 text contracts](../../../docs/natural-language-processing-conventions.md). The count^0.75 law uses mapped training counts, including UNK only when it actually occurred after pruning.

## 8. Step-by-Step Working Process

Validate settings/corpus, build a local vocabulary, enumerate symmetric fixed-window pairs within each sentence, and sample fixed noise with a private generator. Initialize both tables with small nonzero values; unused UNK rows are zero. Compute stable loss and analytic gradients, apply a global-norm-clipped full-batch step, and backtrack at most30 times until loss does not increase. Stop on the epoch budget, exactly stationary gradient or line-search stagnation. Commit model state only after successful local fitting. The iteration budget is not convergence.

## 9. Pseudocode

```text
vocabulary <- permitted training texts
pairs <- every center/context event within the fixed window
noise <- iid count^(3/4) replacement draws, fixed for this fit
W_in, W_out <- small seeded random tables
repeat at most epochs:
    loss, gradients <- positive and noise logistic terms
    scatter-add repeated row contributions
    try at most30 clipped descent steps, halving learning rate
    accept a nonincreasing objective; otherwise stop
return trained tables, actual samples, history and status
```

## 10. Dry Run

For `['a b a']`, window1, known IDs a1,b2 give pairs `(1,2),(2,1),(2,1),(1,2)`. Repeated occurrences remain distinct events. Mapped counts a2,b1 give noise weights `2^(3/4)` and1, with zero unused-UNK mass. At zero logits and K2, loss is `3*log(2)` per pair. Actual training uses nonzero initialization so both tables can learn. The independent duplicate-index test uses center vector1, zero output vectors and two identical noise IDs; its exact mean output gradient is+.5, requiring accumulated contributions.

## 11. Time Complexity

T is total tokens, U distinct raw terms, V mapped vocabulary, w window, P positive pairs, K negatives, d width, E epochs and B≤30 backtracking attempts. Token counting is O(T), vocabulary selection O(U log U), pairs O(Tw), noise O(PK), and training O(BEP(K+1)d), with P≤2wT. Early stationary termination can be cheaper; average convergence iterations are data-dependent. No faster worst-case guarantee is claimed.

## 12. Space Complexity

Vectors/gradients take O(Vd), pairs O(P), noise IDs O(PK), gathered noise vectors O(PKd), and history O(E). Corpus/vocabulary use O(T+U); no recursion. V≤128,d≤16,w≤4,K≤8,E≤200. Fits reject P*(K+1)*d*E>20,000,000; the separately bounded backtracking factor B is explicit.

## 13. Python Implementation

The [solution](python/solution.py) exposes context_pairs, noise_distribution, sample_negatives, sgns_loss_gradients and Word2Vec. [Independent tests](tests/test_python.py) hand-calculate loss/one update and central differences for every coordinate in both trainable tables. Unchanged B7 owns the stable sigmoid and clipped numerical step; SGNS mathematics remain local. No complete embedding library is called.

## 14. C++ Implementation

C++ is optional for ML and is not implemented here. No placeholder source or C++ test pass is claimed. Existing DSA Python/C++17/C++20 requirements remain mandatory.

## 15. Input and Output Examples

From repository root:

```sh
.venv/bin/python machine-learning/natural-language-processing/word2vec/python/example.py
.venv/bin/python -m pytest machine-learning/natural-language-processing/word2vec -q
```

Actual output, rounded only for display:

```json
{"texts": ["red fox runs", "red fox jumps", "blue bird flies", "blue bird sings"], "configuration": {"dimension": 4, "window": 2, "negative_samples": 3, "epochs": 80, "random_state": 21}, "vocabulary": ["<UNK>", "bird", "blue", "flies", "fox", "jumps", "red", "runs", "sings"], "pairs": 24, "loss_initial": 2.769128, "loss_final": 2.144723, "status": "iteration-budget", "red_embedding": [0.1941, 0.3151, 0.5679, 0.9533], "fox_embedding": [0.7267, 0.9511, -0.0381, 0.918], "unknown_embedding": [0.0, 0.0, 0.0, 0.0]}
```

The actual learned parameters and objective decrease demonstrate fitting. They do not establish semantic analogy accuracy.

## 16. Edge Cases

Empty documents are permitted within a corpus but at least one text must contain two tokens. Separate singleton texts never become context pairs. Repeats, noise collisions, Unicode, punctuation and one-symbol mapped vocabularies are valid. Empty/all-singleton training, invalid IDs/shapes/counts/settings, nonfinite parameters and excessive work fail. Lookup of zero/multiple tokens fails. Unknown rows follow the declared trained-or-zero rule. Failed refit preserves prior learned state; returned vector mutation does not change the model.

## 17. Advantages

Positive/noise terms, both tables and actual samples are inspectable. Fixed samples make loss comparisons and finite differences reproducible. Sentence boundaries and training-only counts prevent accidental leakage. Stable softplus avoids taking logarithms of rounded sigmoid values.

## 18. Disadvantages and Limitations

Fixed noise can overfit its draws and differs from resampling every epoch. Fixed windows omit dynamic windows, frequent-word subsampling and phrase discovery. Dense bounded full-batch training targets education. Float64 sigmoid tails can round to0/1; finite objectives and gradients remain controlled. A finite budget is not an optimum or semantic-quality certificate. Seeds and nonunique representations make coordinate equality inappropriate across independent models.

## 19. When to Use It

Use to study local embedding objectives, negative sampling, repeated-index differentiation and reproducible tiny-corpus learning. Assess downstream usefulness separately on permitted held-out data.

## 20. When Not to Use It

Do not expect a pretrained multilingual model, calibrated language probabilities, contextual disambiguation or reliable analogies from this bounded model. N-Grams supply normalized conditional probabilities; BERT/GPT supply separately scoped contextual architectures.

## 21. Comparison With Related Algorithms

| Method | Fitted information |
|---|---|
| Bag of Words / TF-IDF | Document counts / rarity weighting |
| SGNS here | Local sampled positive/noise logistic terms |
| [GloVe](../glove/README.md) | Global positive co-occurrence log-regression |
| BERT/GPT | Context-dependent Transformer token objectives |

## 22. Interview Questions

Why two tables? Tokens have separate center/context roles. Why scatter-add? Repeated sampled IDs address the same parameter row. Is SGNS a normalized language model? No. Why freeze sampling during finite differences? Different random draws define a different function.

## 23. Practice Problems

Hand-enumerate repeated-token windows; derive both table gradients; check finite differences with negative collisions; compare objective curves for fixed noise seeds without demanding coordinate equality; evaluate held-out contexts without refitting the vocabulary.

## 24. References

[Mikolov, Sutskever, Chen, Corrado and Dean, 2013, Distributed Representations of Words and Phrases and their Compositionality](https://arxiv.org/abs/1310.4546), especially the negative-sampling objective. Fixed noise/windows, optimizer, tokenizer and bounds are declared educational conventions. No paper benchmark result is claimed for this model.

## 25. Author Attribution

Owner and maintainer: **[MD.Khalid Hasan](https://github.com/khalidhasan7343)**. [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas); [MIT license](../../../LICENSE); [contributing](../../../CONTRIBUTING.md).
