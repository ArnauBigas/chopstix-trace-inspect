#!/bin/python3

import argparse
import sys

from src.trace import Trace
from src.clustering import dbscan, estimate_dbscan_epsilon

parser = argparse.ArgumentParser(description="Inspect ChopStix traces")
parser.add_argument('trace_file')
parser.add_argument('--num-threads', '-n', type=int)
parser.add_argument('--epsilon', '-e', type=float)
parser.add_argument('--coverage', '-c', type=float, default=0.9)
parser.add_argument('--summary', '-s', action='store_true')
parser.add_argument('--max-memory', type=int)
args = parser.parse_args()

trace = Trace(args.trace_file, args.num_threads)

if args.max_memory != None:
    needed = trace.estimate_needed_memory() / (1024**2)
    if needed > args.max_memory:
        print("Need more memory than allowed to process trace: %d out of %d" % (needed, args.max_memory))
        sys.exit(-1)

print("Analyzing %d subtraces" % trace.get_subtrace_count())

epsilon = args.epsilon
if epsilon == None:
    epsilon = estimate_dbscan_epsilon(trace, args.coverage)

labels = dbscan(trace, epsilon)

clusters = {}
for i in range(len(labels)):
    label = labels[i]

    if label not in clusters:
        clusters[label] = []

    clusters[label].append(i)

if not args.summary:
    for cluster in clusters:
        print("Cluster %2d" % cluster)
        print("----------")
        print(clusters[cluster])
