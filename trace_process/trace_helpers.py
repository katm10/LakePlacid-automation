import os
from dataclasses import dataclass
from enum import Enum
from typing import List


class BranchType(Enum):
    LIKELY = 0
    UNLIKELY = 1
    UNKNOWN = 2
    UNUSED = -1


@dataclass
class Trace:
    command: str
    branches: List[BranchType]


@dataclass
class TraceType:
    command: str
    count: int
    trace: List[BranchType]

    def __str__(self):
        return f"command: {self.command}, count: {self.count}"


def read_trace_dir(dirname):
    traces = []
    functions = set()
    for fname in os.listdir(dirname):
        fname = dirname + "/" + fname
        if os.path.isfile(fname):
            trace, functions = read_trace(fname, functions)
            traces.append(trace)

    return preprocess_traces(traces, functions)


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
            functions.add(fname)
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


def preprocess_traces(traces, functions):
    function_indices = {}
    i = 0
    for function in functions:
        max_offset = 0
        max_offsets = [
            max(trace["branches"][function].keys())
            for trace in traces
            if function in trace["branches"].keys()
        ]
        if len(max_offsets) != 0:
            max_offset = max(max_offsets)
        function_indices[function] = (i, i + max_offset)
        i += max_offset + 1

    processed_traces = []
    for trace in traces:
        trace_array = [BranchType.UNUSED] * i
        for function, branches in trace["branches"].items():
            for offset, val in branches.items():
                if val > 2:
                    trace_array[function_indices[function][0] + offset] = BranchType.UNKNOWN
                    continue
                trace_array[function_indices[function][0] + offset] = BranchType(val)
        processed_traces.append(Trace(trace["command"], trace_array))

    return function_indices, processed_traces


"""
Given a set of traces, organize them into sets of equivalent traces.
"""


def bucket_traces(traces):
    trace_types = []

    def check_types(trace):
        for i in range(len(trace_types)):
            if trace.branches == trace_types[i].trace:
                trace_types[i].count += 1
                return True
        return False

    for trace in traces:
        if not check_types(trace):
            trace_types.append(TraceType(trace.command, 1, trace.branches))

    assert sum(trace_type.count for trace_type in trace_types) == len(traces)
    return trace_types


def combine_traces(traces):
    # Combine the traces
    n = len(traces[0])
    assert all(len(trace) == n for trace in traces)

    combined_trace = traces[0].copy()
    for trace in traces[1:]:
        for i in range(n):
            if combined_trace[i] == BranchType.UNUSED:
                combined_trace[i] = trace[i]
            elif combined_trace[i] == BranchType.UNKNOWN:
                continue
            elif combined_trace[i] == BranchType.LIKELY:
                if trace[i] == BranchType.UNLIKELY or trace[i] == BranchType.UNKNOWN:
                    combined_trace[i] = BranchType.UNKNOWN
            elif combined_trace[i] == BranchType.UNLIKELY:
                if trace[i] == BranchType.LIKELY or trace[i] == BranchType.UNKNOWN:
                    combined_trace[i] = BranchType.UNKNOWN

    return combined_trace
