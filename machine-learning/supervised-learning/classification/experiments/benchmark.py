"""Three fixed synthetic cohorts; no downloads, test tuning or ranking claims.

Continuous scaling is fitted solely to training rows. Count features retain their
event interpretation; ID3 uses fixed, declared numeric bins, while C4.5 sees raw
continuous values alongside explicitly coded categories.
"""
import importlib.util
import json
from pathlib import Path
import sys
import time

import numpy as np

BASE=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('classification_experiment_metrics',BASE/'metrics.py')
metrics=importlib.util.module_from_spec(spec);spec.loader.exec_module(metrics)
support=sys.modules['atlas_classification_support']


def main():
    rng=np.random.default_rng(14028)
    def continuous(n):
        X=rng.normal(size=(n,3));y=(X @ [1.,.6,-.3]+rng.normal(0,.3,n)>0).astype(int)
        return X,y
    train,y_train=continuous(72);test,y_test=continuous(36)
    mean=train.mean(axis=0);scale=train.std(axis=0);scale[scale==0]=1
    X_train=(train-mean)/scale;X_test=(test-mean)/scale
    cases=[
        ('continuous','logistic-regression','LogisticRegression',dict(alpha=.1),X_train,y_train,X_test,y_test,'training-fitted standardization'),
        ('continuous','k-nearest-neighbors','KNearestNeighbors',dict(n_neighbors=5),X_train,y_train,X_test,y_test,'training-fitted standardization'),
        ('continuous','gaussian-naive-bayes','GaussianNaiveBayes',{},X_train,y_train,X_test,y_test,'training-fitted standardization'),
        ('continuous','support-vector-machines','SupportVectorMachine',dict(C=1.,max_iter=50000),X_train,y_train,X_test,y_test,'training-fitted standardization'),
        ('continuous','cart-decision-trees','CARTClassifier',dict(max_depth=4,min_samples_leaf=3),X_train,y_train,X_test,y_test,'training-fitted standardization'),
        ('continuous','linear-discriminant-analysis','LinearDiscriminantAnalysis',dict(reg=.01),X_train,y_train,X_test,y_test,'training-fitted standardization'),
        ('continuous','quadratic-discriminant-analysis','QuadraticDiscriminantAnalysis',dict(reg_param=.1),X_train,y_train,X_test,y_test,'training-fitted standardization'),
    ]
    def counts(n):
        y=np.arange(n)%2;rates=np.array([[5.,1,2,1],[1,5,1,2]])[y]
        return rng.poisson(rates).astype(float),y
    train,train_y=counts(60);test,test_y=counts(30)
    cases.extend([
        ('event-counts','multinomial-naive-bayes','MultinomialNaiveBayes',dict(alpha=1),train,train_y,test,test_y,'raw nonnegative counts'),
        ('event-counts','bernoulli-naive-bayes','BernoulliNaiveBayes',dict(alpha=1,binarize=2.),train,train_y,test,test_y,'presence iff count > 2'),
    ])
    def mixed(n):
        category=rng.integers(0,3,n);value=rng.uniform(-2,2,n);X=np.column_stack((category,value));y=((category==1)|(value>.6)).astype(int)
        return X,y
    train,train_y=mixed(72);test,test_y=mixed(36)
    bins=np.array([-.5,.5]);categorical_train=np.column_stack((train[:,0],np.digitize(train[:,1],bins)));categorical_test=np.column_stack((test[:,0],np.digitize(test[:,1],bins)))
    cases.extend([
        ('mixed','id3-decision-trees','ID3Classifier',dict(max_depth=4),categorical_train,train_y,categorical_test,test_y,'category code plus fixed bins [-.5,.5] of continuous feature'),
        ('mixed','c4-5-decision-trees','C45Classifier',dict(categorical_features=[0],max_depth=4),train,train_y,test,test_y,'column 0 categorical; column 1 raw continuous'),
    ])
    results=[]
    for cohort,topic,cls,parameters,X,y,Q,target,representation in cases:
        start=time.perf_counter();model=getattr(support.load(topic),cls)(**parameters).fit(X,y);elapsed=time.perf_counter()-start
        def evaluate(features,truth):
            report=metrics.classification_report(truth,model.predict(features),classes=model.classes_)
            report['log_loss']=metrics.log_loss(truth,model.predict_proba(features),model.classes_) if hasattr(model,'predict_proba') else None
            if not hasattr(model,'predict_proba'):report['log_loss_unavailable']='SVM provides uncalibrated margins, no probability API'
            return report
        results.append(dict(cohort=cohort,algorithm=topic,parameters=parameters,representation=representation,
                            train_samples=len(X),held_out_samples=len(Q),train=evaluate(X,y),held_out=evaluate(Q,target),
                            fit_seconds=elapsed,n_iter=getattr(model,'n_iter_',None),objective=getattr(model,'objective_',getattr(model,'primal_objective_',None)),
                            duality_gap=getattr(model,'duality_gap_',None),depth=getattr(model,'depth_',None),leaves=getattr(model,'n_leaves_',None)))
    print(json.dumps(dict(seed=14028,selection='All hyperparameters and ID3 bins fixed in source before test evaluation; no tuning',
                          continuous_scaler=dict(fitted_on='training rows only',mean=mean.tolist(),scale=scale.tolist()),
                          scope='Three educational cohorts with model-appropriate domains; no universal superiority or timing claim',results=results),indent=2,allow_nan=False))


if __name__=='__main__':main()
