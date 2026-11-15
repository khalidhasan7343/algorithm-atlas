"""Encode explicit-graph problems in the shared C1 command-line token grammar."""


def encode(kind, n, start, edges, *, limit=0, max_depth=None, goals=(), goal=0, directed=True):
    tokens = [n, len(edges), start]
    if kind == "dls":
        tokens.append(limit)
    elif kind == "iddfs":
        tokens.append(-1 if max_depth is None else max_depth)
    if kind == "bidirectional":
        tokens += [goal, int(directed)]
    else:
        tokens += [len(goals), *sorted(goals)]
    for edge in edges:
        tokens += list(edge)
    return " ".join(str(t) for t in tokens)
