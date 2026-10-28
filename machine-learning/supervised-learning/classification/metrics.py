"""Unweighted classification metrics with explicit class order and zero handling."""
import importlib.util
from pathlib import Path
import sys

import numpy as np

if "atlas_classification_support" not in sys.modules:
    _spec=importlib.util.spec_from_file_location("atlas_classification_support",Path(__file__).with_name("support.py"))
    _module=importlib.util.module_from_spec(_spec);sys.modules[_spec.name]=_module;_spec.loader.exec_module(_module)
support=sys.modules["atlas_classification_support"]


def _ordered_classes(classes):
    original,ordered,_=support.encode_labels(classes)
    if len(original)!=len(ordered) or not np.array_equal(original,ordered):
        raise ValueError("explicit classes must be unique and sorted, matching probability columns")
    return ordered


def _indices(y,classes,n=None):
    original,_,_=support.encode_labels(y,n=n)
    if original.dtype.kind!=classes.dtype.kind:
        raise ValueError("labels and classes must use the same supported family")
    mapping={value:i for i,value in enumerate(classes.tolist())}
    try:return np.array([mapping[value] for value in original.tolist()],dtype=int)
    except KeyError as error:raise ValueError("observed label absent from explicit classes") from error


def classification_report(y_true,y_pred,*,classes=None,positive_label=None):
    """Rows=true/columns=predicted; zero divisions=0; binary positive=class[1].

    Macro averages include every explicit class, including zero-support classes.
    Weighted averages use true support. No sample weighting is implemented.
    """
    truth,_,_=support.encode_labels(y_true)
    prediction,_,_=support.encode_labels(y_pred,n=len(truth))
    if classes is None:
        _,classes,_=support.encode_labels(truth.tolist()+prediction.tolist())
    else:classes=_ordered_classes(classes)
    actual=_indices(truth,classes);predicted=_indices(prediction,classes,n=len(truth))
    confusion=np.zeros((len(classes),len(classes)),dtype=np.int64)
    np.add.at(confusion,(actual,predicted),1)
    true_support=confusion.sum(axis=1);predicted_support=confusion.sum(axis=0);correct=np.diag(confusion)
    precision=np.divide(correct,predicted_support,out=np.zeros(len(classes)),where=predicted_support!=0)
    recall=np.divide(correct,true_support,out=np.zeros(len(classes)),where=true_support!=0)
    f1=np.divide(2*precision*recall,precision+recall,out=np.zeros(len(classes)),where=(precision+recall)!=0)
    vectors=dict(precision=precision,recall=recall,f1=f1)
    binary=None
    if len(classes)==2:
        positive=classes[1].item() if positive_label is None else positive_label
        index=int(_indices([positive],classes)[0])
        positive=classes[index].item()
        binary=dict(positive_label=positive,**{name:float(v[index]) for name,v in vectors.items()})
    elif positive_label is not None:raise ValueError("positive_label applies only to binary reports")
    return dict(classes=classes.tolist(),confusion_matrix=confusion.tolist(),accuracy=float(correct.sum()/len(truth)),
                per_class=[dict(label=label,support=int(true_support[i]),**{name:float(v[i]) for name,v in vectors.items()}) for i,label in enumerate(classes.tolist())],
                macro={name:float(v.mean()) for name,v in vectors.items()},
                weighted={name:float(v @ true_support/len(truth)) for name,v in vectors.items()},binary=binary,
                zero_division=0,confusion_orientation="rows=true, columns=predicted",sample_weighting="unsupported")


def log_loss(y_true,probabilities,classes):
    """Mean -log(probability of true class), clipped below at 1e-15."""
    classes=_ordered_classes(classes)
    a=np.asarray(probabilities)
    if a.ndim!=2 or a.shape[1]!=len(classes) or a.dtype.kind not in "iuf" or a.size>support.MAX_CELLS:
        raise ValueError("numeric probability matrix (n,len(classes)) within cell budget required")
    a=np.array(a,dtype=float,copy=True)
    if not np.isfinite(a).all() or np.any((a<0)|(a>1)) or not np.allclose(a.sum(axis=1),1,atol=1e-10,rtol=1e-10):
        raise ValueError("finite probability rows in [0,1] summing to one required")
    indices=_indices(y_true,classes,n=len(a))
    return float(-np.log(np.clip(a[np.arange(len(a)),indices],1e-15,1)).mean())
