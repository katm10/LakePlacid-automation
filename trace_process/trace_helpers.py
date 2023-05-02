import os
from dataclasses import dataclass


@dataclass
class TraceType:
    count: int
    trace: dict


def read_trace_dir(dirname):
    traces = []
    functions = set()
    for fname in os.listdir(dirname):
        fname = dirname + "/" + fname
        if os.path.isfile(fname):
            trace, functions = read_trace(fname, functions)
            traces.append(trace)
    return traces, functions


def read_trace(fname, functions=set()):
    tf = open(fname, "r")
    command = tf.readline().strip()

    trace = {"command": command, "branches": {}}

    for line in tf:
        line = line.strip()
        tokens = line.split()

        if len(tokens) == 2:
            fname = tokens[1].strip()
            functions.add(fname)
        else:
            fname = tokens[1].strip()
            offset = int(tokens[2].strip())
            val = int(tokens[3].strip())
            if fname not in trace["branches"].keys():
                trace["branches"][fname] = {}
            if offset not in trace["branches"][fname].keys():
                trace["branches"][fname][offset] = val
            else:
                if trace["branches"][fname][offset] != val:
                    trace["branches"][fname][offset] = 2

    return trace, functions


def trace_equals(tr1, tr2):
    return tr1["branches"] == tr2["branches"]


"""
Given a set of traces, organize them into sets of equivalent traces.
"""


def bucket_traces(traces):
    trace_types = []

    def check_types(trace):
        for i in range(len(trace_types)):
            if trace_equals(trace, trace_types[i].trace):
                trace_types[i].count += 1
                return True
        return False

    for trace in traces:
        if not check_types(trace):
            trace_types.append(TraceType(1, trace))

    assert sum(trace_type.count for trace_type in trace_types) == len(traces)
    return trace_types
