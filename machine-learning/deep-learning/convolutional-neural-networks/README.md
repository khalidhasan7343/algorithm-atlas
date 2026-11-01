# Convolutional Neural Network — tiny NCHW regressor

## 1. Algorithm Name

Convolutional Neural Network — tiny NCHW regressor

## 2. Overview

Shared local filters detect the same spatial pattern at each image location, while gradients accumulate every use of each kernel coefficient.

## 3. Problem Statement

X=(N,C,H,W),C<=2,H/W<=8; K=(F,C,k,k),F1..4,k1..3,stride1..2,padding0..1. Output spatial sizes floor((H+2p-k)/s)+1 and similarly W must be positive. Flatten tanh filter maps into one dense scalar regression output; y=(N,1). No pooling.

With P=Hout*Wout, flattened output W has shape(F*P,1), convolution bias(F) and scalar output bias(1).

## 4. Why Do We Need This Algorithm?

Nearby pixels carry spatial relationships. A shared kernel detects the same local pattern at different locations with fewer parameters than a separate dense weight for every patch. Stride and padding make the receptive field and output geometry explicit.

## 5. Real-World Applications

Local contrast and edge measurements in tiny synthetic images, followed by a scalar image target. Larger CNNs support image recognition, but pooling, deep feature hierarchies, augmentation and multiclass classification are outside this example.

## 6. Core Intuition

Shared local filters detect the same spatial pattern at each image location, while gradients accumulate every use of each kernel coefficient.

C[n,f,i,j]=b[f]+sum_(c,u,v) Xpad[n,c,is+u,js+v] K[f,c,u,v]. This is cross-correlation, the usual neural “convolution” convention, without kernel reversal. A=tanh(C), R=flatten(A) W+o; L=mean((R-y)²).

## 7. Prerequisites

Matrix shapes, derivatives/chain rule, floating-point arithmetic and the declared learning objective. Read [B7 contracts](../../../docs/neural-networks-and-deep-learning-conventions.md) and [scope](../../../docs/neural-networks-and-deep-learning-scope.md).

## 8. Step-by-Step Working Process

D=2(R-y)/N; dW=flat(A).T D,do=sum D. Reshape D W.T and multiply by1-A². For every output location, add upstream*input_patch to dK, sum upstream into db, and add upstream*kernel into the padded input adjoint, accumulating overlaps; crop the original input region.

Copy/validate inputs, initialize locally, run bounded CPU gradient updates, and install fitted state only after a finite completed run. Mini-batches are shuffled with a local RNG except full-graph GNN. Defaults epochs100,learning_rate0.1,batch_size16,gradient_clip5 where supported; model-specific architecture controls are stated above. At most10000 updates,20000 parameter values and the common array limits apply. Histories are pre-update minibatch averages; fixed-budget status explicitly does not certify convergence.

## 9. Pseudocode

```text
initialize shared kernels K, channel biases and scalar dense head
for each shuffled image minibatch:
  pad images; cross-correlate each kernel at the declared stride
  H = tanh(convolution); R = flatten(H) @ Wout + bout
  D = 2*(R-y)/batch_rows; backpropagate the dense head
  multiply hidden adjoints by (1-H*H)
  sum kernel/bias adjoints over all images and spatial positions
  accumulate overlapping input-patch adjoints; remove padding
  clip the combined parameter gradient and take one SGD step
```

## 10. Dry Run

For X=[[1,2,3],[4,5,6],[7,8,9]], kernel[[1,0],[0,-1]],bias2,stride1,pad0, all four outputs equal-2. Unit upstream gives dK=[[12,16],[24,28]],db4. Multi-channel padding/stride outputs independently match SciPy correlate2d. The executable example below runs fixed-seed training and emits the actual learned outputs and first/final losses; they are recorded in Phase19 evidence rather than invented.

## 11. Time Complexity

With P=Hout*Wout, fit O(E*N*P*F*C*k²), plus O(E*N*P*F) dense output. Kernel sharing does not eliminate spatial work; stride/padding change P.

## 12. Space Complexity

O(B*F*P+B*C*(H+2p)*(W+2p)) activations/adjoints plus O(F*C*k²+F*P) parameters. No im2col expansion, recursion or framework graph.

## 13. Python Implementation

[CNNRegressor source](python/solution.py) contains the actual architecture and analytic gradients. [Example](python/example.py); [tests](tests/test_python.py). Core imports NumPy/stdlib/local primitives only, never a framework estimator. Loss/forward/backward functions take explicit parameter arrays so independent finite differences can freeze all stochastic inputs. Tests independently check this model’s forward equations/objective, every weight and bias by central finite differences with fixed stochastic inputs, controlled training and repeated seeded outputs. Common tests add invalid rank/domain/shape/limits, constant/duplicate rows, global RNG/input copies, finite-state detection and atomic failed refits.

## 14. C++ Implementation

C++ is optional and absent under the Phase19 ML policy. No placeholder source/test. DSA still requires actual Python/C++17/C++20 tests.

## 15. Input and Output Examples

Run the fixed-seed example from the repository root:

```sh
python machine-learning/deep-learning/convolutional-neural-networks/python/example.py
```

The equivalent JSON input to `python/solution.py` is:

```json
{"X":[[[[-1,-0.5],[0,0.5]]],[[[-0.5,0],[0.5,1]]],[[[0,0.5],[1,0.5]]],[[[0.5,1],[0.5,0]]]],"y":[[-0.25],[0.25],[0.5],[0.5]],"parameters":{"filters":2,"epochs":50,"batch_size":4}}
```

Observed output in this phase's [executed example records](../../../docs/neural-networks-and-deep-learning-evidence/examples-results.json):

```json
{"loss_initial":1.0616779973194008,"loss_final":0.02093795823310415,"optimization_status":"fixed-budget-completed","prediction":[[-0.09299128285455932],[0.1342094758318846],[0.3599010619671436],[0.653681340670251]]}
```

Floating-point last digits may vary across numerical environments. Losses describe the actual small training run and its declared reduction; fixed-budget completion does not establish convergence or generalization.

## 16. Edge Cases

The architecture sizes and loss-normalization axes above are part of the API, not inferred by broadcasting. Fitted tensor trailing dimensions must match at inference; unsupported sequence/image/graph forms fail explicitly. One convolution/tanh/dense head only; no pooling,dilation,groups,batch normalization or arbitrary channel/image sizes. filters is the channel-width control; hidden_dim is unsupported. CNN remains one B7 canonical shared by C10.

Inputs copy caller arrays and use local default_rng. Reject nonfinite/nonreal arrays, bool data, invalid dimensions/learning rates/batches/seeds, excess compute budgets and inference before fit. Fit commits state only after a complete finite run; invalid/failed refits preserve a prior successful model.

## 17. Advantages

The specific Convolutional Neural Network — tiny NCHW regressor forward and reverse equations are visible in a compact NumPy implementation; independent mathematical invariants and per-entry gradients make the mechanism inspectable.

## 18. Disadvantages and Limitations

One convolution/tanh/dense head only; no pooling,dilation,groups,batch normalization or arbitrary channel/image sizes. filters is the channel-width control; hidden_dim is unsupported. CNN remains one B7 canonical shared by C10.

## 19. When to Use It

Use for learning and validating the stated Convolutional Neural Network — tiny NCHW regressor mechanism on a small controlled CPU dataset.

## 20. When Not to Use It

Use a validated production architecture for large-scale workloads or features excluded by this contract. A short synthetic fit does not establish generalization or generative quality.

## 21. Comparison With Related Algorithms

| Model | Structural constraint |
| --- | --- |
| This CNN | Local spatial cross-correlation with shared kernels |
| MLP | Dense coordinates without kernel sharing |
| Residual block | Adds an identity feature path; does not itself imply convolution |

## 22. Interview Questions

How does sharing affect dK? Contributions from every location add. Why crop dx? Padding is fixed, not an extra learned input. Compared with a dense MLP, this model imposes locality and shared filter parameters.

## 23. Practice Problems

For a 3x3 image and 2x2 kernel, expand each cross-correlation by hand. Check why an overlapping input pixel receives several gradient contributions. Change stride from1 to2 and derive the output shape before running the independent SciPy comparison.

## 24. References

[LeCun et al., Gradient-Based Learning Applied to Document Recognition](https://leon.bottou.org/papers/lecun-98h); [SciPy correlate2d independent operation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.correlate2d.html).

## 25. Author Attribution

**MD.Khalid Hasan**, [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../LICENSE); [contribution policy](../../../CONTRIBUTING.md). New Phase19 B7 owner review pending.
