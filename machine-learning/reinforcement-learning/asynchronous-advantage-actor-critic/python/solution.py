"""Concurrent local-rollout actor-critic with lock-protected asynchronous SGD.

Snapshots and global applications are atomic. Rollouts and local gradients run
outside the lock; workers never wait for one another at an update barrier.
This deliberately differs from the original lock-free Hogwild formulation.
"""
import importlib.util
from pathlib import Path
import queue
import sys
import threading
import time
import numpy as np

_spec = importlib.util.spec_from_file_location('atlas_b8_support', Path(__file__).resolve().parents[2] / 'support.py')
support = sys.modules.get(_spec.name)
if support is None:
    support = importlib.util.module_from_spec(_spec)
    sys.modules[_spec.name] = support
    _spec.loader.exec_module(support)
base = support.load('advantage-actor-critic')
loss_gradients = base.loss_gradients


class A3C(base.A2C):
    def train(self, factory=support.Bandit, iterations=100, max_steps=32, workers=2, timeout=30.):
        support.budget(iterations, max_steps)
        support.integer(workers, 'workers', 1, 8)
        support.scalar(timeout, 'timeout', .01, 60.)
        if iterations * max_steps * workers > 100000 or iterations * workers > 10000:
            raise ValueError('worker interaction/update budget exceeded')
        lock, start, stop = threading.Lock(), threading.Event(), threading.Event()
        errors = queue.Queue()
        self.worker_records_, self.loss_history_, self.returns_ = [], [], []
        self.updates_ = 0
        seeds = np.random.SeedSequence(int(self.rng.integers(2 ** 32))).spawn(workers)
        self.worker_seeds_ = [int(seed.generate_state(1)[0]) for seed in seeds]

        def worker(index):
            env = None
            try:
                rng = np.random.default_rng(self.worker_seeds_[index])
                env = factory()
                start.wait(timeout)
                for iteration in range(iterations):
                    if stop.is_set():
                        break
                    with lock:
                        local_actor = support.copy(self.actor)
                        local_critic = support.copy(self.critic)
                        snapshot_version = self.updates_
                    x, a, targets, total = support.collect(local_actor, local_critic, env, rng, max_steps, self.gamma)
                    al, cl, ag, cg = loss_gradients(local_actor, local_critic, x, a, targets)
                    with lock:
                        if stop.is_set():
                            break
                        # Apply worker gradients to current GLOBAL parameters, not its snapshot.
                        actor, critic = support.copy(self.actor), support.copy(self.critic)
                        support.apply(actor, ag, self.learning_rate)
                        support.apply(critic, cg, self.learning_rate)
                        self.actor, self.critic = actor, critic
                        self.updates_ += 1
                        self.returns_.append(total)
                        self.loss_history_.append((al, cl))
                        self.worker_records_.append(dict(worker=index, iteration=iteration,
                            snapshot_version=snapshot_version, applied_version=self.updates_,
                            trajectory_length=len(a), thread_id=threading.get_ident()))
            except BaseException as error:
                errors.put((index, error))
                stop.set()
            finally:
                if env is not None and hasattr(env, 'close'):
                    try:
                        env.close()
                    except BaseException as error:
                        errors.put((index, error))
                        stop.set()

        # Daemon is a last-resort escape for a malicious/blocking user environment;
        # supported environments return promptly and every worker is joined.
        threads = [threading.Thread(target=worker, args=(i,), name=f'atlas-a3c-{i}', daemon=True) for i in range(workers)]
        self.workers_created_ = workers
        deadline = time.monotonic() + timeout
        for thread in threads:
            thread.start()
        start.set()
        for thread in threads:
            thread.join(max(0., deadline - time.monotonic()))
        stop.set()
        self.workers_alive_ = sum(thread.is_alive() for thread in threads)
        if self.workers_alive_:
            # Wait briefly for cooperative bounded environments to observe cancellation.
            for thread in threads:
                thread.join(.1)
            self.workers_alive_ = sum(thread.is_alive() for thread in threads)
            raise RuntimeError('A3C timeout; environment must return promptly for clean shutdown')
        if not errors.empty():
            index, error = errors.get()
            raise RuntimeError(f'A3C worker {index} failed') from error
        self.optimization_status_ = 'fixed-budget-completed'
        return self
