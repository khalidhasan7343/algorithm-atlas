import numpy as np
from numpy.testing import assert_allclose
import pytest
pytestmark=pytest.mark.ml

@pytest.fixture(params=['exponential-smoothing','holt-winters','arima','sarima','prophet'])
def factory(request,b11):
    factories = {'exponential-smoothing':lambda:b11.load('exponential-smoothing').ExponentialSmoothing(),
                 'holt-winters':lambda:b11.load('holt-winters').HoltWinters(2),
                 'arima':lambda:b11.load('arima').ARIMA((0,0,0)),
                 'sarima':lambda:b11.load('sarima').SARIMA((0,0,0),(0,0,0,2)),
                 'prophet':lambda:b11.load('prophet').Prophet(seasonalities=())}
    return factories[request.param]

@pytest.mark.parametrize('bad',[[],[np.nan]*8,[np.inf]*8,[[1,2]]*4,[True]*8,['x']*8,[1e7]*8])
def test_invalid_series(factory,bad):
    with pytest.raises(ValueError):factory().fit(bad)

@pytest.mark.parametrize('h',[0,-1,129,True,1.5])
def test_invalid_horizons(factory,h):
    m=factory().fit(np.arange(8.))
    with pytest.raises(ValueError):m.forecast(h)
    with pytest.raises(ValueError):m.forecast_index(h)

@pytest.mark.parametrize('timestamps',[np.arange(7.),[0,1,2,3,4,5,6,6],[0,1,2,3,4,5,6,8],list(reversed(range(8))),[np.nan]*8])
def test_reject_irregular_duplicate_or_missing_times(factory,timestamps):
    with pytest.raises(ValueError):factory().fit(np.arange(8.),timestamps=timestamps)

def test_datetime_and_frequency_alignment(factory):
    times=np.arange('2026-01-01','2026-01-09',dtype='datetime64[D]')
    m=factory().fit(np.arange(8.),timestamps=times,frequency=86400)
    assert_allclose(m.forecast_index(2).astype('datetime64[D]').astype(int),np.array(['2026-01-09','2026-01-10'],dtype='datetime64[D]').astype(int))
    with pytest.raises(ValueError):factory().fit(np.arange(8.),timestamps=times,frequency=1)
    times[3]=np.datetime64('NaT','D')
    with pytest.raises(ValueError):factory().fit(np.arange(8.),timestamps=times)

def test_ownership_repeated_fit_and_failed_refit_atomicity(factory):
    y=np.arange(8.);m=factory().fit(y);prediction=m.forecast(3);y[:]=1000
    assert_allclose(m.forecast(3),prediction)
    prediction[:]=1000
    assert_allclose(m.forecast(3),factory().fit(np.arange(8.)).forecast(3))
    before=m.forecast(3)
    with pytest.raises(ValueError):m.fit([np.nan]*8)
    assert_allclose(m.forecast(3),before)

@pytest.mark.oracle
@pytest.mark.parametrize('lags',[[1],[1,1],[3],[3,1],[3,1,1]])
def test_inverse_difference_exact_and_forecast_alignment(b11,lags):
    y=np.arange(1.,31.)**2;z,trace=b11.difference(y[:20],lags)
    expected=y[:23].copy()
    for lag in lags:expected=expected[lag:]-expected[:-lag]
    assert_allclose(b11.inverse_difference(expected[-3:],trace),y[20:23])
    assert_allclose(z,expected[:-3])
    assert_allclose(b11.inverse_difference([2e6],[(1,np.array([-1e6]))]),[1e6])

@pytest.mark.oracle
def test_metrics_training_only_scale_and_zero_semantics(b11):
    m=b11.forecast_metrics([2.,4.],[1.,6.],training=[1.,3.,5.])
    assert_allclose([m['mae'],m['mse'],m['rmse'],m['mape'],m['mase']],[1.5,2.5,np.sqrt(2.5),50,.75])
    m=b11.forecast_metrics([0.,0.],[0.,2.]);assert m['mape'] is None and m['smape']==100
    for a,p in [([],[]),([1,2],[1]),([1],[np.inf])]:
        with pytest.raises(ValueError):b11.forecast_metrics(a,p)
    with pytest.raises(ValueError):b11.forecast_metrics([1],[2],training=[3,3,3])

@pytest.mark.parametrize('window',[None,6])
def test_chronological_expanding_and_rolling_no_future_leakage(b11,window):
    factory=lambda:b11.load('exponential-smoothing').ExponentialSmoothing(.4)
    y=np.arange(20.);rows=b11.backtest(factory,y,initial=8,horizon_size=3,step=3,window=window)
    for row in rows:
        cutoff=row['train_stop'];start=row['train_start']
        expected=factory().fit(y[start:cutoff]).forecast(3)
        assert_allclose(row['predicted'],expected);assert_allclose(row['actual'],y[cutoff:cutoff+3])
    changed=y.copy();changed[8:]+=1000
    other=b11.backtest(factory,changed,initial=8,horizon_size=3,step=3,window=window)
    assert_allclose(rows[0]['predicted'],other[0]['predicted'])

@pytest.mark.parametrize('topic',['arima','sarima','prophet'])
@pytest.mark.parametrize('window',[None,36])
def test_training_only_transform_normalization_and_recursive_leakage_audit(b11,topic,window):
    factories={
        'arima':lambda:b11.load('arima').ARIMA((1,1,1),max_iter=60),
        'sarima':lambda:b11.load('sarima').SARIMA((1,1,1),(1,1,1,4),max_iter=60),
        'prophet':lambda:b11.load('prophet').Prophet(changepoints=(12,),seasonalities=((7,1),))}
    y=.2*np.arange(64.)+np.sin(2*np.pi*np.arange(64)/7)+np.random.default_rng(2312).normal(0,.1,64)
    factory=factories[topic]
    rows=b11.backtest(factory,y,initial=48,horizon_size=3,step=8,window=window)
    for row in rows:
        training=y[row['train_start']:row['train_stop']]
        direct=factory().fit(training)
        assert_allclose(row['predicted'],direct.forecast(3),atol=0,rtol=0)
        assert row['test_start']==row['train_stop']
        if topic!='prophet':
            transformed=training.copy()
            if topic=='sarima':transformed=transformed[4:]-transformed[:-4]
            transformed=transformed[1:]-transformed[:-1]
            scale=max(np.std(transformed),np.max(np.abs(transformed))*1e-3,1e-8)
            assert_allclose(direct.normalization_scale_,scale,atol=0,rtol=0)
        else:
            assert_allclose(direct.design_matrix_[:,1],np.arange(len(training))/(len(training)-1))
    changed=y.copy();changed[48:]+=1000
    other=b11.backtest(factory,changed,initial=48,horizon_size=3,step=8,window=window)
    assert_allclose(rows[0]['predicted'],other[0]['predicted'],atol=0,rtol=0)

@pytest.mark.parametrize('kwargs',[dict(initial=0),dict(initial=4,horizon_size=0),dict(initial=4,step=0),dict(initial=4,window=5),dict(initial=4,horizon_size=60),dict(initial=1)])
def test_backtest_rejects_invalid_or_excessive_work_before_fitting(b11,kwargs):
    with pytest.raises(ValueError):b11.backtest(lambda:None,np.arange(50.),**kwargs)


def test_backtest_rejects_invalid_model_factory_and_reused_state(b11):
    with pytest.raises(ValueError):b11.backtest(lambda:None,np.arange(20.),initial=6,horizon_size=3,step=3)
    same=b11.load('exponential-smoothing').ExponentialSmoothing()
    with pytest.raises(ValueError):b11.backtest(lambda:same,np.arange(20.),initial=6,horizon_size=3,step=3)

@pytest.mark.numerical
@pytest.mark.parametrize('metric',['mape','mase'])
def test_nonrepresentable_metric_ratio_reports_numerical_error(b11,metric):
    import warnings
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        with pytest.raises(b11.NumericalError):
            if metric=='mape':b11.forecast_metrics([1e-320],[1.])
            else:b11.forecast_metrics([1.],[2.],training=[0.,1e-320])
    assert not caught
    assert np.isfinite(b11.forecast_metrics([1e-20],[1.])['mape'])
