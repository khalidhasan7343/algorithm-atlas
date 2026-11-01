"""Analytical zero-network worked example; no training side effects on import."""
import json
import numpy as np
from solution import REINFORCE,loss_gradients

def main():
    model=REINFORCE(hidden=2);model.actor={k:np.zeros_like(v) for k,v in model.actor.items()};loss,g=loss_gradients(model.actor,[[1.]],np.array([1]),[1.])
    print(json.dumps(dict(loss=loss,bias_gradient=g["b2"].tolist())))

if __name__=="__main__":main()
