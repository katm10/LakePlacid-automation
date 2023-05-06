def count_unknowns(Z, T_j):
    unknowns = 0
    for function, branches in T_j["branches"].items():
        for offset, val in branches.items():
            if function not in Z.keys():
                Z[function] = {}
            if offset in Z[function].keys():
                if Z[function][offset] != val:
                    unknowns += 1
            else:
                if val == 2:
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
