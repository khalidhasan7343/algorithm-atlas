"""Two weakly linked communities, two labeled training nodes and four unknowns."""
import json
import numpy as np
from solution import GCNClassifier


def main():
    A=np.zeros((6,6))
    for i,j,w in [(0,1,1),(0,2,1),(1,2,1),(2,3,.1),(3,4,1),(3,5,1),(4,5,1)]:A[i,j]=A[j,i]=w
    X=np.array([[1.,0],[1,.2],[.8,.1],[0,1],[.1,.8],[.2,1]])
    model=GCNClassifier(epochs=200,learning_rate=.2,random_state=21).fit(A,X,[0,-1,-1,1,-1,-1])
    print(json.dumps(dict(normalized_adjacency=model.normalized_adjacency_.round(6).tolist(),
        first_propagated_feature=(model.normalized_adjacency_@X)[0].round(6).tolist(),
        loss_initial=round(float(model.loss_history_[0]),8),loss_final=round(float(model.loss_history_[-1]),8),
        predictions=model.predict(A,X).tolist(),updates=model.n_updates_),sort_keys=True))


if __name__ == '__main__':
    main()
