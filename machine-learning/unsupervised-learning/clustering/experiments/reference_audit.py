"""Explicit, bounded reference experiment; not part of runtime fitting or pytest counts."""
import importlib.util
import json
from pathlib import Path
import sys

import numpy as np
from sklearn.cluster import HDBSCAN
from sklearn.metrics import adjusted_rand_score

spec=importlib.util.spec_from_file_location('atlas_clustering_support',Path(__file__).resolve().parents[1]/'support.py')
s=sys.modules.get(spec.name)
if s is None:
    s=importlib.util.module_from_spec(spec);sys.modules[spec.name]=s;spec.loader.exec_module(s)


def main():
    records=[]
    for seed in range(16200,16210):
        X=np.random.default_rng(seed).normal(size=(18,2))
        ours=s.load('hdbscan').HDBSCAN(min_cluster_size=3,min_samples=2).fit(X)
        reference=HDBSCAN(min_cluster_size=3,min_samples=2,algorithm='brute',copy=True).fit(X)
        agreement=float(adjusted_rand_score(ours.labels_,reference.labels_))
        difference=float(np.max(np.abs(ours.probabilities_-reference.probabilities_)))
        assert agreement==1 and difference<1e-10
        records.append(dict(seed=seed,rows=18,features=2,adjusted_rand=agreement,max_probability_difference=difference))
    print(json.dumps(dict(status='passed',data='np.random.default_rng(seed).normal(size=(18,2))',
        parameters=dict(min_cluster_size=3,min_samples=2,metric='euclidean',alpha=1,cluster_selection_method='eom',allow_single_cluster=False),
        cases=records,pytest_count='separate experiment; not added to pytest totals'),indent=2))


if __name__=='__main__':main()
