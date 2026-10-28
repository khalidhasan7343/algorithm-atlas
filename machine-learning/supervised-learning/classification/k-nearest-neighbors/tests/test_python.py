import numpy as np
from numpy.testing import assert_allclose, assert_array_equal
import pytest
from sklearn.neighbors import KNeighborsClassifier as Reference

pytestmark = pytest.mark.ml


@pytest.mark.numerical
def test_known_votes_distance_ties_duplicates_and_k_bounds(algorithm):
    X = [[-1], [1], [1], [3]]; y = ["z", "a", "b", "a"]
    model = algorithm.KNearestNeighbors(1).fit(X, y)
    assert model.predict([[0]])[0] == "z"  # equal distance selects original row 0
    model = algorithm.KNearestNeighbors(2).fit(X, y)
    assert model.predict([[1]])[0] == "a"  # tied class votes choose sorted label
    assert_allclose(model.predict_proba([[1]]), [[.5, .5, 0]])
    model = algorithm.KNearestNeighbors(4).fit(X, y)
    assert_allclose(model.predict_proba([[100]]), [[.5, .25, .25]])
    with pytest.raises(ValueError): algorithm.KNearestNeighbors(5).fit(X, y)


@pytest.mark.numerical
@pytest.mark.parametrize("k", [1, 5, 17])
def test_seeded_exhaustive_distance_and_vote_oracle(algorithm, k):
    rng = np.random.default_rng(14021)
    for _ in range(8):
        X = rng.integers(-3, 4, size=(17, 3)).astype(float); y = rng.integers(-2, 2, size=17)
        query = rng.normal(size=(9, 3)); model = algorithm.KNearestNeighbors(k).fit(X, y)
        distances, indices = model.kneighbors(query)
        expected=[]
        for i, q in enumerate(query):
            # Python scalar distances/sort independent of vectorized retrieval.
            order=sorted(range(len(X)), key=lambda j: (sum((float(q[c])-float(X[j,c]))**2 for c in range(3)), j))[:k]
            assert_array_equal(indices[i], order)
            assert_allclose(distances[i], [sum((q-X[j])**2)**.5 for j in order], atol=1e-12)
            counts={label:sum(y[j]==label for j in order) for label in sorted(set(y))}
            expected.append(max(counts, key=lambda label: (counts[label], -label)))
        assert_array_equal(model.predict(query), expected)


@pytest.mark.reference
@pytest.mark.parametrize("k", [1, 3, 12])
def test_reference_without_boundary_distance_ties(algorithm, k):
    rng=np.random.default_rng(14022); X=rng.normal(size=(12, 4)); y=np.array(["a", "b", "c"]*4); query=rng.normal(size=(11,4))
    model=algorithm.KNearestNeighbors(k).fit(X,y); reference=Reference(k, algorithm="brute").fit(X,y)
    assert_array_equal(model.predict(query),reference.predict(query))
    assert_allclose(model.predict_proba(query),reference.predict_proba(query),atol=1e-14)


@pytest.mark.numerical
def test_large_offsets_and_scaling_changes_neighbor_geometry(algorithm):
    X=9e11+np.array([[-2.], [0], [2]])
    assert algorithm.KNearestNeighbors(1).fit(X,[0,1,2]).predict([[9e11+.25]])[0]==1
    X=np.array([[0.,100], [10,0]]); q=np.array([[1.,0]])
    assert algorithm.KNearestNeighbors(1).fit(X,[0,1]).predict(q)[0]==1
    assert algorithm.KNearestNeighbors(1).fit(X/[1,1000],[0,1]).predict(q/[1,1000])[0]==0


def test_owned_training_state_failed_refit_and_prediction_contract(algorithm):
    X=np.array([[0.], [1]]); y=np.array(["a","b"]); model=algorithm.KNearestNeighbors(1)
    with pytest.raises(ValueError): model.predict(X)
    assert model.fit(X,y) is model
    X[:]=9; y[:]='z'
    assert_array_equal(model.predict([[0],[1]]),['a','b'])
    with pytest.raises(ValueError): model.fit([[0],[1]], [True,False])
    assert_array_equal(model.predict([[0],[1]]),['a','b'])
    assert model.predict_proba(np.empty((0,1))).shape==(0,2)
    with pytest.raises(ValueError): model.predict([[1,2]])
    with pytest.raises(ValueError): model.predict([[np.nan]])


@pytest.mark.parametrize("k", [0,-1,2.0,True,2049])
def test_invalid_k(algorithm,k):
    with pytest.raises(ValueError): algorithm.KNearestNeighbors(k)
