import sys
from trace_helpers import read_trace_dir


# TODO: it seems like nm isn't actually the solution here bc it is missing functions
def read_from_nm(nm_file, trace_dir):
    function_addresses = {}

    # Get all the functions from what appeared in the traces
    _, functions = read_trace_dir(trace_dir, preprocess=False)

    # Read the nm file and create a table of function name -> symbol address
    with open(nm_file, "r") as f:
        nm_lines = f.readlines()
        for line in nm_lines:
            # Format: <symbol address> <type> <symbol name>
            parts = line.split(" ")
            if len(parts) < 3:
                continue

            name = parts[2].strip()
            if name in functions:
                function_addresses[name] = parts[0].strip()

    # Sort the functions by address
    sorted_functions = sorted(function_addresses.items(), key=lambda x: int(x[1], 16))

    for f in sorted_functions:
        print(f[0])


def compare_functions(file1, file2):
    with open(file1, "r") as f1:
        fxns1 = set(f1.readlines())

    with open(file2, "r") as f2:
        fxns2 = set(f2.readlines())

    diff = fxns1 - fxns2

    for fxn in diff:
        print(fxn)


def main():
    if len(sys.argv) < 2:
        print("Usage " + sys.argv[0] + " <filename>")
        exit(1)

    _, functions = read_trace_dir(sys.argv[1], preprocess=False)
    for f in functions:
        print(f)


if __name__ == "__main__":
    main()
