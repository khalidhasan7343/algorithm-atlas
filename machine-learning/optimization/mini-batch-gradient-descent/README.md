# Mini-Batch Gradient Descent

## 1. Algorithm Name

Mini-Batch Gradient Descent,canonical ID `mini-batch-gradient-descent`,B10 Optimization. Implemented variant: **shuffled disjoint mean-gradient mini-batches**.

## 2. Overview

Each epoch partitions one local seeded permutation into groups. A group gradient is the mean over its actual members,including a smaller final tail batch.

## 3. Problem Statement

fun(x) returns the full finite-sum mean objective; gradient(x,indices) returns the mean gradient over the selected indices. Parameters are copied float64 vectors of length1..32; no flattening,broadcasting or implicit bias treatment is performed. Minimize the supplied objective; maximization requires explicit sign changes in both objective and derivative. Callbacks must be trusted,prompt,pure and valid at evaluated points. See [contracts](../../../docs/optimization-conventions.md).

## 4. Why Do We Need This Algorithm?

A group trades update frequency against per-update gradient work. Averaging by the actual selected count keeps the final incomplete batch mathematically consistent; silently dropping it changes the training objective. Optimization is separate from defining or statistically evaluating a predictive model; a lower training objective is not a generalization guarantee.

## 5. Real-World Applications

Small finite-sum teaching experiments where batched averaging and complete sample coverage matter. No production deployment or universal performance superiority is claimed.

## 6. Core Intuition

For selected B,x_next=x-learning_rate*(sum_{i in B} gradient_i(x))/|B|. The gradient(x,indices) callback already returns that mean; the driver applies no second division.

## 7. Prerequisites

Vectors,derivatives,finite-sum normalization,numerical precision and stopping criteria. A gradient is not an objective value; a gradient norm establishes approximate stationarity only under a correct differentiable callback. The test-only quadratic/Rosenbrock objectives are mathematical fixtures,not new canonical algorithms.

## 8. Step-by-Step Working Process

Validate batch_size<=n_samples and prospective epoch/sample work. At each epoch,shuffle once,partition without replacement,update from each selected mean gradient,and evaluate the full objective/mean gradient. All observations appear exactly once,including the tail. Batch_size1 matches reshuffled SGD; batch_sizeN matches full-gradient updates up to roundoff.

## 9. Pseudocode

```text
for each bounded epoch:
    order = local_rng.permutation(N)
    for selected = consecutive slices(order,batch_size):
        x -= learning_rate * mean_gradient(x,selected)
    evaluate full objective and full gradient
return x,status
```

## 10. Dry Run

For N=5 and batch_size2,one epoch has batch lengths[2,2,1],not[2,2] or[2,2,2]. The oracle independently evaluates each selected residual/gradient at the current x and compares all three updates. The tail denominator is1.

## 11. Time Complexity

For U batch updates,E epochs,N samples,D parameters,selected gradient cost GB,full gradient cost GN and full objective cost F,time is O(sum_updates(D+GB)+E(N+F+GN)+F+GN). U per full epoch is ceil(N/batch_size). Best/average optimization iteration counts depend on the objective and settings; the configured budget is an upper bound,not a convergence theorem.

## 12. Space Complexity

Working state O(D+N); returned update trajectory O(UD),index history O(EN),epoch objectives O(E). The prospective E*N cap is20000. No recursion or external dataset/model storage is required.

## 13. Python Implementation

[Source](python/solution.py) exposes `MiniBatchGradientDescent(learning_rate=.05,batch_size=4,random_state=0).minimize(fun,gradient,x0,n_samples=N,max_epochs=100,tolerance=1e-8)`. Stateful `step(x,g)` returns new parameters; `get_state()` returns a deep copy and `reset()` clears state. t counts batch updates; batch_history records copied selected indices. State and sampling restart on each minimize call. The final tail uses its true count. A failed step or minimize call leaves the previous committed state intact. Result fields are x,fun,n_iter,nfev,status,converged,history and diagnostics. Diagnostics include n_updates,njev,gradient_norm,state,trajectory,batch_history.

## 14. C++ Implementation

C++ is optional for this ML canonical and absent. No placeholder source or tests exist. DSA still requires actual Python,C++17 and C++20 execution.

## 15. Input and Output Examples

[Executable example](python/example.py),from repository root:

```sh
.venv/bin/python machine-learning/optimization/mini-batch-gradient-descent/python/example.py
```

It minimizes half mean squared residual on six fixed observations,starts at[3,1],uses learning_rate.1 and compares with the known optimum[1,-2]. The seed is22; mini-batches have size2 when applicable. Actual executed output:

```json
{"analytical": [1.0, -2.0], "converged": true, "gradient_evaluations": 177, "initial": [3.0, 1.0], "iterations": 44, "learning_rate": 0.1, "objective": 0.0, "objective_evaluations": 45, "status": "gradient-tolerance", "updates": 132, "x": [1.0, -1.99999999]}
```

## 16. Edge Cases

Reject empty/nonscalar-shaped parameter vectors,nonfinite data,broadcast gradients,invalid rates/tolerances and invalid budgets. Sample count1..256,epochs1..1000 and epochs*N<=20000 are required. Batch size must be valid and not exceed N. Learning_rate1e-8..10,tolerance1e-12..1. Parameter magnitudes are capped at1e6,gradient components at1e12 and objective magnitude at1e100. Invalid arguments raise ValueError; nonfinite/out-of-domain callback arithmetic or updates raise NumericalError. No NaN replacement is performed.

## 17. Advantages

Explicit mathematics,independent hand/analytical checks,bounded loops,owned state and inspectable histories make this variant useful for learning and auditing. Only full mean-gradient L2 norm at initialization/epoch ends establishes gradient-tolerance. Exhaustion gives epoch-budget and converged=False. No sample/batch loss monotonicity is assumed.

## 18. Disadvantages and Limitations

Batch size and rate interact. A fixed learning rate can oscillate; a batch mean alone says nothing about full-objective stationarity. No distributed minibatching,adaptive schedule or automatic regularization is provided. Callback runtime cannot be bounded by an iteration counter; callbacks must return promptly. Numerical bounds are educational resource/domain limits,not a general constrained optimization solver.

## 19. When to Use It

Use it when the stated callback/representation and update rule match the intended mathematical experiment. Check units,scaling,objective normalization and stopping evidence before interpreting the result.

## 20. When Not to Use It

Do not use this smooth-gradient routine for arbitrary nondifferentiable/discrete objectives,unknown derivatives or constrained feasibility. Consider the separately specified GA/SA canonicals for supported discrete search. No automatic finite-difference gradient or solver delegation is hidden in the core.

## 21. Comparison With Related Algorithms

It interpolates between observation-level SGD and full batch GD through an explicit size,without silently changing the objective normalization. Related canonical paths stay unchanged; previous learners retain their original optimizer behavior.

## 22. Interview Questions

Explain the exact update and state order. Which norm is checked,and when? Does an exhausted budget imply convergence? No. Does zero sampled gradient imply zero full gradient? No. Which coordinates represent a bias,and who defines their derivatives? The caller.

## 23. Practice Problems

Reproduce the dry run,then vary a valid rate and observe both objective and termination status. Check a quadratic gradient with central differences. Trace every selected index and the final tail; compare different fixed seeds without demanding universal improvement. Verification uses Hand-computed mean updates with a tail batch,exact sample coverage,batch-size1 equivalence to SGD,batch-sizeN equivalence to batch GD,and seeded repeated calls. See [tests](tests/test_python.py).

## 24. References

Hinton,[Neural Networks for Machine Learning,lecture6,2012](https://www.cs.toronto.edu/~hinton/coursera/lecture6/lec6.pdf).

[Project scope](../../../docs/optimization-scope.md),[numerical contracts](../../../docs/optimization-conventions.md) and independent tests specify this exact educational variant; no unread source or published benchmark reproduction is claimed.

## 25. Author Attribution

Algorithm Atlas is maintained by **[MD.Khalid Hasan](https://github.com/khalidhasan7343)**. [MIT License](../../../LICENSE); [contribution policy](../../../CONTRIBUTING.md). Preserve source attribution and canonical ownership.
