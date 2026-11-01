# GPT Architecture / Usage

## 1. Algorithm Name

GPT-style decoder-only autoregressive Transformer, scoped to causal architecture inspection, shifted next-token modeling and bounded generation with a trained vocabulary head. GPT names an architecture family; this compact model is not equivalent to a production pretrained GPT.

## 2. Overview

A prefix determines a distribution over its next token. Strict causal attention allows each contextual state to see only its current input and earlier inputs. Training predicts the following token, and generation extends a prefix one sampled token at a time. Only the output head is optimized.

## 3. Problem Statement

IDs are explicit: PAD=0, UNK=1, BOS=2, EOS=3, MASK=4; ordinary IDs are5..V-1. V is6..128. Shared text Vocabulary instead reserves UNK at0: adapt known shared IDs to id+4 and unknown0 to1, never silently treat its IDs as padded neural IDs. For this adapter use shared Vocabulary(max_size<=124), because adding four reserved slots must still fit the neural V<=128 bound. Unicode tokenization/vocabulary fitting follows [B13 contracts](../../../docs/natural-language-processing-conventions.md). Integer-ID batches are B by T, B1..16; boolean and mixed boolean IDs, floats, negative/out-of-vocabulary IDs, empty/all-padding rows and left/interior padding are rejected. Text is tokenized before these models; vocabulary is fit on permitted training text only. No silent truncation. GPT(vocab_size,d_model=8,heads=2,ff_dim=16,layers=1,max_length=32,random_state=0) exposes encode/logits as(B,T,d)/(B,T,V). fit/loss receive full sequences of length2..max_length+1,each with at least two nonpadding tokens. After shifting, encoded inputs fit max_length.

## 4. Why Do We Need This Algorithm?

A left-to-right factorization supports sequence likelihood and next-token generation without using future tokens. Explicit shift and causal-mask checks prevent the easy but incorrect objective of predicting the current input token from itself.

## 5. Real-World Applications

Small autoregressive language-model demonstrations,token-generation mechanics and causal tensor verification. Large pretrained decoders support broader text tasks after substantial training; the frozen random-feature model here makes no such capability or deployment claim.

## 6. Core Intuition

At each position add its token-table vector to its absolute position-table vector. Both tables and all attention/FFN/normalization parameters are **frozen at initialization**. They are parameterized embedding tables, not learned language knowledge. Each block computes Q=XWq+bq,K=XWk+bk,V=XWv+bv, splits width across heads, and applies softmax(QKᵀ/sqrt(d_head))V under the proper mask. Merge heads, apply an output projection, add the residual and layer-normalize. Apply a position-wise two-layer FFN with the explicit tanh approximation GELU(x)=.5x[1+tanh(sqrt(2/pi)(x+.044715x³))], add its residual and layer-normalize again. Stack1..3 blocks. Padding keys are excluded and padded query/context rows are zero; all-masked attention rows fail explicitly. Layer norm uses variance across width and epsilon1e-5, inherited unchanged from B7. GPT additionally restricts attention from position i to key positions j<=i. With shifted targets, state i predicts original token i+1,which is outside its accessible input prefix. This prevents future-token leakage across every stacked block.

## 7. Prerequisites

Prerequisites: vocabulary IDs,[N-gram causal probability models](../n-gram-language-models/README.md), softmax/cross-entropy, matrix products and [B7 Transformers](../../deep-learning/transformers/README.md). Generation is sampling,not a guarantee of grammatical or meaningful text.

## 8. Step-by-Step Working Process

Validate full training IDs and right padding. Form inputs=sequence[:,:-1],targets=sequence[:,1:]. Exclude targets equal to PAD. Encode inputs with causal+padding masks and minimize mean next-token CE over the remaining events. Head W,b receive full-batch gradient descent; frozen representations are cached once. A repeated fit resets head initialization. Each successful update remains finite and only a completed local run replaces fitted head/history state.

## 9. Pseudocode

```text
X <- full_sequence without its final column
y <- full_sequence without its first column
H <- frozen causal Transformer(X)
selected <- (y != PAD)
repeat bounded head epochs:
    optimize mean CE(H[selected] W + b, y[selected])
generate:
    logits <- model(prefix)[last position]
    remove PAD/BOS/MASK from sampling candidates
    sample renormalized softmax(logits/temperature)
    append token; stop on EOS or token budget
```

For M valid events, CE=-sum logP(y)/M; dW=Hᵀ(P-one_hot(y))/M,db=sum(P-one_hot(y))/M. Only W,b gradients are implemented/claimed.

## 10. Dry Run

Training row[2,6,5,6,5,3] gives input[2,6,5,6,5] and target[6,5,6,5,3]. Position0 sees only BOS2 and predicts red6; position1 sees BOS2,red6 and predicts blue5. EOS contributes one target. PAD targets are excluded from both sum and denominator. Changing input positions2 onward must leave logits at positions0 and1 unchanged.

## 11. Time Complexity

Let B=batch size,T=context length,d=model width,f=FFN width,L=block count,h=head count,V=vocabulary size,M=scored targets,E=head epochs. Backbone time is O(LB(Td²+T²d+Tdf)); dense attention is quadratic in T. Full logits cost O(BTdV). Because the backbone is frozen, training caches representations once and costs O(LB(Td²+T²d+Tdf)+EMdV). The same dense calculation applies in best/average/worst cases for fixed shapes; masks change semantics rather than creating a sparse speedup. Generation recomputes each prefix,without a KV cache: G generated steps cost O(sum_g LB(t_g*d²+t_g²*d+t_g*d*f)+B*t_g*d*V) for increasing prefix lengths t_g.

## 12. Space Complexity

Parameters use O(Vd+Tmax*d+L(d²+df)+dV). Forward auxiliary space is O(BTd+BhT²+BTf), with O(LBhT²) retained only when requesting all layer attention diagnostics. Head training caches O(BTd) contextual states and O(MV+Md+dV) temporary head arrays; no backbone backward graph is stored. Python recursion and unbounded search are absent. Generation retains the prefix/output of length<=max_length and one step's forward arrays; no beam tree or KV cache is claimed.

## 13. Python Implementation

The [solution](python/solution.py) specializes the [shared token Transformer](../transformer_support.py). That helper reuses the approved [B7 Transformer layer normalization](../../deep-learning/transformers/python/solution.py) unchanged. Read the [canonical tests](tests/test_python.py) and [shared component oracles](../tests/test_transformer_contracts.py). NumPy performs the stated operations directly; no framework or complete NLP library supplies the model.

## 14. C++ Implementation

ML C++ is optional and is not implemented for this topic. No placeholder source, compiler pass or production implementation is claimed. Existing DSA C++17/C++20 requirements remain unchanged.

## 15. Input and Output Examples

Run from repository root:

```sh
.venv/bin/python machine-learning/natural-language-processing/gpt/python/example.py
.venv/bin/python -m pytest machine-learning/natural-language-processing/gpt machine-learning/natural-language-processing/tests/test_transformer_contracts.py -q
```

Actual locally executed output:

```json
{"training": ["red blue red blue", "red blue red blue"], "ordinary_ids": {"blue": 5, "red": 6}, "training_ids": [[2, 6, 5, 6, 5, 3], [2, 6, 5, 6, 5, 3]], "scored_next_tokens": 10, "loss_start": 1.9766715114039162, "loss_final": 0.07152056668446725, "prefix": [2, 6], "generated_ids": [2, 6, 5, 6, 5, 3], "generated_tokens": ["<BOS>", "red", "blue", "red", "blue", "<EOS>"], "trained_parameters": ["head_weight", "head_bias"], "backbone": "frozen random initialization"}
```

## 16. Edge Cases

Context and generation bounds are checked before sampling: prefix_length+max_new_tokens<=max_length,max_new_tokens0..32. Prefix is one nonpadding integer sequence; zero generated tokens returns an owned copy. EOS-ending prefixes stop immediately. Sampling excludes PAD,BOS,MASK and renormalizes over UNK,EOS and ordinary tokens,then stops when EOS is emitted. Temperature is finite1e-6..100; local random_state controls sampling. Very short/all-padding/invalid training rows and boolean/mixed-boolean IDs fail explicitly.

## 17. Advantages

Causal future-token interventions,manual shifted CE and scalar attention oracles verify distinct mechanisms. Every trained head weight/bias has a central finite-difference check. Tests verify seeded generation against an independently calculated legal sampling distribution,not only repeated outputs.

## 18. Disadvantages and Limitations

d_model2..16, heads1..4 dividing width, ff_dim2..32, layers1..3, max_length1..32, private random_state0..2³²-1. Training uses epochs1..500, learning_rate1e-6..1, with epochs*selected_events*d_model*V<=2e7. No dropout, segment embeddings, NSP, subword/WordPiece/BPE tokenizer, pretrained weights, optimizer state/checkpoint serialization, GPU or network dependency. Finite parameter magnitudes are bounded by1e6; invalid or nonfinite calculations fail rather than replacing NaNs. The fixed epoch budget is not a convergence certificate. This is a post-norm GELU decoder teaching subset,not a byte-identical reproduction of any GPT version. No tied token/output weights,dropout,full-backbone gradients,KV caching or pretrained behavior. Legal-token filtering changes the generation distribution by explicit conditional renormalization; raw logits still cover all V IDs. Toy head-loss reduction does not establish fluent generation or held-out generalization.

## 19. When to Use It

Use to audit next-token alignment,causal attention,head optimization and bounded temperature sampling on a tiny local corpus. Keep training vocabulary/parameters separate from evaluation text.

## 20. When Not to Use It

Do not use as a production generator,compare raw toy loss with unrelated tokenization/vocabularies,or claim full end-to-end pretraining. Do not predict the current input token while reporting next-token loss,or permit a decoder to attend to future positions.

## 21. Comparison With Related Algorithms

| Model | Accessible context | Prediction objective | Sequential generation |
|---|---|---|---|
| GPT-style | Prefix/current input | Next token | Yes,bounded seeded sampling |
| BERT-style | Both sides of a hidden target | Selected masked token | No autoregressive claim |
| N-gram | Last n-1 tokens | Smoothed count probability | Yes,finite-context sampling |

The small GPT/BERT share genuine block operations but use different masks and target construction.

## 22. Interview Questions

Why shift by one? Input position i predicts original token i+1. What does causal masking alone fail to fix? A wrong current-token target still leaks itself. Why filter PAD at generation? It is a batching symbol rather than a token to extend a real prefix. Which parameters train? Only the vocabulary head,not embeddings/attention/FFN/norms.

## 23. Practice Problems

Independently compute CE for one shifted row; intervene on a future token and prove earlier logits unchanged; reproduce one seeded legal-token sample; compare temperature values without refitting vocabulary; add a separately specified KV cache and test parity before claiming its speedup.

## 24. References

[Radford, Narasimhan, Salimans and Sutskever, Improving Language Understanding by Generative Pre-Training (2018)](https://cdn.openai.com/research-covers/language-unsupervised/language_understanding_paper.pdf). [Vaswani et al., Attention Is All You Need (2017)](https://arxiv.org/abs/1706.03762). The frozen-head-only teaching scope,special-token sampling restriction and bounded architecture are explicit local choices.

## 25. Author Attribution

Owner and maintainer: **[MD.Khalid Hasan](https://github.com/khalidhasan7343)**. [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas); [MIT license](../../../LICENSE); [contribution policy](../../../CONTRIBUTING.md). Attribution and licensing remain preserved.

