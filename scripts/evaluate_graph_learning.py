"""Executed small teaching observations; no benchmark/statistical superiority claim."""
import importlib.util
import json
from pathlib import Path
import sys
import time

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('atlas_b9_support',ROOT/'machine-learning/graph-learning/support.py')
support=sys.modules.get(spec.name)
if support is None:
    support=importlib.util.module_from_spec(spec);sys.modules[spec.name]=support;spec.loader.exec_module(support)


def main():
    A=np.zeros((6,6))
    for i,j,w in [(0,1,1),(0,2,1),(1,2,1),(2,3,.1),(3,4,1),(3,5,1),(4,5,1)]:A[i,j]=A[j,i]=w
    X=np.array([[1.,0],[1,.2],[.8,.1],[0,1],[.1,.8],[.2,1]])
    training_labels=np.array([0,-1,-1,1,-1,-1]);truth=np.array([0,0,0,1,1,1])
    outcomes=[]
    for seed in (21,22,23):
        start=time.perf_counter()
        node=support.load('node2vec').Node2Vec(p=.5,q=2.,epochs=100,random_state=seed).fit(A)
        elapsed=time.perf_counter()-start
        E=node.transform();norms=np.linalg.norm(E,axis=1)
        cosine=E@E.T/(norms[:,None]*norms[None,:])
        start=time.perf_counter()
        gcn=support.load('graph-convolutional-networks').GCNClassifier(epochs=200,learning_rate=.2,random_state=seed).fit(A,X,training_labels)
        gcn_elapsed=time.perf_counter()-start;predictions=gcn.predict(A,X)
        outcomes.append(dict(seed=seed,node2vec=dict(initial_loss=float(node.loss_history_[0]),final_loss=float(node.loss_history_[-1]),
            cosine_0_1=float(cosine[0,1]),cosine_0_4=float(cosine[0,4]),elapsed_seconds=elapsed),
            gcn=dict(initial_loss=float(gcn.loss_history_[0]),final_loss=float(gcn.loss_history_[-1]),
                     train_accuracy=float(np.mean(predictions[training_labels>=0]==truth[training_labels>=0])),
                     unknown_node_accuracy=float(np.mean(predictions[training_labels<0]==truth[training_labels<0])),
                     elapsed_seconds=gcn_elapsed)))
    multiclass=[]
    for classes in (2,3,8):
        model=support.load('graph-convolutional-networks').GCNClassifier(hidden_dim=8,epochs=50,learning_rate=.2,random_state=21).fit(
            np.zeros((classes,classes)),np.eye(classes),np.arange(classes))
        probs=model.predict_proba(np.zeros((classes,classes)),np.eye(classes))
        assert probs.shape==(classes,classes) and np.isfinite(probs).all()
        assert np.allclose(probs.sum(1),1.)
        multiclass.append(dict(classes=classes,initial_loss=float(model.loss_history_[0]),final_loss=float(model.loss_history_[-1]),
                               train_accuracy=float(np.mean(model.predict(np.zeros((classes,classes)),np.eye(classes))==np.arange(classes)))))
    data=dict(description='Three predeclared seeds on one tiny synthetic two-community graph; observations only.',
              seeds=[21,22,23],results=outcomes,multiclass_dimension_checks=multiclass,
              limitations='No confidence interval,guaranteed community separation,held-out graph benchmark or generalization claim. Unknown-node accuracy is an observation on this synthetic graph only; elapsed times are actual teaching-run measurements,not comparative benchmarks.')
    (ROOT/'docs/graph-learning-evidence/educational-training-results.json').write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps(data))


if __name__=='__main__':main()
