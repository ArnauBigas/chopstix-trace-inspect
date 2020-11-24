#!/bin/python3

import argparse
import matplotlib.pyplot as plt
import numpy as np
from statistics import mean, stdev

from src.distance import disjoint_sets
from src.trace import Trace

parser = argparse.ArgumentParser(description="Inspect ChopStix traces")
parser.add_argument('trace_file')
parser.add_argument('metric', choices=['count', 'distance', 'nearest_neighbour'])
parser.add_argument('--num-threads', '-n', type=int)
args = parser.parse_args()

trace = Trace(args.trace_file, args.num_threads)

print("Analyzing %d subtraces" % trace.get_subtrace_count())

if (args.metric == 'count'):
    page_counts = list(map(lambda x: len(x.pages), trace.subtraces))
    print("Page count mean: %f, std. dev.: %f" % (mean(page_counts), stdev(page_counts)))

    print(np.unique(page_counts))
    plt.hist(page_counts, width=0.5)
    plt.show()
elif (args.metric == 'distance'):
    distance_matrix = trace.get_distance_matrix(disjoint_sets)

    distances = []
    for i in range(0, len(trace.subtraces)):
        for j in range(i, len(trace.subtraces)):
            distances.append(distance_matrix[i, j])

    plt.plot(range(len(distances)), np.sort(distances))
    plt.show()
elif args.metric == 'nearest_neighbour':
    distance_matrix = trace.get_distance_matrix(disjoint_sets)

    distances = []
    for i in range(0, len(trace.subtraces)):
        distances.append(min([distance_matrix[i, j] for j in range(0, len(trace.subtraces)) if j != i]))

    plt.plot(range(len(trace.subtraces)), np.sort(distances))
    plt.show()
