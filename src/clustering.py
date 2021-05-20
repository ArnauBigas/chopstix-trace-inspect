import os
from sklearn.cluster import DBSCAN
from sklearn import metrics
import numpy as np
import math
import random
import json

from src.distance import disjoint_sets

class ClusteringInformation:

    def __init__(self, epsilon, clusters, noise_invocations):
        self._epsilon = epsilon
        self._clusters = clusters
        self._noise_invocations = noise_invocations

    def get_epsilon(self):
        return self._epsilon

    def get_invocation_count(self):
        count = len(self._noise_invocations)

        for cluster in self._clusters:
            count += len(cluster)

        return count

    def get_cluster_count(self):
        return len(self._clusters)

    def get_all_invocations(self, cluster):
        return self._clusters[cluster]

    def get_random_invocation(self, cluster):
        return random.choice(self._clusters[cluster])

    def get_noise_invocation_count(self):
        return len(self._noise_invocations)

    def get_noise_invocations(self):
        return self._noise_invocations

    def get_cluster_id_for_invocation(self, invocation_id):
        if invocation_id in self._noise_invocations:
            return -1
        else:
            for cluster_id in range(len(self._clusters)):
                if invocation_id in self._clusters[cluster_id]:
                    return cluster_id
        return None

    def to_file(self, path):
        json_obj = {
            "epsilon": self._epsilon,
            "clusters": self._clusters,
            "noise_invocations": self._noise_invocations
        }

        with open(path, "w") as file:
            json.dump(json_obj, file)

    @staticmethod
    def from_file(path):
        with open(path, "r") as file:
            json_obj = json.load(file)

        return ClusteringInformation(json_obj['epsilon'], json_obj['clusters'], json_obj['noise_invocations'])


def estimate_dbscan_epsilon(trace, coverage):
    n = trace.get_invocation_count()

    print("Finding eps parameter based on coverage of %f..." % coverage)
    distance_matrix = trace.get_distance_matrix(disjoint_sets)
    distances = []
    for i in range(n):
        distances.append(min([distance_matrix[i, j] for j in range(n) if j != i]))

    pointLimit = math.ceil((n - 1) * coverage)
    distances = np.sort(distances)
    uniquedist = np.unique(distances)
    distanceLimit = distances[pointLimit]
    nextDist = uniquedist[1 + np.where(uniquedist == distanceLimit)[0]]

    return (distanceLimit + nextDist)/2

def dbscan(trace, epsilon):
    distance_matrix = trace.get_distance_matrix(disjoint_sets)

    print("Clustering using parameters: eps = %f;" % epsilon)
    db = DBSCAN(metric="precomputed", eps=epsilon).fit(distance_matrix)
    core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
    core_samples_mask[db.core_sample_indices_] = True
    labels = db.labels_

    # Number of clusters in labels, ignoring noise if present.
    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise_ = list(labels).count(-1)

    print('Estimated number of clusters: %d' % n_clusters_)
    print('Estimated number of noise points: %d (%f%%)' % (n_noise_, n_noise_*100/trace.get_invocation_set_count()))
    if n_clusters_ > 1:
        silhouette_score = metrics.silhouette_score(distance_matrix, labels,
                                                    metric="precomputed")
        print("Silhouette Coefficient: %0.3f" % silhouette_score)

    clusters = [[] for i in range(n_clusters_)]
    noise_invocations = []
    for i in range(len(labels)):
        label = labels[i]

        if label == -1:
            noise_invocations.extend(trace.invocation_sets[i].invocations)
        else:
            clusters[label].extend(trace.invocation_sets[i].invocations)

    return ClusteringInformation(epsilon, clusters, noise_invocations)
