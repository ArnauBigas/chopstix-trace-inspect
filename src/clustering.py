import os
from sklearn.cluster import DBSCAN
from sklearn import metrics
import numpy as np
import math

from src.distance import disjoint_sets

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
    print('Estimated number of noise points: %d (%f%%)' % (n_noise_, n_noise_*100/trace.get_invocation_count()))
    if n_clusters_ > 1:
        silhouette_score = metrics.silhouette_score(distance_matrix, labels,
                                                    metric="precomputed")
        print("Silhouette Coefficient: %0.3f" % silhouette_score)

    return labels
