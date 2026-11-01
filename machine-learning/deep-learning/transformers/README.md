# Transformer — one numerical-input post-norm encoder

## 1. Algorithm Name

Transformer — one numerical-input post-norm encoder

## 2. Overview

Use content-dependent query/key similarities to mix value vectors, then combine residual, normalized and feedforward paths with positional information.

## 3. Problem Statement

X=(N,T,p),T<=16,p<=16; d_model2..8,heads1..4 with d_model divisible by heads; hidden_dim1..16 is feedforward width. Scalar final-token regression y=(N,1). causal is strict bool.

Parameter shapes: Win(p,d),Wq/Wk/Wv/Wa(d,d),W1(d,f),W2(f,d),Wo(d,1); matching biases and two learned LayerNorm gamma/beta vectors of length d. Heads use(N,heads,T,d/heads).

## 4. Why Do We Need This Algorithm?

Content-dependent attention lets one token use a weighted combination of other permitted tokens in a single layer. Positional encodings supply ordering information that content attention alone lacks. The architecture trades recurrent processing for pairwise attention work and makes masking part of the mathematical contract.

## 5. Real-World Applications

Synthetic numerical sequences whose last target depends on several earlier positions. Full Transformers support language and multimodal tasks, but this numerical encoder has no tokenizer, vocabulary decoder, pretrained weights or language-generation API.

## 6. Core Intuition

Use content-dependent query/key similarities to mix value vectors, then combine residual, normalized and feedforward paths with positional information.

E=X Win+bin+sinusoidal_position. Split Q=E Wq+bq,K,V into heads. A=softmax(Q K.T/sqrt(d_head)+mask),C=merge(A V). H=LN(E+C Wa+ba); Z=LN(H+tanh(H W1+b1) W2+b2); R=Z_last Wo+bo. LN uses learned gamma/beta and epsilon1e-5; mask excludes future positions when causal.

## 7. Prerequisites

Matrix shapes, derivatives/chain rule, floating-point arithmetic and the declared learning objective. Read [B7 contracts](../../../docs/neural-networks-and-deep-learning-conventions.md) and [scope](../../../docs/neural-networks-and-deep-learning-scope.md).

## 8. Step-by-Step Working Process

Output adjoints enter the last-token Z. Each residual addition splits upstream; each LN uses invstd*(g-mean(g)-xhat*mean(g*xhat)) plus gamma/beta reductions. For attention dV=A.T dC,dA=dC V.T,dS=A*(dA-sum(A*dA)); masked entries are zero. dQ=dS K/sqrt(d_head),dK=dS.T Q/sqrt(d_head). Merge heads and accumulate Q/K/V projection adjoints into E and input projection.

Copy/validate inputs, initialize locally, run bounded CPU gradient updates, and install fitted state only after a finite completed run. Mini-batches are shuffled with a local RNG except full-graph GNN. Defaults epochs100,learning_rate0.1,batch_size16,gradient_clip5 where supported; model-specific architecture controls are stated above. At most10000 updates,20000 parameter values and the common array limits apply. Histories are pre-update minibatch averages; fixed-budget status explicitly does not certify convergence.

## 9. Pseudocode

```text
initialize numerical input, Q/K/V, attention-output, feedforward and head projections
add fixed sinusoidal positions to projected inputs E
split projected Q,K,V into heads
S = Q@transpose(K)/sqrt(head_width); apply optional causal mask
A = stable_softmax(S); C = merge_heads(A@V)
H = layer_norm(E+C@Wa+ba)
Z = layer_norm(H+tanh(H@W1+b1)@W2+b2)
predict scalar from Z at the last token; form mean squared loss
reverse head, both normalizations, feedforward and residual branches
backpropagate softmax scores and Q/K/V; sum their adjoints into E
accumulate all projection/normalization parameter gradients; clip and update
```

## 10. Dry Run

Position0 has sin/cos vector(0,1,0,1) at width4. In the causal three-token attention fixture, each row sums1 and every future entry is0; changing a later V leaves earlier attention outputs unchanged. Independent per-head loops verify sqrt(d_head), split/merge and weighted sums. Full-model finite differences cover both1-head unmasked and2-head causal cases. The executable example below runs fixed-seed training and emits the actual learned outputs and first/final losses; they are recorded in Phase19 evidence rather than invented.

## 11. Time Complexity

With embedding d,feedforward f, fit O(E*N*(T*p*d+T*d²+T²*d+T*d*f)). Full attention has quadratic T² work even though T is deliberately bounded. Sampling/token autoregression is not implemented.

## 12. Space Complexity

O(B*heads*T²+B*T*(d+f)) activations/attention adjoints, O(p*d+d²+d*f) parameters. No transformer framework/cache or pretrained weights.

## 13. Python Implementation

[TransformerRegressor source](python/solution.py) contains the actual architecture and analytic gradients. [Example](python/example.py); [tests](tests/test_python.py). Core imports NumPy/stdlib/local primitives only, never a framework estimator. Loss/forward/backward functions take explicit parameter arrays so independent finite differences can freeze all stochastic inputs. Tests independently check this model’s forward equations/objective, every weight and bias by central finite differences with fixed stochastic inputs, controlled training and repeated seeded outputs. Common tests add invalid rank/domain/shape/limits, constant/duplicate rows, global RNG/input copies, finite-state detection and atomic failed refits.

## 14. C++ Implementation

C++ is optional and absent under the Phase19 ML policy. No placeholder source/test. DSA still requires actual Python/C++17/C++20 tests.

## 15. Input and Output Examples

Run the fixed-seed example from the repository root:

```sh
python machine-learning/deep-learning/transformers/python/example.py
```

The equivalent JSON input to `python/solution.py` is:

```json
{"X":[[[-0.4],[-0.2]],[[-0.2],[0.1]],[[0.1],[0.3]],[[0.4],[0.2]]],"y":[[-0.2],[0.1],[0.3],[0.2]],"parameters":{"d_model":4,"heads":2,"hidden_dim":4,"epochs":50,"learning_rate":0.03,"batch_size":4}}
```

Observed output in this phase's [executed example records](../../../docs/neural-networks-and-deep-learning-evidence/examples-results.json):

```json
{"loss_initial":0.7553779662224055,"loss_final":0.044712721898246405,"optimization_status":"fixed-budget-completed","prediction":[[0.142759138584077],[0.10052750523364981],[0.07388194297737347],[0.10492421339161787]]}
```

Floating-point last digits may vary across numerical environments. Losses describe the actual small training run and its declared reduction; fixed-budget completion does not establish convergence or generalization.

## 16. Edge Cases

The architecture sizes and loss-normalization axes above are part of the API, not inferred by broadcasting. Fitted tensor trailing dimensions must match at inference; unsupported sequence/image/graph forms fail explicitly. One encoder block, numerical input projection, fixed sinusoidal positions, post-norm, tanh feedforward and final-token MSE. No token vocabulary, language modeling, cross-attention, decoder, dropout, learned positions, padding masks or KV cache. It is not an LLM. The causal mask always leaves self-attention available; no all-masked row is supported.

Inputs copy caller arrays and use local default_rng. Reject nonfinite/nonreal arrays, bool data, invalid dimensions/learning rates/batches/seeds, excess compute budgets and inference before fit. Fit commits state only after a complete finite run; invalid/failed refits preserve a prior successful model.

## 17. Advantages

The specific Transformer — one numerical-input post-norm encoder forward and reverse equations are visible in a compact NumPy implementation; independent mathematical invariants and per-entry gradients make the mechanism inspectable.

## 18. Disadvantages and Limitations

One encoder block, numerical input projection, fixed sinusoidal positions, post-norm, tanh feedforward and final-token MSE. No token vocabulary, language modeling, cross-attention, decoder, dropout, learned positions, padding masks or KV cache. It is not an LLM. The causal mask always leaves self-attention available; no all-masked row is supported.

## 19. When to Use It

Use for learning and validating the stated Transformer — one numerical-input post-norm encoder mechanism on a small controlled CPU dataset.

## 20. When Not to Use It

Use a validated production architecture for large-scale workloads or features excluded by this contract. A short synthetic fit does not establish generalization or generative quality.

## 21. Comparison With Related Algorithms

| Architecture | Sequence interaction |
| --- | --- |
| This Transformer | Content-weighted permitted token pairs; O(T²) attention |
| RNN/LSTM/GRU | Sequential recurrent state; O(T) recurrence at fixed width |
| CNN | Fixed local receptive windows rather than content-dependent attention |

## 22. Interview Questions

Why divide by sqrt(d_head)? It controls score scale under standard variance assumptions. Why positions? Attention alone does not identify sequence order. Compared with recurrence, attention directly connects permitted token pairs at quadratic sequence cost.

## 23. Practice Problems

Expand one attention head on two tokens using explicit dot products. Change a future value vector and verify earlier outputs remain fixed under the causal mask. Derive the softmax vector-Jacobian product and check a LayerNorm scale gradient independently.

## 24. References

[Vaswani et al., Attention Is All You Need](https://arxiv.org/abs/1706.03762).

## 25. Author Attribution

**MD.Khalid Hasan**, [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../LICENSE); [contribution policy](../../../CONTRIBUTING.md). New Phase19 B7 owner review pending.
