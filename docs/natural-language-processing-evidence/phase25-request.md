# ALGORITHM ATLAS — PHASE 25
# B13: NATURAL LANGUAGE PROCESSING
## FINAL MACHINE LEARNING CATEGORY — COMPLETE CODEX MASTER PROMPT

### 11 Canonical Algorithms and Topics
### From-Scratch Python + NumPy | NLP Pipelines | Word Embeddings | Transformer Architectures | Sequence Labeling | Probabilistic Inference | Dynamic Programming | Mathematical Oracles | Full Regression Audit | Review Package

---

# 0. PROJECT IDENTITY

Repository: `algorithm-atlas`
Owner: MD.Khalid Hasan
GitHub: `khalidhasan7343`
License: MIT

Target phase: **25**
Target category: **B13 — Natural Language Processing**

This is the final category of the Machine Learning B Track in the supplied syllabus.

Expected canonical directory:

`machine-learning/natural-language-processing`

Expected inventory: **11 canonical entries**.

The owner reports that Phase 24 B12 Anomaly Detection has been completed.

## PRIMARY MISSION

Implement, test, document, and review all 11 B13 canonical entries, preserving the repository's mathematical correctness, educational quality, reproducibility, and existing architecture.

This phase must deliver:

1. Genuine Python implementations.
2. NumPy-based mathematical computation.
3. Appropriate text preprocessing.
4. Correct tokenization and vocabulary handling.
5. Correct probabilistic and optimization objectives.
6. Genuine trainable word embeddings.
7. Educational but structurally correct Transformer models.
8. Genuine probabilistic sequence labeling.
9. Correct dynamic programming for parsing.
10. Independent mathematical verification.
11. Gradient checks where applicable.
12. Deterministic randomized testing.
13. Numerical stability verification.
14. Exact 25-section algorithm documentation.
15. Category-level integration.
16. Full previous-ML regression testing.
17. Full DSA regression testing.
18. C++17 and C++20 verification.
19. Comprehensive Phase 25 review report.
20. Reproducible ZIP review package.
21. SHA-256 checksum.
22. JSON metadata.
23. Machine Learning track completion-readiness assessment.

Do not claim that the entire Machine Learning track has passed its final audit merely because B13 is implemented.

Do not commit, push, tag, release, or begin the next phase without explicit owner authorization.

---

# 1. PHASE 24 OWNER APPROVAL GATE

Before implementation:

1. Inspect the Phase 24 B12 Anomaly Detection review report.
2. Verify the three B12 canonical implementations.
3. Inspect the Phase 24 review package metadata.
4. Verify the actual targeted and regression test evidence.
5. Verify the current catalog statuses.
6. Verify explicit owner approval of the Phase 24 handoff.

Expected report:

`docs/reviews/anomaly-detection/ANOMALY-DETECTION-REVIEW-REPORT.md`

If final owner approval is missing or ambiguous, request confirmation and STOP before changing B13 implementation files.

Do not manufacture approval evidence.

Once the owner checkpoint is satisfied, proceed through all B13 implementation batches without requesting approval after each ordinary batch.

---

# 2. AUTHORITATIVE REPOSITORY DISCOVERY

Read:

- `AGENTS.md`
- `catalog.yaml`
- `README.md`
- `pyproject.toml`
- `conftest.py`
- `.gitignore`
- `.github/workflows/ci.yml`
- `docs/progress.md`
- `docs/learning-roadmap.md`
- `docs/algorithm-index.md`
- `docs/ml-development.md`, if present
- ML dependency files
- Existing DSA implementations
- B1–B12 implementations
- B1–B12 review reports
- B7 Deep Learning implementations
- B8 Reinforcement Learning status records
- B10 Optimization implementations
- B11 Hidden Markov Models
- Existing text-processing utilities
- Existing tokenization utilities
- Existing numerical optimization utilities
- Catalog validators
- Documentation generators
- Review-package conventions

Record:

- Git branch
- HEAD commit
- Working-tree status
- Existing uncommitted modifications
- Python version
- NumPy version
- pytest version
- Available optional reference libraries
- C++ compiler availability
- CI configuration
- Phase 24 approval status

Preserve unrelated owner changes.

Do not use destructive Git cleanup.

---

# 3. EXACT B13 CANONICAL INVENTORY

Verify these entries against the CURRENT `catalog.yaml`:

| # | Canonical ID | Algorithm / Topic |
|---|---|---|
| 1 | `bag-of-words` | Bag of Words |
| 2 | `tf-idf` | TF-IDF |
| 3 | `word2vec` | Word2Vec |
| 4 | `glove` | GloVe |
| 5 | `bert` | BERT Architecture / Usage |
| 6 | `gpt` | GPT Architecture / Usage |
| 7 | `hidden-markov-models-pos-tagging` | Hidden Markov Models for POS Tagging |
| 8 | `named-entity-recognition` | Named Entity Recognition |
| 9 | `conditional-random-fields` | Conditional Random Fields |
| 10 | `n-gram-language-models` | N-Gram Language Models |
| 11 | `cyk-parsing` | CYK Parsing Algorithm |

Expected directories:

```text
machine-learning/natural-language-processing/
├── bag-of-words/
├── tf-idf/
├── word2vec/
├── glove/
├── bert/
├── gpt/
├── hidden-markov-models-pos-tagging/
├── named-entity-recognition/
├── conditional-random-fields/
├── n-gram-language-models/
└── cyk-parsing/
```

Inspect the current implementation, documentation, testing, and catalog status of each entry.

Do not rename canonical IDs.

Do not add algorithms outside B13.

Do not create duplicate canonical implementations.

If the current authoritative catalog differs from this historical inventory, report the discrepancy and follow the current catalog.

---

# 4. CRITICAL SPECIFICATION POLICY

Not every B13 entry represents a single uniquely defined mathematical algorithm.

In particular:

- BERT is an architecture and pretraining framework.
- GPT is an autoregressive Transformer architecture family.
- Named Entity Recognition is a task, not one uniquely defined algorithm.

Treat these distinctions seriously.

Before implementing each of these entries:

1. Identify its canonical educational scope.
2. Define the exact mathematical model.
3. Define the supported training or inference objective.
4. Define its input/output contract.
5. Define what is intentionally unsupported.
6. Identify independent verification methods.

Do not invent undocumented capabilities.

Do not claim a small educational Transformer is equivalent to a production-scale pretrained BERT or GPT.

Do not claim Named Entity Recognition is one universal algorithm.

If a specification cannot be established without changing the syllabus meaning, document the blocker and request owner approval.

Continue unrelated B13 work where permitted.

---

# 5. LANGUAGE AND DEPENDENCY POLICY

For Machine Learning:

Mandatory:

- Python.
- NumPy where appropriate.
- Genuine from-scratch core logic.
- Python tests.
- Mathematical verification.
- Reproducible examples.

Optional:

- C++.
- C++ tests.

Do not create placeholder C++ implementations.

Preserve existing DSA requirements:

- Python mandatory.
- C++ mandatory.
- C++17 verification mandatory.
- C++20 verification mandatory.

Do not delegate core implementations to:

- scikit-learn text vectorizers.
- Gensim Word2Vec or GloVe wrappers.
- Hugging Face Transformer models.
- PyTorch Transformer modules.
- TensorFlow/Keras NLP models.
- NLTK HMM or parsing implementations.
- Ready-made CRF implementations.
- Other complete NLP libraries.

External libraries may be used as independent reference oracles where appropriate.

Core implementations must remain educational and independently understandable.

---

# 6. SHARED TEXT PREPROCESSING CONTRACT

Define explicit text-processing conventions.

Support or document:

- Unicode text.
- Whitespace handling.
- Tokenization.
- Case normalization.
- Punctuation handling.
- Vocabulary construction.
- Unknown tokens.
- Padding tokens.
- Start/end tokens where needed.
- Minimum token frequency.
- Deterministic token ordering.
- Sentence boundaries.
- Document boundaries.
- Sequence truncation.
- Sequence padding.

Do not silently change text normalization between training and inference.

Do not assume whitespace tokenization is universally suitable for every language.

Document the supported language and tokenizer limitations.

Test:

- Empty text.
- Empty documents.
- Repeated tokens.
- Unknown words.
- Unicode characters.
- Mixed case.
- Punctuation.
- Very long sequences.
- Duplicate documents.
- Single-token documents.

Avoid network downloads.

---

# 7. IMPLEMENTATION BATCH PLAN

Use five internal batches.

## Batch 1 — Statistical Text Representation

1. Bag of Words.
2. TF-IDF.
3. N-Gram Language Models.

## Batch 2 — Neural Word Embeddings

4. Word2Vec.
5. GloVe.

## Batch 3 — Transformer Architectures

6. BERT Architecture / Usage.
7. GPT Architecture / Usage.

## Batch 4 — Sequence Labeling

8. Hidden Markov Models for POS Tagging.
9. Conditional Random Fields.
10. Named Entity Recognition.

## Batch 5 — Syntactic Parsing

11. CYK Parsing Algorithm.

For each batch:

1. Inspect existing code.
2. Confirm the mathematical specification.
3. Implement missing core logic.
4. Add independent oracles.
5. Add deterministic tests.
6. Add numerical stability tests.
7. Add edge-case tests.
8. Verify executable examples.
9. Complete documentation.
10. Run targeted tests.
11. Fix confirmed defects.
12. Record actual results.

Proceed automatically between batches after successful validation.

Do not request owner approval after every internal batch.

---

# 8. BAG OF WORDS

Canonical ID:

`bag-of-words`

Implement genuine vocabulary-based document vectorization.

Required:

- Deterministic vocabulary.
- Token counting.
- Document-term matrix.
- Fit operation.
- Transform operation.
- Fit-transform operation.
- Unknown-token handling.
- Consistent vocabulary indexing.

Optional:

- Binary occurrence representation.
- Minimum document frequency.
- Maximum vocabulary size.

Document exact supported options.

Required tests:

- Single document.
- Multiple documents.
- Repeated words.
- Unknown words.
- Empty documents.
- Case normalization.
- Vocabulary ordering.
- Document-term matrix dimensions.
- Exact token counts.
- Deterministic output.

Independent oracle:

Construct small hand-counted document-term matrices.

Do not use scikit-learn CountVectorizer as the production implementation.

---

# 9. TF-IDF

Canonical ID:

`tf-idf`

Implement genuine Term Frequency–Inverse Document Frequency.

Required:

1. Vocabulary construction.
2. Term frequency calculation.
3. Document frequency calculation.
4. Inverse document frequency.
5. TF-IDF weighting.
6. Optional normalization.
7. Fit-transform.
8. Transform on unseen documents.

Define the exact TF and IDF formulas.

A common smoothed IDF is:

idf(t) = log((1 + N) / (1 + df(t))) + 1

But follow the chosen documented convention consistently.

Support and document the normalization convention, such as L2 normalization.

Do not claim that all TF-IDF implementations use identical formulas.

Required tests:

- Exact document frequencies.
- Exact IDF values.
- Repeated tokens.
- Common terms.
- Rare terms.
- Unseen words.
- Empty documents.
- Zero vectors.
- Normalization.
- Training/inference consistency.

Independent oracle:

Hand-calculate a tiny corpus's TF-IDF matrix.

Optional scikit-learn comparison must align smoothing, normalization and TF conventions.

---

# 10. N-GRAM LANGUAGE MODELS

Canonical ID:

`n-gram-language-models`

Implement genuine count-based N-Gram Language Models.

Required:

- Unigram counts.
- Bigram counts.
- General configurable N-Gram order.
- Context counts.
- Conditional probabilities.
- Sentence boundary handling.
- Unknown-token handling.
- Text likelihood.
- Perplexity.
- Next-token prediction.
- Optional token generation.

Implement at least one documented smoothing method, such as add-k smoothing.

If additional smoothing methods are supported, test them separately.

Verify:

- Conditional probability normalization.
- Exact count calculations.
- Correct context windows.
- Correct sequence likelihood.
- Correct log probability.
- Correct perplexity.
- Zero-count handling.
- Deterministic generation with fixed seeds.

Do not calculate perplexity using an inconsistent token count.

Do not leak evaluation text into vocabulary or probability estimation unless explicitly defined by the protocol.

---

# 11. WORD2VEC

Canonical ID:

`word2vec`

Implement genuine Word2Vec embedding learning.

Choose and document at least one valid architecture:

- Skip-Gram.
- Continuous Bag of Words.

A suitable educational baseline is Skip-Gram with Negative Sampling.

Required:

1. Vocabulary construction.
2. Token indexing.
3. Context-window generation.
4. Target-context pairs.
5. Input embeddings.
6. Output embeddings.
7. Positive examples.
8. Negative sampling.
9. Stable sigmoid/log-sigmoid.
10. Training objective.
11. Correct gradients.
12. Parameter updates.
13. Embedding extraction.
14. Fixed-seed reproducibility.

Do not return untrained random vectors.

Do not substitute SVD embeddings and label them Word2Vec.

Required tests:

- Context-pair construction.
- Window boundaries.
- Negative sampling.
- Loss values.
- Analytical gradients.
- Finite-difference gradients.
- Embedding dimensions.
- Parameter updates.
- Tiny-corpus training.
- Reproducibility.
- Unknown words.
- Invalid hyperparameters.

Use small dimensions and tiny corpora for CI.

Evaluate learned embeddings cautiously; identical coordinates are not expected across independently trained models.

---

# 12. GLOVE

Canonical ID:

`glove`

Implement genuine Global Vectors for Word Representation.

Required:

- Corpus co-occurrence matrix.
- Context-window weighting.
- Target embeddings.
- Context embeddings.
- Target biases.
- Context biases.
- GloVe weighting function.
- Weighted least-squares objective.
- Correct gradients.
- Parameter updates.
- Embedding extraction.

A standard GloVe objective is:

J = sum_ij f(X_ij) *
    (w_i.T @ w_tilde_j + b_i + b_tilde_j - log(X_ij))^2

where X_ij is a positive co-occurrence count.

Use a documented weighting function and parameter convention.

Do not calculate log(0).

Do not substitute ordinary co-occurrence counts without training and call them GloVe embeddings.

Required tests:

- Co-occurrence counts.
- Window weighting.
- Symmetric/asymmetric context behavior.
- Weighting function.
- Exact loss.
- Analytical gradients.
- Finite-difference gradients.
- Parameter updates.
- Fixed-seed reproducibility.
- Tiny-corpus training.
- Embedding dimensions.

Compare independent objective calculations, not arbitrary embedding coordinates.

---

# 13. BERT ARCHITECTURE / USAGE

Canonical ID:

`bert`

This is an architecture and usage topic, not an instruction to reproduce a production pretrained model.

Implement a compact, structurally faithful educational BERT-style encoder.

Required architectural components:

1. Token embeddings.
2. Positional embeddings.
3. Segment/type embeddings if included in the chosen specification.
4. Multi-head bidirectional self-attention.
5. Correct attention scaling.
6. Padding attention masks.
7. Residual connections.
8. Layer normalization.
9. Position-wise feed-forward network.
10. Encoder stacking.
11. Contextual token representations.
12. Masked Language Modeling objective.
13. A documented inference example.

Optional:

- Next Sentence Prediction, if explicitly included.
- A small classification head.

Do not claim unsupported pretraining tasks.

Use tiny model dimensions for CI.

Do not download pretrained BERT weights.

## Mathematical requirements

For scaled dot-product attention:

Attention(Q,K,V) =
softmax(QK.T / sqrt(d_k)) V

Implement attention masks correctly.

Bidirectional BERT attention must not accidentally use a GPT-style causal mask.

For Masked Language Modeling:

- Select mask positions according to a documented policy.
- Compute loss only on intended prediction targets.
- Prevent accidental target leakage.
- Verify token-logit dimensions.

If implementing training, provide a genuine parameter-update path and test gradients for the trainable components.

If only a restricted subset is trainable, clearly document which components are frozen and why.

Do not claim full end-to-end pretraining if it is not implemented.

Required tests:

- Embedding shapes.
- Attention scores.
- Attention normalization.
- Padding masks.
- Multi-head splitting/merging.
- Residual connections.
- Layer normalization.
- Encoder output shapes.
- Masked-token selection.
- MLM loss.
- Numerical stability.
- Deterministic initialization.
- Tiny training/inference example.
- Finite-difference checks for implemented trainable operations.

---

# 14. GPT ARCHITECTURE / USAGE

Canonical ID:

`gpt`

Implement a compact educational decoder-only autoregressive Transformer.

Required:

1. Token embeddings.
2. Positional embeddings.
3. Multi-head self-attention.
4. Strict causal attention mask.
5. Residual connections.
6. Layer normalization.
7. Feed-forward network.
8. Decoder block stacking.
9. Next-token prediction head.
10. Autoregressive loss.
11. Token-by-token generation.
12. Deterministic seeded sampling.
13. Context-length validation.

Do not import pretrained GPT weights.

Do not claim production GPT equivalence.

## Critical causal correctness

At position t, the model must not attend to future positions.

Test this explicitly:

- Change a future token.
- Verify earlier-position logits remain unchanged.
- Check causal attention weights.
- Check masked softmax behavior.

A standard next-token objective uses shifted targets.

Verify that the input and target sequences are aligned correctly.

Do not train the model to predict the current token from itself while claiming next-token modeling.

If training is supported, implement a genuine optimization path and test gradients for the trainable components.

Do not claim full end-to-end training when only the output head is updated.

Required tests:

- Causal masks.
- Attention probabilities.
- Decoder shapes.
- Next-token alignment.
- Cross-entropy.
- Deterministic generation.
- Temperature handling.
- Invalid token IDs.
- Context length.
- Numerical stability.
- Tiny-corpus learning behavior.
- Gradient checks for implemented trainable operations.

---

# 15. BERT VS GPT ARCHITECTURAL VERIFICATION

Independently verify the defining differences.

BERT:

- Encoder-only educational architecture.
- Bidirectional self-attention.
- Contextual token representation.
- Masked-token objective.

GPT:

- Decoder-only educational architecture.
- Causal self-attention.
- Autoregressive next-token objective.
- Sequential token generation.

Do not reuse one identical attention mask for both models.

Do not label an ordinary MLP as a Transformer.

Do not present the two models as interchangeable.

A shared attention utility is acceptable only if the correct masking semantics are preserved and independently tested.

---

# 16. HMM FOR POS TAGGING

Canonical ID:

`hidden-markov-models-pos-tagging`

This is an application-specific variant of Hidden Markov Models.

Inspect the B11 canonical HMM implementation first.

Preserve B11's canonical ownership.

Implement the POS tagging pipeline with:

- Tokenized sentences.
- Tag vocabulary.
- Initial tag probabilities.
- Tag transition probabilities.
- Word emission probabilities.
- Supervised parameter estimation.
- Unknown-word handling.
- Log-space Viterbi decoding.
- Sentence tagging.
- Tagging evaluation.

Optional:

- Forward-backward posterior tag probabilities.

Do not merely copy the B11 HMM implementation into B13.

Reuse mathematically sound shared utilities where appropriate.

Required tests:

- Hand-tagged tiny corpus.
- Initial tag counts.
- Transition counts.
- Emission counts.
- Unknown words.
- Sentence boundaries.
- Viterbi decoding.
- Log probability.
- Invalid tags.
- Empty sentences.
- Deterministic output.
- B11 HMM compatibility.

Independent oracle:

Enumerate all tag sequences on tiny sentences and verify the best sequence against Viterbi.

---

# 17. CONDITIONAL RANDOM FIELDS

Canonical ID:

`conditional-random-fields`

Implement a genuine linear-chain Conditional Random Field for sequence labeling.

Required:

1. Label vocabulary.
2. Emission feature scores.
3. Transition scores.
4. Sequence score.
5. Log-partition function.
6. Forward dynamic programming.
7. Backward dynamic programming.
8. Conditional log-likelihood.
9. Correct parameter gradients.
10. Parameter optimization.
11. Viterbi decoding.
12. Sequence prediction.

Define start/end transition handling.

Define the supported feature representation.

Use stable log-sum-exp calculations.

Do not substitute a generative HMM and call it a CRF.

Do not substitute independent per-token classification and claim structured prediction.

## Independent oracles

For tiny sequences:

- Enumerate every possible label sequence.
- Calculate the exact partition function.
- Calculate exact sequence probabilities.
- Calculate the maximum-scoring label sequence.
- Compare with forward, backward and Viterbi algorithms.
- Check analytical gradients with finite differences.

Required tests:

- One-token sequence.
- Two-token sequence.
- Multiple labels.
- Transition scores.
- Emission scores.
- Log-partition.
- Log-likelihood.
- Gradients.
- Viterbi path.
- Padding and sequence lengths.
- Invalid labels.
- Numerical stability.
- Deterministic training.

---

# 18. NAMED ENTITY RECOGNITION

Canonical ID:

`named-entity-recognition`

Named Entity Recognition is a task, not a single uniquely defined algorithm.

Before implementation, choose and document one explicit educational baseline.

A suitable choice is:

- Token-level features.
- BIO tagging scheme.
- Linear-chain CRF sequence model.

If another model is chosen, justify it.

Do not present the chosen baseline as the only possible NER algorithm.

Required:

1. Tokenization.
2. Entity label vocabulary.
3. BIO or another explicitly defined tagging scheme.
4. Sequence labeling.
5. Training data representation.
6. Inference.
7. Entity-span extraction.
8. Unknown-token behavior.
9. Exact-span evaluation.
10. Reproducible examples.

If reusing the B13 CRF:

- Preserve the CRF's canonical implementation.
- Add genuine NER-specific preprocessing.
- Add task-specific features.
- Add entity-span decoding.
- Add NER evaluation.
- Avoid duplicate CRF mathematical implementations.

Required tests:

- Single-token entities.
- Multi-token entities.
- Adjacent entities.
- No-entity sentences.
- Invalid BIO transitions.
- Unknown words.
- Sentence boundaries.
- Span extraction.
- Precision.
- Recall.
- F1.
- Deterministic output.

Clearly distinguish token-level accuracy from entity-level exact-match F1.

---

# 19. CYK PARSING ALGORITHM

Canonical ID:

`cyk-parsing`

Implement genuine Cocke–Younger–Kasami parsing for context-free grammars in Chomsky Normal Form.

Required:

1. Grammar representation.
2. Terminal productions.
3. Binary nonterminal productions.
4. CNF validation.
5. Dynamic programming chart.
6. Substring span handling.
7. Grammar rule application.
8. Recognition result.
9. Backpointer reconstruction.
10. Parse-tree output where supported.

Do not silently accept arbitrary CFG rules while claiming CNF correctness.

If grammar conversion is supported, implement and test it separately.

Define epsilon-production handling and empty-string behavior explicitly.

## Mathematical verification

For a sequence of length n, use the correct dynamic programming spans and split points.

Verify that a nonterminal A derives a span if a production A -> BC exists and the span can be split into a left span derived by B and a right span derived by C.

Required tests:

- Single terminal.
- Two-token sentence.
- Three-token sentence.
- Ambiguous grammar.
- Unparseable sentence.
- Invalid grammar.
- Invalid CNF production.
- Unknown terminals.
- Empty input.
- Backpointer correctness.
- Parse-tree correctness.
- Deterministic output.

Independent oracle:

For tiny grammars and short sentences, independently enumerate derivations and compare recognition results.

Do not use the production CYK chart as its sole oracle.

---

# 20. CROSS-ALGORITHM INTEGRATION

Verify meaningful relationships:

- Bag of Words → TF-IDF.
- N-Gram Models → language modeling.
- Word2Vec → local-context embeddings.
- GloVe → global co-occurrence embeddings.
- BERT → bidirectional contextual representations.
- GPT → causal autoregressive representations.
- B11 HMM → B13 POS tagging.
- B13 CRF → B13 NER.
- CYK → grammar-based syntactic parsing.

Do not duplicate canonical algorithms unnecessarily.

Do not introduce circular imports.

Shared utilities must have dedicated tests.

Preserve previous approved implementations.

---

# 21. NUMERICAL STABILITY

Audit:

- Softmax overflow.
- Logarithm of zero.
- Sigmoid overflow.
- Log-sum-exp.
- Zero token counts.
- Empty vocabulary.
- Unknown tokens.
- Zero-length sequences.
- Invalid token IDs.
- Embedding overflow.
- Exploding gradients.
- Invalid attention masks.
- All-masked attention rows.
- Zero probabilities.
- Underflow in HMM inference.
- Underflow in CRF partition calculations.
- Invalid grammar chart indices.
- Excessive sequence lengths.
- Excessive memory allocation.

Use stable mathematical formulations.

Do not silently replace NaNs with arbitrary values.

Bound all training loops and sequence lengths.

---

# 22. INDEPENDENT ORACLE REQUIREMENTS

Use a separate mathematical oracle for each algorithm.

| Algorithm | Independent verification |
|---|---|
| Bag of Words | Hand-counted document-term matrix |
| TF-IDF | Hand-computed TF, DF, IDF and normalization |
| Word2Vec | Independent loss and finite-difference gradients |
| GloVe | Independent co-occurrence objective and gradients |
| BERT | Independent attention, masking and MLM calculations |
| GPT | Independent causal attention and next-token loss |
| HMM POS | Exhaustive tag-sequence enumeration |
| NER | Independent BIO span extraction and exact-match metrics |
| CRF | Exhaustive label-sequence partition and Viterbi oracle |
| N-Gram | Hand-counted conditional probabilities and perplexity |
| CYK | Independent tiny-grammar derivation enumeration |

Do not use production helpers as the sole oracles.

Do not claim an empirical learning result proves mathematical correctness.

---

# 23. GRADIENT CHECKING

For trainable neural or probabilistic models, verify implemented gradients using finite differences.

Apply where relevant:

- Word2Vec.
- GloVe.
- BERT trainable components.
- GPT trainable components.
- CRF.

Use central differences on tiny deterministic problems.

Freeze stochastic sampling during checks.

Avoid nondifferentiable points where possible.

Use appropriate absolute and relative tolerances.

Report which parameter groups were actually checked.

Do not claim complete gradient coverage when only one output layer was checked.

---

# 24. REPRODUCIBILITY AND DATA LEAKAGE

Use local random generators.

Fix seeds for mandatory tests.

Avoid global RNG mutation.

Separate:

- Training corpus.
- Validation corpus.
- Test corpus.

Fit vocabulary and learned parameters only on permitted training data.

Do not train on test labels.

Do not use future tokens in GPT's causal prediction.

Do not leak gold POS or NER tags into prediction features.

Do not use held-out corpus counts in TF-IDF IDF estimation.

Do not use evaluation sentences to fit an N-Gram model unless explicitly part of the training protocol.

Document all evaluation boundaries.

---

# 25. PERFORMANCE AND RESOURCE LIMITS

Keep mandatory tests CPU-friendly.

Use:

- Tiny vocabularies.
- Tiny embedding dimensions.
- Short sequences.
- Few Transformer layers.
- Few attention heads.
- Small training datasets.
- Bounded epochs.
- Bounded beam or decoding sizes where applicable.

Do not require:

- GPUs.
- Pretrained model downloads.
- Large language model checkpoints.
- Internet access.
- Massive text corpora.

Document algorithmic complexity.

For Transformers, discuss the quadratic sequence-length cost of dense self-attention.

For CYK, discuss cubic dependence on sentence length under standard formulations, with grammar-size factors made explicit.

For HMM and CRF, document dependence on sequence length and label/state count.

Benchmark only with actual measurements.

---

# 26. EDUCATIONAL EXAMPLES

Create one runnable example for each canonical entry.

Examples must demonstrate:

- Inputs.
- Model configuration.
- Training or fitting where relevant.
- Inference.
- Outputs.
- Mathematical interpretation.
- Limitations.

Use small synthetic or locally embedded datasets.

Do not download external datasets.

Do not fabricate example outputs.

For BERT and GPT, show small educational architecture behavior, not misleading claims of pretrained language understanding.

For NER and POS tagging, use explicitly labeled toy datasets.

For CYK, show a tiny grammar and parse tree.

---

# 27. DOCUMENTATION REQUIREMENTS

Every B13 canonical algorithm must follow the exact 25-section README structure required by `AGENTS.md`.

Do not reorder headings.

Document:

- Problem definition.
- Mathematical formulation.
- Assumptions.
- Inputs and outputs.
- Core data structures.
- Pseudocode.
- Correctness reasoning.
- Time complexity.
- Space complexity.
- Numerical stability.
- Training objective.
- Hyperparameters.
- Worked example.
- Python implementation.
- Independent verification.
- Testing methodology.
- Applications.
- Limitations.
- Related algorithms.
- References.

For BERT, GPT and NER, explicitly document the selected educational scope.

Do not claim production parity.

Do not create fake C++ files.

---

# 28. CATEGORY README

Create or update:

`machine-learning/natural-language-processing/README.md`

Include:

1. NLP introduction.
2. Exact 11-entry inventory.
3. Text preprocessing.
4. Vocabulary construction.
5. Statistical text representations.
6. N-Gram language modeling.
7. Neural word embeddings.
8. Transformer architectures.
9. BERT versus GPT.
10. Probabilistic sequence models.
11. POS tagging.
12. CRF.
13. NER.
14. Context-free grammar parsing.
15. Evaluation methods.
16. Numerical stability.
17. Computational complexity.
18. Algorithm comparison.
19. Learning roadmap.
20. Canonical implementation links.

Do not duplicate full algorithm implementations in the category README.

---

# 29. CATALOG AND PROGRESS INTEGRATION

Update relevant records:

- `catalog.yaml`
- `docs/progress.md`
- `docs/learning-roadmap.md`
- `docs/algorithm-index.md`
- B13 category README
- Root README where necessary

Preserve:

- All DSA canonical implementations.
- B1–B12 canonical implementations.
- Previous owner approvals.
- Existing canonical IDs.
- Existing canonical paths.
- Shared canonical memberships.
- Previous review reports.
- Explicitly blocked entries.

The B8 Dynamic Policy Optimization entry must remain blocked under the earlier owner-approved decision.

Do not rename, replace, or implement DPO during Phase 25.

Do not mark Phase 25 owner-approved.

---

# 30. TARGETED TESTING

Run:

```bash
python -m pytest machine-learning/natural-language-processing -q
```

Also execute dedicated checks for:

- Tokenization.
- Vocabulary consistency.
- BoW exact counts.
- TF-IDF exact weights.
- N-Gram conditional probabilities.
- N-Gram perplexity.
- Word2Vec loss and gradients.
- GloVe objective and gradients.
- BERT attention masks.
- BERT MLM loss.
- GPT causal masking.
- GPT next-token alignment.
- HMM POS decoding.
- CRF forward-backward.
- CRF Viterbi.
- CRF gradients.
- NER BIO decoding.
- NER entity-level metrics.
- CYK grammar validation.
- CYK recognition and parse trees.
- Numerical stability.
- Reproducibility.
- Invalid inputs.

Do not weaken assertions merely to make tests pass.

---

# 31. FULL REGRESSION TESTING

Run appropriate regression checks across:

- B1 Regression.
- B2 Classification.
- B3 Ensemble Methods.
- B4 Clustering.
- B5 Dimensionality Reduction.
- B6 Association Rule Learning.
- B7 Neural Networks and Deep Learning.
- B8 Reinforcement Learning.
- B9 Graph-Based Learning.
- B10 Optimization.
- B11 Time Series.
- B12 Anomaly Detection.
- B13 Natural Language Processing.
- DSA Python.
- DSA C++17.
- DSA C++20.
- Shared infrastructure.
- Catalog validation.
- Documentation generation.
- CI-equivalent behavior.

Pay particular attention to:

- B11 HMM compatibility.
- B7 neural network compatibility.
- B10 optimizer compatibility.
- Shared numerical utilities.
- Shared text-processing utilities.

Do not silently modify previously approved algorithms.

---

# 32. REQUIRED VALIDATION COMMANDS

Execute:

```bash
python scripts/validate_catalog.py
python scripts/generate_catalog_docs.py --check
python -m pytest --require-cpp
```

Run targeted B13 tests separately.

If the full suite cannot finish:

1. Split it into bounded groups.
2. Execute every feasible group.
3. Record exact commands.
4. Record actual pass/fail/skip counts.
5. Identify unexecuted checks.
6. Explain environmental limitations.

Never claim unexecuted tests passed.

Verify C++17 and C++20 using the repository's actual DSA testing policy.

---

# 33. NEGATIVE INFRASTRUCTURE TESTS

Verify:

- Missing required ML Python implementations are rejected.
- Missing ML Python tests are rejected.
- Invalid canonical paths are rejected.
- Duplicate canonical IDs are rejected.
- Missing README sections are detected.
- Generated documentation drift is detected.
- B13 tests are discovered by CI.
- Optional ML C++ follows repository policy.
- Missing mandatory DSA C++ is rejected.
- C++17 and C++20 requirements remain enforced.
- Existing blocked catalog entries remain valid.

Do not weaken validators.

---

# 34. SECURITY AND RESOURCE AUDIT

Check for:

- Unbounded training loops.
- Unbounded token generation.
- Excessive sequence lengths.
- Excessive vocabulary allocation.
- Excessive attention matrices.
- Unsafe serialization.
- Arbitrary code execution.
- Hidden network calls.
- Pretrained model downloads.
- Unsafe file paths.
- Hardcoded credentials.
- Global RNG mutation.
- Accidental logging of sensitive text.

Use small deterministic datasets.

Keep all mandatory checks offline and CPU-friendly.

---

# 35. PHASE 25 REVIEW REPORT

Create:

`docs/reviews/natural-language-processing/NATURAL-LANGUAGE-PROCESSING-REVIEW-REPORT.md`

Include:

1. Phase identity.
2. B13 category identity.
3. Exact 11-entry inventory.
4. Canonical paths.
5. Existing versus new implementations.
6. Bag of Words correctness.
7. TF-IDF correctness.
8. N-Gram correctness.
9. Word2Vec correctness.
10. Word2Vec gradient verification.
11. GloVe correctness.
12. GloVe gradient verification.
13. BERT architecture scope.
14. BERT attention and MLM verification.
15. GPT architecture scope.
16. GPT causal-mask verification.
17. GPT next-token objective verification.
18. HMM POS correctness.
19. B11 HMM compatibility.
20. CRF correctness.
21. CRF partition-function verification.
22. CRF gradient verification.
23. NER baseline specification.
24. NER span-level evaluation.
25. CYK correctness.
26. CYK independent parsing oracle.
27. Independent mathematical oracles.
28. Numerical stability.
29. Reproducibility.
30. Data leakage audit.
31. Educational examples.
32. Documentation validation.
33. Catalog validation.
34. B1–B12 regression results.
35. DSA regression results.
36. C++17/C++20 results.
37. CI-equivalent checks.
38. Shared utility compatibility.
39. Files created.
40. Files modified.
41. Dependencies.
42. Bugs discovered.
43. Fixes applied.
44. Known limitations.
45. Unresolved blockers.
46. Exact reproduction commands.
47. Review package paths.
48. B Track completion-readiness assessment.
49. Owner approval: pending.

Use actual test results.

Do not fabricate counts, gradients, benchmarks, or mathematical evidence.

---

# 36. PHASE 25 REVIEW PACKAGE

Create:

```text
artifacts/review-packages/natural-language-processing/
├── algorithm-atlas-natural-language-processing-review.zip
├── algorithm-atlas-natural-language-processing-review.zip.sha256
└── algorithm-atlas-natural-language-processing-review.json
```

Include:

- All 11 B13 canonical implementations.
- All B13 tests.
- All B13 algorithm READMEs.
- B13 category README.
- Phase 25 review report.
- Relevant shared NLP utilities.
- Relevant B11 HMM source and tests.
- Relevant B7 deep learning source and tests.
- Relevant B10 optimizer source and tests.
- Relevant previous ML implementations.
- Relevant DSA implementations.
- `AGENTS.md`.
- `catalog.yaml`.
- Root `README.md`.
- `pyproject.toml`.
- `conftest.py`.
- Dependency configuration.
- Validation scripts.
- Documentation generators.
- CI configuration.

Exclude:

- `.git`.
- Virtual environments.
- Python caches.
- pytest caches.
- Compiled binaries.
- Secrets.
- Large datasets.
- Pretrained weights.
- Model checkpoints.
- Historical review ZIPs.
- Nested ZIPs.
- Temporary files.

Verify:

1. ZIP opens.
2. ZIP CRC passes.
3. Extraction paths are safe.
4. Required files exist.
5. SHA-256 matches.
6. JSON metadata matches.
7. Independent extraction succeeds.
8. Catalog validation runs from extracted source.
9. Documentation validation runs from extracted source.
10. Relevant tests run from extracted source.

Record any verification steps that could not execute.

---

# 37. MACHINE LEARNING B TRACK COMPLETION-READINESS ASSESSMENT

This is the final B category, so add a separate track-readiness section to the Phase 25 review report.

Inspect all B categories:

- B1 Regression.
- B2 Classification.
- B3 Ensemble Methods.
- B4 Clustering.
- B5 Dimensionality Reduction.
- B6 Association Rule Learning.
- B7 Neural Networks and Deep Learning.
- B8 Reinforcement Learning.
- B9 Graph-Based Learning.
- B10 Optimization.
- B11 Time Series.
- B12 Anomaly Detection.
- B13 Natural Language Processing.

Produce a category-level status table:

| Category | Catalog entries | Implemented | Blocked | Tests | Documentation | Owner approval |
|---|---|---|---|---|---|---|

Calculate actual totals from the CURRENT catalog.

Do not reuse stale historical totals.

Distinguish:

- Implemented canonical algorithms.
- Shared canonical memberships.
- Blocked canonical algorithms.
- Missing implementations.
- Missing documentation.
- Failed tests.
- Pending owner approvals.

Important:

The B8 Dynamic Policy Optimization entry remains intentionally blocked.

Do not mark the entire B Track as 100% implemented if DPO or another canonical entry remains blocked.

A track can be ready for final review while containing explicitly approved blocked items.

Report this accurately.

Do not silently reopen DPO.

---

# 38. FINAL ML AUDIT RECOMMENDATION

After Phase 25, recommend a separate:

**Machine Learning B Track — Final Comprehensive Audit**

That later audit should cover:

- All B1–B13 categories.
- All canonical ML algorithms.
- Shared canonical memberships.
- Mathematical correctness.
- Independent oracles.
- Numerical stability.
- Test coverage.
- Documentation quality.
- Catalog integrity.
- CI behavior.
- Dependency consistency.
- Reproducibility.
- Security.
- Packaging.
- Owner-approved blockers.
- Final owner sign-off.

Do not execute a separate final-audit phase unless the owner authorizes it.

Do not begin C1 during Phase 25.

---

# 39. FINAL PHASE 25 COMPLETION SUMMARY

Present:

| Field | Result |
|---|---|
| Phase | 25 |
| Category | B13 — Natural Language Processing |
| Catalog entries | 11 |
| Implemented entries | Actual count |
| Incomplete entries | Actual count |
| Blocked entries | Actual count |
| Completed batches | Actual count |
| Bag of Words tests | Actual results |
| TF-IDF tests | Actual results |
| N-Gram tests | Actual results |
| Word2Vec tests | Actual results |
| Word2Vec gradient checks | Actual results |
| GloVe tests | Actual results |
| GloVe gradient checks | Actual results |
| BERT tests | Actual results |
| BERT masking and MLM | Actual results |
| GPT tests | Actual results |
| GPT causal masking | Actual results |
| HMM POS tests | Actual results |
| CRF tests | Actual results |
| CRF gradient checks | Actual results |
| NER tests | Actual results |
| CYK tests | Actual results |
| Independent oracles | Actual results |
| Numerical stability | Actual results |
| Reproducibility | Actual results |
| Data leakage audit | Actual result |
| B1–B12 regression | Actual results |
| DSA regression | Actual results |
| C++17/C++20 | Actual results |
| Catalog validation | Actual result |
| Documentation validation | Actual result |
| CI-equivalent checks | Actual result |
| B8 DPO blocked status | Preserved |
| B Track completion-readiness | Actual assessment |
| Review report | Exact path |
| Review ZIP | Exact path |
| SHA-256 | Exact path |
| JSON metadata | Exact path |
| Owner approval | Pending |

Also provide a per-algorithm table:

| Algorithm | Implementation | Tests | Oracle | Documentation | Status |
|---|---|---|---|---|---|

List:

- Completed algorithms.
- Incomplete algorithms.
- Blocked algorithms.
- Failed tests.
- Skipped tests.
- Unexecuted checks.
- Numerical limitations.
- Architectural limitations.
- Training limitations.
- Dependency changes.
- Infrastructure changes.
- Exact reproduction commands.

Do not claim 11/11 complete unless all mandatory requirements have actually been met.

---

# 40. MANDATORY STOP CONDITION

After completing Phase 25 implementation, tests, documentation, and review artifacts:

**STOP AND WAIT FOR EXPLICIT OWNER REVIEW AND APPROVAL.**

Do not:

- Start Phase 26.
- Start C1 Uninformed Search.
- Start the final ML audit without authorization.
- Commit.
- Push.
- Tag.
- Release.
- Publish.
- Mark Phase 25 owner-approved.
- Modify the B8 DPO decision.
- Invent additional canonical algorithms.
- Hide failed tests.
- Fabricate verification results.

The owner will review the final B13 report and review ZIP.

---

# 41. EXECUTION ORDER

STEP 1 — Verify Phase 24 owner approval.

STEP 2 — Inspect current repository and catalog.

STEP 3 — Verify all 11 B13 canonical entries.

STEP 4 — Implement Bag of Words, TF-IDF, and N-Gram Language Models.

STEP 5 — Implement Word2Vec and GloVe.

STEP 6 — Implement a mathematically specified educational BERT architecture.

STEP 7 — Implement a mathematically specified educational GPT architecture.

STEP 8 — Implement HMM-based POS tagging.

STEP 9 — Implement linear-chain CRF.

STEP 10 — Implement a clearly specified NER baseline.

STEP 11 — Implement CYK Parsing.

STEP 12 — Run independent mathematical oracles.

STEP 13 — Run gradient verification.

STEP 14 — Run numerical stability, reproducibility, and data leakage tests.

STEP 15 — Complete all exact 25-section READMEs.

STEP 16 — Update category documentation and catalog records.

STEP 17 — Run targeted B13 tests.

STEP 18 — Run full B1–B13 regression checks.

STEP 19 — Run DSA Python, C++17, and C++20 regression checks.

STEP 20 — Run catalog, documentation, and CI-equivalent validation.

STEP 21 — Generate Phase 25 review report.

STEP 22 — Generate and verify ZIP, SHA-256, and JSON metadata.

STEP 23 — Produce B Track completion-readiness assessment.

STEP 24 — Present final results.

STEP 25 — STOP for owner review.

Do not request approval between ordinary implementation batches.

Ask for owner input only when a genuine approval, mathematical specification, or catalog ambiguity requires it.

**BEGIN PHASE 25 ONLY AFTER SATISFYING THE PHASE 24 OWNER APPROVAL CHECKPOINT.**