import sys
import greedy
import brute_force
from top_down import get_traces_dp
from trace_helpers import *
from time import perf_counter

"""
Goal: Given a percentage n of traces that should be completed within the kernel, find the minimum
set of functions to meet this requirement.

Ideas:
1.
    - Simplify trace info down to just (function_name, branch, is_taken) and store these in a set
        (ie. it does not matter if some branch is taken 1000x or 1x)
    - Sort traces by this new set length
    - Take a union over the n% of shortest traces

2.
    - Again, simplify trace info down to just (function_name, branch, is_taken) and store these in a set
    - Order branches by how many traces they are used in
    - Add all branches used in > n% of traces, test how many traces are now satisfied, rinse and
      repeat until n% is hit (maybe speed up a bit with binary search strategy)
"""


def get_traces_greedy(trace_types, threshold_p=0.75):
    # Greedily grab the most common trace types until we hit some threshold
    trace_length = sum(trace_type.count for trace_type in trace_types)
    threshold = int(threshold_p * trace_length)
    satisfied = 0

    trace_types = sorted(enumerate(trace_types), key=lambda x: x[1].count, reverse=True)
    i = 0
    chosen_types = []
    while satisfied < threshold:
        satisfied += trace_types[i][1].count
        chosen_types.append(trace_types[i][0])
        i += 1

    return chosen_types


def get_metrics(manifest_function, trace_types, threshold_p=0.75):
    init_time = perf_counter()
    chosen_traces = manifest_function(trace_types, threshold_p)
    end_time = perf_counter()

    result_trace = combine_traces([trace_types[i].trace for i in chosen_traces])

    print(f"Chosen traces: {[str(trace_types[i]) for i in chosen_traces]}")

    # Display time
    print(f"Time: {end_time - init_time}")

    # Get number of satisfied traces
    satisfied = sum(trace_types[i].count for i in chosen_traces)
    trace_length = sum(trace_type.count for trace_type in trace_types)
    print(f"Percent satisfied: {satisfied / trace_length * 100}")

    # Get count of unknowns
    branch_res = [0, 0, 0]
    for _, branches in result_trace.items():
        for _, value in branches.items():
            if value > 2:
                continue
            branch_res[value] += 1

    total_branches = sum(max(b.keys()) for _, b in result_trace.items())
    print(
        "Branch counts:\ntotal branches:{}\nlikely:{}\nunlikely:{}\nunknown:{}".format(
            total_branches, branch_res[0], branch_res[1], branch_res[2]
        )
    )

    print(chosen_traces)
    return chosen_traces


def print_manifest(chosen_traces, trace_types, functions):
    # Combine the traces
    combined_trace = combine_traces([trace_types[i].trace for i in chosen_traces])

    # Figure out which functions are never used here
    functions = set(f for f in functions if f not in combined_trace.keys())

    # Now print everything in the right format
    print(len(functions) + len(combined_trace))

    for f in functions:
        print(f + " 0 0")

    for f, branches in combined_trace.items():
        print(f + " " + str(1 + max(branches.keys())) + " " + str(len(branches)))


def main():
    if len(sys.argv) < 2:
        print("Usage " + sys.argv[0] + " <filename>")
        exit(1)

    traces, functions = read_trace_dir(sys.argv[1])
    trace_types = bucket_traces(traces)

    # chosen_dp = get_metrics(get_traces_dp, trace_types)
    # print_manifest(chosen_dp, trace_types, functions)

    # chosen_simple = get_metrics(get_traces_greedy, trace_types)
    # print_manifest(chosen_simple, trace_types, functions)

    chosen_brute = get_metrics(brute_force.get_traces, trace_types)
    print_manifest(chosen_brute, trace_types, functions)

    chosen_greedy = get_metrics(greedy.get_traces, trace_types)
    print_manifest(chosen_greedy, trace_types, functions)


if __name__ == "__main__":
    main()
