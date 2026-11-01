# BERT Architecture / Usage

## 1. Algorithm Name

BERT-style bidirectional Transformer encoder, scoped to architecture inspection and masked-language modeling (MLM) with a trained linear head. BERT is an architecture/pretraining framework, not one universal algorithm or a claim of pretrained language understanding.

## 2. Overview

A token representation can depend on both earlier and later visible tokens. This implementation teaches genuine multi-head contextual computation and a masked-token objective on tiny local data. Only the vocabulary head is optimized; every backbone parameter remains fixed.

## 3. Problem Statement

IDs are explicit: PAD=0, UNK=1, BOS=2, EOS=3, MASK=4; ordinary IDs are5..V-1. V is6..128. Shared text Vocabulary instead reserves UNK at0: adapt known shared IDs to id+4 and unknown0 to1, never silently treat its IDs as padded neural IDs. For this adapter use shared Vocabulary(max_size<=124), because adding four reserved slots must still fit the neural V<=128 bound. Unicode tokenization/vocabulary fitting follows [B13 contracts](../../../docs/natural-language-processing-conventions.md). Integer-ID batches are B by T, B1..16; boolean and mixed boolean IDs, floats, negative/out-of-vocabulary IDs, empty/all-padding rows and left/interior padding are rejected. Text is tokenized before these models; vocabulary is fit on permitted training text only. No silent truncation. BERT(vocab_size,d_model=8,heads=2,ff_dim=16,layers=1,max_length=32,random_state=0) accepts sequences up to max_length. encode returns owned contextual arrays(B,T,d), optionally per-layer attention(B,h,T,T). logits returns(B,T,V).

## 4. Why Do We Need This Algorithm?

Bidirectional context is useful when a missing word or token-level decision depends on its right context as well as its left. Separating a transparent architecture from its optimization scope makes it possible to verify masking without claiming that random frozen features understand natural language.

## 5. Real-World Applications

Educational masked-token reconstruction, inspection of contextual attention and comparison with causal decoding. Real pretrained BERT encoders are used for many language tasks; this compact frozen-feature model does not reproduce their training,scale or measured performance.

## 6. Core Intuition

At each position add its token-table vector to its absolute position-table vector. Both tables and all attention/FFN/normalization parameters are **frozen at initialization**. They are parameterized embedding tables, not learned language knowledge. Each block computes Q=XWq+bq,K=XWk+bk,V=XWv+bv, splits width across heads, and applies softmax(QKᵀ/sqrt(d_head))V under the proper mask. Merge heads, apply an output projection, add the residual and layer-normalize. Apply a position-wise two-layer FFN with the explicit tanh approximation GELU(x)=.5x[1+tanh(sqrt(2/pi)(x+.044715x³))], add its residual and layer-normalize again. Stack1..3 blocks. Padding keys are excluded and padded query/context rows are zero; all-masked attention rows fail explicitly. Layer norm uses variance across width and epsilon1e-5, inherited unchanged from B7. BERT uses a bidirectional allowed-key mask with no causal restriction. A later visible token may affect an earlier token representation. Its MLM policy always replaces every selected ordinary input token with MASK before encoding, so the selected gold embedding cannot leak into its own prediction.

## 7. Prerequisites

Prerequisites: tokenization, fixed vocabulary IDs, matrix multiplication, softmax/cross-entropy, [B7 Transformer blocks](../../deep-learning/transformers/README.md), and training/evaluation separation. No existing pretrained representations are assumed.

## 8. Step-by-Step Working Process

Validate IDs and a nonempty boolean selection matching(B,T). Training selections choose ordinary original targets>=5. Replace selected IDs with MASK; encode bidirectionally; select only target-position states; compute logits HW+b. Minimize mean negative log probability of the original selected IDs. Repeated fit resets head parameters to the same configured initialization, trains local copies and commits only a successful run. Backbone arrays never enter an update.

## 9. Pseudocode

```text
corrupted <- copy(original IDs)
corrupted[selected ordinary targets] <- MASK
H <- frozen bidirectional Transformer(corrupted)
repeat E bounded epochs:
    P <- softmax(H[selected] W + b)
    delta <- (P - one_hot(original[selected])) / M
    W <- W - learning_rate * H[selected]^T delta
    b <- b - learning_rate * sum(delta)
```

Loss is -sum_selected logP(gold)/M. Gradients are checked for **all coordinates of W and b only**; no backbone derivative/pretraining coverage is claimed.

## 10. Dry Run

With ordinary mapping cat5,runs6,sleeps7, two training rows are[2,5,6,3] and[2,5,7,3]. Selecting column1 makes corrupted rows[2,4,6,3] and[2,4,7,3]. Their two targets are both5. The original5 is absent from both encoded target positions. Every other position contributes zero objective weight. The example below reports actual initial/final loss and predictions.

## 11. Time Complexity

Let B=batch size,T=context length,d=model width,f=FFN width,L=block count,h=head count,V=vocabulary size,M=scored targets,E=head epochs. Backbone time is O(LB(Td²+T²d+Tdf)); dense attention is quadratic in T. Full logits cost O(BTdV). Because the backbone is frozen, training caches representations once and costs O(LB(Td²+T²d+Tdf)+EMdV). The same dense calculation applies in best/average/worst cases for fixed shapes; masks change semantics rather than creating a sparse speedup.

## 12. Space Complexity

Parameters use O(Vd+Tmax*d+L(d²+df)+dV). Forward auxiliary space is O(BTd+BhT²+BTf), with O(LBhT²) retained only when requesting all layer attention diagnostics. Head training caches O(BTd) contextual states and O(MV+Md+dV) temporary head arrays; no backbone backward graph is stored. Python recursion and unbounded search are absent.

## 13. Python Implementation

The [solution](python/solution.py) specializes the [shared token Transformer](../transformer_support.py). That helper reuses the approved [B7 Transformer layer normalization](../../deep-learning/transformers/python/solution.py) unchanged. Read the [canonical tests](tests/test_python.py) and [shared component oracles](../tests/test_transformer_contracts.py). NumPy performs the stated operations directly; no framework or complete NLP library supplies the model.

## 14. C++ Implementation

ML C++ is optional and is not implemented for this topic. No placeholder source, compiler pass or production implementation is claimed. Existing DSA C++17/C++20 requirements remain unchanged.

## 15. Input and Output Examples

Run from repository root:

```sh
.venv/bin/python machine-learning/natural-language-processing/bert/python/example.py
.venv/bin/python -m pytest machine-learning/natural-language-processing/bert machine-learning/natural-language-processing/tests/test_transformer_contracts.py -q
```

Actual locally executed output:

```json
{"training": ["cat runs", "cat sleeps"], "ordinary_ids": {"cat": 5, "runs": 6, "sleeps": 7}, "input_ids": [[2, 5, 6, 3], [2, 5, 7, 3]], "inference_ids": [[2, 4, 6, 3], [2, 4, 7, 3]], "loss_start": 2.10093735745106, "loss_final": 0.0201852292713438, "predicted_ids": [5, 5], "predicted_tokens": ["cat", "cat"], "context_shape": [2, 4, 4], "trained_parameters": ["head_weight", "head_bias"], "backbone": "frozen random initialization"}
```

## 16. Edge Cases

All-empty inputs,all-padding sequences,left/interior padding,invalid IDs,mask shape/type errors,empty target selection and selecting PAD/UNK/BOS/EOS as gold fail explicitly. select_mask samples ceil(fraction*ordinary_count) positions without replacement using a local seed, fraction1e-6..1; there must be an ordinary token. Inference logits/predict_masked also accept an already-MASK selected position without needing its gold token; fit/loss reject MASK as gold. Padded query states are zero, but raw vocabulary logits there may equal the head bias and must not be scored.

## 17. Advantages

Independent attention and full-block calculations verify the actual architecture. Bidirectional future-token intervention, padding-key/embedding invariance, exact MLM CE and complete trained-head finite differences verify distinct claims. Tiny training demonstrates a real parameter update while frozen-parameter checks establish its honest scope.

## 18. Disadvantages and Limitations

d_model2..16, heads1..4 dividing width, ff_dim2..32, layers1..3, max_length1..32, private random_state0..2³²-1. Training uses epochs1..500, learning_rate1e-6..1, with epochs*selected_events*d_model*V<=2e7. No dropout, segment embeddings, NSP, subword/WordPiece/BPE tokenizer, pretrained weights, optimizer state/checkpoint serialization, GPU or network dependency. Finite parameter magnitudes are bounded by1e6; invalid or nonfinite calculations fail rather than replacing NaNs. The fixed epoch budget is not a convergence certificate. The all-selected-to-MASK policy is a declared educational variant rather than the original BERT mixed masking recipe. Frozen random features plus a linear head cannot provide full end-to-end adaptation,pretrained semantics or credible production accuracy. Attention weights are computations, not causal explanations of language understanding.

## 19. When to Use It

Use to learn how masked reconstruction and bidirectional attention interact,inspect small tensor shapes, and independently audit a head gradient. Fit only on the local training corpus and retain separate evaluation text.

## 20. When Not to Use It

Do not use as a replacement for a pretrained encoder or infer general language capability from fitting two toy sentences. Do not expose selected gold tokens to the encoder or score padding/unselected tokens as if they were MLM targets.

## 21. Comparison With Related Algorithms

| Model | Visible context | Objective | This implementation trains |
|---|---|---|---|
| BERT-style encoder | Both sides except hidden selected token | Selected-token MLM | Vocabulary head only |
| GPT-style decoder | Prefix/current input only | Shifted next-token CE | Vocabulary head only |
| Word2Vec | Local training contexts | SGNS | Input/output word vectors |

Both small Transformers share component code but have independently tested different attention masks and objectives.

## 22. Interview Questions

Why hide selected original tokens? Otherwise bidirectional attention could copy the target. Why divide by sqrt(d_head)? It controls dot-product scale across head widths. Does a lower toy loss prove language understanding? No. Which gradients are checked? Every trained head weight/bias; no frozen-backbone gradient claim.

## 23. Practice Problems

Calculate two-key attention by hand; change a visible future token and inspect earlier contextual states; prove padded keys have zero attention; finite-difference every head coordinate; compare two masking fractions without fitting held-out vocabulary.

## 24. References

[Devlin, Chang, Lee and Toutanova, BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding (2018;NAACL2019)](https://arxiv.org/abs/1810.04805). [Vaswani et al., Attention Is All You Need (2017)](https://arxiv.org/abs/1706.03762). The frozen-head-only scope,small bounds,tanh GELU approximation and mask policy are explicit implementation choices,not production parity.

## 25. Author Attribution

Owner and maintainer: **[MD.Khalid Hasan](https://github.com/khalidhasan7343)**. [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas); [MIT license](../../../LICENSE); [contribution policy](../../../CONTRIBUTING.md). Attribution and licensing remain preserved.

