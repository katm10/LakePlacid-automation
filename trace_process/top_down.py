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
    _, chosen = A(round(trace_length * threshold), len(trace_types) - 1)

    return chosen


"""
See how many unknowns are added by combining Z and T_j
"""


def f(Z, T_j):
    Z = Z.copy()
    unknowns = 0
    for function, branches in T_j["branches"].items():
        if function not in Z.keys():
            Z[function] = {}
        for offset, val in branches.items():
            if offset in Z[function].keys():
                if Z[function][offset] != val:
                    unknowns += 1
                    Z[function][offset] = 2
            else:
                Z[function][offset] = val
                if val == 2:
                    unknowns += 1
    return Z, unknowns


def A(k, j, chosen=frozenset(), Z={}):
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
        k - trace_types[j].count, j - 1, chosen | {j}, Z=Z_with_j
    )
    unknowns_without_j, chosen_without_j = A(k, j - 1, chosen, Z=Z)

    unknowns_with_j += unknowns_from_j

    if unknowns_with_j < unknowns_without_j:
        memo[(k, j, chosen)] = (unknowns_with_j, chosen_with_j | {j})
        return (unknowns_with_j, chosen_with_j | {j})
    else:
        memo[(k, j, chosen)] = (unknowns_without_j, chosen_without_j)
        return (unknowns_without_j, chosen_without_j)
