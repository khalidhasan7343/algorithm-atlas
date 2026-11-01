import itertools
import math
import numpy as np
import pytest
pytestmark=[pytest.mark.ml]


def crf(b13,**kwargs):
    return b13.load('conditional-random-fields').LinearChainCRF(['A','B'],2,**kwargs)


def enumerate_oracle(m,x):
    p=m.parameters_;rows=[]
    for y in itertools.product(range(len(m.labels_)),repeat=len(x)):
        if not m.allowed_start_[y[0]] or any(not m.allowed_transitions_[a,b] for a,b in zip(y,y[1:])):continue
        value=p['start'][y[0]]+p['end'][y[-1]]
        value+=sum(sum(float(x[t,f])*float(p['emission'][f,y[t]]) for f in range(x.shape[1])) for t in range(len(x)))
        value+=sum(float(p['transition'][a,b]) for a,b in zip(y,y[1:]))
        rows.append((y,value))
    maximum=max(score for _,score in rows);z=maximum+math.log(sum(math.exp(score-maximum) for _,score in rows))
    token=np.zeros((len(x),len(m.labels_)));pair=np.zeros((len(x)-1,len(m.labels_),len(m.labels_)))
    for y,value in rows:
        weight=math.exp(value-z)
        for t,label in enumerate(y):token[t,label]+=weight
        for t,(a,b) in enumerate(zip(y,y[1:])):pair[t,a,b]+=weight
    return rows,z,token,pair


@pytest.mark.oracle
@pytest.mark.parametrize('length',[1,2,3,4])
@pytest.mark.parametrize('masked',[False,True])
def test_crf_partition_forward_backward_viterbi_exhaustive(b13,length,masked):
    allowed=np.array([[True,True],[False,True]]) if masked else None
    m=crf(b13,allowed_transitions=allowed);rng=np.random.default_rng(51)
    for value in m.parameters_.values():value[:]=rng.normal(size=value.shape)*.4
    x=rng.normal(size=(length,2));rows,z,tok,pair=enumerate_oracle(m,x);info=m.infer(x)
    np.testing.assert_allclose(info['log_partition'],z,atol=1e-12)
    np.testing.assert_allclose(info['token_marginals'],tok,atol=1e-12)
    np.testing.assert_allclose(info['pair_marginals'],pair,atol=1e-12)
    path,value=m.decode(x);best=max(rows,key=lambda row:row[1])
    assert tuple(path)==best[0];np.testing.assert_allclose(value,best[1],atol=1e-12)
    for y,score in rows:np.testing.assert_allclose(m.log_probability(x,[m.labels_[i] for i in y]),score-z)
    np.testing.assert_allclose(info['log_forward'][0]+info['log_backward'][0]-z,np.log(tok[0]))


@pytest.mark.oracle
@pytest.mark.numerical
@pytest.mark.parametrize('group',['emission','transition','start','end'])
@pytest.mark.parametrize('masked',[False,True])
def test_crf_gradient_all_parameter_groups_finite_difference(b13,group,masked):
    m=crf(b13,allowed_transitions=np.array([[True,True],[False,True]]) if masked else None)
    rng=np.random.default_rng(4)
    for value in m.parameters_.values():value[:]=rng.normal(size=value.shape)*.2
    x=np.array([[.3,-.2],[.6,.4],[-.1,.8]]);y=['A','A','B']
    loss,g=m.loss_gradients(x,y);eps=1e-6;actual=[]
    for index in np.ndindex(m.parameters_[group].shape):
        old=m.parameters_[group][index];m.parameters_[group][index]=old+eps;plus=m.loss_gradients(x,y)[0]
        m.parameters_[group][index]=old-eps;minus=m.loss_gradients(x,y)[0];m.parameters_[group][index]=old
        actual.append((plus-minus)/(2*eps))
    np.testing.assert_allclose(g[group].ravel(),actual,rtol=2e-6,atol=3e-9)


@pytest.mark.oracle
def test_crf_hand_zero_scores_loss_gradient_and_update(b13):
    m=crf(b13,l2=0,learning_rate=.1,max_iter=1,tolerance=0);x=np.array([[1.,0.],[1.,1.]])
    loss,g=m.loss_gradients(x,['A','B'])
    assert loss==math.log(4);assert m.predict(x)==['A','A']
    np.testing.assert_allclose(g['emission'],[[0,0],[.5,-.5]])
    np.testing.assert_allclose(g['transition'],[[.25,-.75],[.25,.25]])
    np.testing.assert_allclose(g['start'],[-.5,.5]);np.testing.assert_allclose(g['end'],[.5,-.5])
    m.fit([x],[['A','B']]);assert m.n_iter_==1 and not m.converged_
    for name in g:np.testing.assert_allclose(m.parameters_[name],-.1*g[name])
    assert m.loss_history_[-1]<m.loss_history_[0]


@pytest.mark.oracle
def test_crf_bio_legal_partition_impossible_and_constraints(b13):
    cls=b13.load('conditional-random-fields').LinearChainCRF
    m=cls(['O','B-X','I-X'],1,allowed_start=[True,True,False],allowed_transitions=[[True,True,False],[True,True,True],[True,True,True]])
    np.testing.assert_allclose(m.log_partition([[1],[1]]),math.log(5),rtol=0,atol=1e-14)
    assert m.infer([[1],[1]])['token_marginals'][0,2]==0
    with pytest.raises(ValueError):m.loss_gradients([[1],[1]],['O','I-X'])
    impossible=cls(['A'],1,allowed_start=[False])
    with pytest.raises(ValueError):impossible.infer([[1]])
    with pytest.raises(ValueError):impossible.decode([[1]])


@pytest.mark.numerical
def test_crf_numerical_extreme_scores_padding_lengths_and_ownership(b13):
    m=crf(b13);m.parameters_['emission'][:]=[[1000,-1000],[-900,900]]
    x=np.array([[1.,0.],[0.,1.]])
    np.testing.assert_allclose(m.infer(x)['token_marginals'].sum(1),1)
    assert np.isfinite(m.log_partition(x)) and np.isfinite(m.loss_gradients(x,['A','B'])[0])
    padded=np.vstack((x,[100,100]));assert m.predict(padded,length=2)==m.predict(x)
    assert m.log_partition(padded,length=2)==m.log_partition(x)
    out=m.infer(x);out['token_marginals'][:]=5;np.testing.assert_allclose(m.infer(x)['token_marginals'].sum(1),1)
    path,_=m.decode(x);path[:]=99;assert m.decode(x)[0].max()<2


def test_crf_deterministic_training_objective_l2_and_no_eval_leak(b13):
    x=[np.eye(2),np.array([[1.,.1],[.1,1.]])];y=[['A','B'],['A','B']]
    a,b=crf(b13),crf(b13);a.fit(x,y);b.fit(x,y)
    for name in a.parameters_:np.testing.assert_array_equal(a.parameters_[name],b.parameters_[name])
    assert a.loss_history_[-1]<a.loss_history_[0] and np.all(np.diff(a.loss_history_)<=0)
    assert a.predict(x[0])==y[0]
    before={n:p.copy() for n,p in a.parameters_.items()};a.log_probability(x[0],['B','A'])
    for n in before:np.testing.assert_array_equal(before[n],a.parameters_[n])
    assert a.loss_history_[0]==math.log(4)
    expected=sum(a.loss_gradients(features,labels)[0] for features,labels in zip(x,y))/2+.5*a.l2*sum(np.sum(p*p) for p in a.parameters_.values())
    np.testing.assert_allclose(expected,a.loss_history_[-1])


def test_crf_fit_padding_equivalence_and_atomicity(b13):
    x=np.eye(2);a,b=crf(b13,max_iter=4),crf(b13,max_iter=4)
    a.fit([x],[['A','B']]);b.fit([np.vstack((x,[99,99]))],[['A','B']],lengths=[2])
    for n in a.parameters_:np.testing.assert_array_equal(a.parameters_[n],b.parameters_[n])
    before={n:p.copy() for n,p in a.parameters_.items()}
    with pytest.raises(ValueError):a.fit([x],[['BAD','B']])
    for n in before:np.testing.assert_array_equal(before[n],a.parameters_[n])


@pytest.mark.parametrize('x',[[],[[float('nan'),0]],[[True,False]],[[1]],np.zeros((65,2)),[[101,0]],[[1j,0]],[[float('inf'),0]]])
def test_crf_invalid_features(b13,x):
    with pytest.raises(ValueError):crf(b13).infer(x)


@pytest.mark.parametrize('kwargs',[{'n_features':0},{'labels':[]},{'labels':['A','A']},{'labels':['']},{'max_iter':201},{'l2':-1},{'learning_rate':0},{'tolerance':float('nan')},{'allowed_start':[1,1]},{'allowed_transitions':[[True]]}])
def test_crf_invalid_hyperparameters(b13,kwargs):
    options=dict(labels=['A','B'],n_features=2);options.update(kwargs)
    with pytest.raises(ValueError):b13.load('conditional-random-fields').LinearChainCRF(**options)


@pytest.mark.parametrize('length',[0,3,True,float('nan')])
def test_crf_invalid_lengths(b13,length):
    with pytest.raises(ValueError):crf(b13).predict(np.eye(2),length=length)


@pytest.mark.parametrize('labels',[[],['A'],['A','X'],[0,1]])
def test_crf_invalid_labels(b13,labels):
    with pytest.raises(ValueError):crf(b13).loss_gradients(np.eye(2),labels)


def test_crf_invalid_parameter_state_and_work_bound(b13):
    m=crf(b13);m.parameters_['start'][0]=np.inf
    with pytest.raises(ValueError):m.infer(np.eye(2))
    big=b13.load('conditional-random-fields').LinearChainCRF(list('ABCDEFGH'),1,max_iter=200)
    with pytest.raises(ValueError):big.fit([np.ones((64,1))]*32,[['A']*64]*32)


def test_crf_dense_work_budget_and_mutated_fit_settings(b13):
    cls=b13.load('conditional-random-fields').LinearChainCRF
    big=cls(list('ABCDEFGH'),128,max_iter=200)
    with pytest.raises(ValueError):big.fit([np.ones((64,128))]*16,[['A']*64]*16)
    m=crf(b13);m.max_iter=100000
    with pytest.raises(ValueError):m.fit([np.eye(2)],[['A','B']])


@pytest.mark.numerical
def test_crf_backtracking_high_feature_scale_is_monotonic(b13):
    m=crf(b13,learning_rate=1.,l2=.1,max_iter=5).fit([100*np.eye(2)],[['A','B']])
    assert np.isfinite(m.loss_history_).all() and np.all(np.diff(m.loss_history_)<=0)
    assert m.loss_history_[-1]<m.loss_history_[0]
