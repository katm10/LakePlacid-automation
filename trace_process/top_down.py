from trace_helpers import BranchType

"""
Dynamic Programming method:

A(k, j, Z) = min(f(Z, T_j) + A(k-1, j-1, Z U T_j), A(k, j-1, Z))

where
    A(k, j, Z) = the minimum number of unknowns while satisfying k traces
    f(Z, T_j) = how many unknowns are added by combining Z and T_j
    k = number of traces to satisfy
    j = index of the trace to add
    Z = the combined trace so far
"""
trace_types = []
memo = {}


def get_traces_dp(types, threshold=0.75):
    global trace_types
    trace_types = types

    trace_length = sum(trace_type.count for trace_type in trace_types)
    _, chosen = A(round(trace_length * threshold), len(trace_types) - 1, [BranchType.UNUSED] * len(trace_types[0].trace))

    return chosen


"""
See how many unknowns are added by combining Z and T_j
"""


def f(Z, T_j):
    assert(len(Z) == len(T_j))
    Z = Z.copy()
    unknowns = 0

    for i in range(len(T_j)):
        if Z[i] == BranchType.UNUSED:
            Z[i] = T_j[i]
        elif Z[i] == BranchType.UNKNOWN:
            continue
        elif Z[i] == BranchType.LIKELY:
            if T_j[i] == BranchType.UNLIKELY or T_j[i] == BranchType.UNKNOWN:
                Z[i] = BranchType.UNKNOWN
        elif Z[i] == BranchType.UNLIKELY:
            if T_j[i] == BranchType.LIKELY or T_j[i] == BranchType.UNKNOWN:
                Z[i] = BranchType.UNKNOWN
    
    return Z, unknowns


def A(k, j, Z, chosen=frozenset()):
    global memo

    if (k, j, chosen) in memo.keys():
        return memo[(k, j, chosen)]
    if k <= 0:
        return (0, chosen)
    if j < 0:
        return (float("inf"), chosen)

    T_j = trace_types[j].trace
    Z_with_j, unknowns_from_j = f(Z, T_j)

    unknowns_with_j, chosen_with_j = A(
        k - trace_types[j].count, j - 1, Z_with_j, chosen | {j}
    )
    unknowns_without_j, chosen_without_j = A(k, j - 1, Z, chosen)

    unknowns_with_j += unknowns_from_j

    if unknowns_with_j < unknowns_without_j:
        memo[(k, j, chosen)] = (unknowns_with_j, chosen_with_j | {j})
        return (unknowns_with_j, chosen_with_j | {j})
    else:
        memo[(k, j, chosen)] = (unknowns_without_j, chosen_without_j)
        return (unknowns_without_j, chosen_without_j)
