"""Small seeded anomaly observations; novelty and training-only evaluation stay distinct."""
import importlib.util
import json
from pathlib import Path
import sys
import time
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
_spec=importlib.util.spec_from_file_location('atlas_b12_support',ROOT/'machine-learning/anomaly-detection/support.py')
s=sys.modules.get(_spec.name)
if s is None:
    s=importlib.util.module_from_spec(_spec);sys.modules[_spec.name]=s;_spec.loader.exec_module(s)


def main():
    records=[]
    for seed in (21,22,23):
        rng=np.random.default_rng(seed)
        for case in ('gaussian','uniform','different-density-clusters','high-dimensional'):
            d=16 if case=='high-dimensional' else 2
            def normal(n):
                if case=='uniform':return rng.uniform(-.5,.5,(n,d))
                if case=='different-density-clusters':return np.r_[rng.normal(0,.05,(n//2,d)),rng.normal(3,.3,(n-n//2,d))]
                return rng.normal(0,.3,(n,d))
            training=np.r_[normal(60),rng.normal(7,.2,(6,d))]
            train_labels=np.r_[np.ones(60,dtype=int),-np.ones(6,dtype=int)]
            query=np.r_[normal(30),rng.normal(7,.2,(4,d))]
            query_labels=np.r_[np.ones(30,dtype=int),-np.ones(4,dtype=int)]
            methods=[('isolation-forest',s.load('isolation-forest').IsolationForest(32,max_samples=32,contamination=.1,random_state=seed)),
                     ('one-class-svm',s.load('one-class-svm').OneClassSVM(.1,max_iter=5000)),
                     ('local-outlier-factor',s.load('local-outlier-factor').LocalOutlierFactor(5,contamination=.1))]
            for topic,model in methods:
                start=time.perf_counter();model.fit(training);elapsed=time.perf_counter()-start
                if topic=='local-outlier-factor':
                    predictions,scores,labels=model.predict(),model.anomaly_scores(),train_labels
                    mode='training-set outlier detection;not held-out novelty'
                else:
                    predictions,scores,labels=model.predict(query),model.anomaly_scores(query),query_labels
                    mode='unseen independently sampled query novelty evaluation'
                row=dict(topic=topic,case=case,seed=seed,training_rows=66,features=d,training_anomalies=6,
                         evaluation_mode=mode,evaluation_rows=len(labels),metrics=s.anomaly_metrics(labels,predictions,scores),
                         threshold=model.threshold_,status=model.status_,converged=model.converged_,elapsed_seconds=elapsed)
                if topic=='one-class-svm':row.update(iterations=model.n_iter_,kkt_residual=model.kkt_residual_,pair_gap=model.pair_gap_,feasibility=model.feasibility_residual_,primal_dual_gap=model.primal_dual_gap_)
                records.append(row)
    data=dict(records=records,generating_process='Seeds21/22/23;60 Gaussian/uniform/two-density inliers+6 far Gaussian training anomalies;independent30+4 queries;16 features in the high-dimensional case. Labels are used only after unsupervised fitting.',
              limits='All declared outcomes retained. Different datasets and training-only LOF versus held-out novelty are not a direct performance ranking. Timings are executed observations,not CI thresholds or superiority claims. No universal anomaly ranking or calibrated probability guarantee.')
    (ROOT/'docs/anomaly-detection-evidence/educational-training-results.json').write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps(data))


if __name__=='__main__':main()
