# Genetic Algorithms

## 1. Algorithm Name

Genetic Algorithms,canonical ID `genetic-algorithms`,B10 Optimization. Implemented variant: **elitist binary tournament GA with uniform crossover and bit-flip mutation**.

## 2. Overview

A population of bit strings is ranked by its explicit minimization objective. Tournament selection,uniform crossover and independent bit flips create offspring; at least one elite retains the best candidate. One B10 canonical serves C3/C4 rather than duplicated implementations.

## 3. Problem Statement

Minimize a deterministic finite real objective on binary integer/bool vectors of length1..32. No gradient,Hessian or smoothness is required. Objective outputs must be real finite scalars with magnitude<=1e100. Callbacks are trusted,pure,prompt and receive read-only copies. This binary representation is the feasible domain,not a general constraint solver. Existing C3/C4 memberships reuse this one B10 canonical.

## 4. Why Do We Need This Algorithm?

Selection favors lower objective values while variation proposes new encodings. An elite protects best-so-far quality,not average population quality. Fitness may be negative; no invalid probability normalization of signed fitness is used. Optimization is separate from defining or statistically evaluating a predictive model; a lower training objective is not a generalization guarantee.

## 5. Real-World Applications

Teaching binary candidate selection,variation and bounded population-search experiments; all existing optimization/local/global-search memberships share this foundation. No production deployment or universal performance superiority is claimed.

## 6. Core Intuition

Sample a tournament without replacement and choose argmin(fitness,index). With crossover_rate,one Bernoulli(.5) mask makes complementary uniform-crossover children. Each bit flips independently with mutation_rate. Copy elite_count best candidates unchanged. No gradient or adaptive-moment state exists.

## 7. Prerequisites

Binary representations,probability,local random generators,objective ordering and finite search spaces. Distinguish a stochastic transition law from empirical performance and a caller-specified target from a proven global optimum.

## 8. Step-by-Step Working Process

Validate population/binary dimensions and total fitness budget before initialization. Evaluate the initial population once. Each generation stable-sorts elites,caches their deterministic fitness,selects parents from uniform tournaments,and evaluates only newly created children. Ties use the lower population index. Stop at the requested target,generation budget or optional stagnation count. Elitism makes retained best fitness nonincreasing; it does not certify a global optimum.

## 9. Pseudocode

```text
initialize/evaluate bounded binary population
while target not met and generation budget remains:
    copy stable best elites and their fitness
    select tournament parents
    crossover with a uniform mask when requested
    independently flip bits; evaluate new children
    record population best and any stagnation
return best candidate,status
```

## 10. Dry Run

For ordered unique fitness[-2,0,3,5] and every possible size2 tournament among4 candidates,the exact winner probabilities are[1/2,1/3,1/6,0]. For parents000 and111 with mask[T,F,T],children are010 and101. An all-True mutation mask complements every bit; all-False leaves it unchanged. Independent tests replay a complete generation and verify evaluation counts.

## 11. Time Complexity

For P population size,D bits,t tournament size,F objective cost and E generations,a conservative per-generation bound is O(P²+PD+P log P+(P-elite_count)F),including the implementation's full-permutation tournament sampling. Initial evaluations cost O(PF). Actual nfev=P+E*(P-elite_count). Best/average optimization iteration counts depend on the objective and settings; the configured budget is an upper bound,not a convergence theorem.

## 12. Space Complexity

Working population/offspring memory O(PD),fitness O(P); best-objective history O(E). Populations are bounded at64 and bit width32. No unbounded search tree or recursion is built. No recursion or external dataset/model storage is required.

## 13. Python Implementation

[Source](python/solution.py): `GeneticAlgorithm(population_size=16,crossover_rate=.8,mutation_rate=.05,tournament_size=2,elite_count=1,random_state=0).minimize(fun,n_bits,initial_population=None,max_generations=100,target_value=None,stagnation_generations=None)`. Pure inspection helpers are tournament_selection,uniform_crossover and bit_flip_mutation. Results expose population,fitness,stagnation count and fitness_evaluations. There is no invented step/get_state or gradient interface; each solve restarts its local Generator.

## 14. C++ Implementation

C++ is optional for this ML canonical and absent. No placeholder source or tests exist. DSA still requires actual Python,C++17 and C++20 execution.

## 15. Input and Output Examples

[Executable example](python/example.py),from repository root:

```sh
.venv/bin/python machine-learning/optimization/genetic-algorithms/python/example.py
```

The example searches12 bits with population12,mutation_rate.1,crossover_rate.8,one elite and seed22. Its Hamming target has independently known optimum0; max_generations200. Target-reached means that explicit known threshold was met. Actual executed output:

```json
{"converged": true, "initial_best": 4.0, "iterations": 9, "known_target_value": 0, "objective": 0.0, "objective_evaluations": 111, "seed": 22, "status": "target-reached", "x": [1, 0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 0]}
```

## 16. Edge Cases

Population2..64,tournament2..P,elites1..P-1,bits1..32,generations1..1000. Crossover/mutation rates include0 and1. Require P+(P-elites)*max_generations<=20000 before allocation/evaluation. Initial populations must be exactly P-by-D integer/bool binary matrices. Invalid shapes,bits,probabilities,seeds and budgets fail clearly. Odd population sizes are supported; an unneeded last paired child is not evaluated.

## 17. Advantages

Explicit mathematics,independent hand/analytical checks,bounded loops,owned state and inspectable histories make this variant useful for learning and auditing. A supplied target_value yields target-reached only when observed best fitness meets it. Without that target,generation-budget or stagnation remains converged=False,even if a separately known optimum was encountered. No finite-run global convergence theorem is claimed.

## 18. Disadvantages and Limitations

Only binary encoding is implemented. Selection and variation can stagnate or miss a global optimum. Pure deterministic fitness is required because elite values are cached. Results on one small target do not establish universal search quality. Callback runtime cannot be bounded by an iteration counter; callbacks must return promptly. Numerical bounds are educational resource/domain limits,not a general constrained optimization solver.

## 19. When to Use It

Use it when the stated callback/representation and update rule match the intended mathematical experiment. Check units,scaling,objective normalization and stopping evidence before interpreting the result.

## 20. When Not to Use It

Do not use this binary variant for arbitrary real/permutation encodings without specifying new operators. For tiny domains,exhaustive enumeration may provide an exact answer. For smooth continuous vectors,use the relevant B10 gradient or curvature routine. No automatic encoding,derivative computation or constraint repair is hidden here.

## 21. Comparison With Related Algorithms

Simulated annealing follows one current state and may accept worse moves. GA evolves a population with elitism. Neither is a gradient method or a universal finite-run global solver. Related canonical paths stay unchanged; previous learners retain their original optimizer behavior.

## 22. Interview Questions

Why can signed fitness use tournaments? Selection compares objective order rather than normalizing signed numbers as probabilities. Which history is monotonic? Retained best under elitism. Does stagnation prove global optimality? No. How many new evaluations occur per generation? P-elite_count.

## 23. Practice Problems

Enumerate all size2 tournaments among4 uniquely ranked candidates. Reproduce fixed-mask crossover and mutation. Exhaustively enumerate a tiny binary domain and check a supplied target. Replay one full generation independently. Compare all declared seeds and preserve failures; no threshold is weakened to force target success.

## 24. References

Mitchell,[An Introduction to Genetic Algorithms — verified publisher record](https://mitpress.mit.edu/9780262631853/an-introduction-to-genetic-algorithms/); this project explicitly specifies its tournament/uniform/bit-flip variant rather than claiming to reproduce an unread book implementation.

[Project scope](../../../docs/optimization-scope.md),[numerical contracts](../../../docs/optimization-conventions.md) and independent tests specify this exact educational variant; no unread source or published benchmark reproduction is claimed.

## 25. Author Attribution

Algorithm Atlas is maintained by **[MD.Khalid Hasan](https://github.com/khalidhasan7343)**. [MIT License](../../../LICENSE); [contribution policy](../../../CONTRIBUTING.md). Preserve source attribution and canonical ownership.
