"""Fixed small train/test cohorts; observations, not performance superiority claims."""
import importlib.util
import json
from pathlib import Path
import sys
import time

import numpy as np

spec=importlib.util.spec_from_file_location('atlas_ensemble_support',Path(__file__).resolve().parents[1]/'support.py')
s=sys.modules.get(spec.name)
if s is None:
    s=importlib.util.module_from_spec(spec);sys.modules[spec.name]=s;spec.loader.exec_module(s)


def main():
    rng=np.random.default_rng(15027);X=rng.uniform(-2,2,size=(64,2));order=rng.permutation(64)
    train,test=order[:48],order[48:]
    regression_y=1+.8*X[:,0]-.3*X[:,1]+.4*(X[:,0]>0)+rng.normal(0,.08,64)
    labels=np.where(X[:,0]+.3*X[:,1]>0,'positive','negative')
    results=[]
    models={
        'single-tree-classifier':s.module_at('atlas_ensemble_tree',s.ROOT/'tree.py').WeightedTree(task='classification',max_depth=2),
        'single-tree-regressor':s.module_at('atlas_ensemble_tree',s.ROOT/'tree.py').WeightedTree(max_depth=2),
    }
    for count in (3,9):
        models['bagging-classifier-'+str(count)]=s.load('bagging').BaggingClassifier(n_estimators=count,max_depth=2,random_state=15027)
        models['forest-classifier-'+str(count)]=s.load('random-forest').RandomForestClassifier(n_estimators=count,max_depth=2,random_state=15027)
        models['bagging-regressor-'+str(count)]=s.load('bagging').BaggingRegressor(n_estimators=count,max_depth=2,random_state=15027)
        models['forest-regressor-'+str(count)]=s.load('random-forest').RandomForestRegressor(n_estimators=count,max_depth=2,random_state=15027)
    models.update({
        'adaboost':s.load('adaboost').AdaBoostClassifier(n_estimators=9,learning_rate=.5),
        'voting':s.load('voting-classifiers').VotingClassifier(voting='soft'),
        'stacking-classifier':s.load('stacking').StackingClassifier(n_splits=3),
        'stacking-regressor':s.load('stacking').StackingRegressor(n_splits=3),
        'gbm':s.load('gradient-boosting-machine').GradientBoostingRegressor(n_estimators=9,learning_rate=.2),
        'xgboost':s.load('xgboost').XGBoostRegressor(n_estimators=9,learning_rate=.2),
        'catboost':s.load('catboost').CatBoostRegressor(categorical_features=[1],n_estimators=4,learning_rate=.2,max_depth=2,random_state=15027),
    })
    for name,model in models.items():
        classifier=('classifier' in name or name in ('adaboost','voting'))
        features=X
        if name=='catboost':
            features=np.empty(X.shape,dtype=object);features[:,0]=X[:,0];features[:,1]=np.where(X[:,1]>0,'upper','lower')
        y=labels if classifier else regression_y
        started=time.perf_counter();model.fit(features[train],y[train]);fit_seconds=time.perf_counter()-started
        record=dict(model=name,task='classification' if classifier else 'regression',fit_seconds=fit_seconds)
        for part,indices in (('train',train),('test',test)):
            started=time.perf_counter();prediction=model.predict(features[indices]);elapsed=time.perf_counter()-started
            if classifier:
                evaluation=s.metrics.classification_report(y[indices],prediction,classes=model.classes_)
                if hasattr(model,'predict_proba'):evaluation['log_loss']=s.metrics.log_loss(y[indices],model.predict_proba(features[indices]),model.classes_)
            else:evaluation=s.regression.regression_metrics(y[indices],prediction)
            record[part]=dict(metrics=evaluation,prediction_seconds=elapsed)
        results.append(record)
    print(json.dumps(dict(seed=15027,cohort=64,n_train=48,n_test=16,p=2,train_indices=train.tolist(),test_indices=test.tolist(),
        preprocessing='No fitted preprocessing; all numeric models share raw features. CatBoost explicitly replaces feature 1 with its sign category, so it is a distinct feature view.',
        parameters='Fixed before evaluation; no tuning on test. Base/3/9-size comparisons are descriptive.',
        limitations='Single synthetic split; observational timings; no universal winner, improvement or speed claim.',results=results),indent=2))


if __name__=='__main__':main()
