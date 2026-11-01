# Named Entity Recognition

## 1. Algorithm Name

Named Entity Recognition (NER), implemented here as one explicit educational baseline: token features plus a constrained linear-chain CRF using strict BIO/IOB2 labels. NER is a task, not a uniquely defined universal algorithm.

## 2. Overview

Fit a training-only feature vocabulary to labeled toy sentences, train the canonical B13 CRF and decode legal entity labels. Convert labels to typed half-open token spans and evaluate exact-span precision,recall and F1 separately from token accuracy.

## 3. Problem Statement

Input is1..32 tokenized nonempty training sentences with aligned strict BIO labels, at most64 tokens per sentence and1024 training tokens. Each token is one NFC-normalized shared-tokenizer token of at most128 code points. At most3 entity types yield at most7 labels including O, with at most128 frozen feature columns. predict accepts token lists; predict_text uses the case-preserving shared tokenizer and returns tokens,labels and spans. Empty fitted queries return empty outputs.

## 4. Why Do We Need This Algorithm?

Recognizing an entity is more than labeling one word. Multiword entities need boundaries and consistent types, while exact-span evaluation must penalize partially correct boundaries. The task-specific pipeline adds these semantics around one reusable probabilistic sequence model.

## 5. Real-World Applications

Transparent toy information-extraction and entity-boundary experiments, local annotation validation and structured-evaluation teaching. The tiny local corpus and lexical/shape features do not establish real-world domain coverage.

## 6. Core Intuition

O means outside,B-TYPE begins an entity,I-TYPE continues the immediately preceding B/I entity of the same type. I cannot start a sentence or follow O/a different type. Features are binary bias,casefolded word,suffix of up to two code points,initial uppercase,all-uppercase and digit indicators. Only feature names observed in training receive columns. Unknown words retain any known shape/suffix/bias features. The canonical CRF models complete legal BIO paths; this module adds no duplicate partition or Viterbi implementation.

## 7. Prerequisites

Prerequisites: [canonical CRF](../conditional-random-fields/README.md), tokenization, supervised annotation and set-based evaluation. Train/test separation applies to feature names and CRF parameters. Entity types use bounded ASCII alphanumeric/underscore strings; exact case is significant. Shared tokenizer uses Unicode word runs and individual punctuation, not linguistic segmentation or subword embeddings.

## 8. Step-by-Step Working Process

Validate token/BIO alignment and strict span legality. Collect entity types and deterministic O/B/I label order; fit a sorted training-only feature dictionary. Construct legal start/transition masks and dense binary feature matrices. Train the cached canonical CRF with all four parameter groups. At query create features against the frozen dictionary,decode one legal path and scan labels into spans. Evaluate per-sentence span sets so matching offsets in different sentences cannot count as a true positive.

## 9. Pseudocode

```text
validate every training BIO sequence
freeze sorted observed token/shape feature names
labels <- O plus B/I for sorted entity types
legal_start <- labels other than I-*
legal_next[I-X] <- only preceding B-X or I-X
fit canonical CRF(training features,gold BIO,masks)
query features <- frozen dictionary; predict legal path
scan BIO: B opens span,I continues,O/B closes prior span
compare (sentence_id,type,start,end) sets for exact metrics
```

## 10. Dry Run

Gold [B-PER,I-PER,O,B-LOC] has spans(PER,0,2) and(LOC,3,4). Prediction[B-PER,O,O,B-LOC] has spans(PER,0,1) and(LOC,3,4). Only LOC matches:precision=recall=F1=.5,while token accuracy=.75. Adjacent B-PER/B-PER creates two separate one-token entities. I-PER at sentence start is invalid rather than silently repaired.

## 11. Time Complexity

For T tokens,F frozen features,K BIO labels, dense feature storage/build is O(TF) allocation plus bounded per-token feature work. CRF inference costs O(T(FK+K²)),training follows its bounded iteration/backtracking contract. Span extraction and metric set construction are O(total tokens) expected time. Feature-name sorting costs O(U log U) for U observed names.

## 12. Space Complexity

The task pipeline stores O(F) feature names, O(TF) sequence features and the canonical O(FK+K²) CRF parameters. Decoding uses O(TK) paths, while probability/gradient computations may require O(TK²) pair marginals. Evaluation stores O(number of entity spans) sets with sentence identities.

## 13. Python Implementation

[Python source](python/solution.py) owns token features,BIO legality,span extraction and metrics; s.load reuses [the canonical CRF source](../conditional-random-fields/python/solution.py). [Tests](tests/test_python.py) verify hand spans,legal masks,features,unknown words,failed-refit atomicity,exact metrics,training and canonical class identity. [The executable example](python/example.py) uses explicitly labeled local toy sentences.

## 14. C++ Implementation

C++ is optional for ML and absent for this task baseline. No placeholder source/test is counted. Existing DSA C++17/C++20 tests remain required.

## 15. Input and Output Examples

From repository root:

```sh
.venv/bin/python machine-learning/natural-language-processing/named-entity-recognition/python/example.py
.venv/bin/python -m pytest machine-learning/natural-language-processing/named-entity-recognition -q
```

Actual executed output:

```json
{"training": [["John", "visits", "Paris"], ["Mary", "visits", "Rome"], ["New", "York", "shines"]], "gold": [["B-PER", "O", "B-LOC"], ["B-PER", "O", "B-LOC"], ["B-LOC", "I-LOC", "O"]], "baseline": "BIO feature CRF", "features": 18, "initial_loss": 3.713572, "final_loss": 0.155776, "query": {"tokens": ["John", "visits", "Paris"], "labels": ["B-PER", "O", "B-LOC"], "spans": [["PER", 0, 1], ["LOC", 2, 3]]}, "unknown_query": {"tokens": ["Alice", "visits", "Rome"], "labels": ["B-PER", "O", "B-LOC"], "spans": [["PER", 0, 1], ["LOC", 2, 3]]}, "training_metrics": {"true_positive": 5, "predicted": 5, "gold": 5, "precision": 1.0, "recall": 1.0, "f1": 1.0, "token_accuracy": 1.0}}
```

These are actual local toy results; training performance is not a held-out quality estimate.

## 16. Edge Cases

Reject malformed BIO tags,illegal I transitions,misaligned labels,non-token strings,too many entity types/features and resource excess. Empty queries yield no entities; an all-O training set produces an O-only model. No-entity precision/recall/F1 use explicit0 for zero denominators; token accuracy is None when no tokens exist. Unknown words never create query-time feature columns. Returned feature arrays and prediction dictionaries do not expose model feature storage.

## 17. Advantages

The chosen baseline teaches entity boundaries,task-specific features,structured legality and exact evaluation while preserving one canonical CRF. Sorted dictionaries,zero-initialized deterministic CRF training and private/no random sampling give reproducible local examples.

## 18. Disadvantages and Limitations

No pretrained language knowledge,neural character encoder,subword model,nested/overlapping entity scheme,character-offset mapping or large-corpus performance claim. Spans use token offsets after the documented tokenizer. Case/lexical/suffix features are limited and vocabulary drift reduces quality. A legal BIO path can still be an incorrect entity prediction; constraints establish structural validity,not semantic truth.

## 19. When to Use It

Use as an explicit bounded feature-CRF NER baseline or to test span-label/evaluation semantics with tiny annotated sentences. Report held-out exact-span F1 with a stated annotation/tokenization protocol.

## 20. When Not to Use It

Do not call this the only NER algorithm,compare incompatible annotation/tokenization schemes without alignment,fit on evaluation labels,score partial overlaps as exact matches,or infer production performance from the tiny training corpus. Do not confuse high token accuracy on mostly O labels with entity quality.

## 21. Comparison With Related Algorithms

POS tagging predicts grammatical categories and uses token accuracy. This NER baseline predicts typed BIO boundaries and evaluates complete entity spans. The generic CRF owns mathematical inference/training; this task owns feature extraction and BIO semantics. Transformer-based NER is a different model scope and is not claimed here.

## 22. Interview Questions

Does I-LOC after B-PER continue an entity? No,it is structurally invalid. Can an unknown token still receive an entity tag? Yes,known shape/suffix/bias features and transitions still apply. Does a one-token boundary error count as a true positive? No,exact type/start/end must all match.

## 23. Practice Problems

Hand-extract spans for adjacent and multiword entities; derive the .5 exact-F1/.75 token-accuracy example; construct identical offsets across different sentences; verify query feature names remain frozen; compare all-O token accuracy with entity F1; enumerate tiny constrained CRF paths.

## 24. References

Erik F. Tjong Kim Sang and Jorn Veenstra (1999), [Representing Text Chunks](https://arxiv.org/abs/cs/9907006), on sequence-label representations. John Lafferty,Andrew McCallum,Fernando Pereira (2001), [Conditional Random Fields](https://www.cs.columbia.edu/~jebara/6772/papers/crf.pdf), for the reused conditional sequence model. Strict BIO,features,limits and exact-span evaluation are explicitly selected here,not asserted to define all NER systems.

## 25. Author Attribution

Owner and maintainer: **[MD.Khalid Hasan](https://github.com/khalidhasan7343)**. [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas); [MIT license](../../../LICENSE); [contributing](../../../CONTRIBUTING.md).
