"""Fixed small clustering cohorts; no test-fitted preprocessing or superiority claims."""
import importlib.util
import json
from pathlib import Path
import sys
import time

import numpy as np

spec=importlib.util.spec_from_file_location('atlas_clustering_support',Path(__file__).resolve().parents[1]/'support.py')
s=sys.modules.get(spec.name)
if s is None:
    s=importlib.util.module_from_spec(spec);sys.modules[spec.name]=s;spec.loader.exec_module(s)
metrics=s.module_at('atlas_clustering_metrics',s.ROOT/'metrics.py')


def main():
    rng=np.random.default_rng(16027)
    X=np.r_[rng.normal(-2.5,.12,(40,2)),rng.normal(2.5,.12,(40,2)),rng.uniform(-4,4,(16,2))]
    truth=np.r_[np.zeros(40,int),np.ones(40,int),np.full(16,-1,int)]
    order=rng.permutation(96);train,test=order[:64],order[64:]
    definitions=[
        ('k-means','KMeans',dict(n_clusters=2,n_init=5,random_state=16027)),
        ('agglomerative-hierarchical-clustering','AgglomerativeClustering',dict(n_clusters=2,linkage='ward')),
        ('divisive-hierarchical-clustering','DivisiveClustering',dict(n_clusters=2)),
        ('dbscan','DBSCAN',dict(eps=.5,min_samples=4)),
        ('hdbscan','HDBSCAN',dict(min_cluster_size=5,min_samples=4)),
        ('mean-shift','MeanShift',dict(bandwidth=.5,cluster_all=False)),
        ('gaussian-mixture-models','GaussianMixture',dict(n_components=2,means_init=[[-2.5,-2.5],[2.5,2.5]],reg_covar=.001,tol=1e-6)),
        ('spectral-clustering','SpectralClustering',dict(n_clusters=2,gamma=.3,n_init=5,random_state=16027)),
    ]
    results=[]
    for slug,name,parameters in definitions:
        model=getattr(s.load(slug),name)(**parameters)
        started=time.perf_counter();model.fit(X[train]);elapsed=time.perf_counter()-started
        record=dict(algorithm=slug,parameters=parameters,fit_seconds=elapsed,
                    train=metrics.clustering_report(X[train],model.labels_,truth=truth[train]),
                    test=None,test_policy='Transductive method; no invented out-of-sample labels')
        if hasattr(model,'predict'):
            started=time.perf_counter();prediction=model.predict(X[test]);query_seconds=time.perf_counter()-started
            record['test']=metrics.clustering_report(X[test],prediction,truth=truth[test])
            record['test_prediction_seconds']=query_seconds
            record['test_policy']='New-row centroid/mode/component assignment from fitted training model'
        if slug=='k-means':
            record['diagnostics']=dict(train_inertia=model.inertia_,test_squared_distance_sum=-model.score(X[test]),iterations=model.n_iter_)
        elif slug=='gaussian-mixture-models':
            record['diagnostics']=dict(train_mean_log_likelihood=model.score(X[train]),test_mean_log_likelihood=model.score(X[test]),
                                       train_aic=model.aic(X[train]),train_bic=model.bic(X[train]),iterations=model.n_iter_)
        elif slug=='spectral-clustering':
            record['diagnostics']=dict(normalized_cut=model.normalized_cut_,graph_components=model.n_connected_components_)
        elif slug=='hdbscan':
            assigned=model.probabilities_[model.labels_>=0]
            record['diagnostics']=dict(selected_clusters=model.n_clusters_,mean_assigned_membership=float(assigned.mean()) if len(assigned) else None)
        elif slug=='mean-shift':
            record['diagnostics']=dict(modes=len(model.cluster_centers_),max_seed_iterations=model.n_iter_)
        results.append(record)
    print(json.dumps(dict(seed=16027,cohort=96,n_train=64,n_test=32,p=2,train_indices=train.tolist(),test_indices=test.tolist(),
        construction='40 rows N((-2.5,-2.5),.12² I), 40 rows N((2.5,2.5),.12² I), 16 uniform background rows in [-4,4]^2; background truth label=-1.',
        preprocessing='None fitted; raw same numeric features. Fixed hyperparameters and initial means specified before evaluation; no test tuning or target labels passed to fit.',
        evaluation='ARI includes all rows and treats noise as one label. Silhouette excludes predicted noise, reports coverage, and is None when undefined. True labels are synthetic provenance, not guaranteed geometric groups.',
        limitations='Single controlled construction/split; transductive training labels are not held-out classifier accuracy. GMM is misspecified for uniform background. Timings are observational, with no universal winner/speed claim.',
        results=results),indent=2,allow_nan=False))


if __name__=='__main__':main()
