import read_trace
import sys
import os
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


def print_manifest_old(trace):
    print(len(trace["functions"]))

    for f in trace["functions"]:
        offsets = []
        if f in trace["branches"]:
            for offset in trace["branches"][f].keys():
                offsets += [offset]
        if len(offsets) > 0:
            print(f + " " + str(1 + max(offsets)) + " " + str(len(offsets)))
        else:
            print(f + " 0 0")
        if f in trace["branches"]:
            for offset in trace["branches"][f].keys():
                values = trace["branches"][f][offset]
                choice = 0
                if len(values) > 1:
                    choice = 2
                elif len(values) == 1 and values[0] == 0:
                    choice = 0
                else:
                    choice = 1
                print(str(offset) + " " + str(choice))


def trace_equals(tr1, tr2):
    return tr1["branches"] == tr2["branches"]


def get_traces(traces):
    trace_types = []

    def check_types(trace):
        for i in range(len(trace_types)):
            trace_type = trace_types[i][0]
            if trace_equals(trace, trace_type):
                trace_types[i][1] += 1
                return True
        return False

    for trace in traces:
        if not check_types(trace):
            trace_types.append([trace, 1])

    assert sum(count for _, count in trace_types) == len(traces)

    # Greedily grab the most common trace types until we hit some threshold
    threshold_p = 0.75
    threshold = int(threshold_p * len(traces))
    satisfied = 0

    trace_types = sorted(trace_types, key=lambda x: x[1], reverse=True)
    i = 0
    while satisfied < threshold:
        satisfied += trace_types[i][1]
        i += 1

    """
    print(
        f"Satisfied {satisfied} out of {len(traces)} for {satisfied/len(traces)*100}%"
    )
    """
    return [trace_type for trace_type, _ in trace_types[:i]]


def print_manifest(traces, functions):
    traces = get_traces(traces)

    # Combine the traces
    combined_trace = {}
    for trace in traces:
        for function, branches in trace["branches"].items():
            if function not in combined_trace.keys():
                combined_trace[function] = {}
            for offset, val in branches.items():
                # if val > 2:
                    # print(f"{function} at offset {offset} has value {val}")
                if offset in combined_trace[function].keys():
                    if combined_trace[function][offset] != val:
                        combined_trace[function][offset] = 2
                else:
                    combined_trace[function][offset] = val

    # Figure out which functions are never used here
    functions = set(f for f in functions if f not in combined_trace.keys())

    # Now print everything in the right format
    print(len(functions) + len(combined_trace))

    for f in functions:
        print(f + " 0 0")

    branch_res = [0, 0, 0]
    for f, branches in combined_trace.items():
        print(f + " " + str(1 + max(branches.keys())) + " " + str(len(branches)))
        for offset, value in branches.items():
            #print(f"{offset} {value}")
            if value > 2:
                # print(f"WARNING: found switch (value {value})")
                continue
            branch_res[value] += 1

    # Some metrics
    total_branches = sum(max(b.keys()) for _, b in combined_trace.items())
    """
    print(
        "METRICS:\ntotal branches:{}\nlikely:{}\nunlikely:{}\nunknown:{}".format(
            total_branches, branch_res[0], branch_res[1], branch_res[2]
        )
    )
    """


def main():
    if len(sys.argv) < 2:
        print("Usage " + sys.argv[0] + " <filename>")
        exit(1)

    #t1 = perf_counter()
    print_manifest_old(read_trace.read_trace_dir_old(sys.argv[1]))
    #t2 = perf_counter()
    #traces, functions = read_trace.read_trace_dir(sys.argv[1])
    #print_manifest(traces, functions)
    #t3 = perf_counter()

    #print(f"Old method: {t2 - t1}")
    #print(f"New method: {t3 - t2}")


if __name__ == "__main__":
    main()
