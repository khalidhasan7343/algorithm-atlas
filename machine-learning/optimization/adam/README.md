# Adam

## 1. Algorithm Name

Adam,canonical ID `adam`,B10 Optimization. Implemented variant: **bias-corrected Adam with epsilon outside corrected sqrt**.

## 2. Overview

Adam tracks both a first-moment EMA and a second raw-moment EMA. Bias correction compensates their zero initial state; this does not make the method a second-order Hessian optimizer.

## 3. Problem Statement

fun(x) returns one objective scalar; gradient(x) returns its full gradient with exactly the same vector shape. Parameters are copied float64 vectors of length1..32; no flattening,broadcasting or implicit bias treatment is performed. Minimize the supplied objective; maximization requires explicit sign changes in both objective and derivative. Callbacks must be trusted,prompt,pure and valid at evaluated points. See [contracts](../../../docs/optimization-conventions.md).

## 4. Why Do We Need This Algorithm?

The first moment smooths direction while the corrected squared moment rescales coordinates. Exact indexing and epsilon placement materially affect the first steps. Optimization is separate from defining or statistically evaluating a predictive model; a lower training objective is not a generalization guarantee.

## 5. Real-World Applications

Teaching and auditing small differentiable training objectives,with the stated state/regularization convention. No production deployment or universal performance superiority is claimed.

## 6. Core Intuition

m_next=beta1*m+(1-beta1)*g; v_next=beta2*v+(1-beta2)*g². At step t starting at1,set m_hat=m_next/(1-beta1^t),v_hat=v_next/(1-beta2^t),then x_next=x-learning_rate*m_hat/(sqrt(v_hat)+epsilon). No weight decay or AMSGrad.

## 7. Prerequisites

Vectors,derivatives,finite-sum normalization,numerical precision and stopping criteria. A gradient is not an objective value; a gradient norm establishes approximate stationarity only under a correct differentiable callback. The test-only quadratic/Rosenbrock objectives are mathematical fixtures,not new canonical algorithms.

## 8. Step-by-Step Working Process

Initialize both moments at zero,compute raw-gradient moments,apply step-t bias corrections,and update parameters. The equivalent -expm1(t*log(beta)) evaluates corrections stably near beta1; beta0 is handled exactly. Parameter/state validation is transactional. A zero new gradient can still move a nonzero past first moment.

## 9. Pseudocode

```text
m = v = zeros(D); t = 0
for each update:
    t += 1
    m = beta1*m + (1-beta1)*g
    v = beta2*v + (1-beta2)*g²
    x -= rate * (m/(1-beta1^t)) / (sqrt(v/(1-beta2^t)) + epsilon)
```

## 10. Dry Run

At the first step,m_hat=g and v_hat=g²,so with learning_rate=.2,epsilon=.25,x=[1,1],g=[2,-4],x_next=[1-.4/2.25,1+.8/4.25]. The denominator is not sqrt(g²+epsilon). Independent two-step checks verify both raw moments and corrections.

## 11. Time Complexity

For D parameters,T updates,full objective cost F and gradient cost G,total time is O((T+1)(F+G)+TD). Each state update is linear in D; no Hessian is evaluated. Best/average optimization iteration counts depend on the objective and settings; the configured budget is an upper bound,not a convergence theorem.

## 12. Space Complexity

Owned working moment/velocity state is O(D); the returned trajectory costs O((T+1)D) and objective history O(T). No recursion or external dataset/model storage is required.

## 13. Python Implementation

[Source](python/solution.py) exposes `Adam(learning_rate=.001,beta1=.9,beta2=.999,epsilon=1e-8).minimize(fun,gradient,x0,max_iter=1000,tolerance=1e-8)`. Stateful `step(x,g)` returns new parameters; `get_state()` returns a deep copy and `reset()` clears state. State contains first_moment,second_moment and step t. Both arrays start at zero; reset clears both. Public state copies cannot mutate the optimizer. A failed step or minimize call leaves the previous committed state intact. Result fields are x,fun,n_iter,nfev,status,converged,history and diagnostics. Diagnostics include n_updates,njev,gradient_norm,state,trajectory.

## 14. C++ Implementation

C++ is optional for this ML canonical and absent. No placeholder source or tests exist. DSA still requires actual Python,C++17 and C++20 execution.

## 15. Input and Output Examples

[Executable example](python/example.py),from repository root:

```sh
.venv/bin/python machine-learning/optimization/adam/python/example.py
```

It minimizes f(x)=.5*x.T*diag(2,4)*x-[2,-8].T*x,starts at[3,1],and compares with the unregularized task optimum[1,-2]. The executable shows the actual learning rate and termination status; its budget is1000 iterations. AdamW intentionally decays only the first coordinate. The full gradient is deterministic. Actual executed output:

```json
{"converged": true, "gradient_norm": 7.7e-09, "initial": [3.0, 1.0], "iterations": 387, "learning_rate": 0.05, "objective": -9.0, "objective_evaluations": 388, "status": "gradient-tolerance", "task_optimum": [1.0, -2.0], "updates": 387, "x": [1.0, -2.0]}
```

## 16. Edge Cases

Reject empty/nonscalar-shaped parameter vectors,nonfinite data,broadcast gradients,invalid rates/tolerances and invalid budgets. max_iter1..10000 is required. Learning_rate1e-8..10,tolerance1e-12..1. Parameter magnitudes are capped at1e6,gradient components at1e12 and objective magnitude at1e100. Invalid arguments raise ValueError; nonfinite/out-of-domain callback arithmetic or updates raise NumericalError. No NaN replacement is performed.

## 17. Advantages

Explicit mathematics,independent hand/analytical checks,bounded loops,owned state and inspectable histories make this variant useful for learning and auditing. The driver checks the supplied full task-gradient L2 norm,not the step length. Exhausting a budget is not convergence. Correct finite steps do not imply global convergence of Adam on all convex/nonconvex objectives.

## 18. Disadvantages and Limitations

Adam uses first derivatives,not Hessian information. It has known failure regimes; no universal convergence or performance theorem is claimed. This variant excludes AMSGrad,decay and learning-rate schedules. Callback runtime cannot be bounded by an iteration counter; callbacks must return promptly. Numerical bounds are educational resource/domain limits,not a general constrained optimization solver.

## 19. When to Use It

Use it when the stated callback/representation and update rule match the intended mathematical experiment. Check units,scaling,objective normalization and stopping evidence before interpreting the result.

## 20. When Not to Use It

Do not use this smooth-gradient routine for arbitrary nondifferentiable/discrete objectives,unknown derivatives or constrained feasibility. Consider the separately specified GA/SA canonicals for supported discrete search. No automatic finite-difference gradient or solver delegation is hidden in the core.

## 21. Comparison With Related Algorithms

RMSProp lacks its first moment and bias correction. AdamW decouples explicit decay from these raw-gradient moments; adding L2 to the gradient is a different update. Related canonical paths stay unchanged; previous learners retain their original optimizer behavior.

## 22. Interview Questions

Explain the exact update and state order. Which norm is checked,and when? Does an exhausted budget imply convergence? No. Does zero sampled gradient imply zero full gradient? No. Which coordinates represent a bias,and who defines their derivatives? The caller.

## 23. Practice Problems

Reproduce the dry run,then vary a valid rate and observe both objective and termination status. Check a quadratic gradient with central differences. Choose an SPD quadratic,solve its optimum independently,and derive its coordinate error recurrence. Verification uses Independent first/two-step formulas,epsilon-placement checks,high-precision Decimal bias-correction comparison near beta1,zero-gradient moment persistence and shared transactional tests. See [tests](tests/test_python.py).

## 24. References

Kingma and Ba,[Adam: A Method for Stochastic Optimization,ICLR2015;preprint2014](https://arxiv.org/abs/1412.6980).

[Project scope](../../../docs/optimization-scope.md),[numerical contracts](../../../docs/optimization-conventions.md) and independent tests specify this exact educational variant; no unread source or published benchmark reproduction is claimed.

## 25. Author Attribution

Algorithm Atlas is maintained by **[MD.Khalid Hasan](https://github.com/khalidhasan7343)**. [MIT License](../../../LICENSE); [contribution policy](../../../CONTRIBUTING.md). Preserve source attribution and canonical ownership.
