# Bag of Words

## 1. Algorithm Name

Bag of Words. Bag of Words represents each document by retained training-term counts. Word order is discarded; repeated occurrences are retained unless binary=True.

## 2. Overview

Fit a deterministic training vocabulary, then map each independent document into one count coordinate per retained word. This is representation, not a classifier or learned semantic embedding.

## 3. Problem Statement

Unicode NFC, optional casefold, word runs and individual punctuation; no stop-word/stemming/subword model. Document boundaries are list elements. Training-only vocabulary uses count pruning then lexical indices; held-out tokens cannot alter it. Input limits:64 documents,2048 total tokens,128 tokens per text and4096 code points; empty text is allowed, empty corpus rejected. No silent truncation. BagOfWords(lowercase=True,min_count=1,max_features=127,binary=False) bounds retained known columns1..127; min_count refers to corpus token count, not document frequency.

fit returns self; vocabulary_ maps known terms to zero-based columns, feature_names_ is a tuple, and transform/fit_transform return owned int64 arrays(N,V). Unknown terms are ignored. An all-empty corpus has V=0 and valid shape(N,0).

## 4. Why Do We Need This Algorithm?

A coordinate describes how many times a token occurs. Lexical ordering makes column identities stable under training-document permutation; frequency pruning uses lexical ties. Exact counts and column identities are independently auditable. Training/inference separation is clear and the representation composes directly with canonical TF-IDF.

## 5. Real-World Applications

Document retrieval, corpus count inspection and transparent classification feature baselines. Fit vocabulary on permitted training documents and evaluate any downstream classifier separately.

## 6. Core Intuition

C[d,j]=sum over tokens t in document d of indicator(t=vocabulary[j]). Binary mode instead returns indicator(C[d,j]>0). Counts use the same fitted tokenizer/normalization at training and inference.

A coordinate describes how many times a token occurs. Lexical ordering makes column identities stable under training-document permutation; frequency pruning uses lexical ties.

## 7. Prerequisites

Prerequisites: Python collections/NumPy arrays, counting, basic probability/logarithms where applicable, and training/query separation. Each row is independent. Shared Vocabulary keeps UNK at0 internally; the BoW representation deliberately omits that column so unknown input contributes no artificial known-word count.

## 8. Step-by-Step Working Process

Validate corpus, fit a fresh local vocabulary, commit owned names/map, then tokenize each transform document and bincount known IDs. Invalid refit validates before replacing fitted state.

## 9. Pseudocode

```text
fit training token counts -> retain vocabulary -> assign lexical IDs
for each document:
    tokenize with fitted convention
    count each known token in its column
    optionally replace positive counts with1
```

## 10. Dry Run

Training ["Cat cat dog","DOG!",""] gives columns !,cat,dog and rows[0,2,1],[1,0,1],[0,0,0]. Query "cat unseen" gives[0,1,0]. The unseen word never becomes a feature.

## 11. Time Complexity

Tokenization/counting is O(T); vocabulary selection O(U log U); dense transform is O(T+NV). T is total tokens, U distinct training tokens, N documents and V retained terms.

## 12. Space Complexity

Dense output O(NV), vocabulary/count tables O(U+V), tokenized bounded corpus O(T). There is no recursion, network or external dataset.

## 13. Python Implementation

The [Python/NumPy implementation](python/solution.py) uses the stated mechanism directly. Read the [independent tests](tests/test_python.py) and [executed example](python/example.py). Text validation and fitted vocabulary conventions are in [B13 contracts](../../../docs/natural-language-processing-conventions.md). No complete NLP estimator is called.

## 14. C++ Implementation

C++ is optional for ML and is not implemented here. No placeholder source or test pass is claimed. Existing DSA C++17/C++20 requirements remain mandatory.

## 15. Input and Output Examples

From repository root:

```sh
.venv/bin/python machine-learning/natural-language-processing/bag-of-words/python/example.py
.venv/bin/python -m pytest machine-learning/natural-language-processing/bag-of-words -q
```

Actual output:

```json
{"texts": ["Cat cat dog", "DOG!", ""], "features": ["!", "cat", "dog"], "counts": [[0, 2, 1], [1, 0, 1], [0, 0, 0]], "query": [[0, 1, 0]]}
```

## 16. Edge Cases

Empty/duplicate/single-token texts,Unicode,case,punctuation,unseen terms and all-empty features are tested. Invalid corpus/settings fail explicitly. Returned count modifications do not alter the model.

## 17. Advantages

Exact counts and column identities are independently auditable. Training/inference separation is clear and the representation composes directly with canonical TF-IDF.

## 18. Disadvantages and Limitations

Loses order and meaning; rare/unknown words can disappear. Dense matrices are unsuitable for large vocabularies. The tokenizer is a teaching convention, not universal linguistic segmentation.

## 19. When to Use It

Use as a transparent corpus baseline, feature source or input to TF-IDF. Fit only permitted training data.

## 20. When Not to Use It

Avoid expecting contextual meaning,semantic similarity or sequence probabilities. Use trainable embeddings or scoped Transformers for those different tasks.

## 21. Comparison With Related Algorithms

BoW is local raw counts; TF-IDF multiplies corpus-informed rarity weights; N-grams retain limited sequential contexts.

## 22. Interview Questions

Why ignore unknowns? They have no fitted known coordinate. Why are columns deterministic? Pruning ties and final order are explicit. Is max_features silent truncation? It is a declared learned vocabulary cap.

## 23. Practice Problems

Hand-count a punctuation-rich corpus; compare binary and repeated counts; prove permutation invariance of vocabulary ordering; test a query containing only unseen words.

## 24. References

[Manning, Raghavan and Schütze, Introduction to Information Retrieval, term frequency](https://nlp.stanford.edu/IR-book/html/htmledition/term-frequency-and-weighting-1.html). Exact tokenizer/pruning/empty-vocabulary conventions are declared implementation choices.

## 25. Author Attribution

Owner and maintainer: **[MD.Khalid Hasan](https://github.com/khalidhasan7343)**. [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas); [MIT license](../../../LICENSE); [contributing](../../../CONTRIBUTING.md).

