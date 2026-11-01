# Conditional Random Fields (CRF)

## 1. Algorithm Name

Dense-feature linear-chain Conditional Random Field (CRF), with optional legal-start/transition masks and trainable emission, transition, start and end scores.

## 2. Overview

Condition a globally normalized distribution over label sequences on fixed per-token features. Stable dynamic programming computes its partition, posterior marginals and best path; genuine conditional-likelihood training updates every supported score-parameter group.

## 3. Problem Statement

Construct LinearChainCRF(labels,n_features) with1..8 unique string labels and1..128 feature columns. A sequence is a real T-by-F matrix,1<=T<=64, with finite magnitudes<=100. Labels align with active positions. Optional length selects a nonempty active prefix of padded rows; inactive labels are not supplied. Inference is valid at constructor-initialized zero parameters. Prediction returns string labels; decode returns owned integer path plus unnormalized score.

## 4. Why Do We Need This Algorithm?

Independent token classifiers ignore output-label dependencies. A CRF lets transition preferences and local observations influence one joint decision, avoiding a claim that every token decision is independent. Structural masks can exclude illegal paths without changing the global-normalization principle.

## 5. Real-World Applications

Small sequence-labeling baselines and mathematical demonstrations of structured probabilistic inference. The canonical CRF is reused by [the explicitly scoped BIO NER pipeline](../named-entity-recognition/README.md).

## 6. Core Intuition

Score(x,y)=start[y0]+end[y(T-1)]+sum_t x[t]·W[:,yt]+sum_(t>0) A[y(t-1),yt]. P(y|x)=exp(score-logZ(x)); logZ is log-sum-exp over all legal paths. Forward alpha0=start+emission0; alpha_t[j]=emission_t[j]+LSE_i(alpha_(t-1)[i]+A[i,j]). Backward beta_last=end and beta_t[i]=LSE_j(A[i,j]+emission_(t+1)[j]+beta_(t+1)[j]). Illegal start/transition energies are -infinity. These are unnormalized scores, not HMM transition probabilities.

## 7. Prerequisites

Prerequisites: matrix products, log-sum-exp, dynamic programming and derivatives of log-partition functions. Shared B13 logsumexp reuses unchanged B11 numerical logic. Features are fixed real values supplied by the caller; this canonical does not learn a token vocabulary or a neural feature extractor.

## 8. Step-by-Step Working Process

Compute emissions=XW, legal forward/backward tables, token marginals exp(alpha+beta-logZ) and adjacent-pair marginals. Negative log-likelihood gradient is expected minus observed feature counts. In particular dW=X.T*(token_marginals-onehot), dA=sum(pair_marginals)-observed pairs, dstart=first-token residual and dend=last-token residual. Train a mean sequence NLL plus(.5*l2*sum of squared parameters), with exact gradients for all four groups, full-batch descent and up to32 bounded backtracking trials per step. Fit resets to zero deterministically and commits only valid final state.

## 9. Pseudocode

```text
E <- X W; illegal start/transitions <- -infinity
alpha[0] <- start+E[0]
for t=1..T-1: alpha[t,j] <- E[t,j]+LSE_i(alpha[t-1,i]+A[i,j])
logZ <- LSE_j(alpha[T-1,j]+end[j])
run backward recursion; compute token/pair posterior counts
gradients <- expected counts - gold counts
training: average NLL + L2; backtrack finite gradient updates
decoding: replace LSE with max and retain parent indices
```

## 10. Dry Run

At zero parameters with two labels and two positions, all four paths have score0, logZ=log4 and probability1/4. For X=[[1,0],[1,1]], gold A/B, dW=[[0,0],[.5,-.5]], dA=[[.25,-.75],[.25,.25]], dstart=[-.5,.5], dend=[.5,-.5]. One l2=0,rate=.1 update is exactly negative.1 times those arrays. For BIO labels O,B-X,I-X, legal starts O/B-X and matching I continuation leave five legal two-position paths, giving logZ=log5 at zero parameters.

## 11. Time Complexity

One forward/backward/gradient evaluation costs O(T(FK+K²)), where T is active length,F features,K labels. Viterbi has the same asymptotic bound including emissions. For E iterations and S training sequences, multiply by total active positions and at most32 backtracking trials per iteration. Production does not enumerate K**T paths. Work guard is max_iter*total_active_T*(FK+K²)<=2e7 before the fixed backtracking factor; total tokens<=1024 and max_iter<=200.

## 12. Space Complexity

Parameters require O(FK+K²+K). Forward/backward and Viterbi parents require O(TK); reported pair marginals require O(TK²). Training stores bounded input sequences and one gradient/candidate set; it does not retain an automatic differentiation graph.

## 13. Python Implementation

[Python source](python/solution.py) implements actual global forward/backward, expected-count gradients, bounded optimization and Viterbi. [Tests](tests/test_python.py) independently enumerate paths and central-difference every coordinate in emission,transition,start,end groups, with and without structural masks. Public loss_gradients is unregularized single-sequence NLL; fit history includes mean loss and L2. [The example](python/example.py) trains all groups on a two-token feature sequence.

## 14. C++ Implementation

C++ is optional for this ML canonical and is not provided. No dummy source or pass is claimed; DSA C++17/C++20 remains mandatory.

## 15. Input and Output Examples

From repository root:

```sh
.venv/bin/python machine-learning/natural-language-processing/conditional-random-fields/python/example.py
.venv/bin/python -m pytest machine-learning/natural-language-processing/conditional-random-fields -q
```

Actual executed output:

```json
{"features": [[1.0, 0.0], [0.0, 1.0]], "gold": ["A", "B"], "initial_log_partition": 1.386294, "initial_loss": 1.386294, "final_regularized_loss": 0.050036, "status": "iteration-budget", "updates": 80, "predicted": ["A", "B"], "conditional_probability": 0.984514, "token_marginals": [[0.991964, 0.008036], [0.008036, 0.991964]], "trainable_groups": ["emission", "transition", "start", "end"]}
```

These are actual local toy results; training performance is not a held-out quality estimate.

## 16. Edge Cases

One-token sequences have no pair transitions but have both start and end scores. Impossible legal-path sets raise ImpossibleSequenceError. Illegal gold paths, malformed labels/features/masks, zero active length, nonfinite parameters and resource excess fail. Padded feature rows must themselves be finite and bounded, but cannot affect an active-prefix prediction. Constructor masks are copied. Failed fit validates data before replacing parameters; query marginals/paths are owned arrays.

## 17. Advantages

Exact global normalization, independent exhaustive verification and explicit score gradients make structured decisions inspectable. Legal masks support task constraints while retaining probability mass only on permitted paths. Token and pair posteriors are available.

## 18. Disadvantages and Limitations

This is a first-order linear model with fixed dense features, not a neural CRF or arbitrary graph. Training is bounded approximate optimization, not a guarantee of a global optimum by the iteration limit. Parameters are finite with magnitudes<=1e4; scores can still lose precision at large finite magnitudes. Stable log-sum-exp avoids overflow and posterior rows are normalized for roundoff, but no arbitrary NaN repair is performed. Padding is a contiguous active prefix, not an arbitrary attention mask.

## 19. When to Use It

Use for tiny structured-label experiments, auditable feature models and BIO NER with exact constraints. Inspect actual loss_history_, status_, converged_ and n_iter_ rather than claiming convergence from any loss decrease.

## 20. When Not to Use It

Do not substitute per-token softmax, HMM row normalization or greedy decoding while calling it this global CRF. Do not feed gold labels into query features. Avoid large vocabularies/long sequences beyond the declared bounds or unsupported higher-order/latent labels.

## 21. Comparison With Related Algorithms

HMM assigns a joint word/label model with normalized transition/emission rows. CRF assigns P(labels|features) using one sequence-level partition; transitions need not sum to1. Independent token classification is the restricted case without learned dependencies. The NER application supplies token features and BIO masks without duplicating this engine.

## 22. Interview Questions

Why do gradients contain expected counts? Differentiating logZ averages score derivatives under the conditional model. Why does Viterbi differ from marginal argmax? It optimizes an entire legal path. Which groups are checked? Every coordinate of all four supported groups, including masked cases.

## 23. Practice Problems

Enumerate all eight paths for a length3,two-label sequence; derive token/pair marginals independently; check finite differences with fixed features; show illegal BIO paths have zero mass; compare a constrained path optimum with independent token argmax; test padding without refitting.

## 24. References

John Lafferty, Andrew McCallum, Fernando Pereira (2001), [Conditional Random Fields: Probabilistic Models for Segmenting and Labeling Sequence Data](https://www.cs.columbia.edu/~jebara/6772/papers/crf.pdf). The dense-feature form, bounded optimizer, score ordering and legal-mask APIs are this educational implementation’s explicit scope.

## 25. Author Attribution

Owner and maintainer: **[MD.Khalid Hasan](https://github.com/khalidhasan7343)**. [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas); [MIT license](../../../LICENSE); [contributing](../../../CONTRIBUTING.md).
