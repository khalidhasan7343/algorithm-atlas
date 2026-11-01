# Hidden Markov Models for POS Tagging

## 1. Algorithm Name

Supervised categorical Hidden Markov Model (HMM) for part-of-speech tagging. This is the B13 application pipeline; the general B11 HMM remains the canonical numerical inference implementation.

## 2. Overview

Learn an initial-tag distribution, tag-to-tag transitions and word emissions from explicitly tagged sentences. Decode a new token sequence with log-space Viterbi and optionally inspect posterior tag probabilities. There is no unsupervised EM step in this supervised estimator.

## 3. Problem Statement

Input is1..32 nonempty tokenized training sentences, matching nonempty string POS tags, and at most1024 training tokens. A sentence has at most64 tokens, each at most128 code points and exactly one shared-tokenizer token. Output tags follow the input token positions. At most8 distinct tags and16 word symbols including UNK are supported, matching the unchanged B11 engine. Raw-text tag_text uses the shared tokenizer with case preserved before the configured vocabulary normalization.

## 4. Why Do We Need This Algorithm?

Independent word classification ignores neighboring tags. A first-order tag transition model can distinguish otherwise ambiguous emissions while preserving an inspectable probability calculation. Supervised count estimates need little infrastructure and show precisely where unknown-word smoothing enters.

## 5. Real-World Applications

Educational POS baselines, small labeled sequence experiments and demonstrations of generative sequence inference. A toy-trained tagger is not evidence of broad-domain or multilingual tagging accuracy.

## 6. Core Intuition

For tags y and words w, joint probability is pi[y0]*B[y0,w0]*product_t(A[y(t-1),yt]*B[yt,wt]). Initial counts count sentences, transition counts count only adjacent positions inside a sentence, and emissions count aligned tag/word pairs. Each table row uses add-alpha smoothing: (count+alpha)/(row_total+alpha*row_width), alpha1e-8..100. There is no learned EOS transition; inference is for an explicitly supplied sequence length.

## 7. Prerequisites

Prerequisites: categorical probability, supervised labels, counting and [the B11 HMM](../../time-series/hidden-markov-models/README.md). Shared B13 Vocabulary.fit_tokens preserves supplied token boundaries while applying per-token NFC and optional casefold, minimum count and bounded frequency retention before lexicographic indices. This prevents Unicode casefold expansion (for example İ to i plus combining dot) from being retokenized differently during fitting and inference. UNK occupies index0; max_size1..16 includes it. Pruned training tokens also contribute emissions to UNK, and held-out words never expand the vocabulary.

## 8. Step-by-Step Working Process

Validate all sentence/tag alignments before committing state. Fit the training-only vocabulary, construct sorted tag indices, accumulate independent sentence counts and normalize smoothed tables. Instantiate the unchanged B11 CategoricalHMM with all probability arrays. Encode a query with the frozen vocabulary, use B11 decode/score/infer, and map decoded integer states back to the fixed tag names.

## 9. Pseudocode

```text
validate independent token/tag sentences
fit bounded training vocabulary; sort unique tags
for each sentence:
    increment its first tag
    count each tag/word and each internal adjacent tag pair
row-normalize counts + alpha
construct canonical B11 HMM(pi,A,B)
query <- frozen word IDs; tags <- B11 log-Viterbi(query)
```

## 10. Dry Run

Training sentences dogs/run, cats/sleep and dogs/sleep all have tags N/V. With alpha1, pi=[4/5,1/5], A[N]=[1/5,4/5] and A[V]=[1/2,1/2]. Vocabulary is UNK,cats,dogs,run,sleep. Emission rows are [1,2,3,1,1]/8 and [1,1,1,2,3]/8. The best dogs/run path is N/V with joint probability(4/5)*(3/8)*(4/5)*(2/8)=.06. Summing every tag path gives the word likelihood, which differs from the best-path joint probability.

## 11. Time Complexity

Let M be training tokens,S sentences,K tags,V retained symbols and T query length. Counting is O(M+S); vocabulary selection is O(U log U) for U unique words. Table normalization costs O(KV+K²). Viterbi/forward/backward cost O(TK²), not exponential K**T. Exhaustive enumeration exists only in tiny independent tests.

## 12. Space Complexity

Counts and model storage are O(KV+K²+V); Viterbi/backpointers and posterior storage are O(TK). Training copies bounded normalized tokens for validation. Returned query tags/posteriors are owned outputs, not views into fitted count tables.

## 13. Python Implementation

[The pipeline source](python/solution.py) owns supervised text/tag estimation and loads the unchanged B11 engine through the shared cached loader. [Tests](tests/test_python.py) verify exact tables, exhaustive paths, direct engine parity, unknown words, ownership and atomic failed refits. [The example](python/example.py) trains and evaluates actual local toy data.

## 14. C++ Implementation

ML C++ is optional and is not implemented for this application. No placeholder or C++ pass is claimed. Existing DSA Python/C++17/C++20 requirements remain unchanged.

## 15. Input and Output Examples

From repository root:

```sh
.venv/bin/python machine-learning/natural-language-processing/hidden-markov-models-pos-tagging/python/example.py
.venv/bin/python -m pytest machine-learning/natural-language-processing/hidden-markov-models-pos-tagging -q
```

Actual executed output:

```json
{"training": [["dogs", "run"], ["cats", "sleep"], ["dogs", "sleep"]], "tags": ["N", "V"], "vocabulary": ["<UNK>", "cats", "dogs", "run", "sleep"], "initial": [0.8, 0.2], "transition": [[0.2, 0.8], [0.5, 0.5]], "query": ["unknown", "sleep"], "predicted": ["N", "V"], "best_joint_log_probability": -3.506558, "observation_log_likelihood": -3.250625, "posterior": [[0.83871, 0.16129], [0.104839, 0.895161]], "training_accuracy": 1.0}
```

These are actual local toy results; training performance is not a held-out quality estimate.

## 16. Edge Cases

Empty query tokens return empty tags, empty posterior and log probability0 after fitted-state validation. Empty training sentences are rejected. Positive smoothing prevents zero-probability unknown emissions and supplies uniform transition rows for tags never observed before another tag. Malformed tags, too many tags, mixed invalid token boundaries, excessive lengths and failed refits fail before replacing a previously valid model.

## 17. Advantages

Exact count diagnostics, deterministic sorted states, explicit smoothing and log-space decoding make predictions auditable. Sharing B11 inference prevents a second inconsistent Viterbi implementation.

## 18. Disadvantages and Limitations

First-order transitions and conditionally independent word emissions are restrictive. Unknown words share one emission symbol. The tokenizer is not a universal linguistic tokenizer; morphology, subwords, contextual embeddings and trainable end-state distributions are unsupported. Bounds intentionally exclude realistic large POS vocabularies. Smoothing changes the maximum-likelihood count model and its alpha must be disclosed.

## 19. When to Use It

Use for an inspectable supervised sequence baseline when a tiny finite word/tag vocabulary and explicit sentence boundaries are sufficient. Report held-out token accuracy separately from training accuracy.

## 20. When Not to Use It

Avoid treating toy memorization as held-out accuracy, joining sentences to create artificial transitions, using gold query tags as inference features, or changing the vocabulary at evaluation time. Choose a different explicitly scoped model for large contextual language tasks.

## 21. Comparison With Related Algorithms

HMM maximizes joint word/tag probabilities with normalized emissions/transitions. [CRF](../conditional-random-fields/README.md) normalizes complete label sequences conditional on arbitrary fixed features. [NER](../named-entity-recognition/README.md) here is a task-specific BIO CRF pipeline with entity-span evaluation, not POS tagging. General B11 HMM retains unsupervised Baum-Welch, which this supervised application does not duplicate.

## 22. Interview Questions

Why is the initial denominator the number of sentences? There is one first tag per sentence. Why exclude final tags from outgoing transition totals? They have no observed successor. Why can best-path score be below word likelihood? Likelihood sums all tag paths.

## 23. Practice Problems

Enumerate all2**T tag paths for a three-word query; independently reconstruct smoothed tables; vary alpha without refitting on test words; compare case-sensitive and casefolded vocabularies; add a sentence and verify no transition spans the boundary.

## 24. References

Lawrence R. Rabiner (1989), [A Tutorial on Hidden Markov Models and Selected Applications in Speech Recognition](https://web.ece.ucsb.edu/Faculty/Rabiner/ece259/Reprints/tutorial%20on%20hmm%20and%20applications.pdf), DOI10.1109/5.18626. The supervised token/count/bounds contract is specified here; [B11 source](../../time-series/hidden-markov-models/python/solution.py) owns reused categorical inference.

## 25. Author Attribution

Owner and maintainer: **[MD.Khalid Hasan](https://github.com/khalidhasan7343)**. [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas); [MIT license](../../../LICENSE); [contributing](../../../CONTRIBUTING.md).
