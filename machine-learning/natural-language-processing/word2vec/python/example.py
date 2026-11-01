"""A trained toy SGNS model; printed coordinates do not establish semantic quality."""
import json
import numpy as np
from solution import Word2Vec


def main():
    texts = ['red fox runs','red fox jumps','blue bird flies','blue bird sings']
    model = Word2Vec(4, epochs=80, negative_samples=3, random_state=21).fit(texts)
    print(json.dumps(dict(texts=texts, configuration=dict(dimension=4, window=2,
        negative_samples=3, epochs=80, random_state=21), vocabulary=model.vocab_.tokens_,
        pairs=len(model.pairs_), loss_initial=round(float(model.loss_history_[0]),6),
        loss_final=round(float(model.loss_history_[-1]),6), status=model.optimization_status_,
        red_embedding=np.round(model.embedding('red'),4).tolist(),
        fox_embedding=np.round(model.embedding('fox'),4).tolist(),
        unknown_embedding=model.embedding('unseen').tolist())))


if __name__ == '__main__':
    main()
