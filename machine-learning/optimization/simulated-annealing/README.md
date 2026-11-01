# Simulated Annealing

## 1. Algorithm Name

Simulated Annealing,canonical ID `simulated-annealing`,B10 Optimization. Implemented variant: **one-bit Metropolis search with bounded geometric cooling**.

## 2. Overview

One binary current state proposes a uniform one-bit neighbor. Improving/equal moves are accepted; worsening moves may be accepted at positive temperature. The returned answer is the retained best,not necessarily the last chain state. One canonical serves B10/C3/C4.

## 3. Problem Statement

Minimize a deterministic finite real objective on binary integer/bool vectors of length1..32. No gradient,Hessian or smoothness is required. Objective outputs must be real finite scalars with magnitude<=1e100. Callbacks are trusted,pure,prompt and receive read-only copies. This binary representation is the feasible domain,not a general constraint solver. Existing C3/C4 memberships reuse this one B10 canonical.

## 4. Why Do We Need This Algorithm?

Allowing some worsening moves can leave a local basin. Cooling changes acceptance over time; finite geometric cooling and a finite budget do not imply the asymptotic global guarantee of a different schedule. Optimization is separate from defining or statistically evaluating a predictive model; a lower training objective is not a generalization guarantee.

## 5. Real-World Applications

Small binary local-search experiments that explicitly distinguish current versus best state and inspect temperature-dependent acceptance. No production deployment or universal performance superiority is claimed.

## 6. Core Intuition

For delta=f(proposal)-f(current),accept with p=min(1,exp(-delta/T)). Each of D bits is selected uniformly. The actual worsening decision uses log(U)<-delta/T,with U=0 handled explicitly; equal/improving moves need no extra uniform draw. T_t=T0*cooling^t,checked against a floor in log space before exp.

## 7. Prerequisites

Binary representations,probability,local random generators,objective ordering and finite search spaces. Distinguish a stochastic transition law from empirical performance and a caller-specified target from a proven global optimum.

## 8. Step-by-Step Working Process

Validate the initial bit string and evaluate it once. At each bounded iteration,check the temperature floor,flip one uniform bit,evaluate its objective,and apply the Metropolis decision. Update current state only when accepted; retain best state separately. Record actual accepted flags,current/best histories and temperatures. A target may stop early; floor or iteration exhaustion is not global convergence.

## 9. Pseudocode

```text
current = copy(x0); best = current
for each bounded iteration:
    compute log temperature; stop if at/below floor
    propose a uniform one-bit neighbor
    accept if improvement/equality or log(U) < -delta/temperature
    retain current and best separately
return best,status and chain diagnostics
```

## 10. Dry Run

At delta=log2 and T=1,a worsening proposal has probability1/2. At delta<=0 acceptance is1. For T0=1,cooling=.5,floor=.25,two proposals use temperatures1 and.5 before the floor stops evaluation. Tests independently replay an entire seeded chain and verify its non-monotonic current energy and monotonic retained best.

## 11. Time Complexity

For D bits,K evaluated proposals and objective cost F,each iteration costs O(D+F); total O(K(D+F)+F). One initial and K proposal evaluations give nfev=K+1; rejected proposals still count. Best/average optimization iteration counts depend on the objective and settings; the configured budget is an upper bound,not a convergence theorem.

## 12. Space Complexity

Working current/best vectors O(D); returned current trajectory O(KD),accepted/temperature/current/best histories O(K). These real history costs are separate from constant-state annealing theory. No recursion or external dataset/model storage is required.

## 13. Python Implementation

[Source](python/solution.py): `SimulatedAnnealing(initial_temperature=1,cooling=.95,minimum_temperature=1e-12,random_state=0).minimize(fun,x0,max_iter=1000,target_value=None)`. `metropolis_probability(delta,T)` exposes the transition acceptance formula for inspection; the core decision uses log uniforms. Diagnostics contain current_x,current_fun,current_history,trajectory,accepted,temperatures and target_value. Each solve is fresh; no derivative/stateful step interface is invented.

## 14. C++ Implementation

C++ is optional for this ML canonical and absent. No placeholder source or tests exist. DSA still requires actual Python,C++17 and C++20 execution.

## 15. Input and Output Examples

[Executable example](python/example.py),from repository root:

```sh
.venv/bin/python machine-learning/optimization/simulated-annealing/python/example.py
```

The example starts with twelve zeros,uses a known Hamming target,seed22,T0=1,cooling.95 and max_iter1000. Its independent target value is0; actual best,iterations,evaluation count and termination are printed. Actual executed output:

```json
{"converged": true, "initial_best": 6.0, "iterations": 48, "known_target_value": 0, "objective": 0.0, "objective_evaluations": 49, "seed": 22, "status": "target-reached", "x": [1, 0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 0]}
```

## 16. Edge Cases

Bits1..32,max_iter1..10000,initial_temperature1e-8..1e6,cooling.001..1,minimum_temperature1e-12..initial_temperature. Cooling1 is a valid fixed-temperature finite-budget chain. Initial temperature at its floor stops without a proposal; an already met target has priority. Invalid bits,temperature,schedule,target or nonfinite objective fail clearly. Worsening probability may underflow in the inspection helper; the core compares log uniforms without forming that exponential.

## 17. Advantages

Explicit mathematics,independent hand/analytical checks,bounded loops,owned state and inspectable histories make this variant useful for learning and auditing. A caller-provided target_value can produce target-reached. Otherwise temperature-floor and iteration-budget are non-converged statuses. The current chain can worsen while best-so-far remains monotonic. No gradient stationarity or global optimality is fabricated.

## 18. Disadvantages and Limitations

This is a binary one-bit symmetric proposal scheme,not arbitrary continuous annealing or a proof of global convergence. Geometric cooling can freeze early. Floating-point PRNG/probability resolution limits extreme events; log decisions avoid forming tiny exp values in the actual chain. Callback runtime cannot be bounded by an iteration counter; callbacks must return promptly. Numerical bounds are educational resource/domain limits,not a general constrained optimization solver.

## 19. When to Use It

Use it when the stated callback/representation and update rule match the intended mathematical experiment. Check units,scaling,objective normalization and stopping evidence before interpreting the result.

## 20. When Not to Use It

Do not use this binary variant for arbitrary real/permutation encodings without specifying new operators. For tiny domains,exhaustive enumeration may provide an exact answer. For smooth continuous vectors,use the relevant B10 gradient or curvature routine. No automatic encoding,derivative computation or constraint repair is hidden here.

## 21. Comparison With Related Algorithms

GA maintains a population and protects elites; this method follows one chain,accepts some worse current states and retains a separate best. Gradient methods need differentiable continuous callbacks,which this variant does not. Related canonical paths stay unchanged; previous learners retain their original optimizer behavior.

## 22. Interview Questions

Why distinguish current from best? Worse current moves are intentional exploration; the best must not be lost. Why use a symmetric one-bit proposal? It gives the stated simple Metropolis ratio without a proposal correction. Does a temperature floor prove convergence? No. Why draw no extra uniform for equal/improving moves? Their acceptance is exactly1.

## 23. Practice Problems

Build the exact transition matrix on two bits at fixed temperature and verify normalization/detailed balance against Gibbs weights. Independently replay a seeded chain,including which worsening moves consume uniforms. Verify every evaluation is counted,then study cooling/seed variation without claiming a finite-run global theorem.

## 24. References

Kirkpatrick,Gelatt and Vecchi,[Optimization by Simulated Annealing,Science1983 — accessible paper](https://hedibert.org/wp-content/uploads/2013/12/1983KirkpatrickGelattVecchi.pdf).

[Project scope](../../../docs/optimization-scope.md),[numerical contracts](../../../docs/optimization-conventions.md) and independent tests specify this exact educational variant; no unread source or published benchmark reproduction is claimed.

## 25. Author Attribution

Algorithm Atlas is maintained by **[MD.Khalid Hasan](https://github.com/khalidhasan7343)**. [MIT License](../../../LICENSE); [contribution policy](../../../CONTRIBUTING.md). Preserve source attribution and canonical ownership.
