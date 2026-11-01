# TF-IDF

## 1. Algorithm Name

TF-IDF. TF-IDF combines document term counts with training-corpus document rarity. This canonical uses smoothed IDF and optional L2 row normalization.

## 2. Overview

Construct fixed-dimensional weighted document vectors without fitting counts or vocabulary on evaluation documents. Different TF-IDF formulas exist; this lesson specifies one.

## 3. Problem Statement

Unicode NFC, optional casefold, word runs and individual punctuation; no stop-word/stemming/subword model. Document boundaries are list elements. Training-only vocabulary uses count pruning then lexical indices; held-out tokens cannot alter it. Input limits:64 documents,2048 total tokens,128 tokens per text and4096 code points; empty text is allowed, empty corpus rejected. No silent truncation. TFIDF(norm="l2",lowercase=True,min_count=1,max_features=127); norm is l2 or None. TF is raw count, never hidden logarithmic or binary scaling.

feature_names_/vocabulary_ identify columns; document_frequency_,idf_,n_documents_ retain fitted statistics; transform returns owned float64(N,V), including valid zero vectors/zero columns.

## 4. Why Do We Need This Algorithm?

Terms appearing in fewer training documents receive larger weights, while repeated occurrences increase raw TF. This is a retrieval weighting convention, not an estimate of token probability. Auditable TF/DF separation and direct BoW reuse. An aligned independent sklearn comparison checks the chosen smoothing/normalization/tokenization conventions.

## 5. Real-World Applications

Document retrieval and lexical similarity baselines with a fixed training corpus; normalized vectors support cosine comparisons. No production deployment or accuracy claim is inferred.

## 6. Core Intuition

df_j=sum_d indicator(C_dj>0); idf_j=log((N+1)/(df_j+1))+1. Raw weight A_dj=C_dj*idf_j. For norm=l2 divide by sqrt(sum_j A_dj²) when nonzero, otherwise retain zero. Natural logarithms throughout.

Terms appearing in fewer training documents receive larger weights, while repeated occurrences increase raw TF. This is a retrieval weighting convention, not an estimate of token probability.

## 7. Prerequisites

Prerequisites: Python collections/NumPy arrays, counting, basic probability/logarithms where applicable, and training/query separation. Reuse canonical BagOfWords for vocabulary/counts rather than duplicating tokenization. Document frequency counts document presence, not total occurrences.

## 8. Step-by-Step Working Process

Fit a fresh BoW, compute boolean presence column sums and smoothed IDF, then commit. Transform uses only fitted counts/IDF; row normalization never updates corpus statistics.

## 9. Pseudocode

```text
C <- canonical BoW(training)
df <- column sums of (C>0)
idf <- log((N+1)/(df+1))+1
query counts <- fitted BoW(query)
A <- query counts * idf
optional nonzero-row L2 normalization
```

## 10. Dry Run

For ["a a b","b c",""] columns are a,b,c; df=[1,2,1]. IDF=[1+log2,1+log(4/3),1+log2]. Row1=[2*(1+log2),1+log(4/3),0]. Empty query is zero; unseen terms do not affect df.

## 11. Time Complexity

Vocabulary fit O(T+U log U); dense weighting/normalization O(NV); queries O(T_query+N_query V). No iterative optimizer runs.

## 12. Space Complexity

O(NV) temporary counts/weights, O(U+V) vocabulary and IDF. Sparse output is not implemented.

## 13. Python Implementation

The [Python/NumPy implementation](python/solution.py) uses the stated mechanism directly. Read the [independent tests](tests/test_python.py) and [executed example](python/example.py). Text validation and fitted vocabulary conventions are in [B13 contracts](../../../docs/natural-language-processing-conventions.md). No complete NLP estimator is called.

## 14. C++ Implementation

C++ is optional for ML and is not implemented here. No placeholder source or test pass is claimed. Existing DSA C++17/C++20 requirements remain mandatory.

## 15. Input and Output Examples

From repository root:

```sh
.venv/bin/python machine-learning/natural-language-processing/tf-idf/python/example.py
.venv/bin/python -m pytest machine-learning/natural-language-processing/tf-idf -q
```

Actual output:

```json
{"texts": ["a a b", "b c", ""], "features": ["a", "b", "c"], "df": [1, 2, 1], "idf": [1.6931471805599454, 1.2876820724517808, 1.6931471805599454], "weights": [[3.386294361119891, 1.2876820724517808, 0.0], [0.0, 1.2876820724517808, 1.6931471805599454], [0.0, 0.0, 0.0]], "query": [[0.0, 0.0, 1.6931471805599454]]}
```

## 16. Edge Cases

Common/rare terms,duplicate documents,unknown words,empty rows and empty vocabulary are tested. Zero rows remain finite under L2 normalization. Invalid norm/corpus/settings fail; failed refit preserves prior fitted statistics.

## 17. Advantages

Auditable TF/DF separation and direct BoW reuse. An aligned independent sklearn comparison checks the chosen smoothing/normalization/tokenization conventions.

## 18. Disadvantages and Limitations

Ignores order/semantics and depends on training-corpus composition. Smoothed positive IDF does not guarantee downstream accuracy. No sublinear TF,sparse output or automatic language normalization.

## 19. When to Use It

Use for document similarity/retrieval baselines with explicitly training-only statistics and aligned normalization.

## 20. When Not to Use It

Avoid treating weights as probabilities or comparing vectors fit on different vocabularies. Do not refit IDF on the held-out corpus.

## 21. Comparison With Related Algorithms

BoW provides counts; TF-IDF rescales columns; neural embeddings instead fit objectives over token contexts. Different IDF/TF variants require aligned comparisons.

## 22. Interview Questions

Why df rather than count? Corpus rarity is document presence. Why add1? It is the chosen smoothing convention. Does an empty row normalize? It stays zero.

## 23. Practice Problems

Derive the tiny matrix by hand; compare norm=None and l2; duplicate one training document and explain IDF changes; verify a held-out rare term cannot alter fitted IDF.

## 24. References

[Introduction to Information Retrieval, inverse document frequency](https://nlp.stanford.edu/IR-book/html/htmledition/inverse-document-frequency-1.html). The +1 smoothing formula is explicitly selected here, not attributed as the only TF-IDF definition.

## 25. Author Attribution

Owner and maintainer: **[MD.Khalid Hasan](https://github.com/khalidhasan7343)**. [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas); [MIT license](../../../LICENSE); [contributing](../../../CONTRIBUTING.md).

