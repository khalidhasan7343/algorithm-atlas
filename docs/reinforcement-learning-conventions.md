# B8 RL numerical and environment contracts

Owner MD.Khalid Hasan, MIT. [Scope](reinforcement-learning-scope.md).

Observations are finite float64 vectors(d,) or batches(N,d); discrete actions are
native integer indices, continuous actions have explicit vector bounds. Reward
and raw observation magnitudes≤1e6. No bool/complex coercion or negative-index
wraparound. Public numerical functions reject nonfinite state/results. Local
Generator instances control randomness without changing global NumPy RNG state.

`reset(seed)` returns an initial observation, `step(action)` returns next observation,
reward,terminated,truncated,info. True terminals mask bootstrap. Time limits and
caller rollout cuts retain the next-state value. REINFORCE requires complete
terminal episodes and rejects cuts because it has no tail critic. Environments
reject step before reset/after done. Chain supplies discrete states0..2, left/right
retreat/advance and reward1 at terminal2; Bandit supplies[1], actions0/1,rewards0/1;
Continuous samples x∈[-1,1],a∈[-1,1],r=-(a-x/2)^2 in one step. Tests also supply
finite stochastic MDPs, vector encodings and multi-step environments without new
catalog topics or dataset dependencies.

Networks use tanh hidden units and linear heads with explicit analytic adjoints.
Stable shifted log-softmax supports categorical policies. Actor and critic gradients
clip independently at joint norm10; clipping is not a convergence guarantee.
REINFORCE uses the sum of gamma^t times reward-to-go log-probability terms for
its episodic discounted objective. A2C/A3C/PPO use the documented mean sampled
n-step advantage surrogate, with frozen advantages/targets and no GAE claim.
PPO retains old selected-action log probabilities across every epoch/minibatch;
clipping is a surrogate incentive, not a hard KL constraint.

DQN uses half-MSE fixed targets, uniform FIFO replay and hard target copies.
DDPG uses a tanh-bounded actor, state/action-concatenated Q critic, half-MSE TD
loss, deterministic actor gradient through fixed critic and soft targets. It uses
Gaussian noise,128 initial uniform exploratory interactions with critic-only updates,
critic rate.02 and slower actor rate.001. Critic hidden biases initialize uniformly
in[-.5,.5] to expose a non-odd tanh basis for quadratic rewards. Actor initialization
and all prior B7 utilities remain unchanged. Default toy training uses2400 episodes;
this is a finite diagnostic budget, not a universal task/hyperparameter promise.

A2C collects independent environments synchronously under frozen actor/critic.
A3C uses actual threads with independent environment/RNG/snapshot state; rollouts
and gradients execute outside its lock. Snapshots and global actor/critic updates
are lock-protected; worker-computed gradients apply to current globals, possibly
stale. There is no per-update rendezvous. This differs from original lock-free
Hogwild writes. Multiworker order is nondeterministic; only single-worker diagnostics
promise repeated seeded ordering. Errors cancel peers, close environments, join
workers and propagate their cause. Custom environments must return promptly;
Python cannot forcibly kill an indefinitely blocked callback. Timeout reports that
limitation and does not claim clean shutdown in that unsupported case.

Bounds: feature/action/hidden dimensions≤32 (DDPG input/action≤16 each); arrays
≤65536 cells; iterations/episodes≤5000,max_steps≤256,interactions≤100000;
replay≤4096,gradient updates≤10000,workers≤8. A2C environments≤8; PPO rollout
episodes≤32,epochs≤32,batch≤4096 with a conservative optimizer bound. MCTS
uses deterministic single-agent planning, terminal outcomes only, UCT, explicit
iteration/depth/branch bounds and no stochastic-transition or adversarial claim.

Training returns/losses are sampled pre-update diagnostics. Separate evaluation
resets environments and disables epsilon/sampling/noise (greedy categorical or
noise-free deterministic actions). Independent Bellman/gradient oracles establish
mathematics; small multi-seed learning checks establish only the stated diagnostic
behavior. No GPU, heavy framework, hidden network, weight or dataset download.
B7 primitives were inspected but retain their original array-fit APIs and bytes;
streaming transitions and concurrent worker state live in B8 support instead.
