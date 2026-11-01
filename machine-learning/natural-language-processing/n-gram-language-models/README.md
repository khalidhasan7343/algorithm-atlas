# N-Gram Language Models

## 1. Algorithm Name

N-Gram Language Models. A fixed-order count language model predicts each token from the preceding n-1 tokens using explicit add-k smoothing.

## 2. Overview

Estimate conditional probabilities from independent training sentences and score unseen sentences in log space. This is a finite-context probabilistic model, not a neural language model.

## 3. Problem Statement

Unicode NFC, optional casefold, word runs and individual punctuation; no stop-word/stemming/subword model. Document boundaries are list elements. Training-only vocabulary uses count pruning then lexical indices; held-out tokens cannot alter it. Input limits:64 documents,2048 total tokens,128 tokens per text and4096 code points; empty text is allowed, empty corpus rejected. No silent truncation. NGramLanguageModel(order=2,k=1,min_count=1,max_size=127,lowercase=True). Order1..5,k1e-8..100. Prediction vocabulary contains retained words,UNK and EOS; BOS is context-only.

counts_/context_counts_ retain exact training events; distribution(context) returns owned probabilities in tokens_ order. probability,log_probability,perplexity,predict_next and seeded bounded generate are available. Generation returns token strings and stops at EOS or max_tokens<=128.

## 4. Why Do We Need This Algorithm?

Add-k allocates probability to unseen continuations; entirely unseen contexts become uniform. Prefix markers make short and empty sentences well-defined; EOS accounts for ending a sentence. Exact probabilities,normalization and event counts are easy to audit. Sentence boundaries and perplexity denominator are explicit.

## 5. Real-World Applications

Finite-context predictive text baselines, language-model teaching and small-vocabulary likelihood comparisons under a common held-out tokenization protocol.

## 6. Core Intuition

For history h of n-1 tokens,P(w|h)=(C(h,w)+k)/(C(h)+kV). Prepend n-1 BOS markers and append exactly one EOS per sentence. LogP(sentence)=sum over ordinary tokens and EOS logP(w|h); perplexity=exp(-LogP/(number ordinary tokens+1)). No sentence-crossing windows.

Add-k allocates probability to unseen continuations; entirely unseen contexts become uniform. Prefix markers make short and empty sentences well-defined; EOS accounts for ending a sentence.

## 7. Prerequisites

Prerequisites: Python collections/NumPy arrays, counting, basic probability/logarithms where applicable, and training/query separation. The training-only vocabulary maps rare/unseen words to UNK before count estimation. Unigram order uses an empty context. Ties in next-token argmax follow deterministic prediction-vocabulary order.

## 8. Step-by-Step Working Process

Fit separate local counters for every padded training sentence; commit after validation. At query map words to frozen IDs,form exact-length contexts and accumulate log probabilities including EOS. Sampling uses a private RNG and a strict token budget.

## 9. Pseudocode

```text
for each training sentence:
    events <- BOS repeated n-1 + encoded words + EOS
    count (history,event) and history at each prediction
query P <- (event count+k)/(history count+kV)
score <- sum(log P), denominator <- query words+EOS
```

## 10. Dry Run

Corpus ["a b","a a"],bigram,k1 has start P(a)=3/6. After a,P(b)=2/7; after b,P(EOS)=2/5. LogP("a b")=log(3/6)+log(2/7)+log(2/5); perplexity uses denominator3. Tests calculate this independently.

## 11. Time Complexity

Fit O(nT+U log U) including bounded tuple contexts; scalar probability currently builds V probabilities so scoring O(L(n+V)); generation O(G(n+V)). n,T,V,L,G are bounded.

## 12. Space Complexity

O(nT+V) counters/vocabulary; O(n+G) sampling state/output, O(V) probability query. No exponential enumeration in production.

## 13. Python Implementation

The [Python/NumPy implementation](python/solution.py) uses the stated mechanism directly. Read the [independent tests](tests/test_python.py) and [executed example](python/example.py). Text validation and fitted vocabulary conventions are in [B13 contracts](../../../docs/natural-language-processing-conventions.md). No complete NLP estimator is called.

## 14. C++ Implementation

C++ is optional for ML and is not implemented here. No placeholder source or test pass is claimed. Existing DSA C++17/C++20 requirements remain mandatory.

## 15. Input and Output Examples

From repository root:

```sh
.venv/bin/python machine-learning/natural-language-processing/n-gram-language-models/python/example.py
.venv/bin/python -m pytest machine-learning/natural-language-processing/n-gram-language-models -q
```

Actual output:

```json
{"training": ["a b", "a a"], "tokens": ["<UNK>", "a", "b", "<EOS>"], "start_probabilities": [0.16666666666666666, 0.5, 0.16666666666666666, 0.16666666666666666], "query": "a b", "log_probability": -2.8622008809294686, "perplexity": 2.596247050925552, "generated": ["a"]}
```

## 16. Edge Cases

Orders1..5,unknown histories,empty sentences,rare words,zero-count events and fixed-seed sampling are tested. Positive k avoids log0. Invalid context length/type,order,k,corpus and generation budget fail.

## 17. Advantages

Exact probabilities,normalization and event counts are easy to audit. Sentence boundaries and perplexity denominator are explicit.

## 18. Disadvantages and Limitations

No interpolation,backoff,Kneser-Ney or long-range semantics. Add-k can over-smooth sparse high-order contexts. Perplexity depends on vocabulary/order/tokenization and is not directly comparable across incompatible protocols.

## 19. When to Use It

Use as a small transparent sequence baseline and test causal count estimation with genuinely held-out sentences.

## 20. When Not to Use It

Avoid adding evaluation counts or interpreting toy generation as fluent language understanding. Use explicit larger modeling scope for long-range contexts.

## 21. Comparison With Related Algorithms

BoW ignores order; N-grams retain n-1 context; GPT uses causal contextual attention but a different objective/parameterization. HMM models latent tags with generative emissions.

## 22. Interview Questions

Does perplexity count EOS? Yes,both likelihood and denominator do. Are BOS events predicted? No. What is an unseen history distribution? Uniform under positive add-k.

## 23. Practice Problems

Hand-count unigram and trigram versions; sum each conditional distribution; compare smoothing on held-out text without refitting; show that sentence shuffling does not create boundary-spanning events.

## 24. References

[Jurafsky and Martin, Speech and Language Processing, N-gram Language Models](https://web.stanford.edu/~jurafsky/slp3/). The exact bounds,UNK/order and BOS/EOS denominator conventions are specified here.

## 25. Author Attribution

Owner and maintainer: **[MD.Khalid Hasan](https://github.com/khalidhasan7343)**. [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas); [MIT license](../../../LICENSE); [contributing](../../../CONTRIBUTING.md).

