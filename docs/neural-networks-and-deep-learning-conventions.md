# B7 bounded numerical contracts

New models use copied finite real float64 arrays |value|<=1e6, fitting2..128 rows,
query0..256 rows, <=16 numeric features and262144 cells. Binary MLP y is a1D integer
0/1 vector; other supervised models use y=(N,1) MSE. Sequence tensors N,T,p have
1<=T<=16; images use N,C,H,W with C<=2,H/W<=8. GNN graphs have2..32 nodes.
Unsupported booleans/strings/complex/object/nonfinite data and shape mismatches fail.
The already approved vanilla AE retains its separate B5 contracts unchanged.

Bounded seeded Gaussian initialization and mini-batch SGD use local default_rng;
fit initializes locally and installs state only after all finite updates. Epochs
1..2000, batch1..128, learning_rate1e-6..1, hidden widths1..16, gradient_clip1e-6..1000;
at most10000 updates and20000 parameter entries. Global norm clipping does not
claim to solve vanishing gradients or guarantee convergence. Histories average
pre-update minibatch losses, not a monotonic full-data objective. Fixed-budget
completion explicitly has converged_=False and optimization_status_.

Architectures own their actual equations and analytic gradients. Shared support
contains validation, stable sigmoid/softmax/logit BCE, MSE, dictionary SGD and
bounded loop bookkeeping only; no universal autodiff engine. All stochastic gradient
checks freeze corruption/latent/noise/timesteps across plus/minus perturbations.
Sampling uses a separate explicit local seed and no pretrained weights/downloads.

Per-model contracts/variants and their inference tensor layouts are in the exact
25-section lessons. The scope is compact educational NumPy, not production parity.
ML C++ optional; DSA Python/C++17/C++20 and AI structural checks remain mandatory.

VAE inverse_transform accepts finite latent coordinates in their own units, without
the original raw-feature magnitude cap. Its smooth logvar5*tanh(raw) bounds the
variational family to[-5,5]. Every new public numerical result is checked finite;
NaN parameter tampering cannot silently emit an invalid prediction. Diffusion
q_sample validates nonnegative per-row timestep indices and exact noise shape;
reverse_mean rejects negative indices rather than using NumPy wraparound.

CNN uses NCHW cross-correlation, not a flipped mathematical convolution; no pooling.
GRU reset is applied before the candidate recurrent matrix. LSTM is the modern
forget-gated form. Transformer is one post-norm numerical-input encoder, not a
language model. GNN trains one entire undirected graph in node order. GAN uses
non-saturating logistic loss with separate1:1 D/G updates; the10000-update limit
counts both. Short-chain DDPM sampling assumes a standard-normal terminal prior,
which may approximate its forward terminal marginal poorly; fidelity is not claimed.
