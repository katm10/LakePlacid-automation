import itertools
from trace_helpers import *

def count_unknowns(combined_trace):
    unknowns = 0
    for _, branches in combined_trace.items():
        for _, value in branches.items():
            if value > 2:
                continue
            elif value == 2:
                unknowns += 1
    return unknowns

def get_traces(trace_types, threshold=0.75):
    types = list(range(len(trace_types)))

    trace_length = sum(trace_type.count for trace_type in trace_types)
    threshold = int(threshold * trace_length)

    min_unknowns = float("inf")
    min_chosen_types = []
    
    for i in range(len(trace_types)):
        for chosen_types in itertools.combinations(types, i):
            # Verify that this is valid
            satisfied = sum(trace_types[i].count for i in chosen_types)
            if satisfied < threshold:
                continue

            combined_trace = combine_traces([trace_types[i].trace for i in chosen_types])            
            unknowns = count_unknowns(combined_trace)
            if unknowns < min_unknowns:
                min_unknowns = unknowns
                min_chosen_types = chosen_types

    return min_chosen_types