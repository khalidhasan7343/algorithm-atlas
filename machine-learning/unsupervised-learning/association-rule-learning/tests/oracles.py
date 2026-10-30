"""Test-only direct powerset/count oracles; independent of all core mining helpers."""
from fractions import Fraction
from itertools import combinations


def brute_itemsets(data, minimum):
    rows = [set(row) for row in data]
    universe = sorted(set().union(*rows)) if rows else []
    assert len(universe) <= 8, 'test oracle deliberately bounded'
    result = {}
    for size in range(1, len(universe)+1):
        for values in combinations(universe, size):
            count = sum(all(value in row for value in values) for row in rows)
            if rows and Fraction(count,len(rows)) >= Fraction(str(minimum)):
                result[frozenset(values)] = count
    return result


def sparse_reference(data, minimum):
    from sklearn.preprocessing import MultiLabelBinarizer
    import numpy as np
    if not data:
        return {}
    encoder = MultiLabelBinarizer(sparse_output=True)
    incidence = encoder.fit_transform(data).tocsr()
    universe = encoder.classes_.tolist()
    result = {}
    for size in range(1,len(universe)+1):
        for columns in combinations(range(len(universe)),size):
            row_sums = np.asarray(incidence[:,columns].sum(axis=1)).ravel()
            count = int(np.count_nonzero(row_sums==size))
            if Fraction(count,len(data))>=Fraction(str(minimum)):
                result[frozenset(universe[j] for j in columns)] = count
    return result


def brute_rules(data, minimum_support, minimum_confidence):
    counts = brute_itemsets(data,minimum_support)
    result = {}
    for union,count in counts.items():
        values = sorted(union)
        for size in range(1,len(values)):
            for left in combinations(values,size):
                A = frozenset(left); B = union-A
                a = sum(A <= set(row) for row in data)
                b = sum(B <= set(row) for row in data)
                if Fraction(count,a)>=Fraction(str(minimum_confidence)):
                    result[A,B]=(count,Fraction(count,len(data)),Fraction(count,a),Fraction(count*len(data),a*b))
    return result
