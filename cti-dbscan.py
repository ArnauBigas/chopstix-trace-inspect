#!/bin/python3

import argparse
import sys

from src.trace import Trace
from src.clustering import dbscan, estimate_dbscan_epsilon

parser = argparse.ArgumentParser(description="Inspect ChopStix traces")
parser.add_argument('trace_files', nargs='+')
parser.add_argument('--num-threads', '-n', type=int)
parser.add_argument('--epsilon', '-e', type=float)
parser.add_argument('--coverage', '-c', type=float, default=0.9)
parser.add_argument('--summary', '-s', action='store_true')
parser.add_argument('--max-memory', type=int)
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

        clusters[label].extend(trace.invocation_sets[i].invocations)

    if not args.summary:
        for cluster in clusters:
            print("Cluster %d" % cluster)
            print("----------")
            print(clusters[cluster])
