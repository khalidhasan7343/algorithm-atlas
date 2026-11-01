"""Run from repository root: python machine-learning/graph-learning/pagerank/python/example.py."""
import json
from solution import PageRank


def main():
    graph = [[0, 1, 1], [0, 0, 1], [0, 0, 0]]
    model = PageRank().fit(graph)
    print(json.dumps(dict(adjacency=graph, damping=.85,
                          transition=model.transition_matrix_.round(8).tolist(),
                          scores=model.scores_.round(8).tolist(),
                          sum=round(float(model.scores_.sum()), 8), converged=model.converged_), sort_keys=True))


if __name__ == '__main__':
    main()
