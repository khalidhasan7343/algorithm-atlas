"""Small numerical/data/SGD utilities; architectures and analytic gradients stay local."""
from functools import lru_cache,wraps
import importlib.util
import json
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parent
TOPICS=('multilayer-perceptron','convolutional-neural-networks','residual-networks',
        'recurrent-neural-networks','long-short-term-memory','gated-recurrent-units',
        'transformers','denoising-autoencoders','sparse-autoencoders','variational-autoencoders',
        'generative-adversarial-networks','diffusion-models','graph-neural-networks','vanilla-autoencoders')


def numerical(function):
    @wraps(function)
    def guarded(*args,**kwargs):
        try:
            with np.errstate(over='raise',divide='raise',invalid='raise',under='ignore'):
                result=function(*args,**kwargs)
                def check(value):
                    if isinstance(value,np.ndarray) and not np.isfinite(value).all():raise ValueError('nonfinite numerical output')
                    if isinstance(value,(tuple,list)):
                        for part in value:check(part)
                check(result)
                return result
        except (FloatingPointError,OverflowError,np.linalg.LinAlgError) as error:
            raise ValueError('unresolved numerical computation; rescale data or reduce learning rate') from error
    return guarded


def integer(x,name,low,high):
    if type(x) is not int or not low<=x<=high:
        raise ValueError(f'{name} must be native int in {low}..{high}')
    return x


def scalar(x,name,low,high,positive=False):
    if isinstance(x,(bool,np.bool_)) or not isinstance(x,(int,float,np.integer,np.floating)):
        raise ValueError(f'{name} must be a finite real')
    x=float(x)
    if not np.isfinite(x) or not low<=x<=high or (positive and x==low):
        raise ValueError(f'{name} outside supported range')
    return x


def boolean(x,name):
    if type(x) is not bool:raise ValueError(f'{name} must be bool')
    return x


def array(X,ndim=2,*,fitting=False,shape=None):
    a=np.asarray(X)
    if a.ndim!=ndim or a.dtype.kind not in 'iuf' or a.size>262144:
        raise ValueError('numeric real array with supported rank/cell count required')
    if len(a)>(128 if fitting else 256) or (fitting and len(a)<2) or any(d<1 for d in a.shape[1:]):
        raise ValueError('sample/empty-dimension bounds exceeded')
    if shape is not None and a.shape[1:]!=tuple(shape):raise ValueError('feature/tensor shape differs from fitted shape')
    a=np.array(a,dtype=float,copy=True)
    if not np.isfinite(a).all() or np.any(abs(a)>1e6):raise ValueError('finite values with magnitude<=1e6 required')
    return a


def tabular(X,**kwargs):
    a=array(X,**kwargs)
    if a.shape[1]>16:raise ValueError('at most16 features')
    return a


def sequence(X,**kwargs):
    a=array(X,ndim=3,**kwargs)
    if a.shape[1]>16 or a.shape[2]>16:raise ValueError('sequence length/features<=16')
    return a


def images(X,**kwargs):
    a=array(X,ndim=4,**kwargs)
    if a.shape[1]>2 or max(a.shape[2:])>8:raise ValueError('NCHW images: channels<=2,H/W<=8')
    return a


def latent(Z,k):
    a=np.asarray(Z)
    if a.ndim!=2 or a.shape[1]!=k or len(a)>256 or a.dtype.kind not in 'iuf':raise ValueError('finite latent matrix with fitted bottleneck required')
    a=np.array(a,dtype=float,copy=True)
    if not np.isfinite(a).all():raise ValueError('nonfinite latent coordinates')
    return a


def targets(y,n,binary=False):
    a=np.asarray(y)
    if binary:
        raw=np.asarray(y,dtype=object)
        valid=(raw.ndim==1 and len(raw)==n and all(isinstance(v,(int,np.integer)) and not isinstance(v,(bool,np.bool_)) and v in (0,1) for v in raw.tolist()))
        if not valid:raise ValueError('binary y must be integer0/1 vector, excluding bool/float labels')
        return np.asarray(y,dtype=float)[:,None]
    a=array(y,shape=(1,))
    if len(a)!=n:raise ValueError('target length differs from X')
    return a


def sigmoid(x):
    # tanh formulation never forms an overflowing exp(-x).
    return .5*(1+np.tanh(.5*x))


def softmax(x):
    shifted=x-np.max(x,axis=-1,keepdims=True)
    weights=np.exp(shifted)
    return weights/weights.sum(axis=-1,keepdims=True)


def mse(prediction,target):
    residual=prediction-target
    return float(np.mean(residual**2)),2*residual/residual.size


def bce(logits,target):
    return float(np.mean(np.logaddexp(0,logits)-target*logits)),(sigmoid(logits)-target)/target.size


def weight(rng,n,m):
    return rng.normal(0,np.sqrt(2/(n+m)),(n,m))


def copy_parameters(parameters):
    if sum(v.size for v in parameters.values())>20000:raise ValueError('parameter budget exceeded')
    return {key:np.array(value,dtype=float,copy=True) for key,value in parameters.items()}


def step(parameters,gradients,learning_rate,clip):
    # One global norm across owned gradient blocks, computed with uniform scaling.
    largest=max((float(np.max(abs(g))) for g in gradients.values()),default=0.)
    norm=largest*np.sqrt(sum(float(np.sum((g/largest)**2)) for g in gradients.values())) if largest else 0.
    factor=min(1.,clip/norm) if norm else 1.
    result={}
    for key,value in parameters.items():
        if key in gradients and gradients[key].shape!=value.shape:raise ValueError('gradient shape mismatch')
        result[key]=value-learning_rate*factor*gradients[key] if key in gradients else value.copy()
        if not np.isfinite(result[key]).all():raise ValueError('nonfinite parameter update')
    if set(gradients)-set(parameters):raise ValueError('unknown parameter gradient')
    return result,norm


def options(epochs,learning_rate,batch_size,random_state,gradient_clip):
    integer(epochs,'epochs',1,2000);scalar(learning_rate,'learning_rate',1e-6,1.)
    integer(batch_size,'batch_size',1,128);integer(random_state,'random_state',0,2**32-1)
    scalar(gradient_clip,'gradient_clip',1e-6,1000)


def train(parameters,X,y,loss_gradient,*,epochs,learning_rate,batch_size,rng,gradient_clip,shuffle=True):
    if epochs*((len(X)+batch_size-1)//batch_size)>10000:raise ValueError('at most10000 minibatch updates')
    parameters=copy_parameters(parameters);history=[];largest=0.;updates=0
    for _ in range(epochs):
        order=rng.permutation(len(X)) if shuffle else np.arange(len(X))
        accumulated=0.
        for start in range(0,len(X),batch_size):
            indices=order[start:start+batch_size]
            loss,gradient=loss_gradient(parameters,X[indices],None if y is None else y[indices],rng)
            if not np.isfinite(loss) or any(not np.isfinite(g).all() for g in gradient.values()):raise ValueError('nonfinite loss/gradient')
            parameters,norm=step(parameters,gradient,learning_rate,gradient_clip)
            largest=max(largest,norm);updates+=1;accumulated+=loss*len(indices)
        history.append(accumulated/len(X))
    return parameters,dict(loss_history_=np.array(history),n_iter_=epochs,n_updates_=updates,
        max_gradient_norm_=largest,optimization_status_='fixed-budget-completed',converged_=False)


class Settings:
    def __init__(self,hidden_dim=4,epochs=100,learning_rate=.1,batch_size=16,random_state=0,gradient_clip=5.):
        self.hidden_dim,self.epochs,self.learning_rate=hidden_dim,epochs,learning_rate
        self.batch_size,self.random_state,self.gradient_clip=batch_size,random_state,gradient_clip
        self._settings()

    def _settings(self):
        integer(self.hidden_dim,'hidden_dim',1,16)
        options(self.epochs,self.learning_rate,self.batch_size,self.random_state,self.gradient_clip)

    def _train(self,params,X,y,loss,rng,**extra):
        return train(params,X,y,loss,epochs=self.epochs,learning_rate=self.learning_rate,
                     batch_size=self.batch_size,rng=rng,gradient_clip=self.gradient_clip,**extra)

    def _query(self,X,validator=tabular):
        if not hasattr(self,'parameters_'):raise ValueError('fit must succeed before inference')
        return validator(X,shape=self.input_shape_)


def normalize(X):
    mean=X[0]+np.mean(X-X[0],axis=0);A=X-mean
    scale=float(np.max(abs(A))) or 1.
    return A/scale,mean,scale


@lru_cache(None)
def module_at(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=sys.modules.get(name)
    if module is None:
        module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    return module


@lru_cache(None)
def load(name):
    if name not in TOPICS:raise ValueError('unknown B7 canonical')
    return module_at('atlas_b7_'+name.replace('-','_'),ROOT/name/'python/solution.py')


def main(estimator,kind):
    try:
        data=json.load(sys.stdin)
        if not isinstance(data,dict) or 'X' not in data or set(data)-{'X','y','parameters','adjacency','n_samples'}:raise ValueError('JSON requires X and supported optional fields')
        params=data.get('parameters',{})
        if not isinstance(params,dict):raise ValueError('parameters must be object')
        model=estimator(**params)
        if kind=='gnn':model.fit(data['X'],data.get('y'),data.get('adjacency'))
        elif kind in ('classifier','regression','sequence','cnn'):model.fit(data['X'],data.get('y'))
        else:model.fit(data['X'])
        output=dict(loss_initial=float(model.loss_history_[0]),loss_final=float(model.loss_history_[-1]),optimization_status=model.optimization_status_)
        if kind=='gnn':output['prediction']=model.predict(data['X'],data['adjacency']).tolist()
        elif kind in ('classifier','regression','sequence','cnn'):output['prediction']=model.predict(data['X']).tolist()
        elif kind in ('ae','vae'):
            output.update(embedding=model.transform(data['X']).tolist(),reconstruction=model.reconstruct(data['X']).tolist())
            if kind=='vae':output['sample']=model.sample(data.get('n_samples',3),random_state=0).tolist()
        else:output['sample']=model.sample(data.get('n_samples',3),random_state=0).tolist()
        print(json.dumps(output,allow_nan=False))
    except (ValueError,TypeError) as error:
        print('error: '+str(error),file=sys.stderr);raise SystemExit(2)
