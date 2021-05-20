#!/bin/python3

import argparse
from src.clustering import ClusteringInformation

def summary(args):
    cluster = ClusteringInformation.from_file(args.cluster_file)

    print("Cluster information parsed.")
    print("Epsilon parameter: ", cluster.get_epsilon())
    print("Invocation count: ", cluster.get_invocation_count())
    print("Cluster count: ", cluster.get_cluster_count())
    print("Noise invocations: ", cluster.get_noise_invocation_count())

def noise(args):
    cluster = ClusteringInformation.from_file(args.cluster_file)

    for invocation in cluster.get_noise_invocations():
        print(invocation)

def representative(args):
    cluster = ClusteringInformation.from_file(args.cluster_file)
    print(cluster.get_random_invocation(args.cluster_index))

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Inspect cluster data")

    subparsers = parser.add_subparsers()

    parser_summary = subparsers.add_parser('summary')
    parser_summary.set_defaults(function=summary)

    parser_summary = subparsers.add_parser('noise')
    parser_summary.set_defaults(function=noise)

    parser_summary = subparsers.add_parser('representative')
    parser_summary.add_argument('cluster_index', type=int)
    parser_summary.set_defaults(function=representative)

    parser.add_argument('cluster_file')

    args = parser.parse_args()
    args.function(args)
