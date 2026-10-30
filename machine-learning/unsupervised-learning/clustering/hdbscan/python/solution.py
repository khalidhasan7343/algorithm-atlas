import importlib.util
from pathlib import Path
import sys

import numpy as np

if 'atlas_clustering_support' not in sys.modules:
    _spec = importlib.util.spec_from_file_location('atlas_clustering_support', Path(__file__).resolve().parents[2]/'support.py')
    _module = importlib.util.module_from_spec(_spec)
    sys.modules[_spec.name] = _module
    _spec.loader.exec_module(_module)
s = sys.modules['atlas_clustering_support']


class HDBSCAN(s.Clusterer):
    """Exact dense HDBSCAN*: mutual reachability, condensation and EOM.

    Euclidean alpha=1; root excluded; self-inclusive min_samples convention.
    Condensed lambda is scaled by max pairwise distance, a global positive factor
    that preserves EOM comparisons and membership ratios while protecting tiny X.
    """
    def __init__(self, *, min_cluster_size=5, min_samples=None):
        self.min_cluster_size = s.integer(min_cluster_size, 'min_cluster_size', 2, 256)
        self.min_samples = min_samples

    @s.numerical
    def fit(self, X):
        X = s.features(X, fitting=True, max_samples=256)
        minimum = s.integer(self.min_cluster_size, 'min_cluster_size', 2, len(X))
        support = minimum if self.min_samples is None else s.integer(self.min_samples, 'min_samples', 1, len(X))
        n = len(X)
        D = s.pairwise(X)
        core = np.sort(D, axis=1)[:, support-1]
        reachability = np.maximum(np.maximum(D, core[:, None]), core[None, :])
        distance_scale = float(D.max()) or 1.0

        # Dense Prim: float mutual-reachability weights do not satisfy the
        # existing integer-weight DSA Prim contract, so this is local machinery.
        visited = np.zeros(n, dtype=bool)
        best = np.full(n, np.inf)
        parent = np.full(n, -1, dtype=int)
        best[0] = 0
        edges = []
        for _ in range(n):
            vertex = int(np.argmin(np.where(visited, np.inf, best)))
            visited[vertex] = True
            if parent[vertex] >= 0:
                left, right = sorted((int(parent[vertex]), vertex))
                edges.append((left, right, float(best[vertex])))
            for other in np.flatnonzero(~visited):
                weight = reachability[vertex, other]
                if weight < best[other] or (weight == best[other] and vertex < parent[other]):
                    best[other] = weight
                    parent[other] = vertex

        # Convert sorted MST edges into a complete single-linkage hierarchy.
        roots = list(range(n))
        node_of_root = list(range(n))
        members = {i: (i,) for i in range(n)}
        children, heights, sizes = [], [], []
        def find(vertex):
            while roots[vertex] != vertex:
                roots[vertex] = roots[roots[vertex]]
                vertex = roots[vertex]
            return vertex
        for left, right, weight in sorted(edges, key=lambda e: (e[2], e[0], e[1])):
            A, B = find(left), find(right)
            assert A != B
            node_left, node_right = sorted((node_of_root[A], node_of_root[B]))
            node = n+len(children)
            children.append((node_left, node_right))
            heights.append(weight)
            members[node] = members[node_left]+members[node_right]
            sizes.append(len(members[node]))
            roots[B] = A
            node_of_root[A] = node

        def density(height):
            if height == 0:
                return np.inf
            value = distance_scale/height
            if not np.isfinite(value) or value > 1e300:
                raise ValueError('unresolved relative density dynamic range')
            return value

        root_cluster = n
        births = {root_cluster: 0.0}
        cluster_members = {root_cluster: tuple(range(n))}
        cluster_children = {root_cluster: []}
        exits = {root_cluster: {}}
        condensed = []

        def lose_points(cluster, points, level):
            for point in points:
                exits[cluster][point] = level
                condensed.append((cluster, point, level, 1))

        def condense(node, cluster):
            left, right = children[node-n]
            level = density(heights[node-n])
            A, B = members[left], members[right]
            largeA, largeB = len(A) >= minimum, len(B) >= minimum
            if largeA and largeB:
                for child, points in ((left, A), (right, B)):
                    # These observations leave the current cluster together.
                    exits[cluster].update((point, level) for point in points)
                    child_cluster = n+len(births)
                    births[child_cluster] = level
                    cluster_members[child_cluster] = points
                    cluster_children[child_cluster] = []
                    exits[child_cluster] = {}
                    cluster_children[cluster].append(child_cluster)
                    condensed.append((cluster, child_cluster, level, len(points)))
                    condense(child, child_cluster)
            elif largeA:
                lose_points(cluster, B, level)
                condense(left, cluster)
            elif largeB:
                lose_points(cluster, A, level)
                condense(right, cluster)
            else:
                lose_points(cluster, A+B, level)

        condense(2*n-2, root_cluster)
        stability = {}
        for cluster, birth in births.items():
            total = 0.0
            assert set(exits[cluster]) == set(cluster_members[cluster])
            for departure in exits[cluster].values():
                # Equal infinity endpoints are a zero-duration tie event;
                # finite birth -> infinite departure has infinite persistence.
                interval = 0.0 if departure == birth else departure-birth
                total += max(0.0, interval)
            stability[cluster] = total

        def choose(cluster):
            selected = []
            descendant_score = 0.0
            for child in cluster_children[cluster]:
                score, child_selection = choose(child)
                descendant_score += score
                selected.extend(child_selection)
            if cluster != root_cluster and stability[cluster] >= descendant_score:
                return stability[cluster], [cluster]
            return descendant_score, selected

        _, selected = choose(root_cluster)
        selected.sort(key=lambda cluster: min(cluster_members[cluster]))
        labels = np.full(n, -1, dtype=np.int64)
        probabilities = np.zeros(n)
        for label, cluster in enumerate(selected):
            maximum = max(exits[cluster].values())
            for point, departure in exits[cluster].items():
                assert labels[point] == -1
                labels[point] = label
                if np.isinf(maximum):
                    probabilities[point] = 1.0 if np.isinf(departure) else 0.0
                elif maximum > 0:
                    probabilities[point] = min(departure, maximum)/maximum
                else:
                    probabilities[point] = 1.0
        dtype = [('parent', 'i8'), ('child', 'i8'), ('lambda_val', 'f8'), ('child_size', 'i8')]
        self.__dict__.update(n_features_in_=X.shape[1], labels_=labels, probabilities_=probabilities,
                             core_distances_=core.copy(), mutual_reachability_=reachability.copy(),
                             minimum_spanning_tree_=np.array(edges).reshape(-1, 3),
                             single_linkage_tree_=np.column_stack((children, heights, sizes)),
                             condensed_tree_=np.array(condensed, dtype=dtype),
                             cluster_stabilities_=dict(stability), cluster_births_=dict(births),
                             cluster_members_=dict(cluster_members), cluster_exit_lambdas_=exits,
                             cluster_children_=cluster_children, selected_clusters_=tuple(selected),
                             n_clusters_=len(selected), min_samples_=support,
                             distance_scale_=distance_scale)
        return self


if __name__ == '__main__':
    s.main(HDBSCAN)
