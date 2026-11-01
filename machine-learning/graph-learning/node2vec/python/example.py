"""Small deterministic Node2Vec learning example; no universal geometry claim."""
import json
import numpy as np
from solution import Node2Vec


def main():
    A = np.zeros((6, 6))
    for i,j,w in [(0,1,1),(0,2,1),(1,2,1),(2,3,.2),(3,4,1),(3,5,1),(4,5,1)]:
        A[i,j] = A[j,i] = w
    model = Node2Vec(p=.5,q=2.,epochs=100,random_state=21).fit(A)
    E = model.transform()
    norms = np.linalg.norm(E,axis=1)
    similarity = E @ E.T / (norms[:,None] * norms[None,:])
    print(json.dumps(dict(walks=model.walks_[:2],pairs=model.positive_pairs_[:6].tolist(),
        shape=list(E.shape),loss_initial=round(float(model.loss_history_[0]),8),
        loss_final=round(float(model.loss_history_[-1]),8),
        cosine_0_1=round(float(similarity[0,1]),8),cosine_0_4=round(float(similarity[0,4]),8),
        updates=model.n_updates_),sort_keys=True))


if __name__ == '__main__':
    main()
