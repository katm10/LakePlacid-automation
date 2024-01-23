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

    print(
        "Branch counts:\nlikely:{}\nunlikely:{}\nunknown:{}"
          .format(result_trace.count(BranchType.LIKELY),
                  result_trace.count(BranchType.UNLIKELY),
                  result_trace.count(BranchType.UNKNOWN)))
    
    print("Resulting manifest:")

    return chosen_traces


def print_manifest(chosen_traces, trace_types, function_indices):
    # Combine the traces
    combined_trace = combine_traces([trace_types[i].trace for i in chosen_traces])

    # Now print everything in the right format
    print(len(function_indices.keys()))

    for function_name, (start_indx, end_indx) in function_indices.items():
        branches = combined_trace[start_indx : end_indx + 1]
        n_branches = sum(branch != BranchType.UNUSED for branch in branches)
        if n_branches == 0:
            print(f"{function_name} 0 0")
        else:
            print(f"{function_name} {len(branches)} {n_branches}")

        for i, branch in enumerate(branches):
            if branch == BranchType.UNUSED:
                continue
            print(f"{i} {branch.value}")


def main():
    if len(sys.argv) < 2:
        print("Usage " + sys.argv[0] + " <filename>")
        exit(1)

    function_indices, traces = read_trace_dir(sys.argv[1])
    trace_types = bucket_traces(traces)

    chosen_dp = get_traces_dp(trace_types)
    print_manifest(chosen_dp, trace_types, function_indices)

    # chosen_simple = get_metrics(get_traces_greedy, trace_types)
    # print_manifest(chosen_simple, trace_types, function_indices)

    # chosen_brute = get_metrics(brute_force.get_traces, trace_types)
    # print_manifest(chosen_brute, trace_types, function_indices)

    # chosen_greedy = get_metrics(greedy.get_traces, trace_types)
    # print_manifest(chosen_greedy, trace_types, function_indices)


if __name__ == "__main__":
    main()
