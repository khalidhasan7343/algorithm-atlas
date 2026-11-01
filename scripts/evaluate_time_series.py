"""Execute modest chronological forecasts and held-out HMM likelihood observations."""
import importlib.util
import json
from pathlib import Path
import sys
import time
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location('atlas_b11_support', ROOT/'machine-learning/time-series/support.py')
s = sys.modules.get(_spec.name)
if s is None:
    s = importlib.util.module_from_spec(_spec)
    sys.modules[_spec.name] = s
    _spec.loader.exec_module(s)


def main():
    rng = np.random.default_rng(2313)
    t = np.arange(64.)
    seasonal = rng.normal(0, .1, 64)
    for i in range(4, len(seasonal)):
        seasonal[i] += .6*seasonal[i-4]
    tasks = [
        ('exponential-smoothing', 7+rng.normal(0, .1, 64), lambda:s.load('exponential-smoothing').ExponentialSmoothing(.3)),
        ('holt-winters', 10+.1*t+np.array([-1., .5, 1., -.5])[t.astype(int)%4]+rng.normal(0, .05, 64), lambda:s.load('holt-winters').HoltWinters(4)),
        ('arima', np.cumsum(.2+rng.normal(0, .05, 64)), lambda:s.load('arima').ARIMA((1, 1, 1))),
        ('sarima', seasonal, lambda:s.load('sarima').SARIMA((0, 0, 0), (1, 0, 0, 4), include_intercept=False)),
        ('prophet', 3+.1*t+.2*np.maximum(t-24, 0)+np.sin(2*np.pi*t/7)+rng.normal(0, .03, 64), lambda:s.load('prophet').Prophet(changepoints=(24,), seasonalities=((7, 1),)))]
    forecasts = []
    for topic, y, factory in tasks:
        start = time.perf_counter()
        model = factory().fit(y[:56])
        prediction = model.forecast(8)
        records = dict(topic=topic, generator_seed=2313, train_range=[0, 56], test_range=[56, 64], protocol='fixed-origin recursive8-step',
                       actual=y[56:].tolist(), predicted=prediction.tolist(), forecast_index=model.forecast_index(8).tolist(),
                       heldout_metrics=s.forecast_metrics(y[56:], prediction, training=y[:56], seasonal_period=4 if topic in ('holt-winters','sarima') else 1),
                       status=model.status_, converged=model.converged_, elapsed_seconds=time.perf_counter()-start)
        for name, window in [('expanding', None), ('rolling', 36)]:
            rows = s.backtest(factory, y, initial=48, horizon_size=4, step=8, window=window)
            records[name] = [dict(train_start=row['train_start'], train_stop=row['train_stop'], test_start=row['test_start'], test_stop=row['test_stop'], metrics=row['metrics']) for row in rows]
        forecasts.append(records)
    pi = np.array([.6, .4]);A = np.array([[.7, .3], [.2, .8]]);B = np.array([[.8, .2], [.3, .7]])
    def sample(length):
        state = int(rng.choice(2, p=pi));observations = []
        for _ in range(length):
            observations.append(int(rng.choice(2, p=B[state])))
            state = int(rng.choice(2, p=A[state]))
        return observations
    training = [sample(45), sample(40)];test = sample(30);hmm = []
    for seed in (21, 22, 23):
        model = s.load('hidden-markov-models').CategoricalHMM(2, 2, random_state=seed)
        before = model.score(test)
        model.fit(training, max_iter=25)
        hmm.append(dict(seed=seed, train_lengths=[45, 40], heldout_length=30, heldout_log_likelihood_before=before,
                        heldout_log_likelihood_after=model.score(test), training_likelihood_history=model.log_likelihood_history_.tolist(),
                        status=model.status_, converged=model.converged_, iterations=model.n_iter_))
    data = dict(seed=2313, forecasts=forecasts, hmm=hmm, source='Synthetic level/trend/seasonal/AR/integrated/changepoint and independently sampled categorical sequences; no downloads.',
                limits='Different tasks are not a performance ranking. Held-out metrics use unseen targets; all declared seeds/outcomes retained. Forecast accuracy is not proof of algorithm correctness. HMM held-out likelihood need not improve; no global EM optimum or statistical consistency claim.')
    (ROOT/'docs/time-series-evidence/educational-training-results.json').write_text(json.dumps(data, indent=2)+'\n')
    print(json.dumps(data))


if __name__ == '__main__':
    main()
