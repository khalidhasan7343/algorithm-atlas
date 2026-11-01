# Multilayer Perceptron — binary tanh classifier

## 1. Algorithm Name

Multilayer Perceptron — binary tanh classifier

## 2. Overview

A one-hidden-layer feedforward binary classifier with explicit stable logit loss and chain-rule backpropagation.

## 3. Problem Statement

X=(N,p),2<=N<=128,p<=16; y=(N,) integer0/1 labels. W1=(p,h),b1=(h),W2=(h,1),b2=(1). predict returns0/1 and predict_proba returns(N,2) in class order0,1.

## 4. Why Do We Need This Algorithm?

A nonlinear hidden representation can separate patterns such as XOR that one linear decision boundary cannot.

## 5. Real-World Applications

Small tabular binary classification and inspectable gradient experiments; no claim of production calibration or universal fit quality.

## 6. Core Intuition

Compose learned affine maps with a nonlinear hidden activation, then adjust each map according to its contribution to binary prediction loss.

H=tanh(X W1+b1), logits=H W2+b2. L=mean(logaddexp(0,logit)-y*logit). Probabilities use a stable sigmoid; no log of an underflowed probability is formed.

## 7. Prerequisites

Matrix shapes, derivatives/chain rule, floating-point arithmetic and the declared learning objective. Read [B7 contracts](../../../docs/neural-networks-and-deep-learning-conventions.md) and [scope](../../../docs/neural-networks-and-deep-learning-scope.md).

## 8. Step-by-Step Working Process

Let D=(sigmoid(logits)-y)/N. dW2=H.T D, db2=sum D. Hidden preactivation gradient G=(D W2.T)*(1-H²); dW1=X.T G, db1=sum G. Every bias/weight entry is verified by central finite differences.

Glorot-like Gaussian initialization uses local seed. Fixed epochs with shuffled mini-batches, global gradient-norm clipping and SGD. Defaults hidden_dim4,epochs100,learning_rate0.1,batch_size16,gradient_clip5,seed0. Bounded budgets expose fixed-budget-completed and converged_=False; this is no convergence certificate.

## 9. Pseudocode

```text
initialize weights/biases with local RNG
repeat bounded epochs and minibatches:
  tanh hidden; linear logits; stable BCE
  backpropagate output and hidden gradients
  clip global gradient norm; update parameters
predict by sigmoid>=0.5
```

## 10. Dry Run

Executed example uses X=[(-1,-1),(-1,1),(1,-1),(1,1)], y=(0,1,1,0), hidden8,seed19002,600 full-batch steps at learning_rate0.5. Tests and the CLI verify predicted labels exactly(0,1,1,0) and final training BCE<0.1. The manual forward test independently expands both affine maps, tanh, BCE and all four gradient blocks on a two-row numerical fixture.

## 11. Time Complexity

For N rows,p inputs,h hidden units,E epochs, fit O(E*N*(p*h+h)); mini-batch overhead depends on ceil(N/B). Prediction for q rows O(q*p*h). No optimization convergence-rate guarantee.

## 12. Space Complexity

O(B*(p+h)) activation/gradient work, O(p*h+h) parameters and O(N*p) copied input. No recursion, automatic differentiation graph or model checkpoint.

## 13. Python Implementation

[MLPClassifier source](python/solution.py) contains the actual architecture and analytic gradients. [Example](python/example.py); [tests](tests/test_python.py). Core imports NumPy/stdlib/local primitives only, never a framework estimator. Loss/forward/backward functions take explicit parameter arrays so independent finite differences can freeze all stochastic inputs. Manual forward/BCE/backprop, full finite differences, SciPy expit reference, extreme logits, separable/XOR learning, repeated seeded weights, invalid labels/settings and atomic refits are checked.

## 14. C++ Implementation

C++ is optional and absent under the Phase19 ML policy. No placeholder source/test. DSA still requires actual Python/C++17/C++20 tests.

## 15. Input and Output Examples

Run the fixed-seed example from the repository root:

```sh
python machine-learning/deep-learning/multilayer-perceptron/python/example.py
```

The equivalent JSON input to `python/solution.py` is:

```json
{"X":[[-1,-1],[-1,1],[1,-1],[1,1]],"y":[0,1,1,0],"parameters":{"hidden_dim":8,"epochs":600,"learning_rate":0.5,"batch_size":4,"random_state":19002}}
```

Observed output in this phase's [executed example records](../../../docs/neural-networks-and-deep-learning-evidence/examples-results.json):

```json
{"loss_initial":0.7064654793541177,"loss_final":0.0032179842591330116,"optimization_status":"fixed-budget-completed","prediction":[0,1,1,0]}
```

Floating-point last digits may vary across numerical environments. Losses describe the actual small training run and its declared reduction; fixed-budget completion does not establish convergence or generalization.

## 16. Edge Cases

Single-class binary labels are accepted; a two-class separation guarantee is not inferred. Integer labels0/1 only; reject float/bool or column-vector labels. Constant/duplicate rows are valid. Empty query rows are supported with fitted p; fit requires at least2 rows.

Inputs copy caller arrays and use local default_rng. Reject nonfinite/nonreal arrays, bool data, invalid dimensions/learning rates/batches/seeds, excess compute budgets and inference before fit. Fit commits state only after a complete finite run; invalid/failed refits preserve a prior successful model.

## 17. Advantages

Simple interpretable nonlinear features, stable BCE and fully visible chain rule.

## 18. Disadvantages and Limitations

One tanh hidden layer and binary outputs only; no multiclass mode, dropout, batch normalization, regularization or arbitrary architecture. Saturation/nonconvexity can limit learning. Training success on one seed does not prove generalization.

## 19. When to Use It

Use to study nonlinear binary decisions and exact parameter gradients on small numeric data.

## 20. When Not to Use It

Use a validated task-specific model for large datasets or calibrated/multiclass predictions; this scope does not implement them.

## 21. Comparison With Related Algorithms

Logistic regression uses one linear logit; this MLP adds nonlinear hidden features. A residual network adds an identity path, while CNNs share spatial kernels rather than treating every input coordinate independently.

## 22. Interview Questions

Why compute BCE from logits? It avoids log0 and overflow from naive probability formulas. Why divide D by N? The loss is the sample mean. Why is hidden nonlinearity needed for XOR? Composed linear layers still define a linear boundary.

## 23. Practice Problems

Derive the hidden chain rule. Repeat the gradient check after changing one bias. Compare XOR fitting with hidden width1 versus8 without claiming every initialization must learn.

## 24. References

[Rumelhart, Hinton and Williams, Learning representations by back-propagating errors](https://www.cs.toronto.edu/~hinton/absps/naturebp.pdf); [SciPy expit oracle](https://docs.scipy.org/doc/scipy/reference/generated/scipy.special.expit.html).

## 25. Author Attribution

**MD.Khalid Hasan**, [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../LICENSE); [contribution policy](../../../CONTRIBUTING.md). New Phase19 B7 owner review pending.
