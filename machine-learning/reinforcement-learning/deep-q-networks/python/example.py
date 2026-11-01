"""Analytical zero-network worked example; no training side effects on import."""
import json
import numpy as np
from solution import DQN,loss_gradients

def main():
    model=DQN(hidden=2);model.online={k:np.zeros_like(v) for k,v in model.online.items()};loss,g=loss_gradients(model.online,[[1.]],np.array([1]),[1.])
    print(json.dumps(dict(loss=loss,bias_gradient=g["b2"].tolist())))

if __name__=="__main__":main()
