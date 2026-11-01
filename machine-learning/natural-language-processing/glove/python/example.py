"""Positive global cooccurrences and genuine trained GloVe vectors on a toy corpus."""
import json
import numpy as np
from solution import GloVe


def main():
    texts = ['red fox runs','red fox jumps','blue bird flies','blue bird sings']
    model = GloVe(4, epochs=80, random_state=21).fit(texts)
    red, fox, blue = (model.vocabulary_[w] for w in ('red','fox','blue'))
    print(json.dumps(dict(texts=texts, configuration=dict(dimension=4, window=2,
        symmetric=True, x_max=10., alpha=.75, epochs=80, random_state=21),
        vocabulary=model.vocab_.tokens_, red_fox_count=model.cooccurrences_[red,fox],
        red_blue_count=model.cooccurrences_[red,blue],
        loss_initial=round(float(model.loss_history_[0]),6),
        loss_final=round(float(model.loss_history_[-1]),6), status=model.optimization_status_,
        red_embedding=np.round(model.embedding('red'),4).tolist(),
        fox_embedding=np.round(model.embedding('fox'),4).tolist(),
        unknown_embedding=model.embedding('unseen').tolist())))


if __name__ == '__main__':
    main()
