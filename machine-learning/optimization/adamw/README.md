# AdamW

## 1. Algorithm Name

AdamW,canonical ID `adamw`,B10 Optimization. Implemented variant: **canonical Adam plus explicit decoupled masked weight decay**.

## 2. Overview

AdamW reuses the existing B10 Adam canonical math. The provided task gradient enters the moments unchanged; a separate shrinkage term acts on the old parameters selected by a mask.

## 3. Problem Statement

fun(x) returns one objective scalar; gradient(x) returns its full gradient with exactly the same vector shape. Parameters are copied float64 vectors of length1..32; no flattening,broadcasting or implicit bias treatment is performed. Minimize the supplied objective; maximization requires explicit sign changes in both objective and derivative. Callbacks must be trusted,prompt,pure and valid at evaluated points. See [contracts](../../../docs/optimization-conventions.md).

## 4. Why Do We Need This Algorithm?

Putting a decay term into an adaptively scaled gradient couples regularization to the moment statistics. Decoupled decay intentionally avoids that coupling and is not generally a fixed L2-regularized objective. Optimization is separate from defining or statistically evaluating a predictive model; a lower training objective is not a generalization guarantee.

## 5. Real-World Applications

Teaching and auditing small differentiable training objectives,with the stated state/regularization convention. No production deployment or universal performance superiority is claimed.

## 6. Core Intuition

First compute the canonical Adam candidate from raw g. Then x_next=Adam_candidate-learning_rate*weight_decay*mask*x_old. The decay uses OLD x,not the already updated candidate. A boolean mask can exclude an explicitly represented bias.

## 7. Prerequisites

Vectors,derivatives,finite-sum normalization,numerical precision and stopping criteria. A gradient is not an objective value; a gradient norm establishes approximate stationarity only under a correct differentiable callback. The test-only quadratic/Rosenbrock objectives are mathematical fixtures,not new canonical algorithms.

## 8. Step-by-Step Working Process

Validate the decay coefficient and mask before any state commit. Reuse Adam moment/correction logic,subtract the independent shrinkage and validate the final result. weight_decay0 or an all-False mask reduces exactly to Adam. The bounded variant requires learning_rate*weight_decay<=1. A nonzero active decay shrinks even when g=0.

## 9. Pseudocode

```text
candidate,new_moments = canonical_Adam_update(old_x,raw_gradient)
new_x = candidate - learning_rate * weight_decay * decay_mask * old_x
validate new_x before committing moments
with active decay,use the explicit iteration budget
```

## 10. Dry Run

At learning_rate=.1,weight_decay=.2,mask=[True,False] and old x=[1,-2],subtract[.02,0] from the ordinary Adam candidate. The raw moments equal plain Adam exactly; they differ from coupled L2-gradient moments. With zero task gradients,one selected coordinate repeatedly shrinks by.98.

## 11. Time Complexity

For D parameters,T updates,full objective cost F and gradient cost G,total time is O((T+1)(F+G)+TD). Each state update is linear in D; no Hessian is evaluated. Best/average optimization iteration counts depend on the objective and settings; the configured budget is an upper bound,not a convergence theorem.

## 12. Space Complexity

Owned working moment/velocity state is O(D); the returned trajectory costs O((T+1)D) and objective history O(T). No recursion or external dataset/model storage is required.

## 13. Python Implementation

[Source](python/solution.py) exposes `AdamW(learning_rate=.001,beta1=.9,beta2=.999,epsilon=1e-8,weight_decay=.01,decay_mask=None).minimize(fun,gradient,x0,max_iter=1000,tolerance=1e-8)`. Stateful `step(x,g)` returns new parameters; `get_state()` returns a deep copy and `reset()` clears state. The canonical Adam moment state is reused,not duplicated. The owned boolean decay mask must match D; None decays all coordinates. Copying the original mask after construction cannot alter it. A failed step or minimize call leaves the previous committed state intact. Result fields are x,fun,n_iter,nfev,status,converged,history and diagnostics. Diagnostics include n_updates,njev,gradient_norm,state,trajectory.

## 14. C++ Implementation

C++ is optional for this ML canonical and absent. No placeholder source or tests exist. DSA still requires actual Python,C++17 and C++20 execution.

## 15. Input and Output Examples

[Executable example](python/example.py),from repository root:

```sh
.venv/bin/python machine-learning/optimization/adamw/python/example.py
```

It minimizes f(x)=.5*x.T*diag(2,4)*x-[2,-8].T*x,starts at[3,1],and compares with the unregularized task optimum[1,-2]. The executable shows the actual learning rate and termination status; its budget is1000 iterations. AdamW intentionally decays only the first coordinate. The full gradient is deterministic. Actual executed output:

```json
{"converged": false, "gradient_norm": 0.0072123206, "initial": [3.0, 1.0], "iterations": 1000, "learning_rate": 0.05, "objective": -8.999986995608, "objective_evaluations": 1001, "status": "iteration-budget", "task_optimum": [1.0, -2.0], "updates": 1000, "x": [0.99639384, -2.0]}
```

## 16. Edge Cases

Reject empty/nonscalar-shaped parameter vectors,nonfinite data,broadcast gradients,invalid rates/tolerances and invalid budgets. max_iter1..10000 is required. Learning_rate1e-8..10,tolerance1e-12..1. Parameter magnitudes are capped at1e6,gradient components at1e12 and objective magnitude at1e100. Invalid arguments raise ValueError; nonfinite/out-of-domain callback arithmetic or updates raise NumericalError. No NaN replacement is performed.

## 17. Advantages

Explicit mathematics,independent hand/analytical checks,bounded loops,owned state and inspectable histories make this variant useful for learning and auditing. With nonzero active decay,the driver disables raw-task-gradient convergence stopping and reports iteration-budget,converged=False. It still exposes task loss and raw gradient norm. With zero/inactive decay it uses Adam gradient stopping. No false L2 optimum is reported.

## 18. Disadvantages and Limitations

The reported objective is the supplied task loss,not an invented L2 penalty. A budget result may be useful but is not a convergence proof. The mask/decay strength are explicit modeling choices; no coordinate is assumed to be a bias automatically. Callback runtime cannot be bounded by an iteration counter; callbacks must return promptly. Numerical bounds are educational resource/domain limits,not a general constrained optimization solver.

## 19. When to Use It

Use it when the stated callback/representation and update rule match the intended mathematical experiment. Check units,scaling,objective normalization and stopping evidence before interpreting the result.

## 20. When Not to Use It

Do not use this smooth-gradient routine for arbitrary nondifferentiable/discrete objectives,unknown derivatives or constrained feasibility. Consider the separately specified GA/SA canonicals for supported discrete search. No automatic finite-difference gradient or solver delegation is hidden in the core.

## 21. Comparison With Related Algorithms

Plain Adam is its shared canonical base. Coupled L2 changes moment inputs and is inequivalent. Decay on the updated candidate or all bias coordinates silently changes the documented method. Related canonical paths stay unchanged; previous learners retain their original optimizer behavior.

## 22. Interview Questions

Explain the exact update and state order. Which norm is checked,and when? Does an exhausted budget imply convergence? No. Does zero sampled gradient imply zero full gradient? No. Which coordinates represent a bias,and who defines their derivatives? The caller.

## 23. Practice Problems

Reproduce the dry run,then vary a valid rate and observe both objective and termination status. Check a quadratic gradient with central differences. Choose an SPD quadratic,solve its optimum independently,and derive its coordinate error recurrence. Verification uses Independent decoupled old-parameter updates,masked bias checks,raw-moment equality to Adam,coupled-L2 inequality,zero-gradient shrinkage and zero-decay trajectory equivalence. See [tests](tests/test_python.py).

## 24. References

Loshchilov and Hutter,[Decoupled Weight Decay Regularization,ICLR2019;preprint2017](https://arxiv.org/abs/1711.05101).

[Project scope](../../../docs/optimization-scope.md),[numerical contracts](../../../docs/optimization-conventions.md) and independent tests specify this exact educational variant; no unread source or published benchmark reproduction is claimed.

## 25. Author Attribution

Algorithm Atlas is maintained by **[MD.Khalid Hasan](https://github.com/khalidhasan7343)**. [MIT License](../../../LICENSE); [contribution policy](../../../CONTRIBUTING.md). Preserve source attribution and canonical ownership.
