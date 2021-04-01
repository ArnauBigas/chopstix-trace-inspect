#!/bin/python3

import argparse
import sys
import random

from src.trace import Trace
from src.clustering import dbscan, estimate_dbscan_epsilon

parser = argparse.ArgumentParser(description="Inspect ChopStix traces")
parser.add_argument('trace_files', nargs='+', help='Traces to cluster.')
parser.add_argument('--num-threads', '-n', type=int, help='Number of threads to use during the clustering')
parser.add_argument('--epsilon', '-e', type=float, help='Epsilon parameter to pass to the DBSCAN clusterer')
parser.add_argument('--coverage', '-c', type=float, default=0.9, help='Unused.')
parser.add_argument('--summary', '-s', action='store_true', help='Print summary instead of cluster indices')
parser.add_argument('--random', '-r', action='store_true', help='Choose random invocation from invocation set')
parser.add_argument('--max-memory', type=int, help="Don't use more than this amount of memory during clustering")
args = parser.parse_args()

for trace_file in args.trace_files:
    print("Analyzing trace %s" % trace_file)

    trace = Trace(trace_file, args.num_threads)

    if args.max_memory != None:
        needed = trace.estimate_needed_memory() / (1024**2)
        if needed > args.max_memory:
            print("Need more memory than allowed to process trace: %d out of %d" % (needed, args.max_memory))
            continue

    print("Clustering %d invocations (%d sets)" % (trace.get_invocation_count(), trace.get_invocation_set_count()))

    epsilon = args.epsilon
    if epsilon == None:
        epsilon = estimate_dbscan_epsilon(trace, args.coverage)

    labels = dbscan(trace, epsilon)

    clusters = {}
    for i in range(len(labels)):
        label = labels[i]

        if label not in clusters:
            clusters[label] = []

        if args.random:
            clusters[label].append(random.choice(trace.invocation_sets[i].invocations))
        else:
            clusters[label].extend(trace.invocation_sets[i].invocations)

    if not args.summary:
        for cluster in clusters:
            print("Cluster %d" % cluster)
            print("----------")
            print(clusters[cluster])
