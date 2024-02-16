from trace_helpers import BranchType


def count_unknowns(Z, T_j):
    assert len(Z) == len(T_j)
    unknowns = 0

    for i in range(len(T_j)):
        if Z[i] == BranchType.LIKELY:
            if T_j[i] == BranchType.UNLIKELY or T_j[i] == BranchType.UNKNOWN:
                unknowns += 1
        elif Z[i] == BranchType.UNLIKELY:
            if T_j[i] == BranchType.LIKELY or T_j[i] == BranchType.UNKNOWN:
                unknowns += 1

    return unknowns


def get_traces(trace_types, threshold=0.75):
    # Start with the most common trace type
    trace = max(trace_types, key=lambda x: x.count)
    j = trace_types.index(trace)
    Z = trace.trace

    # Find the trace with the minimum # of unknowns added at each step
    trace_length = sum(trace_type.count for trace_type in trace_types)
    threshold = int(threshold * trace_length)
    satisfied = trace.count
    chosen_types = [j]
    while satisfied < threshold:
        min_unknowns = float("inf")
        chosen_index = -1
        for i in range(len(trace_types)):
            if i in chosen_types:
                continue
            unknowns = count_unknowns(Z, trace_types[i].trace)
            if unknowns < min_unknowns:
                min_unknowns = unknowns
                chosen_index = i

        chosen_types.append(chosen_index)
        satisfied += trace_types[chosen_index].count

    return chosen_types
