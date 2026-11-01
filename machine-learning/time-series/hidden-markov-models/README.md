# Hidden Markov Models — Categorical Emissions

## 1. Algorithm Name

A categorical hidden Markov model represents a first-order latent state chain and conditionally independent observed symbols. This canonical includes stable forward/backward inference,Viterbi decoding,posterior probabilities and genuine multi-sequence Baum-Welch training.

## 2. Overview

Given a finite categorical observation sequence and initial/transition/emission distributions,evaluate its probability,infer hidden-state posteriors,decode a most probable joint state path and optionally estimate parameters by ML EM. HMM inference is not forced into a univariate continuous forecasting API.

## 3. Problem Statement

n_states K1..8,n_symbols M1..16;observation codes are integers0..M-1 with sequence length1..2048. Explicit initial pi,transition A and emission B must all be supplied together,finite/nonnegative/normalized and shape(K),(K,K),(K,M). Otherwise a local seeded Dirichlet initializer is used. fit accepts a list of1..16 independent sequences,total<=4096,max_iter1..200,tolerance1e-12..1 and work cap max_iter*total*K²<=2e7.

forward/backward return log-domain dynamic-programming tables;score returns log observation likelihood. infer returns log_likelihood,log_forward,log_backward,gamma state posteriors and xi pair posteriors. decode returns an owned integer path and its log joint probability. fit returns self with normalized initial_/transition_/emission_,initial-inclusive log_likelihood_history_,n_iter_,status_ and converged_.

## 4. Why Do We Need This Algorithm?

Observed symbols need not reveal their generating regime directly. A latent Markov chain separates state dynamics from observation emissions; dynamic programming avoids explicitly summing or maximizing exponentially many hidden paths.

## 5. Real-World Applications

Tiny categorical regime sequences,discrete process modeling and sequence-inference teaching are suitable applications. The [POS tagging application](../../natural-language-processing/hidden-markov-models-pos-tagging/README.md) reuses this engine with supervised word/tag estimation; no speech-scale performance is claimed.

## 6. Core Intuition

alpha_t(j)=B[j,o_t]*sum_i(alpha_(t-1)(i)*A[i,j]),alpha_0=pi*B[:,o0]. beta_last=1;beta_t(i)=sum_j(A[i,j]*B[j,o_(t+1)]*beta_(t+1)(j)). Compute products as sums of logs and marginalizations with logsumexp. Gamma_t(i)=alpha_t(i)*beta_t(i)/P(o);xi_t(i,j)=alpha_t(i)*A[i,j]*B[j,o_(t+1)]*beta_(t+1)(j)/P(o). Viterbi replaces sum with max and retains backpointers.

Forward sums all hidden paths ending in each state;backward sums all possible suffixes. Their products give local posterior occupancy. Viterbi retains only the best predecessor for a joint path,which is different from selecting the most likely state independently at each time.

## 7. Prerequisites

Discrete probability,normalized vectors/matrices,Markov chains,logarithms,log-sum-exp,dynamic programming and latent-variable expected counts are prerequisites. Distinguish likelihood,marginal posterior occupancy and best joint path decoding.

## 8. Step-by-Step Working Process

Validate symbols and probability rows. Evaluate forward/backward in log space,including structural zeros represented by -inf. Normalize gamma/xi without fabricating mass for impossible data. For each EM iteration,accumulate initial posterior counts,within-sequence transition counts and symbol-specific emission counts. Normalize each usable row;retain an old row when expected occupancy is exactly zero. Evaluate the updated total likelihood,check monotonicity up to the declared roundoff tolerance,then stop on relative likelihood improvement or the finite budget. Commit fitted state only after success.

## 9. Pseudocode

```text
for each independent sequence:
    log_alpha <- forward logsumexp recursion
    log_beta <- backward logsumexp recursion
    gamma,xi <- normalized posterior masses
repeat bounded EM iterations:
    sum initial,transition,emission expectations per sequence
    normalize nonzero expected-count rows;retain zero-occupancy rows
    recompute total likelihood
    reject invalid/materially decreasing likelihood
    stop on relative likelihood tolerance
```

## 10. Dry Run

For pi=[.6,.4],A=[[.7,.3],[.2,.8]],B=[[.8,.2],[.3,.7]] and observations[0,1],enumerate paths00,01,10,11. Their joint weights are.0672,.1008,.0048,.0672,total.24. Forward likelihood equals.24;Viterbi selects path01 with joint probability.1008. Tests enumerate all paths and posterior counts independently,including a complete one-step EM oracle.

## 11. Time Complexity

Forward,backward,Viterbi and pairwise posterior inference cost O(T*K²). Multiple-sequence EM costs O(I*sum(T)*(K²+K*M)) with this implementation emission-count loop. The bounded work guard controls the dynamic-programming term;K,M,T,I are all independently capped. Enumeration is used only in tiny independent tests,not production inference.

## 12. Space Complexity

Forward/backward/gamma/Viterbi tables cost O(T*K);explicit xi costs O(T*K²). Parameters cost O(K²+K*M). EM processes one sequence posterior at a time and accumulates fixed-size counts,plus O(I) likelihood history. Long inputs do not multiply tiny raw probabilities into underflow.

## 13. Python Implementation

The canonical [CategoricalHMM](python/solution.py) performs the stated mechanism from scratch with NumPy/standard library. Shared [B11 contracts](../../../docs/time-series-conventions.md) define validation and ownership. No ready-made forecasting estimator is called. See [meaningful tests](tests/test_python.py) and the executable [example](python/example.py).

## 14. C++ Implementation

C++ is optional under the authorized ML policy and is not implemented here. No placeholder C++ files or C++ pass claims. Existing DSA Python/C++17/C++20 requirements are preserved.

## 15. Input and Output Examples

From the repository root:

```sh
.venv/bin/python machine-learning/time-series/hidden-markov-models/python/example.py
```

Actual captured output:

```json
{"initial_log_likelihood": -3.64812146, "viterbi": [0, 1, 1, 1, 1], "path_log_probability": -4.88137027, "posterior": [[0.67096774, 0.32903226], [0.21290323, 0.78709677], [0.16129032, 0.83870968], [0.36129032, 0.63870968], [0.18709677, 0.81290323]], "training_log_likelihood_before": -7.53838298, "training_log_likelihood_after": -6.52482708, "iterations": 25, "status": "iteration-budget", "converged": false}
```

Re-run targeted verification with `.venv/bin/python -m pytest machine-learning/time-series/hidden-markov-models -q`.

## 16. Edge Cases

K1,M1,singleton sequences,structural zeros and unreachable states are supported. An impossible sequence has score=-inf;posterior,Viterbi and EM raise ImpossibleSequenceError. Unknown symbols,probability rows not summing to1,nonfinite values,partial parameters and excessive sizes/work fail. Exactly zero expected occupancy retains old transition/emission rows;no arbitrary uniform replacement or silent zero division.

## 17. Advantages

Likelihood,path and posterior calculations are inspectable and independently verified by exhaustive enumeration. Log-domain computation supports long,very unlikely sequences. Multiple-sequence EM respects separate initial states and never creates transitions across sequence boundaries.

## 18. Disadvantages and Limitations

Categorical emissions only;no Gaussian/neural emissions,duration model or continuous forecasting interface. EM has local optima,label switching and identifiability limitations. Pure ML may learn structural zeros;no pseudocount/MAP guarantee is claimed. Local predecessor ties use first-index argmax,not a universal global lexicographic tie rule. Impossible data must be addressed by an appropriate model rather than fabricated probability mass.

## 19. When to Use It

Use when a small discrete latent regime chain plausibly generates categorical symbols. Report likelihood/posteriors/path as different quantities. If training,show actual likelihood history,status and sensitivity across predeclared initializations.

## 20. When Not to Use It

Do not treat marginal posterior argmax as Viterbi decoding or assume a local EM optimum is global. Do not concatenate independent sequences during EM. Continuous observations require a different emission specification rather than silently casting to integer symbols.

## 21. Comparison With Related Algorithms

ARIMA models temporal dependence in observed numeric values;HMM separates hidden states from observed symbols. Viterbi alone is a decoding algorithm;this canonical also evaluates likelihoods,posteriors and trainable expected-count updates. The separate B13 POS-tagging canonical reuses this inference engine and adds supervised word/tag estimation,unknown-token handling and task evaluation.

## 22. Interview Questions

Why can posterior inference reject a sequence while score returns -inf? Conditional probabilities are undefined when the conditioning event has probability0. Why does Baum-Welch retain a zero-occupancy row? The current likelihood gives no information for that row. Why are independent sequence boundaries special? Each starts from pi and contributes no cross-boundary transition.

## 23. Practice Problems

Enumerate all hidden paths for length3 and compare forward/Viterbi. Derive gamma/xi from path weights. Hand-compute one multi-sequence EM update. Prove singleton sequences contribute no transition counts. Test long rare-emission sequences without raw probability multiplication. Compare predeclared initialization seeds without claiming global optimality.

## 24. References

[https://web.mit.edu/6.435/www/Rabiner89.pdf](https://web.mit.edu/6.435/www/Rabiner89.pdf)

[https://doi.org/10.1109/5.18626](https://doi.org/10.1109/5.18626)

The [phase conventions](../../../docs/time-series-conventions.md) distinguish educational variants from full libraries and record the actual estimation objective. References support mathematics;executed local tests supply implementation evidence.

## 25. Author Attribution

Maintainer: **[MD.Khalid Hasan](https://github.com/khalidhasan7343)**. [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas),[MIT license](../../../LICENSE),[contribution policy](../../../CONTRIBUTING.md).

