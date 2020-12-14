#!/bin/python3

import argparse
from src.trace import Trace

parser = argparse.ArgumentParser(description="Inspect ChopStix traces")
parser.add_argument('trace_file')
args = parser.parse_args()

trace = Trace(args.trace_file)

print("Trace parsed.")
print("Invocation Count: ", trace.get_invocation_count())
print("Subtrace Count:   ", trace.get_subtrace_count())
