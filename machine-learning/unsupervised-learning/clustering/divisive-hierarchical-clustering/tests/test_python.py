import numpy as np
from numpy.testing import assert_allclose, assert_array_equal
import pytest

pytestmark = pytest.mark.ml


@pytest.mark.oracle
@pytest.mark.numerical
def test_hand_calculated_splinter_seed_moves_and_cut(clustering_support):
    model = clustering_support.load('divisive-hierarchical-clustering').DivisiveClustering(2).fit([[0], [2], [10], [12]])
    assert_array_equal(model.labels_, [0, 0, 1, 1])
    first = model.splits_[0]
    assert first['splinter_seed'] == 0
    assert first['moves'][0][0] == 1
    assert_allclose(first['moves'][0][1], 7)
    assert {first['left'], first['right']} == {(0, 1), (2, 3)}
    assert_allclose(model.distances_, [2, 2, 12])


@pytest.mark.oracle
@pytest.mark.parametrize('seed', [16021, 16022, 16023])
def test_every_splinter_choice_against_independent_dissimilarity_sums(clustering_support, seed):
    rng = np.random.default_rng(seed)
    X = rng.normal(size=(8, 2))
    model = clustering_support.load('divisive-hierarchical-clustering').DivisiveClustering(3).fit(X)
    distance = {(i, j): float(np.sqrt(sum((X[i]-X[j])**2))) for i in range(8) for j in range(8)}
    active = [tuple(range(8))]
    for split in model.splits_:
        parent = split['parent']
        eligible = [g for g in active if len(g) > 1]
        maximum = max(max(distance[i,j] for i in g for j in g) for g in eligible)
        assert_allclose(split['diameter'], maximum)
        expected_seed = max(parent, key=lambda i: (sum(distance[i,j] for j in parent)/(len(parent)-1), -i))
        assert split['splinter_seed'] == expected_seed
        splinter = [expected_seed]
        rest = [i for i in parent if i != expected_seed]
        for chosen, gain in split['moves']:
            gains = {i: sum(distance[i,j] for j in rest if j != i)/(len(rest)-1)-sum(distance[i,j] for j in splinter)/len(splinter) for i in rest}
            assert chosen == max(gains, key=lambda i: (gains[i], -i))
            assert_allclose(gain, gains[chosen], atol=1e-13)
            rest.remove(chosen);splinter.append(chosen)
        assert set(rest) == set(split['left']) and set(splinter) == set(split['right'])
        active.remove(parent);active.extend((split['left'], split['right']))
    assert sorted(active) == [(i,) for i in range(8)]
    assert model.children_.shape == (7, 2)
    assert model.counts_[-1] == 8


@pytest.mark.numerical
def test_duplicates_singleton_and_uniform_scaling(clustering_support):
    cls = clustering_support.load('divisive-hierarchical-clustering').DivisiveClustering
    one = cls(1).fit([[1]])
    assert one.children_.shape == (0, 2) and one.labels_.tolist() == [0]
    duplicate = cls(3).fit([[.1], [.1], [.1]])
    assert_array_equal(duplicate.labels_, [0, 1, 2])
    X = np.array([[0.], [2.], [10.], [12.]])
    a = cls(2).fit(X);b = cls(2).fit(X*1e-200)
    assert_array_equal(a.labels_, b.labels_)
    assert_allclose(b.distances_/1e-200, a.distances_, atol=1e-12)


@pytest.mark.parametrize('value', [0, -1, True, 129])
def test_bad_cluster_count(clustering_support, value):
    with pytest.raises(ValueError):
        clustering_support.load('divisive-hierarchical-clustering').DivisiveClustering(value)
